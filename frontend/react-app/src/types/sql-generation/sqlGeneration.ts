export interface AccessViolation {
    entity: string;
    policy_type: string;
    policy_name: string | null;
    reason: string;
}

export interface SqlGenerationResponse {
    query_scope: {
        intent: string;
        entities: {
            tables: string[];
            columns: string[];
        };
    };
    user_input: string;
    sql_query: string;
    sql_response: any | null;
    injected_str: string | null;
}

