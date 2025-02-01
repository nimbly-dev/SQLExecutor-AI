
import logging
from model.schema.schema import Schema
from model.tenant.tenant import Tenant
from model.exceptions.base_exception_message import BaseExceptionMessage
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from ast import literal_eval
from fastapi import HTTPException
from typing import List, Optional
from model.chat_interface.context_user_row import ContextUserRow  

logger = logging.getLogger(__name__)

class SQLContextIntegrationService:
    
    @staticmethod
    async def get_custom_fields_from_context_table(
        tenant: Tenant,
        context_table: str,
        user_identifier_field: str,
        user_identifier_value: str,
        custom_fields: List[str],
        sql_flavor: str,
        custom_get_context_query: str = None,
        schema_name: str = None
    ):
        """
        Retrieve custom fields from the SQL context table for various SQL flavors.
        Prioritizes `custom_get_context_query` if provided.
        """
        if not context_table or not user_identifier_field or not custom_fields:
            raise HTTPException(
                status_code=400,
                detail="SQL context configuration is incomplete. Please verify the schema settings."
            )

        # Use the custom query if provided
        if custom_get_context_query:
            query = custom_get_context_query
            query_params = {"user_identifier_value": user_identifier_value}
        else:
            # Dynamically construct query
            custom_fields_str = ", ".join(custom_fields)
            query = (
                f"SELECT {custom_fields_str} FROM {context_table} "
                f"WHERE {user_identifier_field} = :user_identifier_value"
            )
            query_params = {"user_identifier_value": user_identifier_value}

        # Run SQL based on the flavor
        if sql_flavor == "mysql":
            context_query_result = SqlRunnerService.run_sql(
                query=query,
                tenant=tenant,
                params=query_params,
                schema_name=schema_name  # Required only for MySQL
            )
        else:
            context_query_result = SqlRunnerService.run_sql(
                query=query,
                tenant=tenant,
                params=query_params
            )

        if isinstance(context_query_result, str):
            error_message = BaseExceptionMessage(
                message="Failed to retrieve custom fields from context table. "
                        "Please check the SQL context settings.",
                reason=context_query_result,
            ).dict()
            raise HTTPException(status_code=500, detail=error_message)

        return context_query_result[0] if context_query_result else None