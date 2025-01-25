export interface TenantSetting {
    setting_key: string;
    setting_detail: {
        setting_description: string;
        setting_basic_name: string;
        setting_default_value: string;
        setting_value: string;
        is_custom_setting: boolean;
    };
}