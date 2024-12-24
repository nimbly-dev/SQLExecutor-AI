from config import settings

class DefaultPromptInstructionsUtil:

    SQL_PROMPT_INSTRUCTION = """
    Translate the user request into an SQL query using the provided schema. Follow relationships, constraints, and types defined in the schema.
    Output only the SQL and nothing else.
    """
    
    INTENT_INSTRUCTION = """
    Identify the intent (fetch_data, update_data, delete_data, insert_data, schema_info) and the entities 
    (tables and columns) based on the User Query. Ensure the following:
    - Focus only on tables and columns explicitly mentioned in the query.
    - Use dot notation for columns (e.g., table_name.column_name).
    - If column details are ambiguous, include ["*"] for the respective table.
    - Avoid inferring or deriving columns like totals, sums, or aggregates.
    - If the query implies multiple tables without explicit columns, use ["*"] for each table.
    """

    INTENT_JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string"
            },
            "entities": {
                "type": "object",
                "properties": {
                    "tables": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "columns": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["tables", "columns"],
                "additionalProperties": False
            }
        },
        "required": ["intent", "entities"],
        "additionalProperties": False
    }


    @staticmethod
    def get_intent_json_schema_and_content_instruction():
        """Return precomputed static content"""
        return DefaultPromptInstructionsUtil.INTENT_JSON_SCHEMA, DefaultPromptInstructionsUtil.INTENT_INSTRUCTION
    
    @staticmethod
    def get_sql_generation_instructions():
        return DefaultPromptInstructionsUtil.SQL_PROMPT_INSTRUCTION