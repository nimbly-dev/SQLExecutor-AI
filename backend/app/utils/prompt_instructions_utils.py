from config import settings

class DefaultPromptInstructionsUtil:

    SQL_PROMPT_INSTRUCTION = """
    Generate an SQL query based on the provided schema.  
    Respect relationships, constraints, and types.  
    Avoid '*'. Output SQL only.
    """
    INTENT_INSTRUCTION = """
    Identify the intent (fetch_data, update_data, delete_data, insert_data, schema_info) and entities (tables, columns) based on the query. 

    - Use dot notation (table_name.column_name) for columns.  
    - Default to ["table.*"] for ambiguous or unspecified columns.  
    - Avoid inferred columns (e.g., totals, sums).  
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