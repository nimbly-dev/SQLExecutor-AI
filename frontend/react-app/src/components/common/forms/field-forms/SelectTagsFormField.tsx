import React, { useState, useRef } from 'react';
import {
  TextField,
  Box,
  Chip,
  Menu,
  MenuItem,
  ListItemText,
  Tooltip,
  tooltipClasses,
  styled,
  TooltipProps,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

export interface SelectOption {
  value: string;
  disabled: boolean;
}

export interface SelectTagsFormFieldProps {
  /** All available options */
  options: SelectOption[];
  /** Currently selected values */
  selected: string[];
  /** Callback fired when the selection changes */
  onChange: (newSelected: string[], action: 'add' | 'remove', changedValue?: string) => void;
  /** Label for the select field */
  label?: string;
  /** Placeholder text for the select field */
  placeholder?: string;
  /** Additional props for the TextField */
  textFieldProps?: Record<string, any>;
  /** Whether to show selected values in the text field */
  showSelectedInField?: boolean;
  /** Custom text to show in the text field */
  customTextValue?: string;
  /** Tooltip message */
  tooltipMessage?: string;
  /** Optional function to get tooltip text for a value */
  getTooltip?: (value: string) => string;
}

const StyledTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    fontSize: '0.875rem', 
    padding: '8px 12px',
    lineHeight: '1.4',
    backgroundColor: theme.palette.grey[900],
  },
}));

/**
 * A form field component that allows users to select multiple tags from a dropdown menu.
 * 
 * @component
 * @param {Object} props - The component props
 * @param {Array<{value: string, disabled?: boolean}>} props.options - Array of options to select from
 * @param {string[]} props.selected - Array of currently selected values
 * @param {(selected: string[], action: 'add' | 'remove', value: string) => void} props.onChange - Callback fired when selection changes
 * @param {string} [props.label] - Label text for the field
 * @param {string} [props.placeholder='Select an option'] - Placeholder text when no value is selected
 * @param {Object} [props.textFieldProps] - Additional props to pass to TextField component
 * @param {boolean} [props.showSelectedInField=false] - Whether to show selected values in the text field
 * @param {string} [props.customTextValue] - Custom text to display in text field
 * @param {string} [props.tooltipMessage] - Message to show in tooltip for the entire field
 * @param {(option: string) => string} [props.getTooltip] - Function to get tooltip text for individual tags
 * 
 * @returns {JSX.Element} A form field component with dropdown selection and tag display
 */
const SelectTagsFormField: React.FC<SelectTagsFormFieldProps> = ({
  options,
  selected,
  onChange,
  label = '',
  placeholder = 'Select an option',
  textFieldProps = {},
  showSelectedInField = false,
  customTextValue,
  tooltipMessage,
  getTooltip,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  
  const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = (
    event: {},
    reason: "backdropClick" | "escapeKeyDown"
  ) => {
    setAnchorEl(null);
  };

  const handleOptionClick = (option: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option), 'remove', option);
    } else {
      onChange([...selected, option], 'add', option);
    }
  };

  const handleTagDelete = (option: string, event: React.MouseEvent) => {
    event.stopPropagation();
    onChange(selected.filter((s) => s !== option), 'remove', option);
  };

  const getTextFieldValue = () => {
    if (customTextValue) {
      return customTextValue;
    }
    if (showSelectedInField) {
      return selected.join(', ');
    }
    return '';
  };

  return (
    <Box onClick={(e) => e.stopPropagation()}>
      <StyledTooltip title={tooltipMessage || ''} open={!!tooltipMessage}>
        <Box
          onClick={handleClick}
          sx={{ cursor: 'pointer', position: 'relative' }}
        >
          <TextField
            label={label}
            placeholder={placeholder}
            fullWidth
            variant="outlined"
            size="small"
            {...textFieldProps}
            value={getTextFieldValue()}
            InputProps={{
              readOnly: true,
            }}
          />
        </Box>
      </StyledTooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={(e) => e.stopPropagation()}
        MenuListProps={{
          'aria-labelledby': 'basic-button',
        }}
        sx={{
          zIndex: 9999,
        }}
      >
        {options.map((option) => (
          <MenuItem
            key={option.value}
            onClick={(e) => !option.disabled && handleOptionClick(option.value, e)}
            selected={selected.includes(option.value)}
            disabled={option.disabled}
            sx={{ 
              minWidth: '200px',
              opacity: option.disabled ? 0.5 : 1,
              cursor: option.disabled ? 'not-allowed' : 'pointer'
            }}
          >
            <ListItemText primary={option.value} />
          </MenuItem>
        ))}
      </Menu>

      <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {selected.map((option) => (
          <StyledTooltip 
            key={option} 
            title={getTooltip ? getTooltip(option) : ''}
            placement="top"
          >
            <Chip
              label={option}
              onDelete={(e) => handleTagDelete(option, e)}
              deleteIcon={<CloseIcon />}
              onClick={(e) => e.stopPropagation()}
            />
          </StyledTooltip>
        ))}
      </Box>
    </Box>
  );
};

export default SelectTagsFormField;
