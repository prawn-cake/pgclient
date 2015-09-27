# -*- coding: utf-8 -*-
import unittest
import psycopg2
import mock
from pgclient.exceptions import ErrorsRegistry as registry, PgClientError


class ErrorsRegistryTest(unittest.TestCase):
    def test_registry(self):
        from psycopg2 import errorcodes
        codes = {k: v for k, v in errorcodes.__dict__.items()
                 if k.startswith('CLASS_')}

        self.assertTrue(registry.ERRORS)
        # print(set(codes.values()) - set(registry.ERRORS.keys()))
        self.assertEqual(len(codes), len(registry.ERRORS))
        for code, cls in registry.ERRORS.items():
            self.assertTrue(issubclass(cls, PgClientError))

    def test_get_error_class(self):
        pg_code = '42P01'
        cls = registry.get_error_class(pg_code)
        self.assertTrue(issubclass(cls, PgClientError))
        self.assertEqual(cls.CLASS_CODE, '42')

    def test_get_error(self):
        error = mock.MagicMock(spec=psycopg2.Error)
        pg_code = '08006'
        pg_error = 'error'
        diag = 'connection_failure'
        message = 'Connection failure'
        setattr(error, 'pgcode', pg_code)
        setattr(error, 'pgerror', pg_error)
        setattr(error, 'diag', diag)
        setattr(error, 'message', message)
        instance = registry.get_error(error)
        self.assertIsInstance(instance, PgClientError)

        self.assertEqual(instance.message, message)
        self.assertEqual(instance.pgcode, pg_code)
        self.assertTrue(instance.diag, diag)
        self.assertIn(instance.pgerror, pg_error)