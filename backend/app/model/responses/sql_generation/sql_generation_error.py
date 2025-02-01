from enum import Enum
from pydantic import BaseModel
from typing import Any, List, Optional, Dict

from model.query_scope.query_scope import QueryScope

class ErrorType(str, Enum):
    """
    Enum for different types of errors that can occur during SQL generation.
    """
    ACCESS_DENIED = "access_denied"
    QUERY_SCOPE_ERROR = "query_scope_error"
    SCHEMA_DISCOVERY_ERROR = "schema_discovery_error"
    VALIDATION_ERROR = "validation_error"
    RUNTIME_ERROR = "runtime_error"

class AccessViolationType(str, Enum):
    """
    Enum for different types of access violations.
    """
    TABLE_ACCESS_DENIED = "table_access_denied"
    COLUMN_ACCESS_DENIED = "column_access_denied"
    POLICY_VIOLATION = "policy_violation"
    MISSING_PERMISSION = "missing_permission"

class QueryScopeErrorType(str, Enum):
    """
    Enum for different types of query scope resolution errors.
    """
    NO_COLUMN_REMAIN = "no_column_remain"
    COLUMN_NOT_QUALIFIED = "column_not_qualified"
    TABLE_NOT_FOUND = "table_not_found"
    COLUMN_NOT_FOUND = "column_not_found"
    UNRESOLVED_WILDCARD = "unresolved_wildcard"
    INVALID_SYNTAX = "invalid_syntax"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"

class SchemaDiscoveryErrorType(str, Enum):
    """
    Enum for different types of schema discovery errors.
    """
    NO_MATCHING_SCHEMA = "no_matching_schema"
    MULTIPLE_SCHEMAS = "multiple_schemas"
    INVALID_SCHEMA = "invalid_schema"
    SCHEMA_NOT_FOUND = "schema_not_found"

class AccessViolation(BaseModel):
    """
    Represents an access violation error in SQL generation.

    Attributes:
        entity (str): The name of the table or column where the access violation occurred.
        policy_type (str): The type of policy that was violated. Can be "global", "group", or "user".
        policy_name (Optional[str]): The name of the group or the user ID if applicable. Defaults to None.
        reason (str): The reason for the access violation.
    """
    entity: str 
    policy_type: str 
    policy_name: Optional[str] = None  
    reason: str
    violation_type: AccessViolationType
    failed_condition: Optional[str] = None

class QueryScopeResolutionErrorResponse(BaseModel):
    """
    QueryScopeResolutionErrorResponse represents the response model for errors encountered during query scope resolution.

    Attributes:
        user_query_scope (QueryScope): The scope of the user's query.
        issues (List[Dict[str, Any]]): A list of issues encountered, such as unmatched tables or unresolved wildcards.
        suggestions (Optional[List[str]]): Optional suggestions for resolving the issues.
        message (str): A high-level summary of the error.
    """
    error_type: ErrorType = ErrorType.QUERY_SCOPE_ERROR
    scope_error_type: QueryScopeErrorType
    user_query_scope: QueryScope
    issues: List[Dict[str, Any]] 
    suggestions: Optional[List[str]] = None
    sensitive_columns_removed: Optional[List[str]] = None
    message: str 

class SchemaDiscoveryErrorResponse(BaseModel):
    """
    SchemaDiscoveryErrorResponse represents the response model for errors encountered during schema discovery.
    
    Attributes:
        user_query_scope (QueryScope): The scope of the user's query.
        matched_schemas (Optional[List[str]]): Schemas that were matched, if ambiguous.
        unmatched_tables (Optional[List[str]]): Tables that couldn't be resolved.
        unmatched_columns (Optional[List[str]]): Columns that couldn't be resolved.
        message (str): High-level summary of the error.
        suggestions (Optional[List[str]]): Suggestions to resolve the issue.
    """
    error_type: ErrorType = ErrorType.SCHEMA_DISCOVERY_ERROR
    discovery_error_type: SchemaDiscoveryErrorType
    user_query_scope: QueryScope
    matched_schemas: Optional[List[str]] = None 
    unmatched_tables: Optional[List[str]] = None 
    unmatched_columns: Optional[List[str]] = None  
    message: str 
    suggestions: Optional[List[str]] = None  


class AccessControlViolationResponse(BaseModel):
    """
    SqlGenerationErrorResponse represents the response model for SQL generation errors.

    Attributes:
        user_query_scope (QueryScope): The scope of the user's query.
        denied_tables (List[str]): A list of tables that the user is denied access to.
        denied_columns (List[str]): A list of columns that the user is denied access to.
        access_violations (List[AccessViolation]): A list of access violations encountered.
        user_input (str): The original user input that caused the error.
        sql_query (Optional[str]): The SQL query that was attempted, if any.
        injected_str (Optional[str]): Any injected string that was part of the error, if any.
    """
    error_type: ErrorType = ErrorType.ACCESS_DENIED
    user_query_scope: QueryScope
    denied_tables: List[str]
    denied_columns: List[str]
    access_violations: List[AccessViolation]
    user_input: str


class SqlRunErrorResponse(BaseModel):
    """
    SqlRunErrorResponse represents the response model for errors encountered during SQL execution.

    Attributes:
        error_type (ErrorType): The type of error that occurred.
        message (str): A high-level summary of the error.
        user_query_scope (Optional[QueryScope]): The scope of the user's query.
        user_input (Optional[str]): The original user input that caused the error.
        sql_query (Optional[str]): The SQL query that was attempted.
        error_message (Optional[str]): The error message from the SQL execution.
    """
    error_type: ErrorType = ErrorType.RUNTIME_ERROR
    message: str
    user_query_scope: Optional[QueryScope] = None
    user_input: Optional[str] = None
    sql_query: Optional[str] = None
    error_message: Optional[str] = None