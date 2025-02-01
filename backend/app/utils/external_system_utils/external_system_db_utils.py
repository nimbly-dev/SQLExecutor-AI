from typing import Optional
from utils.tenant_manager.setting_utils import SettingUtils
from model.tenant.tenant import Tenant
from api.core.constants.tenant.settings_categories import (
    EXTERNAL_SYSTEM_MYSQL_DB_SETTING,
    EXTERNAL_SYSTEM_POSTGRES_DB_SETTING
)

def build_db_url_based_on_dialect(tenant: Tenant, dialect: str, schema: Optional[str] = None):
    """Build the database URL based on the tenant configuration."""
    
    if dialect == "postgresql":
        EXTERNAL_TENANT_DB_USERNAME = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_POSTGRES_DB_SETTING,
            setting_key="EXTERNAL_TENANT_POSTGRES_DB_USERNAME"
        )
        EXTERNAL_TENANT_DB_PASSWORD = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_POSTGRES_DB_SETTING,
            setting_key="EXTERNAL_TENANT_POSTGRES_DB_PASSWORD"
        )
        EXTERNAL_TENANT_DB_HOST = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_POSTGRES_DB_SETTING,
            setting_key="EXTERNAL_TENANT_POSTGRES_DB_HOST"
        )
        EXTERNAL_TENANT_DB_PORT = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_POSTGRES_DB_SETTING,
            setting_key="EXTERNAL_TENANT_POSTGRES_DB_PORT"
        )
        EXTERNAL_TENANT_DB_NAME = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_POSTGRES_DB_SETTING,
            setting_key="EXTERNAL_TENANT_POSTGRES_DB_NAME"
        )
        return  f"postgresql://{EXTERNAL_TENANT_DB_USERNAME}:{EXTERNAL_TENANT_DB_PASSWORD}@{EXTERNAL_TENANT_DB_HOST}:{EXTERNAL_TENANT_DB_PORT}/{EXTERNAL_TENANT_DB_NAME}"
    elif dialect == "mysql":
        EXTERNAL_TENANT_DB_USERNAME = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_MYSQL_DB_SETTING,
            setting_key="EXTERNAL_TENANT_MYSQL_DB_USERNAME"
        )
        EXTERNAL_TENANT_DB_PASSWORD = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_MYSQL_DB_SETTING,
            setting_key="EXTERNAL_TENANT_MYSQL_DB_PASSWORD"
        )
        EXTERNAL_TENANT_DB_HOST = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_MYSQL_DB_SETTING,
            setting_key="EXTERNAL_TENANT_MYSQL_DB_HOST"
        )
        EXTERNAL_TENANT_DB_PORT = SettingUtils.get_setting_value(
            settings=tenant.settings,
            category_key=EXTERNAL_SYSTEM_MYSQL_DB_SETTING,
            setting_key="EXTERNAL_TENANT_MYSQL_DB_PORT"
        )
        return f"mysql+pymysql://{EXTERNAL_TENANT_DB_USERNAME}:{EXTERNAL_TENANT_DB_PASSWORD}@{EXTERNAL_TENANT_DB_HOST}:{EXTERNAL_TENANT_DB_PORT}/{schema}"
    
    return None