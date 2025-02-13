import { useState, useCallback, useEffect } from 'react';
import { 
  SettingsResponse, 
  SettingsUpdatePayload, 
  TransformedSettings,
  SettingDetail 
} from '@sqlexecutor-types/chat-interface/chatInterfaceSettings';
import { fetchChatInterfaceSettings, updateChatInterfaceSettings } from 'services/chatInterfaceSettingsService';
import { toast } from 'react-toastify';

export const useSettingsManagement = (initialSettings: TransformedSettings | null) => {
  const [pendingSettings, setPendingSettings] = useState<TransformedSettings | null>(initialSettings);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    setPendingSettings(initialSettings);
  }, [initialSettings]);

  const handleSettingToggle = useCallback((groupTitle: string, settingKey: string) => {
    setPendingSettings((current) => {
      if (!current) return null;

      const newGroups = current.groups.map(group => {
        if (group.title === groupTitle) {
          return {
            ...group,
            settings: {
              ...group.settings,
              [settingKey]: {
                ...group.settings[settingKey],
                setting_toggle: !group.settings[settingKey].setting_toggle
              }
            }
          };
        }
        return group;
      });

      setHasChanges(true);
      return { ...current, groups: newGroups };
    });
  }, []);

  const getDependencies = useCallback((groups: TransformedSettings['groups']) => {
    const dependencies: Record<string, boolean> = {};
    groups.forEach(group => {
      Object.entries(group.settings).forEach(([key, setting]) => {
        dependencies[key] = setting.setting_toggle;
      });
    });
    return dependencies;
  }, []);

  const handleSaveSettings = async () => {
    if (!pendingSettings || !hasChanges) return;

    const sessionId = sessionStorage.getItem('contextUserSessionId');
    if (!sessionId) {
      toast.error('No active session');
      return;
    }

    try {
      const payload: SettingsUpdatePayload = {
        QUERY_SCOPE: {},
        SQL_INJECTORS: {},
        SQL_GENERATION: {}
      };

      pendingSettings.groups.forEach(group => {
        switch (group.title) {
          case 'Query Scope Setting':
            Object.entries(group.settings).forEach(([key, value]) => {
              payload.QUERY_SCOPE[key] = value.setting_toggle;
            });
            break;
          case 'SQL Injectors':
            Object.entries(group.settings).forEach(([key, value]) => {
              payload.SQL_INJECTORS[key] = value.setting_toggle;
            });
            break;
          case 'SQL Generation':
            Object.entries(group.settings).forEach(([key, value]) => {
              payload.SQL_GENERATION[key] = value.setting_toggle;
            });
            break;
        }
      });

      await updateChatInterfaceSettings(sessionId, payload);
      const updatedSettings = await fetchChatInterfaceSettings(sessionId);
      const transformed = transformSettingsResponse(updatedSettings);
      setPendingSettings(transformed);
      setHasChanges(false);
      toast.success('Settings updated successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save settings');
    }
  };

  return {
    pendingSettings,
    handleSettingToggle,
    handleSaveSettings,
    getDependencies,
    hasActiveSession: () => !!sessionStorage.getItem('contextUserSessionId'),
    hasChanges
  };
};

// Helper function to transform API response to our format
export function transformSettingsResponse(response: SettingsResponse): TransformedSettings {
  return {
    parentToggle: true,
    groups: [
      {
        title: 'Query Scope Setting', // Consistent title
        description: 'Control query scope behavior',
        settings: Object.entries(response.data.query_scope_setting.QUERY_SCOPE_SETTINGS).reduce((acc, [key, value]) => {
          acc[key] = {
            ...value,
            setting_toggle: value.setting_toggle
          };
          return acc;
        }, {} as Record<string, SettingDetail>)
      },
      {
        title: 'SQL Injectors',
        description: 'Configure SQL query injection behavior and safety features',
        settings: Object.entries(response.data.injectors_setting.SQL_INJECTORS).reduce((acc, [key, value]) => {
          acc[key] = {
            ...value,
            setting_toggle: value.setting_toggle
          };
          return acc;
        }, {} as Record<string, SettingDetail>)
      },
      {
        title: 'SQL Generation',
        description: 'Control SQL query generation behavior',
        settings: Object.entries(response.data.sql_generation.SQL_GENERATION).reduce((acc, [key, value]) => {
          acc[key] = {
            ...value,
            setting_toggle: value.setting_toggle
          };
          return acc;
        }, {} as Record<string, SettingDetail>)
      }
    ]
  };
}
