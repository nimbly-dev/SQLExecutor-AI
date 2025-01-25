from utils.tenant_manager.setting_utils import SettingUtils
from model.tenant.tenant import Tenant
from api.core.constants.tenant.settings_categories import EXTERNAL_SYSTEM_DB_SETTING

def build_db_url(tenant: Tenant):
    """Build the database URL based on the tenant configuration."""
    EXTERNAL_TENANT_DB_DIALECT = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_DIALECT"
    )
    EXTERNAL_TENANT_DB_USERNAME = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_USERNAME"
    )
    EXTERNAL_TENANT_DB_PASSWORD = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_PASSWORD"
    )
    EXTERNAL_TENANT_DB_HOST = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_HOST"
    )
    EXTERNAL_TENANT_DB_PORT = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_PORT"
    )
    EXTERNAL_TENANT_DB_NAME = SettingUtils.get_setting_value(
        settings=tenant.settings,
        category_key=EXTERNAL_SYSTEM_DB_SETTING,
        setting_key="EXTERNAL_TENANT_DB_NAME"
    )
    
    db_url = f"{EXTERNAL_TENANT_DB_DIALECT}://{EXTERNAL_TENANT_DB_USERNAME}:{EXTERNAL_TENANT_DB_PASSWORD}@{EXTERNAL_TENANT_DB_HOST}:{EXTERNAL_TENANT_DB_PORT}/{EXTERNAL_TENANT_DB_NAME}"
    return db_url
