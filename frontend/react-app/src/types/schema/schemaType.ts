/*Schema Summary*/
export interface SchemaSummary {
    schema_name: string;
    description: string;
    context_type: string;
    user_identifier: string;
}

export interface SchemaResponse {
    schemas: SchemaSummary[];
    total: number;
    page: number;
    page_size: number;
}

export interface SchemaFilters {
    name?: string;
    contextType?: string;
    page?: number;
    pageSize?: number;
}

export type ContextType = 'all' | 'api' | 'sql';

/*Schema Object*/

export enum VALID_TYPES_ENUM {
    INTEGER = "INTEGER",
    TEXT = "TEXT",
    DECIMAL = "DECIMAL",
    BOOLEAN = "BOOLEAN",
    DATE = "DATE",
}
export type VALID_TYPES = keyof typeof VALID_TYPES_ENUM;

export enum VALID_CONSTRAINTS_ENUM  {
    PRIMARY_KEY = "PRIMARY KEY",
    FOREIGN_KEY = "FOREIGN KEY",
    UNIQUE = "UNIQUE",
    NOT_NULL = "NOT NULL"
}
export type VALID_CONSTRAINTS = keyof typeof VALID_CONSTRAINTS_ENUM;

export enum VALID_JOINS_ENUM {
    INNER = "INNER",
    LEFT = "LEFT",
    RIGHT = "RIGHT",
    OUTER = "OUTER"
}
export type VALID_JOINS = keyof typeof VALID_JOINS_ENUM;

export interface Column {
    type: string;
    description?: string;
    constraints: string[];
    synonyms: string[];
    exclude_description_on_generate_sql: boolean;
    is_sensitive_column: boolean;
}

export interface Joins {
    description?: string;
    exclude_description_on_generate_sql: boolean;
    table: string;
    on: string;
    type: string;
}

export interface Table {
    description?: string;
    synonyms: string[];
    columns: Record<string, Column>;
    relationships?: Record<string, Joins>;
    exclude_description_on_generate_sql: boolean;
}

export interface SQLContext {
    table: string;
    user_identifier: string;
    custom_fields: string[];
    custom_get_context_query?: string;
}

export interface APIContext {
    get_user_endpoint: string;
    user_identifier: string;
    custom_fields: string[];
    auth_method: string;
}

export interface ContextSetting {
    sql_context?: SQLContext;
    api_context?: APIContext;
}

export interface SchemaChatInterfaceIntegrationSetting {
    enabled: boolean; 
    get_contexts_query: string;
    get_contexts_count_query: string;
}

export interface Schema {
    tenant_id: string;
    _id?: string;
    schema_name: string;
    description: string;
    exclude_description_on_generate_sql: boolean;
    tables: Record<string, Table>; 
    filter_rules?: string[];
    synonyms?: string[];
    context_type: string;
    context_setting: ContextSetting;
    schema_chat_interface_integration?: SchemaChatInterfaceIntegrationSetting;
}

export interface UpdateSchemaRequest {
    schema_name: string;
    description?: string;
    tables: Record<string, Table>;  
    exclude_description_on_generate_sql: boolean;
    filter_rules?: string[];
    context_type: string;
    context_setting: ContextSetting;
    schema_chat_interface_integration?: SchemaChatInterfaceIntegrationSetting;
}