# -*- coding: utf-8 -*-
import abc
import six
from collections import OrderedDict, Iterable
import copy


@six.add_metaclass(abc.ABCMeta)
class BaseQueryBuilder(object):
    # OrderedDict must use here, define tokens and templates for each new query
    # class

    # NOTE: tokens order is important
    TOKENS = OrderedDict([
        # {token_key}, [{token_template}, {value}]
        # ('SELECT', ['SELECT %s', None]),
    ])

    def __init__(self):
        # Init tokens with templates
        # NOTE: tokens order is important
        self.tokens = copy.deepcopy(self.TOKENS)

    def _set_token(self, token_name, value):
        """Token setter

        :param token_name: str: name of token, i.e 'SELECT', 'FROM', etc
        :param value: value of token
        """
        self.tokens[token_name][1] = value

    def _reset_tokens(self, exclude=None):
        """Reset all tokens values excluding given

        :param exclude: Iterable: keys of exclude tokens
        """
        for key, (template, value) in self.tokens.items():
            if exclude and isinstance(exclude, Iterable):
                if key in exclude:
                    continue
            value = None

    def execute(self, cursor):
        """Build queryset and execute it

        :param cursor: connection.cursor
        :return: cursor: connection.cursor
        """
        return cursor.execute(
            # unpack ordered dict, build select string
            ' '.join([
                template for key, (template, value) in self.tokens.items()
                if value
            ]),

            # unpack ordered dict, pass values
            # isinstance(value, bool) -- need for such parameters as DESC
            # (without any values)
            tuple([
                value for key, (template, value) in self.tokens.items()
                if value and not isinstance(value, bool)])
        )


class SelectQuery(BaseQueryBuilder):
    """Select query builder.
    The idea is to use builder pattern to make select query to database with
    query tokens.

    For example:

    select('*')._from('my_table').where('a>b').order_by('desc').
    """
    TOKENS = OrderedDict([
        ('SELECT', ['SELECT %s', None]),
        ('FROM', ['FROM %s', None]),
        ('WHERE', ['WHERE %s', None]),
        ('GROUP_BY', ['GROUP BY %s', None]),
        ('ORDER_BY', ['ORDER BY %s', None]),
        ('DESC', ['DESC', None]),
        ('LIMIT', ['LIMIT %s', None]),
        ('OFFSET', ['OFFSET %s', None])
    ])

    def select(self, *fields):
        # Filter False parameters
        fields = filter(None, fields)
        if fields:
            self._set_token('SELECT', ', '.join(fields))
        else:
            self._set_token('SELECT', '*')
        return self

    def _from(self, table_name):
        """SQL FROM operator.
        NOTE: `from` is already reserved by python import, use `_from` instead

        :param table_name: str: table name
        """
        self._set_token('FROM', table_name)
        return self

    def where(self, raw_condition=None):
        if raw_condition is not None:
            self._set_token('WHERE', raw_condition)
        return self

    def order_by(self, *args):
        # Filter False args
        args = filter(None, args)
        if args:
            self._set_token('ORDER_BY', ', '.join(args))
        return self

    def desc(self):
        """Ordering descending option
        """
        self._set_token('DESC', True)
        return self

    def limit(self, value):
        self._set_token('LIMIT', int(value))
        return self

    def group_by(self, *args):
        args = filter(None, args)
        if args:
            self._set_token('GROUP_BY', ', '.join(args))
        return self


class InsertQuery(BaseQueryBuilder):
    """Insert query builder.
    Workflow:

    >>> insert_query.into('MyTable')
        .fields('name', 'gender',)
        .values('Alex', 'M')
        .returning('id')
        .execute(cursor)

    """

    TOKENS = OrderedDict([
        ('INSERT', ['INSERT INTO %s', None]),
        ('DEFAULT', ['DEFAULT VALUES', None]),  # for all default values
        ('fields', ['(%s)', None]),             # non-sql token
        ('VALUES', ['VALUES (%s)', None]),
        ('values_multi', ['VALUES %s', None]),  # for multiple rows
        ('RETURNING', ['RETURNING %s', None]),
    ])

    def into(self, table_name):
        self._set_token('INSERT', table_name)
        return self

    def fields(self, *fields):
        fields = filter(None, fields)
        self._set_token('fields', ', '.join(fields))
        return self

    def values(self, *values):
        self._set_token('VALUES', ', '.join(values))
        return self

    def values_multi(self, list_of_values):
        """Method allows to build multiple rows insert

        :param list_of_values: Iterable: list of multiple rows values
        For example:
            [('Alex', 'M'), ('Jane', 'F')]

        """
        if isinstance(list_of_values, Iterable):
            prepared_values = [', '.join(item) for item in list_of_values]
            self._set_token(
                'values_multi',
                # prepare rows by join of prepared_values
                ', '.join(['({})'.format(item) for item in prepared_values])
            )
        return self

    def defaults(self):
        """Allows to insert row with all defaults values
        Simulate the following: INSERT INTO {table_name} DEFAULT VALUES'
        """
        # reset tokens exclude table name
        self._reset_tokens(exclude=('INSERT', ))
        self._set_token('DEFAULT', True)
        return self

    def returning(self, *fields):
        fields = filter(None, fields)
        self._set_token('RETURNING', ', '.join(fields))
        return self


class UpdateQuery(BaseQueryBuilder):
    pass


class DeleteQuery(BaseQueryBuilder):
    pass


class QueryFacade(object):
    """Query facade. Combine all queries into the one facade

    Usage:
    >>> from pgclient.query import query_facade as qf

    >>> qs = qf.select('id', 'name')._from('MyTable').execute(cursor)
    >>> result_set = qs.fetchall()
    """

    @staticmethod
    def select(*fields):
        return SelectQuery().select(*fields)

    @staticmethod
    def insert(table_name):
        return InsertQuery().into(table_name)

    @staticmethod
    def update(self):
        raise NotImplementedError('Not yet implemented')

    @staticmethod
    def delete(self):
        raise NotImplementedError('Not yet implemented')


query_facade = QueryFacade()