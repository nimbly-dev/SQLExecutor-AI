import aiohttp
import logging
import jwt
from datetime import datetime, timezone

from api.core.services.tenant_manager.tenant_manager_service import TenantManagerService
from model.requests.authentication.auth_login_request import AuthLoginRequest
from model.tenant import Tenant
from model.decoded_jwt_token import DecodedJwtToken

class ExternalJWTAuthorizationServiceWrapper:
    
    @staticmethod
    async def call_external_login(tenant: Tenant, auth_request: AuthLoginRequest):
        # Get settings
        settings = tenant.settings or {}
        login_endpoint_setting = settings.get("EXTERNAL_JWT_LOGIN_ENDPOINT")
        auth_field_setting = settings.get("EXTERNAL_JWT_AUTH_FIELD")
        passkey_field_setting = settings.get("EXTERNAL_JWT_AUTH_PASSKEY_FIELD")

        # Validate tenant settings
        if not login_endpoint_setting or not login_endpoint_setting.setting_value:
            raise ValueError("Login endpoint is not defined for the tenant.")
        if not auth_field_setting or not auth_field_setting.setting_value:
            raise ValueError("Authentication field is not defined for the tenant.")
        if not passkey_field_setting or not passkey_field_setting.setting_value:
            raise ValueError("Passkey field is not defined for the tenant.")

        login_endpoint = login_endpoint_setting.setting_value
        auth_field = auth_field_setting.setting_value
        passkey_field = passkey_field_setting.setting_value

        # Construct payload dynamically
        payload = {
            auth_field: auth_request.auth_field,
            passkey_field: auth_request.auth_passkey_field,
        }

        logging.debug(f"Constructed payload for tenant {tenant.tenant_id}: {payload}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(login_endpoint, json=payload) as response:
                    if response.status != 200:
                        logging.error(
                            f"Login failed for tenant {tenant.tenant_id} with status {response.status}."
                        )
                        raise ValueError(f"Login failed with status code: {response.status}")

                    logging.info(f"Login successful for tenant {tenant.tenant_id}.")
                    return await response.json()
            except Exception as e:
                logging.error(f"Error during login for tenant {tenant.tenant_id}: {str(e)}")
                raise ValueError(f"An error occurred during login: {str(e)}")

    @staticmethod
    def decode_json_token(tenant: Tenant, user_token) -> DecodedJwtToken:
        settings = tenant.settings or {}

        # Extract required settings
        access_token = user_token.get("access_token")

        # Safely retrieve `setting_value` from the Setting object
        jwt_custom_fields = eval(settings.get("EXTERNAL_JWT_CUSTOM_FIELDS", {}).setting_value if "EXTERNAL_JWT_CUSTOM_FIELDS" in settings else "[]")
        user_identifier_field = settings.get("EXTERNAL_JWT_USER_IDENTIFIER_FIELD", {}).setting_value if "EXTERNAL_JWT_USER_IDENTIFIER_FIELD" in settings else None
        external_jwt_secret_key = settings.get("EXTERNAL_JWT_SECRET_KEY", {}).setting_value if "EXTERNAL_JWT_SECRET_KEY" in settings else None

        if not access_token:
            raise ValueError("Access token is missing in the user token.")
        if not (jwt_custom_fields and user_identifier_field and external_jwt_secret_key):
            raise ValueError("Required JWT settings are missing or incomplete.")

        try:
            token_bytes = access_token.encode("utf-8") if isinstance(access_token, str) else access_token
            decoded_payload = jwt.decode(token_bytes, external_jwt_secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

        # Extract custom fields from the token
        user_identifier_value = decoded_payload.get(user_identifier_field)
        if not user_identifier_value:
            raise ValueError(f"User identifier field '{user_identifier_field}' is missing in the token.")

        custom_field_values = {
            field: decoded_payload.get(field) for field in jwt_custom_fields if field in decoded_payload
        }
        if not custom_field_values:
            raise ValueError(f"None of the custom fields {jwt_custom_fields} were found in the token.")

        exp_timestamp = decoded_payload.get("exp")

        return DecodedJwtToken(
            tenant_id=tenant.tenant_id,
            custom_fields=custom_field_values,
            user_identifier=user_identifier_value,
            expiration= datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat() if exp_timestamp else None
        )