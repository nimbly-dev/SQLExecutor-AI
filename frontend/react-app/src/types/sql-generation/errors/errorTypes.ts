export enum ErrorType {
  ACCESS_DENIED = "access_denied",
  QUERY_SCOPE_ERROR = "query_scope_error",
  SCHEMA_DISCOVERY_ERROR = "schema_discovery_error",
  VALIDATION_ERROR = "validation_error",
  RUNTIME_ERROR = "runtime_error"
}

export enum AccessViolationType {
  TABLE_ACCESS_DENIED = "table_access_denied",
  COLUMN_ACCESS_DENIED = "column_access_denied",
  POLICY_VIOLATION = "policy_violation",
  MISSING_PERMISSION = "missing_permission"
}

export enum QueryScopeErrorType {
  TABLE_NOT_FOUND = "table_not_found",
  COLUMN_NOT_FOUND = "column_not_found",
  UNRESOLVED_WILDCARD = "unresolved_wildcard",
  INVALID_SYNTAX = "invalid_syntax",
  AMBIGUOUS_REFERENCE = "ambiguous_reference"
}

export enum SchemaDiscoveryErrorType {
  NO_MATCHING_SCHEMA = "no_matching_schema",
  MULTIPLE_SCHEMAS = "multiple_schemas",
  INVALID_SCHEMA = "invalid_schema",
  SCHEMA_NOT_FOUND = "schema_not_found"
}

export interface Entities {
  tables: string[];
  columns: string[];
}

export interface QueryScope {
  intent: string;
  entities: Entities;
}

export type ErrorTypes = any; // ...stub type definition...