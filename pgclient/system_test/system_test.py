# -*- coding: utf-8 -*-
"""Integration system test for database manager"""

import sys
import os
import os.path as op
import psycopg2
from psycopg2.pool import PoolError
import time

sys.path.append(
    op.abspath(op.dirname(__file__)) + '/../'
)

import unittest
import random
from pgclient.client import PostgresClient


NAMES = ['Alex', 'Andrea', 'Ashley', 'Casey', 'Chris', 'Dorian', 'Jerry']


class PostgresClientSystemTest(unittest.TestCase):
    DB_USER = 'postgres'
    DB_PASSWORD = 'test'
    DB_NAME = 'test'
    DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
    TABLE_NAME = 'users'
    POOL_SIZE = 3

    def setUp(self):
        self.dsn = 'user={} password={} dbname={} host=localhost port={}'\
            .format(self.DB_USER, self.DB_PASSWORD, self.DB_NAME, self.DB_PORT)
        try:
            self.pg_client = PostgresClient(dsn=self.dsn,
                                            pool_size=self.POOL_SIZE)
        except psycopg2.OperationalError as err:
            print('Check that postgres docker container is started. '
                  'Check README for more information')
            raise psycopg2.OperationalError(err.message)

        try:
            self._create_table()
        except psycopg2.DatabaseError:
            self._drop_table()
            self._create_table()

        # Insert 100 entries
        with self.pg_client.cursor as cursor:
            for _ in range(100):
                insert_str = "INSERT INTO {} (username) VALUES (%s)".format(
                    self.TABLE_NAME)
                cursor.execute(insert_str, (random.choice(NAMES),))

    def _create_table(self):
        # Init database with test data
        with self.pg_client.cursor as cursor:
            cursor.execute(
                "CREATE TABLE {} "
                "(id SERIAL, username VARCHAR NOT NULL );".format(
                    self.TABLE_NAME))
        print('Table {} has been created'.format(self.TABLE_NAME))

    def _drop_table(self):
        with self.pg_client.cursor as cursor:
            cursor.execute('DROP TABLE {}'.format(self.TABLE_NAME))
        print('Table {} has been dropped'.format(self.TABLE_NAME))

    def tearDown(self):
        self._drop_table()

    def test_create_with_wrong_pool_value(self):
        with self.assertRaises(ValueError) as err:
            pg_client = PostgresClient(dsn=self.dsn, pool_size=0)
            self.assertIsNone(pg_client)
            self.assertIn('Wrong pool_size value', err)

    def test_cursor(self):
        with self.pg_client.cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result_set = cursor.fetchall()
        self.assertEqual(len(result_set), 100)

    def test_dict_cursor(self):
        with self.pg_client.dict_cursor as cursor:
            cursor.execute('SELECT * FROM users')
        result_set = cursor.fetchall()
        item = result_set[0]
        self.assertIn('id', item)
        self.assertIn('username', item)
        self.assertIn(item['username'], NAMES)

    def test_named_tuple_cursor(self):
        with self.pg_client.nt_cursor as cursor:
            cursor.execute('SELECT * FROM users')
        result_set = cursor.fetchall()
        item = result_set[0]
        self.assertIsInstance(item.id, int)
        self.assertIsInstance(item.username, str)

    def test_success_transaction(self):
        with self.pg_client.cursor as transaction:
            insert_str = "INSERT INTO {} (username) VALUES (%s)".format(
                self.TABLE_NAME)
            transaction.execute(insert_str, (random.choice(NAMES), ))
            transaction.execute('SELECT * FROM users')
        result_set = transaction.fetchall()
        self.assertEqual(len(result_set), 101)

    def test_rollback_transaction(self):
        # Inserting null username value must raise an error
        with self.assertRaises(psycopg2.DatabaseError) as err:
            with self.pg_client.cursor as transaction:
                transaction.execute(
                    "INSERT INTO {} (username) VALUES (%s)".format(
                        self.TABLE_NAME),
                    (None, ))
                print('abc')
        self.assertIn('null value in column', str(err.exception))
        print('transaction finished')

    def test_connection_pool_overflow(self):
        # Consume all connection to check overflow case
        connections = []
        for i in range(self.POOL_SIZE):
            connections.append(self.pg_client.acquire_conn())

        with self.assertRaises(PoolError) as err:
            with self.pg_client.cursor as cursor:
                self.assertIsNone(cursor)
                self.assertIn('connection pool exhausted', err)

        # Release all connections back to pool
        for conn in connections:
            self.pg_client.release_conn(conn)

    @unittest.skip('docker container is not prepared for this')
    def test_reconnection(self):
        """This test should be long.

        """
        for _ in range(10):
            with self.pg_client.cursor as cursor:
                time.sleep(0.5)
                cursor.execute('SELECT * FROM users')
                time.sleep(0.5)
            result_set = cursor.fetchall()
            self.assertTrue(result_set)
            time.sleep(1)