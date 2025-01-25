import React, { useCallback } from 'react';
import { Typography, Box, Button, useTheme, Divider } from '@mui/material';
import SQLSettingsGroup from './SQLSettingsGroup';
import { Setting, SettingDetail, TransformedSettingsGroup } from '../../../types/chat-interface/chatInterfaceSettings';
import '../../../styles/sqlexecutor-playground/right-cards/settings.scss';

export interface SettingsAccordionProps {
  section: {
    parentToggle?: boolean;
    groups: TransformedSettingsGroup[];
  };
  onToggle: (groupTitle: string, settingKey: string) => void;
  dependencies: Record<string, boolean>;
  onSave: () => void;
  isSessionActive: boolean;
  hasChanges: boolean;
}

const SettingsAccordion: React.FC<SettingsAccordionProps> = ({
  section,
  onToggle,
  dependencies,
  onSave,
  isSessionActive,
  hasChanges,
}) => {
  const theme = useTheme();
  const checkActiveSession = useCallback(() => !!sessionStorage.getItem('contextUserSessionId'), []);

  const dividerStyle = {
    opacity: 0.1,
    borderColor: theme.palette.mode === 'dark' 
      ? 'rgba(255, 255, 255, 0.2)' 
      : 'rgba(0, 0, 0, 0.2)'
  };

  return (
    <Box 
      className="settings-container" 
      sx={{
        backgroundColor: theme.palette.mode === 'dark' 
          ? theme.palette.background.default 
          : theme.palette.background.paper,
        borderRadius: 1,
        padding: 1.5, 
      }}
    >
      <Box className="settings-content">
        <Typography 
          variant="subtitle1" 
          sx={{ 
            mb: 1.5,
            color: theme.palette.text.primary,
            fontWeight: 'bold', // Changed to bold
            fontSize: '0.95rem' 
          }}
        >
          SQL Generation Settings
        </Typography>
        <Divider sx={{ ...dividerStyle, mb: 2 }} />
        
        {section.groups.map((group, idx) => (
          <Box
            key={idx}
            className={`settings-group ${!checkActiveSession() ? 'settings-group--disabled' : ''}`}
            sx={{ mb: idx < section.groups.length - 1 ? 2 : 1.5 }}
          >
            <Typography 
              variant="subtitle2" 
              sx={{ 
                mb: 1,
                fontSize: '0.875rem', 
                fontWeight: 500
              }}
            >
              {group.title}
            </Typography>
            <SQLSettingsGroup
              group={{ title: group.title, settings: group.settings }}
              disabled={!checkActiveSession()}
              onToggle={(settingKey) => onToggle(group.title, settingKey)}
              dependencies={dependencies}
            />
            {idx < section.groups.length - 1 && (
              <Divider 
                sx={{ 
                  ...dividerStyle, 
                  mt: 2
                }} 
              />
            )}
          </Box>
        ))}
      </Box>
      <Divider sx={{ ...dividerStyle }} />
      <Box 
        className="settings-footer" 
        sx={{ 
          mt: 1.5,
          pt: 1.5,
          display: 'flex',
          justifyContent: 'flex-end',
        }}
      >
        <Button
          variant="contained"
          size="small" // Changed to small
          onClick={onSave}
          disabled={!isSessionActive || !hasChanges}
        >
          {hasChanges ? 'Save Changes' : 'No Changes'}
        </Button>
      </Box>
    </Box>
  );
};

export default SettingsAccordion;
