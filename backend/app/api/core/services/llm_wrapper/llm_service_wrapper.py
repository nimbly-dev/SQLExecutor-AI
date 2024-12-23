from utils.database import mongodb
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

            logging.info(f"Token Usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")

            # return {
            #     "prompt": {
            #         "input": user_input.input,
            #         "token_input": prompt_tokens,
            #         "token_output": completion_tokens,
            #         "token_total": total_tokens
            #     },
            #     "query_scope": query_scope
            # }
            return query_scope

        except Exception as e:
            logging.error(f"Error in OpenAI API: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate structured query scope: {str(e)}"
            )