import aiohttp
import logging
import jwt
import time
import hmac
import hashlib
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Dict, List
from model.requests.external_system_integration.fetch_external_context_request import CreateExternalSessionRequest
from model.schema.context import APIContext
from model.tenant.tenant import Tenant
from model.authentication.external_user_decoded_jwt_token import DecodedJwtToken
from api.core.constants.tenant.settings_categories import(
    API_CONTEXT_INTEGRATION,
    API_KEYS
)
from utils.tenant_manager.setting_utils import SettingUtils

class APIContextIntegrationService:

    @staticmethod
    async def call_external_get_user_endpoint(
        tenant: Tenant, 
        api_context: APIContext, 
        request: CreateExternalSessionRequest
    ):
        """
        Call the external get-user endpoint with HMAC authentication.
        """
        settings = tenant.settings or {}

        # Extract necessary fields from APIContext and Tenant settings
        get_user_endpoint = api_context.get_user_endpoint
        identifier_field = api_context.user_identifier
        client_secret_key = api_context.auth_method == "hmac" and SettingUtils.get_setting_value(
            settings, 
            "API_KEYS", 
            "EXTERNAL_SYSTEM_CLIENT_TOKEN"
        )

        # Validate the presence of required settings
        if not get_user_endpoint:
            raise ValueError("Get-user endpoint is not defined in API context settings.")
        if not identifier_field:
            raise ValueError("Identifier field is not defined in API context settings.")
        if not client_secret_key:
            raise ValueError("Client secret key is not defined for the tenant.")

        user_identifier = request.context_user_identifier_value
        timestamp = str(int(time.time()))
        message = f"{user_identifier}:{timestamp}"

        # Generate HMAC signature
        signature = hmac.new(
            client_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"HMAC {signature}",
            "X-Timestamp": timestamp
        }

        logging.debug(f"Headers for tenant {tenant.tenant_id}: {headers}")

        query_param = f"{identifier_field}={user_identifier}"
        url = f"{get_user_endpoint}?{query_param}"

        logging.debug(f"Calling external get-user endpoint: {url}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    logging.debug(f"External get-user response status for tenant {tenant.tenant_id}: {response.status}")

                    if response.status != 200:
                        try:
                            error_body = await response.json()
                        except Exception:
                            error_body = await response.text()

                        logging.warning(
                            f"Get-user failed for tenant {tenant.tenant_id} with status {response.status}: {error_body}"
                        )

                        error_detail = error_body if isinstance(error_body, str) else error_body.get("detail", "Authentication failed")
                        
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_detail
                        )

                    logging.info(f"Get-user successful for tenant {tenant.tenant_id}.")
                    return await response.json()

            except aiohttp.ClientError as e:
                logging.error(f"Network error during get-user for tenant {tenant.tenant_id}: {str(e)}")
                raise HTTPException(
                    status_code=502,  
                    detail=f"External service unavailable: {str(e)}"
                )

    @staticmethod
    async def call_external_get_users_context_counts(tenant: Tenant) -> Dict[str, int]:
        """
        Call the external get-users-context-counts endpoint with HMAC authentication.
        """
        settings = tenant.settings or {}

        get_users_context_counts_endpoint = SettingUtils.get_setting_value(
            settings,
            API_CONTEXT_INTEGRATION,
            "EXTERNAL_API_CONTEXT_GET_USERS_COUNT_ENDPOINT", 
        )
        client_secret_key = SettingUtils.get_setting_value(
            settings,
            API_KEYS,
            "EXTERNAL_SYSTEM_CLIENT_TOKEN"
        )

        # Validate settings
        if not get_users_context_counts_endpoint:
            raise ValueError("Get-users-context-counts endpoint is not defined for the tenant.")
        if not client_secret_key:
            raise ValueError("Client secret key is not defined for the tenant.")

        # Generate HMAC signature
        timestamp = str(int(time.time()))
        message = f"{timestamp}" 
        signature = hmac.new(
            client_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"HMAC {signature}",
            "X-Timestamp": timestamp
        }

        logging.debug(f"Headers for tenant {tenant.tenant_id}: {headers}")
        logging.debug(f"Calling external get-users-context-counts endpoint: {get_users_context_counts_endpoint}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(get_users_context_counts_endpoint, headers=headers) as response:
                    logging.debug(f"External get-users-context-counts response status for tenant {tenant.tenant_id}: {response.status}")

                    if response.status != 200:
                        error_body = await response.text()
                        try:
                            error_body = await response.json()
                        except Exception:
                            pass

                        logging.warning(
                            f"Get-users-context-counts failed for tenant {tenant.tenant_id} with status {response.status}: {error_body}"
                        )

                        error_detail = error_body if isinstance(error_body, str) else error_body.get("detail", "Authentication failed")
                        
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_detail
                        )

                    # Parse the response and normalize to an integer
                    raw_data = await response.json()
                    logging.debug(f"Raw data received: {raw_data}")

                    if isinstance(raw_data, int):  # If it's already an integer
                        return raw_data

                    if isinstance(raw_data, str) and raw_data.isdigit():  # If it's a numeric string
                        return int(raw_data)

                    if isinstance(raw_data, dict):  # If it's a dictionary
                        possible_keys = ["total_users", "total_counts", "count"]
                        for key in possible_keys:
                            if key in raw_data:
                                value = raw_data[key]
                                if isinstance(value, int):  # Integer value
                                    return value
                                if isinstance(value, str) and value.isdigit():  # Numeric string value
                                    return int(value)
                            
                    raise HTTPException(
                        status_code=502,
                        detail="External service returned an unexpected format."
                    )

            except aiohttp.ClientError as e:
                logging.error(f"Network error during get-users-context-counts for tenant {tenant.tenant_id}: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail=f"External service unavailable: {str(e)}"
                )


    @staticmethod
    async def call_external_get_users_endpoint(tenant: Tenant, 
                                               page: int, 
                                               limit: int, 
                                               order_direction: str = "ASC") -> List[Dict]:
        """
        Call the external get-users endpoint with HMAC authentication.
        """
        settings = tenant.settings or {}

        get_users_endpoint = SettingUtils.get_setting_value(
            settings, 
            API_CONTEXT_INTEGRATION,
            "EXTERNAL_API_CONTEXT_GET_USERS_ENDPOINT"
        )
        identifier_field = SettingUtils.get_setting_value(
            settings, 
            API_CONTEXT_INTEGRATION, 
            "EXTERNAL_API_CONTEXT_IDENTIFIER_FIELD"
        )
        client_secret_key = SettingUtils.get_setting_value(
            settings, 
            API_KEYS, 
            "EXTERNAL_SYSTEM_CLIENT_TOKEN"
        )

        # Validate settings
        if not get_users_endpoint:
            raise ValueError("Get-users endpoint is not defined for the tenant.")
        if not identifier_field:
            raise ValueError("Identifier field is not defined for the tenant.")
        if not client_secret_key:
            raise ValueError("Client secret key is not defined for the tenant.")

        timestamp = str(int(time.time()))
        message = f"{page}:{limit}:{order_direction}:{timestamp}"
        signature = hmac.new(
            client_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"HMAC {signature}",
            "X-Timestamp": timestamp
        }

        params = {
            "page": page,
            "limit": limit,
            "order_by": identifier_field,
            "order_direction": order_direction
        }

        logging.debug(f"Headers for tenant {tenant.tenant_id}: {headers}")
        logging.debug(f"Calling external get-users endpoint: {get_users_endpoint} with params: {params}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(get_users_endpoint, headers=headers, params=params) as response:
                    logging.debug(f"External get-users response status for tenant {tenant.tenant_id}: {response.status}")

                    if response.status != 200:
                        error_body = await response.text()
                        try:
                            error_body = await response.json()
                        except Exception:
                            pass

                        logging.warning(
                            f"Get-users failed for tenant {tenant.tenant_id} with status {response.status}: {error_body}"
                        )

                        error_detail = error_body if isinstance(error_body, str) else error_body.get("detail", "Authentication failed")
                        
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_detail
                        )

                    users_data = await response.json()
                    logging.info(f"Get-users successful for tenant {tenant.tenant_id}.")
                    return users_data

            except aiohttp.ClientError as e:
                logging.error(f"Network error during get-users for tenant {tenant.tenant_id}: {str(e)}")
                raise HTTPException(
                    status_code=502,  
                    detail=f"External service unavailable: {str(e)}"
                )
                
    

    @staticmethod
    def decode_json_token(tenant: Tenant, user_token) -> DecodedJwtToken:
        settings = tenant.settings or {}

        # Extract required settings
        access_token = user_token.get("access_token")
        jwt_custom_fields = eval(SettingUtils.get_setting_value(settings, API_CONTEXT_INTEGRATION, "EXTERNAL_API_CONTEXT_CUSTOM_FIELDS") or "[]")
        user_identifier_field = SettingUtils.get_setting_value(settings, API_CONTEXT_INTEGRATION, "EXTERNAL_API_CONTEXT_IDENTIFIER_FIELD")
        external_jwt_secret_key = SettingUtils.get_setting_value(settings, API_KEYS, "EXTERNAL_SYSTEM_CLIENT_TOKEN")

        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Access token is missing in the user token."
            )
        if not (jwt_custom_fields and user_identifier_field and external_jwt_secret_key):
            raise HTTPException(
                status_code=400,
                detail="Required JWT settings are missing or incomplete."
            )

        try:
            token_bytes = access_token.encode("utf-8") if isinstance(access_token, str) else access_token
            decoded_payload = jwt.decode(token_bytes, external_jwt_secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=400,
                detail="Token has expired."
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid Token."
            )

        # Extract custom fields from the token
        user_identifier_value = decoded_payload.get(user_identifier_field)
        print(decoded_payload)
        if not user_identifier_value:
            raise HTTPException(
                status_code=400,
                detail=f"User identifier field '{user_identifier_field}' is missing in the token. Please contect the Tenant Administrator for assistance"
            )

        custom_field_values = {
            field: decoded_payload.get(field) for field in jwt_custom_fields if field in decoded_payload
        }
        if not custom_field_values:
            raise HTTPException(
                status_code=400,
                detail=f"None of the custom fields {jwt_custom_fields} were found in the token. Please contect the Tenant Administrator for assistance"
            )

        exp_timestamp = decoded_payload.get("exp")

        return DecodedJwtToken(
            tenant_id=tenant.tenant_id,
            custom_fields=custom_field_values,
            user_identifier=user_identifier_value,
            expiration= datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat() if exp_timestamp else None
        )