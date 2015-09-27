# -*- coding: utf-8 -*-
import logging
from contextlib import contextmanager

import psycopg2
import psycopg2.pool as pgpool
import psycopg2.extras as pg_extras
import time

from pgclient.exceptions import ErrorsRegistry


__all__ = ['PostgresClient']

logger = logging.getLogger('postgres-client')


class ReliableThreadConnectionPool(pgpool.ThreadedConnectionPool):
    """Thread connection pool with auto-reconnect feature"""

    def __init__(self, minconn, maxconn, auto_reconnect=True, *args, **kwargs):
        self.auto_reconnect = auto_reconnect
        super(ReliableThreadConnectionPool, self).__init__(minconn, maxconn,
                                                           *args, **kwargs)

    def _connect(self, key=None):
        """Overridden connect method with reconnection features"""

        if not self.auto_reconnect:
            return super(ReliableThreadConnectionPool, self)._connect(key=key)

        conn = None
        while conn is None:
            try:
                conn = super(ReliableThreadConnectionPool, self)._connect(
                    key=key)
            except psycopg2.DatabaseError as err:
                error = ErrorsRegistry.get_error(pg_error=err)
                logger.warning(str(error))
                logger.info('Reconnecting')
                time.sleep(1)
        return conn


class PostgresClient(object):
    def __init__(self, dsn=None, database=None, user=None, password=None,
                 host=None, port=None, pool_size=1, auto_reconnect=True):
        self.dsn = dsn

        # Pass connection params as is
        conn_params = dict(dsn=dsn,
                           database=database,
                           user=user,
                           password=password,
                           host=host,
                           port=port)
        if pool_size < 1:
            raise ValueError('Wrong pool_size value. Must be >= 1. '
                             'Current: {}'.format(pool_size))
        # Init thread-safe connection pool
        self._pool = ReliableThreadConnectionPool(
            minconn=1, maxconn=pool_size, auto_reconnect=auto_reconnect,
            **conn_params)
        self.auto_reconnect = auto_reconnect

    def acquire_conn(self):
        """Get new pool connection

        :return: psycopg2 connection object
        :raise: psycopg2.pool.PoolError: when is no available connections
        """
        conn = self._pool.getconn()
        if self.auto_reconnect:
            conn = self._check_connection(conn=conn)
        return conn

    def release_conn(self, conn, close=False):
        """Release connection to a pool
        Connection will be returned into the pool in a consistent state
        (idle transaction will be rolled back, unknown - closed)

        :param close: enforce to close connection parameter
        :param conn: psycopg2 connection object
        """
        self._pool.putconn(conn, close=close)

    def _check_connection(self, conn):
        """Check connection aliveness and reconnect in case of errors

        :param conn: psycopg connection instance
        :return: working psycopg connection instance
        """
        is_connection_alive = False
        while not is_connection_alive:
            try:
                # Check if connection is alive
                conn.cursor().execute('SELECT 1')
            except psycopg2.Error:
                # The connection is not working, need reconnect
                self._pool.putconn(conn=conn, close=True)
                time.sleep(1)
                conn = self._pool._getconn()
            else:
                is_connection_alive = True
        return conn

    @contextmanager
    def _get_cursor(self, cursor_factory=None):
        """Get connection cursor context manager

        :param cursor_factory: pg_extras.* cursor factory class
        """
        conn = self.acquire_conn()
        try:
            yield conn.cursor(cursor_factory=cursor_factory)
            conn.commit()
        except psycopg2.DatabaseError as err:
            try:
                conn.rollback()
            except psycopg2.Error:
                # connection already closed on rollback
                pass
            raise ErrorsRegistry.get_error(pg_error=err)
        finally:
            self.release_conn(conn)

    @property
    def cursor(self):
        """Default index based cursor"""

        return self._get_cursor()

    @property
    def dict_cursor(self):
        """Return dict cursor. It enables to get fields access via column names
        instead of indexes.
        """
        return self._get_cursor(cursor_factory=pg_extras.DictCursor)

    @property
    def nt_cursor(self):
        """Named tuple based cursor. It enables to get attributes access via
        attributes.
        """
        return self._get_cursor(cursor_factory=pg_extras.NamedTupleCursor)

    @property
    def available_connections(self):
        """Connection pool available connections

        :return: int: number of available connections
        """
        return len(self._pool._pool)