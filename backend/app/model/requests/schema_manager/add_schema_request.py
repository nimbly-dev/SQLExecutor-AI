from pydantic import BaseModel, validator
from typing import Optional, Dict, List
from model.schema.schema_chat_interface_integration_setting import SchemaChatInterfaceIntegrationSetting
from model.schema.table import Table
from model.schema.context import ContextSetting

import re

class AddSchemaRequest(BaseModel):
    schema_name: str  
    description: str
    tables: Dict[str, Table]
    exclude_description_on_generate_sql: bool  
    filter_rules: Optional[List[str]] = [] 
    synonyms: Optional[List[str]] = []
    context_type: str
    context_setting: ContextSetting 
    schema_chat_interface_integration: Optional[SchemaChatInterfaceIntegrationSetting] = None
 
    # Validator for schema_name
    @validator("schema_name")
    def validate_schema_name(cls, v):
        if not isinstance(v, str):
            raise ValueError(f"Schema name must be a string, but got {type(v)}")

        v = v.strip()

        if "\n" in v or "\t" in v or " " in v:
            raise ValueError(f"Invalid schema name: '{v}'. It should not contain spaces, tabs, or newlines.")

        pattern = r"^[a-zA-Z0-9_]+$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid schema name: '{v}'. It should only contain letters, numbers, and underscores, with no spaces.")
        return v

    # Validator for description length
    @validator("description")
    def validate_description(cls, v):
        if len(v) > 64:
            raise ValueError("description must not exceed 64 characters")
        return v

    @validator("context_type")
    def validate_context_type(cls, value):
        if value not in ["sql", "api"]:
            raise ValueError("context_type must be either 'sql' or 'api'")
        return value


    @validator("context_setting")
    def validate_context_setting(cls, value: ContextSetting):
        if value.sql_context:
            sql_context = value.sql_context

            if not sql_context.table:
                raise ValueError("SQL context must have a table defined")
            if not sql_context.user_identifier:
                raise ValueError("SQL context must have a user_identifier defined")

            if sql_context.custom_get_context_query:
                query = sql_context.custom_get_context_query

                # Check for placeholder in query
                if ":user_identifier_value" not in query:
                    raise ValueError(
                        "custom_get_context_query must include the ':user_identifier_value' placeholder."
                    )

                # Validate basic SELECT query structure
                if not re.match(
                    r"^\s*SELECT\s+.+\s+FROM\s+.+\s*;",
                    query,
                    re.IGNORECASE,
                ):
                    raise ValueError(
                        "custom_get_context_query must be a valid SELECT query ending with a semicolon."
                    )

                # Check for forbidden keywords
                forbidden_keywords = ["UPDATE", "INSERT", "DELETE", "DROP", "ALTER"]
                if any(
                    re.search(rf"\b{keyword}\b", query, re.IGNORECASE)
                    for keyword in forbidden_keywords
                ):
                    raise ValueError(
                        f"custom_get_context_query contains forbidden SQL keywords: {', '.join(forbidden_keywords)}"
                    )

        return value
    
    