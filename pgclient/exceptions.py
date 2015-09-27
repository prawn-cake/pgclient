# -*- coding: utf-8 -*-
from psycopg2 import errorcodes as codes


class PgClientError(Exception):
    """ Common pgclient exception class"""
    CLASS_CODE = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__,
            getattr(self, 'message'),
            getattr(self, 'pgcode'),
            getattr(self, 'diag'))


class ErrorsRegistry(object):
    """Registry for all-related postgres errors.
    The idea is to translate psycopg2.Error to more meaningful classes"""

    ERRORS = {}

    @classmethod
    def register(cls, code):
        """Register decorator

        :param code: postgres class error code, for example '08'
        """

        def wrapper(klass):
            klass.CLASS_CODE = code
            cls.ERRORS[code] = klass
            return klass

        return wrapper

    @classmethod
    def get_error_class(cls, pg_code):
        """Get error class from registry by pg code (internal postgresql code)

        :param pg_code: str
        :return:
        """
        return cls.ERRORS.get(pg_code[:2])

    @classmethod
    def get_error(cls, pg_error):
        """Get error instance by psycopg2.Error

        :param pg_error: psycopg2.Error instance
        :return: PgClientError instance
        """
        error_cls = cls.get_error_class(pg_error.pgcode)
        return error_cls(
            message=getattr(pg_error, 'message', pg_error.pgerror),
            pgcode=pg_error.pgcode,
            pgerror=pg_error.pgerror,
            diag=pg_error.diag)


registry = ErrorsRegistry


@registry.register(code=codes.CLASS_SUCCESSFUL_COMPLETION)
class SuccessfulCompletion(PgClientError):
    pass


@registry.register(code=codes.CLASS_WARNING)
class PgWarning(PgClientError):
    pass


@registry.register(code=codes.CLASS_NO_DATA)
class NoDataWarning(PgClientError):
    pass


@registry.register(code=codes.CLASS_SQL_STATEMENT_NOT_YET_COMPLETE)
class SQLStatementNotYetComplete(PgClientError):
    pass


@registry.register(code=codes.CLASS_CONNECTION_EXCEPTION)
class ConnectionException(PgClientError):
    pass


@registry.register(code=codes.CLASS_TRIGGERED_ACTION_EXCEPTION)
class TriggeredActionException(PgClientError):
    pass


@registry.register(code=codes.CLASS_FEATURE_NOT_SUPPORTED)
class FeatureNotSupported(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_TRANSACTION_INITIATION)
class InvalidTransactionInitiation(PgClientError):
    pass


@registry.register(code=codes.CLASS_LOCATOR_EXCEPTION)
class LocatorException(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_GRANTOR)
class InvalidGrantor(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_ROLE_SPECIFICATION)
class InvalidRoleSpecification(PgClientError):
    pass


@registry.register(code=codes.CLASS_DIAGNOSTICS_EXCEPTION)
class DiagnosticsException(PgClientError):
    pass


@registry.register(code=codes.CLASS_CASE_NOT_FOUND)
class CaseNotFound(PgClientError):
    pass


@registry.register(code=codes.CLASS_CARDINALITY_VIOLATION)
class CardinalityViolation(PgClientError):
    pass


@registry.register(code=codes.CLASS_DATA_EXCEPTION)
class DataException(PgClientError):
    pass


@registry.register(code=codes.CLASS_INTEGRITY_CONSTRAINT_VIOLATION)
class IntegrityConstraintViolation(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_CURSOR_STATE)
class InvalidCursorState(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_TRANSACTION_STATE)
class InvalidTransactionState(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_SQL_STATEMENT_NAME)
class InvalidSQLStatementName(PgClientError):
    pass


@registry.register(code=codes.CLASS_TRIGGERED_DATA_CHANGE_VIOLATION)
class TriggeredDataChangeViolation(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_AUTHORIZATION_SPECIFICATION)
class InvalidAuthorizationSpecification(PgClientError):
    pass


@registry.register(
    code=codes.CLASS_DEPENDENT_PRIVILEGE_DESCRIPTORS_STILL_EXIST)
class DependentPrivilegeDescriptorsStillExist(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_TRANSACTION_TERMINATION)
class InvalidTransactionTermination(PgClientError):
    pass


@registry.register(code=codes.CLASS_SQL_ROUTINE_EXCEPTION)
class SQLRoutineException(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_CURSOR_NAME)
class InvalidCursorName(PgClientError):
    pass


@registry.register(code=codes.CLASS_EXTERNAL_ROUTINE_EXCEPTION)
class ExternalRoutineException(PgClientError):
    pass


@registry.register(code=codes.CLASS_EXTERNAL_ROUTINE_INVOCATION_EXCEPTION)
class ExternalRoutineInvocationException(PgClientError):
    pass


@registry.register(code=codes.CLASS_SAVEPOINT_EXCEPTION)
class SavepointException(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_CATALOG_NAME)
class InvalidCatalogName(PgClientError):
    pass


@registry.register(code=codes.CLASS_INVALID_SCHEMA_NAME)
class InvalidSchemaName(PgClientError):
    pass


@registry.register(code=codes.CLASS_TRANSACTION_ROLLBACK)
class TransactionRollback(PgClientError):
    pass


@registry.register(code=codes.CLASS_SYNTAX_ERROR_OR_ACCESS_RULE_VIOLATION)
class SyntaxErrorOrAccessRuleViolation(PgClientError):
    pass


@registry.register(code=codes.CLASS_WITH_CHECK_OPTION_VIOLATION)
class WithCheckOptionViolation(PgClientError):
    pass


@registry.register(code=codes.CLASS_INSUFFICIENT_RESOURCES)
class InsufficientResources(PgClientError):
    pass


@registry.register(code=codes.CLASS_PROGRAM_LIMIT_EXCEEDED)
class ProgramLimitExceeded(PgClientError):
    pass


@registry.register(code=codes.CLASS_OBJECT_NOT_IN_PREREQUISITE_STATE)
class ObjectNotInPrerequisiteState(PgClientError):
    pass


@registry.register(code=codes.CLASS_OPERATOR_INTERVENTION)
class OperatorIntervention(PgClientError):
    pass


@registry.register(code=codes.CLASS_SYSTEM_ERROR)
class PgSystemError(PgClientError):
    pass


@registry.register(code=codes.CLASS_CONFIGURATION_FILE_ERROR)
class ConfigurationFileError(PgClientError):
    pass


@registry.register(code=codes.CLASS_FOREIGN_DATA_WRAPPER_ERROR)
class ForeignDataWrapperError(PgClientError):
    pass


@registry.register(code=codes.CLASS_PL_PGSQL_ERROR)
class PLPgSQLError(PgClientError):
    pass


@registry.register(code=codes.CLASS_INTERNAL_ERROR)
class InternalError(PgClientError):
    pass