import React from 'react';
import { Typography, Box, Tooltip, IconButton, Switch, useTheme } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { SettingDetail } from '../../../types/chat-interface/chatInterfaceSettings';

interface SQLSettingsGroupProps {
  group: {
    title: string;
    settings: Record<string, SettingDetail>;
  };
  disabled: boolean;
  onToggle: (settingKey: string) => void;
  dependencies: Record<string, boolean>;
}

const SQLSettingsGroup: React.FC<SQLSettingsGroupProps> = ({
  group,
  disabled,
  onToggle,
  dependencies,
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      {Object.entries(group.settings).map(([key, setting]) => {
        const isDisabled = setting.depends_on
          ? !dependencies[setting.depends_on]
          : disabled;

        return (
          <Box
            key={key}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <Tooltip title={setting.setting_description} arrow>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Typography sx={{ fontSize: '0.85rem' }}>
                  {setting.setting_basic_name}
                </Typography>
                <IconButton size="small">
                  <InfoOutlinedIcon sx={{ fontSize: '0.9rem' }} />
                </IconButton>
              </Box>
            </Tooltip>
            <Switch
              checked={setting.setting_toggle}
              onChange={() => !isDisabled && onToggle(key)}
              disabled={isDisabled}
              size="small"
            />
          </Box>
        );
      })}
    </Box>
  );
};

export default SQLSettingsGroup;
