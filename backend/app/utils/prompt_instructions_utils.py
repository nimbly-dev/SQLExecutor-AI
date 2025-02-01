from config import settings

class DefaultPromptInstructionsUtil:

    SQL_PROMPT_INSTRUCTION = """
    Generate a SQL query strictly only using columns and table on the provided schema:
    - Respect table relationships; use intermediate tables if needed.
    - Do not assume direct relationships unless specified.
    - Use table aliases for brevity.
    - Avoid using '*'. List only required columns.
    - Ensure all joins are valid based on the schema.
    - Output only the SQL query.
    """
    
    SQL_PROMPT_INSTRUCTION_WITH_QUERY_SCOPE = """
    Generate an SQL query using only tables and columns in the QueryScope.  
    - Use Schema as reference.  
    - Follow defined table relationships; use intermediates if needed.  
    - Do not assume relationships unless explicitly stated.  
    - Use table aliases.  
    - Avoid '*'; list only required columns.  
    - Ensure valid joins per Schema.  
    - Output only the SQL query.  
    """

    INTENT_INSTRUCTION = """
    Identify intent (fetch_data, update_data, delete_data, insert_data, schema_info) and extract relevant tables/columns.
    - Use 'table.column'; 'table.*' only if "all columns" is explicitly requested.
    - Follow table relationships; include 'related_table.column' if linked.
    - Exclude SQL functions (COUNT, SUM, AVG) and keywords.
    - If aggregation is implied, keep only necessary columns (e.g., 'appointments.id' not 'appointments.count').
    - List all required tables explicitly, including primary/foreign keys if referenced.
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
    