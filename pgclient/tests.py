# -*- coding: utf-8 -*-
import unittest
from pgclient.client import DatabaseManager


class DatabaseManagerTest(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager(dsn='localhost')

    def tearDown(self):
        pass

    def test_connection(self):
        conn = self.db_manager.connection
        self.assertTrue(conn)

    def test_cursor(self):
        with self.db_manager.cursor as cursor:
            result = cursor.execute('SELECT * FROM').fetchall()
        self.assertTrue(result)

    def test_dict_cursor(self):
        with self.db_manager.dict_cursor as cursor:
            result = cursor.execute('SELECT * FROM').fetchall()
        self.assertTrue(result)