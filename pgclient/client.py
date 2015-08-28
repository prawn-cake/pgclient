# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.pool as pgpool
import psycopg2.extras as pg_extras
import abc
import six
from contextlib import contextmanager


# TODO: use connection pool by default
# TODO: add transactional contextmanager


class DatabaseManager(object):
    def __init__(self, dsn=None, database=None, user=None, password=None,
                 host=None, port=None, pool_size=1):
        self.dsn = dsn

        # Pass connection params as is
        conn_params = dict(dsn=dsn, database=database, user=user,
                           password=password, host=host, port=port)
        if pool_size < 1:
            raise ValueError('Wrong pool_size value. Must be >= 1. '
                             'Current: {}'.format(pool_size))
        # Init thread-safe connection pool
        self.pool = pgpool.ThreadedConnectionPool(
            minconn=1, maxconn=pool_size, **conn_params)

    @property
    def connection(self):
        """Lazy connection property

        :return: postgresql connection instance
        """
        return self.pool.getconn()

    @contextmanager
    def _get_cursor(self, cursor_factory=None):
        conn = self.connection
        try:
            yield conn.cursor(cursor_factory=cursor_factory)
            conn.commit()
        except psycopg2.DatabaseError as err:
            conn.rollback()
            raise psycopg2.DatabaseError(err)
        finally:
            self.pool.putconn(conn)

    # TODO: rename it
    @property
    def cursor(self):
        return self._get_cursor()

    @property
    def dict_cursor(self):
        """Return dict cursor. It enables accessing via column names instead
        of indexes
        """
        return self._get_cursor(cursor_factory=pg_extras.DictCursor)


@six.add_metaclass(abc.ABCMeta)
class QuerySet(object):
    def __init__(self):
        self.request_tokens = []

    def execute(self, cursor):
        return cursor.execute(' '.join(self.request_tokens))


class SelectRequest(QuerySet):
    """The idea is use builder to select to database:
    select('*').from('my_table').where('a>b').order_by('desc').
    """
    def __init__(self):
        super(SelectRequest, self).__init__()

    def select(self, fields=None):
        self.request_tokens.append(fields or '*')
        return self

    def _from(self, table_name):
        self.request_tokens.append(table_name)
        return self

    def where(self, raw_condition=None):
        if raw_condition is not None:
            self.request_tokens.append(raw_condition)
        return self