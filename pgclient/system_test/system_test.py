# -*- coding: utf-8 -*-
"""Integration system test for database manager"""

import sys
import os.path as op
import psycopg2

sys.path.append(
    op.abspath(op.dirname(__file__)) + '/../'
)

import unittest
from pgclient.client import DatabaseManager
import random


NAMES = ['Alex', 'Andrea', 'Ashley', 'Casey', 'Chris', 'Dorian', 'Jerry']


class DatabaseManagerSystemTest(unittest.TestCase):
    DB_USER = 'postgres'
    DB_PASSWORD = 'test'
    DB_NAME = 'test'
    TABLE_NAME = 'users'

    def setUp(self):
        dsn = 'user={} password={} dbname={} host=localhost'.format(
            self.DB_USER, self.DB_PASSWORD, self.DB_NAME)
        self.db_manager = DatabaseManager(dsn=dsn, pool_size=10)

        try:
            self._create_table()
        except psycopg2.DatabaseError:
            self._drop_table()
            self._create_table()

        # Insert 100 entries
        with self.db_manager.cursor as cursor:
            for _ in range(100):
                insert_str = "INSERT INTO {} (username) VALUES (%s)".format(
                    self.TABLE_NAME)
                cursor.execute(insert_str, (random.choice(NAMES),))

    def _create_table(self):
        # Init database with test data
        with self.db_manager.cursor as cursor:
            cursor.execute(
                "CREATE TABLE {} "
                "(id serial PRIMARY KEY, username VARCHAR NOT NULL );".format(
                    self.TABLE_NAME))
        print('Table {} has been created'.format(self.TABLE_NAME))

    def _drop_table(self):
        with self.db_manager.cursor as cursor:
            cursor.execute('DROP TABLE {}'.format(self.TABLE_NAME))
        print('Table {} has been dropped'.format(self.TABLE_NAME))

    def tearDown(self):
        self._drop_table()

    def test_cursor(self):
        with self.db_manager.cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result_set = cursor.fetchall()
        self.assertEqual(len(result_set), 100)

    def test_dict_cursor(self):
        with self.db_manager.dict_cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result_set = cursor.fetchall()
        item = result_set[0]
        self.assertIn('id', item)
        self.assertIn('username', item)
        self.assertIn(item['username'], NAMES)

    def test_named_tuple_cursor(self):
        with self.db_manager.nt_cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result_set = cursor.fetchall()
        item = result_set[0]
        self.assertIsInstance(item.id, int)
        self.assertIsInstance(item.username, str)

    def test_success_transaction(self):
        with self.db_manager.cursor as transaction:
            insert_str = "INSERT INTO {} (username) VALUES (%s)".format(
                self.TABLE_NAME)
            transaction.execute(insert_str, (random.choice(NAMES), ))
            transaction.execute('SELECT * FROM users')
            result_set = transaction.fetchall()
        self.assertEqual(len(result_set), 101)

    def test_rollback_transaction(self):
        with self.db_manager.cursor as transaction:
            with self.assertRaises(psycopg2.DatabaseError) as err:
                transaction.execute(
                    "INSERT INTO {} (username) VALUES (%s)".format(self.TABLE_NAME),
                    (None, ))
            self.assertIn('null value in column', err.exception.message)


if __name__ == '__main__':
    unittest.main()