import { 
  AccessViolationType, 
  ErrorType, 
  QueryScopeErrorType, 
  SchemaDiscoveryErrorType, 
  QueryScope 
} from './errorTypes';

export interface AccessViolation {
  entity: string;
  policy_type: string;
  policy_name: string | null;
  reason: string;
  violation_type: AccessViolationType;
  failed_condition: string;
}

// Base error interface
interface BaseError {
  error_type: ErrorType;
}

export interface SqlGenerationErrorDetail extends BaseError {
  error_type: ErrorType.ACCESS_DENIED;
  user_query_scope: QueryScope;
  denied_tables: string[];
  denied_columns: string[];
  access_violations: AccessViolation[];
  user_input: string;
}

// Add interface for QueryScopeIssue
export interface QueryScopeIssue {
  type: QueryScopeErrorType;
  input: string;
  suggestions?: string[];
}

export interface QueryScopeResolutionErrorDetail extends BaseError {
  error_type: ErrorType.QUERY_SCOPE_ERROR;
  scope_error_type: QueryScopeErrorType;
  user_query_scope: QueryScope;
  issues: QueryScopeIssue[];
  suggestions?: string[];
  sensitive_columns_removed?: string[];
  message: string;
}

export interface SchemaDiscoveryErrorDetail extends BaseError {
  error_type: ErrorType.SCHEMA_DISCOVERY_ERROR;
  discovery_error_type: SchemaDiscoveryErrorType;
  user_query_scope: QueryScope;
  matched_schemas?: string[];
  unmatched_tables?: string[];
  unmatched_columns?: string[];
  message: string;
  suggestions?: string[];
}

export interface ValidationErrorDetail {
  field: string;
  msg: string;
  type: string;
}

export interface ValidationErrorResponseDetail extends BaseError {
  error_type: ErrorType.VALIDATION_ERROR;
  detail: ValidationErrorDetail[];
}

// Update type alias
export type ValidationErrorResponse = ApiErrorResponse<ValidationErrorResponseDetail>;

export interface GenericErrorDetail extends BaseError {
  error_type: ErrorType.RUNTIME_ERROR;
  message: string;
  detail: string;
}

// API Response types that include the detail wrapper
export interface ApiErrorResponse<T> {
  detail: T;
}

export type APIError =
  | ApiErrorResponse<SqlGenerationErrorDetail>
  | ApiErrorResponse<QueryScopeResolutionErrorDetail>
  | ApiErrorResponse<SchemaDiscoveryErrorDetail>
  | ApiErrorResponse<ValidationErrorResponseDetail>
  | ApiErrorResponse<string>
  | ApiErrorResponse<GenericErrorDetail>;

// Export type aliases for cleaner usage
export type SqlGenerationErrorResponse = ApiErrorResponse<SqlGenerationErrorDetail>;
export type QueryScopeErrorResponse = ApiErrorResponse<QueryScopeResolutionErrorDetail>;
export type SchemaDiscoveryErrorResponse = ApiErrorResponse<SchemaDiscoveryErrorDetail>;
