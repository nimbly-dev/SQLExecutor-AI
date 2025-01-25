// Base setting interface
export interface BaseSetting {
  setting_description: string;
  setting_basic_name: string;
  depends_on?: string;
}

// For API responses
export interface SettingDetail extends BaseSetting {
  setting_toggle: boolean;
}

// For UI components
export interface Setting extends BaseSetting {
  setting_value: boolean;
}

export interface SettingsGroup {
  title: string;
  description: string;
  settings: Record<string, Setting>;
}

export interface TransformedSettingsGroup {
  title: string;
  description: string;
  settings: Record<string, SettingDetail>;
}

export interface TransformedSettings {
  parentToggle: boolean;
  groups: TransformedSettingsGroup[];
}

export interface SettingsSection {
  QUERY_SCOPE_SETTING? : Record<string, SettingDetail>;
  SQL_INJECTORS?: Record<string, SettingDetail>;
  SQL_GENERATION?: Record<string, SettingDetail>;
}

export interface SettingsResponse {
  data: {
    query_scope_setting:{
      QUERY_SCOPE_SETTINGS: Record<string, SettingDetail>
    }
    injectors_setting: {
      SQL_INJECTORS: Record<string, SettingDetail>;
    };
    sql_generation: {
      SQL_GENERATION: Record<string, SettingDetail>;
    };
  };
}

interface UpdateChatInterfaceSettingRequest {
  setting_toggle: boolean;
}

export interface SettingsUpdatePayload {
  QUERY_SCOPE: {
    [key: string]: boolean;
  };
  SQL_INJECTORS: {
    [key: string]: boolean;
  };
  SQL_GENERATION: {
    [key: string]: boolean;
  };
}

export interface SQLSetting {
  setting_description: string;
  setting_basic_name: string;
  setting_value: boolean;
}

export interface SQLSettingDisplay extends SQLSetting {
  depends_on?: string;
}

export interface SQLSettingsGroup {
  title: string;
  description: string;
  settings: Record<string, SQLSettingDisplay>;
}

export interface SQLSettingsSection {
  parentToggle: boolean;
  groups: SQLSettingsGroup[];
}
