# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras as pg_extras
import abc
import six
from contextlib import contextmanager


# TODO: use connection pool by default
# TODO: add transactional contextmanager


class DatabaseManager(object):
    def __init__(self, dsn, pool_size=1):
        self.dsn = dsn
        self._conn = None
        self.pool_size = pool_size

    @property
    def connection(self):
        """Lazy connection property

        :return: postgresql connection instance
        """
        if self._conn is None:
            self._conn = self._get_connection()
        return self._conn

    @property
    def cursor(self):
        return self.connection.cursor()

    @property
    def dict_cursor(self):
        """Return dict cursor. It enables accessing via column names instead
        of indexes
        """
        return self.connection.cursor(cursor_factory=pg_extras.DictCursor)

    def _get_connection(self):
        return psycopg2.connect(dsn=self.dsn)

    @contextmanager
    def get_transaction_cursor(self):
        """Public transaction context manager. Useful for getting transactional
         cursor to be able execute several SQL requests in one transaction

        Example:
            with db_manager.get_transaction_cursor() as t_cursor:
                t_cursor.execute('SELECT * FROM ...')
                t_cursor.execute('INSERT INTO my_table VALUES ...')

        So, the code above will be executed within one transaction

        """
        with self.connection as conn:
            with conn.cursor() as t_cursor:
                yield t_cursor


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