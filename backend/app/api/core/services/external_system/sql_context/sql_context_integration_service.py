
from model.tenant.tenant import Tenant
from model.exceptions.base_exception_message import BaseExceptionMessage
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import SQL_CONTEXT_INTEGRATION
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from ast import literal_eval
from fastapi import HTTPException
from typing import List
from model.chat_interface.context_user_row import ContextUserRow  

class SQLContextIntegrationService:
    
    @staticmethod
    async def get_customfields_from_context_table(tenant: Tenant, context_user_identifier_value: str):
        """Fill up Custom Fields from External Context Table"""
        EXTERNAL_CONTEXT_USER_IDENTIFIER = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="EXTERNAL_CONTEXT_USER_IDENTIFIER"
        )
        EXTERNAL_CONTEXT_CUSTOM_FIELDS = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="EXTERNAL_CONTEXT_CUSTOM_FIELDS"
        )
        EXTERNAL_CONTEXT_TABLE = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="EXTERNAL_CONTEXT_TABLE"
        )
        
        # Parse the string representation of the list into an actual list
        custom_fields_list = literal_eval(EXTERNAL_CONTEXT_CUSTOM_FIELDS)
        custom_fields_str = ", ".join(custom_fields_list)
        
        query_params = {
            "context_user_identifier_value": str(context_user_identifier_value)  # Ensure string type
        }
        
        context_query_result = SqlRunnerService.run_sql(
            query=f"SELECT {custom_fields_str} FROM {EXTERNAL_CONTEXT_TABLE} WHERE {EXTERNAL_CONTEXT_USER_IDENTIFIER} = :context_user_identifier_value",
            tenant=tenant,
            params=query_params
        )

        if isinstance(context_query_result, str):
            error_message = BaseExceptionMessage(
                message="Failed to retrieve custom fields from context table. Please check the tenant settings values for SQL_CONTEXT_INTEGRATION",
                reason=context_query_result,
            ).dict()
            raise HTTPException(status_code=500, detail=error_message)
        
        return context_query_result[0] if context_query_result else None
    

    @staticmethod
    async def get_paginated_context_users_from_context_table(
        tenant: Tenant, 
        page: int, 
        limit: int, 
        order_direction: str = "ASC"
    ) -> List[ContextUserRow]:
        """
        Get paginated context users from the context table, ordered by the external context user identifier.
        """
        EXTERNAL_CONTEXT_USER_IDENTIFIER = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="EXTERNAL_CONTEXT_USER_IDENTIFIER"
        )
        EXTERNAL_CONTEXT_TABLE = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=SQL_CONTEXT_INTEGRATION,
            setting_key="EXTERNAL_CONTEXT_TABLE"
        )
        CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key="FRONTEND_SANDBOX_CHAT_INTERFACE",
            setting_key="CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS"
        )

        if CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS is None:
            error_message = BaseExceptionMessage(
                message="CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS setting is not defined."
            ).dict()
            raise HTTPException(status_code=400, detail=error_message)
        
        try:
            custom_fields_list = literal_eval(CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS)
        except (ValueError, SyntaxError) as e:
            error_message = BaseExceptionMessage(
                message="Invalid CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS format: {CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS}"
            ).dict()
            raise HTTPException(status_code=400, detail=error_message)
        
        if len(custom_fields_list) > 3:
            error_message = BaseExceptionMessage(
                message="CHAT_CONTEXT_DISPLAY_CUSTOM_FIELDS exceeds the maximum allowed custom fields (3)"
            ).dict()
            raise HTTPException(status_code=400, detail=error_message)

        all_fields_list = [EXTERNAL_CONTEXT_USER_IDENTIFIER] + custom_fields_list
        all_fields_str = ", ".join(all_fields_list)

        if order_direction.upper() not in ["ASC", "DESC"]:
            raise ValueError(f"Invalid order direction: {order_direction}")

        # Calculate pagination
        offset = (page - 1) * limit

        query_params = {
            "limit": limit,
            "offset": offset
        }

        context_query = f"""
            SELECT {all_fields_str}
            FROM {EXTERNAL_CONTEXT_TABLE}
            ORDER BY {EXTERNAL_CONTEXT_USER_IDENTIFIER} {order_direction.upper()}
            LIMIT :limit OFFSET :offset
        """

        context_query_result = SqlRunnerService.run_sql(
            query=context_query,
            tenant=tenant,
            params=query_params
        )

        if isinstance(context_query_result, str):
            error_message = BaseExceptionMessage(
                message="Failed to retrieve custom fields from context table. Please check the tenant settings values for SQL_CONTEXT_INTEGRATION",
                reason=context_query_result,
            ).dict()
            raise HTTPException(status_code=403, detail=error_message)

        # Map SQL result to ContextUserRow
        context_users = []
        for row in context_query_result:
            context_user_data = {
                "context_identifier": row.get(EXTERNAL_CONTEXT_USER_IDENTIFIER, ""),
                "custom_fields": {field: row.get(field, "") for field in custom_fields_list}
            }
            context_users.append(ContextUserRow(**context_user_data))

        return context_users
