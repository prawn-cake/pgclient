# -*- coding: utf-8 -*-
import unittest
from pgclient.query import query_facade as qf
from pgclient.query import BaseQueryBuilder
import mock


class BaseQueryBuilderTest(unittest.TestCase):
    pass


class SelectQueryTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = mock.MagicMock()

    def check_calls(self, expected_calls):
        self.assertTrue(self.mock_cursor.execute.called)
        self.assertEqual(
            self.mock_cursor.execute.call_args_list,
            expected_calls)

    def test_simple_select(self):
        # Reset mock firstly
        self.mock_cursor.reset_mock()

        qf.select('')._from('MyTable').execute(self.mock_cursor)
        expected_calls = [mock.call('SELECT %s FROM %s', ('*', 'MyTable'))]
        self.check_calls(expected_calls)

    def test_select_with_params(self):
        self.mock_cursor.reset_mock()

        qf.select('id', 'name')._from('MyTable').execute(self.mock_cursor)
        expected_calls = [
            mock.call('SELECT %s FROM %s', ('id, name', 'MyTable'))]
        self.check_calls(expected_calls)

    def test_select_with_all_params(self):
        self.mock_cursor.reset_mock()

        qf.select('id', 'name', 'visits')\
            ._from('MyTable')\
            .where('id > name')\
            .group_by('visits')\
            .order_by('name').desc().limit(10)\
            .execute(self.mock_cursor)

        expected_calls = [
            mock.call(
                'SELECT %s FROM %s WHERE %s '
                'GROUP BY %s '
                'ORDER BY %s '
                'DESC LIMIT %s',
                ('id, name, visits', 'MyTable', 'id > name', 'visits', 'name',
                 10))
        ]
        self.check_calls(expected_calls)


class InsertQueryTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = mock.MagicMock()

    def check_calls(self, expected_calls):
        self.assertTrue(self.mock_cursor.execute.called)
        self.assertEqual(
            self.mock_cursor.execute.call_args_list,
            expected_calls)

    def test_insert_single_row(self):
        self.mock_cursor.reset_mock()
        qf.insert('MyTable')\
            .values('Alex', 'M')\
            .execute(self.mock_cursor)

        expected_calls = [
            mock.call('INSERT INTO %s VALUES (%s)', ('MyTable', 'Alex, M'))
        ]
        self.check_calls(expected_calls)

    def test_insert_single_row_with_fields(self):
        self.mock_cursor.reset_mock()
        qf.insert('MyTable')\
            .fields('name', 'gender')\
            .values('Alex', 'M')\
            .returning('id')\
            .execute(self.mock_cursor)

        expected_calls = [
            mock.call(
                'INSERT INTO %s (%s) VALUES (%s) RETURNING %s',
                ('MyTable', 'name, gender', 'Alex, M', 'id'))
        ]
        self.check_calls(expected_calls)

    def test_insert_row_with_all_defaults_values(self):
        self.mock_cursor.reset_mock()
        qf.insert('MyTable').defaults().execute(self.mock_cursor)

        expected_calls = [
            mock.call(
                'INSERT INTO %s DEFAULT VALUES',
                ('MyTable', ))
        ]
        self.check_calls(expected_calls)

    def test_insert_multiple_rows(self):
        self.mock_cursor.reset_mock()
        values = [('Alex', 'M'), ('Jane', 'F')]
        qf.insert('MyTable')\
            .values_multi(values)\
            .execute(self.mock_cursor)

        expected_calls = [
            mock.call(
                'INSERT INTO %s VALUES %s',
                ('MyTable', '(Alex, M), (Jane, F)'))
        ]
        self.check_calls(expected_calls)