import React from 'react';
import { Box, useTheme } from '@mui/material';
import SettingsAccordion from './SettingsAccordion';
import { useSettingsManagement } from '../../../hooks/sqlexecutor-playground/right-cards/useSettingsManagement';
import { useSQLExecutorContext } from '../../../pages/SQLExecutorPlayground';
import { TransformedSettings, SettingDetail } from '../../../types/chat-interface/chatInterfaceSettings';

function RightCards() {
  const theme = useTheme();
  const { sqlSettings } = useSQLExecutorContext();
  const {
    pendingSettings,
    handleSettingToggle,
    handleSaveSettings,
    getDependencies,
    hasActiveSession,
    hasChanges
  } = useSettingsManagement(sqlSettings);

  // Default settings structure when no user is impersonated
  const defaultSettings: TransformedSettings = {
    parentToggle: false,
    groups: [
      {
        title: 'Query Scope Setting',
        description: 'Control query scope behavior',
        settings: {
          REMOVE_SENSITIVE_COLUMNS: { // Changed from 'QUERY_SCOPE_ENABLED'
            setting_description: 'Removes sensitive columns that were declared on schema',
            setting_basic_name: 'Remove Sensitive Columns',
            setting_toggle: false
          }
        }
      },
      {
        title: 'SQL Injectors',
        description: 'Configure SQL query injection behavior and safety features',
        settings: {
          SQL_INJECTORS_ENABLED: {
            setting_description: 'Enable SQL injectors',
            setting_basic_name: 'SQL Injectors',
            setting_toggle: false,
          },
          DYNAMIC_INJECTION: {
            setting_description: 'Enable dynamic injection',
            setting_basic_name: 'Dynamic Injection',
            setting_toggle: false,
            depends_on: 'SQL_INJECTORS_ENABLED'
          }
        }
      },
      {
        title: 'SQL Generation',
        description: 'Configure SQL generation behavior and safety features',
        settings: {
          REMOVE_MISSING_COLUMNS_ON_QUERY_SCOPE: {
            setting_description: 'Remove missing columns',
            setting_basic_name: 'Remove Missing Columns',
            setting_toggle: false
          }
        }
      }
    ]
  };

  const settingsToUse = pendingSettings || defaultSettings;

  return (
    <Box
      sx={{
        padding: '20px',
        backgroundColor: 'transparent',
        borderRadius: '5px',
        order: { xs: 1, md: 'unset' },
        marginBottom: { xs: 2, md: 0 },
        opacity: hasActiveSession() ? 1 : 0.7,
        '& > *': {
          backgroundColor: theme.palette.mode === 'dark' ? 'transparent' : '#ffffff',
          boxShadow: theme.palette.mode === 'dark' 
            ? 'none'
            : '0px 4px 6px rgba(0, 0, 0, 0.1)',
          borderRadius: '5px',
          border: `1px solid ${theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0'}`,
        }
      }}
    >
      <SettingsAccordion
        section={settingsToUse}
        onToggle={handleSettingToggle}
        dependencies={getDependencies(settingsToUse.groups)}
        onSave={handleSaveSettings}
        isSessionActive={hasActiveSession()}
        hasChanges={hasChanges}
      />
    </Box>
  );
}

export default RightCards;
