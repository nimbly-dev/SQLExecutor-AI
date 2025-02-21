import React, { useState } from 'react';
import { 
  IconButton, 
  Popover, 
  Box, 
  Typography,
  useTheme
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import LabelOutlinedIcon from '@mui/icons-material/LabelOutlined';
import SyncAltOutlinedIcon from '@mui/icons-material/SyncAltOutlined';
import NumbersOutlinedIcon from '@mui/icons-material/NumbersOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';

const CONDITION_CATEGORIES = [
  {
    title: 'Role Checks',
    icon: LabelOutlinedIcon,
    color: 'info.main',
    examples: [
      {
        code: "'admin' in ${jwt.custom_fields.role}",
        description: 'Check if user has admin role'
      },
      {
        code: "'doctor' in ${jwt.custom_fields.role}",
        description: 'Check if user has doctor role'
      }
    ]
  },
  {
    title: 'Status Checks',
    icon: SyncAltOutlinedIcon,
    color: 'success.main',
    examples: [
      {
        code: "${jwt.custom_fields.is_active} == 'TRUE'",
        description: 'Check if user is active (use TRUE or FALSE)'
      }
    ]
  },
  {
    title: 'Numeric Comparisons',
    icon: NumbersOutlinedIcon,
    color: 'warning.main',
    examples: [
      {
        code: "${jwt.custom_fields.age} > 18",
        description: 'Compare numeric values directly'
      }
    ]
  },
  {
    title: 'Complex Logic',
    icon: SettingsOutlinedIcon,
    color: 'secondary.main',
    examples: [
      {
        code: "('admin' in ${jwt.custom_fields.role}) and (${jwt.custom_fields.is_active} == 'TRUE')",
        description: 'Combine multiple conditions with and/or'
      }
    ]
  }
];

const USAGE_NOTES = [
  {
    title: 'String Values',
    description: "Always wrap text values in single quotes: 'admin', 'TRUE', 'active'"
  },
  {
    title: 'Boolean Values',
    description: "Use 'TRUE' or 'FALSE' (case-sensitive) for boolean comparisons"
  },
  {
    title: 'Field References',
    description: "Use ${jwt.custom_fields.field_name} to access JWT fields"
  },
  {
    title: 'Evaluation',
    description: "Conditions are evaluated as Python expressions at runtime"
  }
];

export const ConditionOutlineHelpIcon: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const theme = useTheme();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton
        onClick={handleClick}
        size="small"
        aria-label="View condition examples"
      >
        <HelpOutlineIcon />
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        slotProps={{
          paper: {
            sx: {
              maxHeight: 400,
              width: 400,
              p: 2,
              overflowY: 'auto'
            }
          }
        }}
      >
        {/* Usage Notes Section */}
        <Typography variant="h6" gutterBottom>
          Important Notes
        </Typography>
        {USAGE_NOTES.map((note, index) => (
          <Box key={index} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="primary">
              {note.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {note.description}
            </Typography>
          </Box>
        ))}

        {/* Examples Section */}
        <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
          Example Conditions
        </Typography>
        {CONDITION_CATEGORIES.map((category) => {
          const Icon = category.icon;
          return (
            <Box key={category.title} sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Icon sx={{ color: category.color }} />
                <Typography variant="subtitle2">
                  {category.title}
                </Typography>
              </Box>
              {category.examples.map((example, index) => (
                <Box key={index} sx={{ ml: 4, mb: 1 }}>
                  <Typography
                    sx={{
                      fontFamily: 'monospace',
                      p: 1,
                      borderRadius: 1,
                      bgcolor: theme.palette.mode === 'light' 
                        ? 'grey.100' 
                        : 'grey.800',
                      fontSize: '0.875rem'
                    }}
                  >
                    {example.code}
                  </Typography>
                  <Typography 
                    variant="caption" 
                    color="text.secondary"
                    sx={{ ml: 1 }}
                  >
                    {example.description}
                  </Typography>
                </Box>
              ))}
            </Box>
          );
        })}
      </Popover>
    </>
  );
};

export default ConditionOutlineHelpIcon;
