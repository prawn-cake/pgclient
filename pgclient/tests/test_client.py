# -*- coding: utf-8 -*-
import unittest
import psycopg2._psycopg
from psycopg2.pool import PoolError
from pgclient.client import DatabaseManager
import mock


class DatabaseManagerTest(unittest.TestCase):
    def setUp(self):
        connection_mock = mock.MagicMock(spec=psycopg2._psycopg.connection)
        self.patcher = mock.patch('psycopg2.connect',
                                  return_value=connection_mock)
        self.patcher.start()
        self.db_manager = DatabaseManager(dsn='fake dsn')

    def tearDown(self):
        self.patcher.stop()

    def test_init(self):
        # Expect absence of errors
        db_manager = DatabaseManager(dsn='fake dsn')
        self.assertIsInstance(db_manager, DatabaseManager)

        # Test wrong pool_size value
        with self.assertRaises(ValueError) as err:
            db_manager = DatabaseManager(dsn='fake dsn', pool_size=0)
            self.assertIsNone(db_manager)
            self.assertIn('Wrong pool_size value', err)

    def test_connection(self):
        self.assertEqual(self.db_manager.available_connections, 1)
        with self.db_manager.dict_cursor as cursor:
            self.assertTrue(cursor)
            self.assertEqual(self.db_manager.available_connections, 0)

    def test_cursor(self):
        data = dict(id=0, username='john')
        return_data = (data.values(), )
        with self.db_manager.cursor as cursor:
            cursor.fetchall.return_value = return_data
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchall()
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0][0], 'john')

    def test_dict_cursor(self):
        with self.db_manager.dict_cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchall()
        self.assertTrue(result)

    def test_named_tuple_cursor(self):
        with self.db_manager.nt_cursor as cursor:
            cursor.execute('SELECT * FROM users')
            result = cursor.fetchall()
        self.assertTrue(result)

    def test_connection_pool_overflow(self):
        with self.db_manager.cursor as cursor1:
            # first connection has got at this point
            self.assertTrue(cursor1)
            with self.assertRaises(PoolError) as err:
                with self.db_manager.cursor as cursor2:
                    self.assertIsNone(cursor2)
                    self.assertIn('connection pool exhausted', err)