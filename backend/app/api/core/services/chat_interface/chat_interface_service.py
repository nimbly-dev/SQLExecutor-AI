from typing import List, Optional
import pymongo
from pymongo import UpdateOne
import logging
from bson import Binary, UUID_SUBTYPE
from uuid import UUID
from fastapi import HTTPException

from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY
from api.core.services.sql_runner.sql_runner_service import SqlRunnerService
from model.chat_interface.context_user_row import ContextUserRow
from model.schema.schema import Schema
from utils.database import mongodb
from model.tenant.tenant import Tenant;
from model.chat_interface.chat_interface_settings import ChatInterfaceSettings;
from model.chat_interface.chat_interface_setting import ChatInterfaceSetting;
from model.requests.chat_interface.toggle_chat_interface_setting import UpdateChatInterfaceSettingRequest;
from model.requests.chat_interface.toggle_chat_interface_settings import UpdateChatInterfaceSettingsRequest;
from model.external_system_integration.external_user_session_data import ExternalSessionData;
from model.external_system_integration.external_user_session_data_setting import ExternalSessionDataSetting;
from model.tenant.setting import Setting;

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs

class ChatInterfaceService:
    
    @staticmethod
    def build_chat_interface_settings(tenant: Tenant, session_data: ExternalSessionData) -> ChatInterfaceSettings:
        """
        Build chat interface settings for the given tenant and session data
        """
         # Get Tenant Settings
        sql_injectors_toggle: Setting  = tenant.settings.get("SQL_INJECTORS", {}).get("SQL_INJECTORS_ENABLED", {})
        dynamic_injection_toggle: Setting =  tenant.settings.get("SQL_INJECTORS", {}).get("DYNAMIC_INJECTION", {})
        remove_sensitive_columns: Setting = tenant.settings.get(POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, {}).get("REMOVE_SENSITIVE_COLUMNS", {})
        
        
        # Get Session Settings
        remove_missing_column_toggle: ExternalSessionDataSetting = session_data.session_settings \
                                                                        .get("SQL_GENERATION", {}) \
                                                                        .get("REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE", {})
        
        chat_interface_settings = ChatInterfaceSettings(
            query_scope_setting={
                "QUERY_SCOPE_SETTINGS":{
                    "REMOVE_SENSITIVE_COLUMNS": ChatInterfaceSetting(
                        setting_basic_name=remove_sensitive_columns.setting_basic_name,
                        setting_toggle=remove_sensitive_columns.setting_value,
                        setting_description=remove_sensitive_columns.setting_description
                    )
                }
            },
            injectors_setting={
                "SQL_INJECTORS": {
                    "SQL_INJECTORS_ENABLED": ChatInterfaceSetting(
                        setting_basic_name=sql_injectors_toggle.setting_basic_name,
                        setting_toggle=sql_injectors_toggle.setting_value,
                        setting_description=sql_injectors_toggle.setting_description
                    ),
                    "DYNAMIC_INJECTION": ChatInterfaceSetting(
                        setting_basic_name=dynamic_injection_toggle.setting_basic_name,
                        setting_toggle=dynamic_injection_toggle.setting_value,
                        setting_description=dynamic_injection_toggle.setting_description
                    )
                }
            },
            sql_generation={
                "SQL_GENERATION": {
                    "REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": ChatInterfaceSetting(
                        setting_basic_name=remove_missing_column_toggle.setting_basic_name,
                        setting_toggle=remove_missing_column_toggle.setting_value,
                        setting_description=remove_missing_column_toggle.setting_description
                    )
                }
            }
        )
        
        return chat_interface_settings

    @staticmethod
    async def apply_patched_chat_interface_settings_on_mongodb(
        tenant: Tenant,
        session_data: ExternalSessionData,
        patch_request: UpdateChatInterfaceSettingsRequest,
    ):
        """
        Patch tenant and session settings in MongoDB with values from patch_request.
        Update only the 'setting_value' field while preserving the document structure.
        """
        collection_sessions = mongodb.db["sessions"]
        collection_tenants = mongodb.db["tenants"]

        session_uuid = session_data.session_id 

        logger.debug("Starting to patch tenant settings.")
        for category, settings in patch_request.dict().items():
            logger.debug(f"Patching tenant category: {category}")
            for setting_name, setting_value in settings.items():
                logger.debug(f"Patching tenant setting: {setting_name} with value: {setting_value}")
                existing_setting = await collection_tenants.find_one(
                    {"tenant_id": tenant.tenant_id},
                    {f"settings.{category}.{setting_name}": 1}
                )
                logger.debug(f"Existing tenant setting retrieved: {existing_setting}")

                if existing_setting and setting_name in existing_setting.get("settings", {}).get(category, {}):
                    update_value = str(setting_value) if isinstance(setting_value, bool) else setting_value

                    result = await collection_tenants.update_one(
                        {"tenant_id": tenant.tenant_id},
                        {
                            "$set": {
                                f"settings.{category}.{setting_name}.setting_value": update_value
                            }
                        }
                    )
                    logger.debug(f"Tenant setting update result for {category}.{setting_name}: {result.modified_count} document(s) modified.")
                else:
                    logger.warning(f"Tenant setting {category}.{setting_name} does not exist for tenant {tenant.tenant_id}.")

        # Patch session settings
        for category, settings in patch_request.dict().items():
            logger.debug(f"Patching session category: {category}")
            for setting_name, setting_value in settings.items():
                # Normalize values for consistent comparison
                patch_value = str(setting_value).lower()

                # Fetch the entire document for debugging purposes
                full_document = await collection_sessions.find_one(
                    {"session_id": session_uuid}  # Directly use UUID object
                )
                logger.debug(f"Full session document for session {session_uuid}: {full_document}")

                # Validate if category and setting exist in the document
                if (
                    full_document
                    and "session_settings" in full_document
                    and category in full_document["session_settings"]
                    and setting_name in full_document["session_settings"][category]
                ):
                    # Fetch current value for comparison
                    current_value = (
                        full_document["session_settings"][category][setting_name]
                        .get("setting_value", "")
                        .lower()
                    )
                    logger.debug(f"Current value for {category}.{setting_name}: {current_value}")

                    # Update only if the values differ
                    if current_value != patch_value:
                        result = await collection_sessions.update_one(
                            {"session_id": session_uuid},  # Directly use UUID object
                            {
                                "$set": {
                                    f"session_settings.{category}.{setting_name}.setting_value": patch_value
                                }
                            }
                        )
                        logger.debug(f"Updated session setting {category}.{setting_name}: {result.modified_count} document(s) modified.")
                    else:
                        logger.debug(f"No update needed for {category}.{setting_name}. Current value matches patch request.")
                else:
                    logger.warning(f"Session setting {category}.{setting_name} does not exist in session {session_uuid}.")
                    
    @staticmethod
    async def get_paginated_context_users_from_context_table(
        tenant: Tenant, 
        page: int, 
        limit: int, 
        order_direction: str = "ASC",
        sort_field: str = "email",
        schema: Optional[Schema] = None
    ) -> List[ContextUserRow]:
        """
        Retrieve paginated user contexts based on schema-defined SQL queries.
        Supports both SQL and API context types for extracting user_identifier.
        """
        schema_integration = schema.schema_chat_interface_integration
        if not schema_integration.enabled:
            raise HTTPException(status_code=400, detail="Schema-based SQL chat interface integration is disabled.")

        get_contexts_query = schema_integration.get_contexts_query
        get_contexts_count_query = schema_integration.get_contexts_count_query

        if not get_contexts_query or not get_contexts_count_query:
            raise HTTPException(
                status_code=400,
                detail="Schema does not define required SQL queries for user context retrieval."
            )

        if order_direction.upper() not in ["ASC", "DESC"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid order direction: {order_direction}. Allowed values are ASC or DESC."
            )

        offset = (page - 1) * limit
        query = (
            get_contexts_query
            .replace("${sort_field}", sort_field)
            .replace("${limit}", str(limit))
            .replace("${offset}", str(offset + 1))
            .replace("${order_direction}", order_direction.upper())
        )

        users_result = SqlRunnerService.run_sql(
            query=query,
            tenant=tenant,
            schema_name=schema.schema_name
        )

        # Determine user_identifier from context setting based on context_type
        if schema.context_type == "sql":
            context_obj = schema.context_setting.sql_context
        elif schema.context_type == "api":
            context_obj = schema.context_setting.api_context
        else:
            raise HTTPException(status_code=400, detail="Unsupported context type in schema settings.")

        if not context_obj or not context_obj.user_identifier:
            raise HTTPException(status_code=400, detail="Missing user_identifier in context setting.")

        if not context_obj or not context_obj.user_identifier:
            raise HTTPException(
                status_code=400,
                detail="Missing user_identifier in context setting."
            )

        context_identifier_field = context_obj.user_identifier

        field_names = list(users_result[0].keys()) if users_result else []
        context_users = []

        for row in users_result:
            context_identifier = row.get(context_identifier_field)
            if context_identifier is None:
                logger.warn(f"Missing context_identifier '{context_identifier_field}' in row: {row}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing context_identifier '{context_identifier_field}' in row: {row}"
                )

            # Map all other fields as custom_fields
            custom_fields_data = {
                field: row.get(field, "")
                for field in field_names if field != context_identifier_field
            }
            context_users.append(
                ContextUserRow(
                    context_identifier=str(context_identifier),
                    custom_fields=custom_fields_data
                )
            )

        return context_users
    
    @staticmethod
    async def get_context_table_count(
        tenant: Tenant,
        count_query: str,
        schema_name: Optional[str] = None
    ) -> int:
        """
        Execute the count query to get the total number of records in the context table.
        """
        count_result = SqlRunnerService.run_sql(
            query=count_query,
            tenant=tenant,
            schema_name=schema_name
        )

        
        if not isinstance(count_result, list) or not count_result:
            logger.error(f"Invalid response format from count query: {count_result}")
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from count query."
            )

        # Extract the first key dynamically (works for COUNT(*) or count)
        count_key = list(count_result[0].keys())[0]  
        total_count = int(count_result[0][count_key])

        return total_count
