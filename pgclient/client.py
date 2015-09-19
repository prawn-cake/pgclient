# -*- coding: utf-8 -*-
from contextlib import contextmanager

import psycopg2
import psycopg2.pool as pgpool
import psycopg2.extras as pg_extras


class PostgresClient(object):
    def __init__(self, dsn=None, database=None, user=None, password=None,
                 host=None, port=None, pool_size=1):
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
        self._pool = pgpool.ThreadedConnectionPool(
            minconn=1, maxconn=pool_size, **conn_params)

    def acquire_conn(self):
        """Get new pool connection

        :return: psycopg2 connection object
        """
        return self._pool.getconn()

    def release_conn(self, conn):
        """Release connection to a pool

        :param conn: psycopg2 connection object
        """
        self._pool.putconn(conn)

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
            conn.rollback()
            raise psycopg2.DatabaseError(err.message)
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