import React, { useState } from 'react';
import {
  TextField,
  Box,
  Chip,
  Tooltip,
  tooltipClasses,
  styled,
  TooltipProps,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

export interface TextListsTagsFormFieldProps {
  /** Currently selected tags */
  tags: string[];
  /** Callback fired when tags change */
  onChange: (newTags: string[]) => void;
  /** Label for the text field */
  label?: string;
  /** Placeholder text for the text field */
  placeholder?: string;
  /** Additional props for the TextField */
  textFieldProps?: Record<string, any>;
  /** Optional function to get tooltip text for a tag */
  getTooltip?: (value: string) => string;
  /** Callback fired when the field loses focus */
  onBlur?: () => void;
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
 * A form field component that allows users to enter text to create tags.
 * Tags can be created by pressing Enter.
 */
/**
 * A form field component that manages a list of tags with text input functionality.
 * 
 * @component
 * @param {Object} props - The component props
 * @param {string[]} props.tags - Array of current tags
 * @param {function} props.onChange - Callback function triggered when tags are added or removed
 * @param {string} [props.label=''] - Label for the text input field
 * @param {string} [props.placeholder='Type and press Enter to add'] - Placeholder text for the input field
 * @param {Object} [props.textFieldProps={}] - Additional props to be passed to the TextField component
 * @param {function} [props.getTooltip] - Optional function that returns tooltip text for a given tag
 * 
 * @returns A text input field with a collection of deletable tag chips below it.
 * Users can add new tags by typing text and pressing Enter.
 * Duplicate tags are prevented from being added.
 * Each tag can be deleted by clicking its delete icon.
 */
const TextListsTagsFormField: React.FC<TextListsTagsFormFieldProps> = ({
  tags,
  onChange,
  onBlur,
  label = '',
  placeholder = 'Type and press Enter to add',
  textFieldProps = {},
  getTooltip,
}) => {
  const [inputValue, setInputValue] = useState<string>('');
  const [localTags, setLocalTags] = useState<string[]>(tags);

  // Update local tags when props change
  React.useEffect(() => {
    setLocalTags(tags);
  }, [tags]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && inputValue.trim()) {
      event.preventDefault();
      // Only update local state
      if (!localTags.includes(inputValue.trim())) {
        const newTags = [...localTags, inputValue.trim()];
        setLocalTags(newTags);
      }
      setInputValue('');
    }
  };

  const handleTagDelete = (tagToDelete: string) => {
    // Only update local state
    const newTags = localTags.filter((tag) => tag !== tagToDelete);
    setLocalTags(newTags);
  };

  // Commit changes on blur
  const handleBlur = () => {
    onChange(localTags);
    onBlur?.();
  };

  return (
    <Box>
      <TextField
        label={label}
        placeholder={placeholder}
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        fullWidth
        variant="outlined"
        size="small"
        {...textFieldProps}
      />
      <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {localTags.map((tag) => (
          <StyledTooltip
            key={tag}
            title={getTooltip ? getTooltip(tag) : ''}
            placement="top"
          >
            <Chip
              label={tag}
              onDelete={() => handleTagDelete(tag)}
              deleteIcon={<CloseIcon />}
            />
          </StyledTooltip>
        ))}
      </Box>
    </Box>
  );
};

export default TextListsTagsFormField;
