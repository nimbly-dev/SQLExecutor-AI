from model.authentication.session_data_setting import SessionDataSetting
from utils.tenant_manager.setting_utils import SettingUtils
from api.core.constants.tenant.settings_categories import POST_PROCESS_QUERYSCOPE_CATEGORY_KEY


def get_default_sql_generation_session_settings(tenant_settings):
    return {
        "SQL_GENERATION": {
            "REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE": SessionDataSetting(
                setting_basic_name="Remove Missing Columns on query scope",
                setting_value=SettingUtils.get_setting_value(tenant_settings, POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, "TENANT_SETTING_REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE") or "true",
                setting_description="REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE description not provided"
            ),
            "IGNORE_COLUMN_WILDCARDS": SessionDataSetting(
                setting_basic_name="Ignore Column Wildcards",
                setting_value=SettingUtils.get_setting_value(tenant_settings, POST_PROCESS_QUERYSCOPE_CATEGORY_KEY, "TENANT_SETTING_IGNORE_COLUMN_WILDCARDS") or "true",
                setting_description="IGNORE_COLUMN_WILDCARDS description not provided"
            )
        }
    }


def get_session_setting(session_settings, category, key):
    """
    Retrieve a specific setting value from session settings.

    :param session_settings: The session settings dictionary.
    :param category: The category of the setting.
    :param key: The specific setting key.
    :return: Setting value or None if not found.
    """
    category_settings = session_settings.get(category, {})
    setting = category_settings.get(key)

    # Handle both Setting object and plain dictionary
    if isinstance(setting, dict):
        return setting.get("setting_value")
    return setting.setting_value if setting else None
