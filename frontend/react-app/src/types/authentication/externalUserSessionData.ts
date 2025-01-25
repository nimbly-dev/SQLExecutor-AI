export interface CustomFields {
    role: string;
    is_admin: boolean;
    is_active: boolean;
    sub: string;
    user_id: number;
}
 
export interface Setting {
    setting_description: string;
    setting_basic_name: string;
    setting_value: string;
}

export interface SettingsCategory {
    [key: string]: Setting; 
}

export interface ExternalSessionSettings {
    [category: string]: SettingsCategory; 
}

interface SessionSetting {
  setting_description: string;
  setting_basic_name: string;
  setting_value: string;
}

interface SessionSettings {
  SQL_GENERATION: {
    [key: string]: SessionSetting;
  };
}

export interface ExternalSessionData {
    session_id: string;
    tenant_id: string;
    user_id: string;
    custom_fields: Record<string, any>;
    created_at: string;
    expires_at: string;
    session_settings: SessionSettings;
}

export interface ExternalContextUserRow {
    username: string;
    custom_fields: {
        [key: string]: string;
    };
}
