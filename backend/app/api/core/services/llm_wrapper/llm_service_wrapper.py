from typing import Dict, Optional
from api.core.constants.tenant.settings_categories import SQL_GENERATION_KEY
from utils.prompt_instructions_utils import DefaultPromptInstructionsUtil
from fastapi import HTTPException
from openai import OpenAI
import logging
import json

from config import settings
from model.tenant.tenant import Tenant
from model.query_scope.query_scope import QueryScope
from model.requests.sql_generation.user_input_request import UserInputRequest
from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from utils.llm_wrapper.sql_generation_output_utils import SQLUtils
from utils.tenant_manager.setting_utils import SettingUtils

class LLMServiceWrapper:

    @staticmethod
    async def get_query_scope_using_default_mode(user_input: UserInputRequest) -> QueryScope:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            json_schema, content_instruction = DefaultPromptInstructionsUtil.get_intent_json_schema_and_content_instruction()

            response = client.chat.completions.create(
                model=f"{settings.DEFAULT_APP_LLM_MODEL}",
                messages=[
                    {
                        "role": "system",
                        "content": content_instruction
                    },
                    {
                        "role": "user",
                        "content": user_input.input
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "query_scope_schema",
                        "schema": json_schema
                    }
                },
                temperature=0.3,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            query_scope = QueryScope(**parsed_data)
            
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # logging.info(f"Token Usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
            print(f"Token Usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
            
            return query_scope

        except Exception as e:
            logging.error(f"Error in OpenAI API: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate structured query scope: {str(e)}"
            )

    @staticmethod
    async def generate_sql_query(user_input: UserInputRequest, 
                                 resolved_schema: Dict, 
                                 tenant: Tenant,
                                 query_scope: Optional[QueryScope] = None) -> str:
        include_query_scope = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_GENERATION_KEY,
            setting_key="INCLUDE_QUERY_SCOPE_ON_SQL_GENERATION"
        ) or False
        
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            if not include_query_scope:
                prompt_instruction = DefaultPromptInstructionsUtil.get_sql_generation_instructions()
                
                messages = [
                {
                    "role": "system",
                    "content": f"{prompt_instruction}\nSchema: {json.dumps(resolved_schema)}"
                },
                    {
                        "role": "user",
                        "content": user_input.input
                    }
                ]

            else:
                prompt_instruction = DefaultPromptInstructionsUtil.SQL_PROMPT_INSTRUCTION_WITH_QUERY_SCOPE
                #Remove unnecessary fields from query scope
                new_query_scope = {
                    "entities": {
                        "tables": query_scope.entities.tables,
                        "columns": query_scope.entities.columns,
                    }
                }
            
                messages = [
                    {
                        "role": "system",
                        "content": f"{prompt_instruction}\nQueryScope: {new_query_scope}\nSchema: {json.dumps(resolved_schema)}"
                    },
                    {
                        "role": "user",
                        "content": user_input.input
                    }
                ]

            response = client.chat.completions.create(
                model=f"{settings.DEFAULT_APP_LLM_MODEL}",
                messages=messages,
                temperature=0.3,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )


            generated_sql = response.choices[0].message.content
            # Validate SQL syntax
            generated_sql = SQLUtils.normalize_sql(generated_sql)

            usage = response.usage
            # logging.info(f"Token Usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
            print(f"Token Usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
            
            # Check for invalid SQL structure
            if not generated_sql.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
                raise ValueError("Invalid SQL Syntax generated.")


            return generated_sql

        except Exception as e:
            logging.error(f"Error in generating SQL query: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate SQL query: {str(e)}"
            )

