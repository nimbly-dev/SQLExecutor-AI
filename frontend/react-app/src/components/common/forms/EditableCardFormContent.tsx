// EditableCardFormContent.tsx
import React, { useState, useEffect } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  TextField,
  Box,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from 'styles/common/forms/EditableCardFormContent.module.scss';

export interface EditableCardFormContentProps {
  /** The key/field name for the card title */
  fieldKey: string;
  /** The value object associated with the field key */
  fieldValue: Record<string, any>;
  /**
   * Callback fired when the field title or its value changes.
   * Returns the updated field key and field value.
   */
  onChange: (newFieldKey: string, newFieldValue: Record<string, any>) => void;
  /** Callback fired when delete is triggered */
  onDelete: () => void;
  /** Child content for the card body */
  children?: React.ReactNode;
  /** Optional initial expanded state */
  defaultExpanded?: boolean;
  /** Label to display before the card title */
  titleLabel: string;
}

const EditableCardFormContent: React.FC<EditableCardFormContentProps> = ({
  fieldKey,
  fieldValue,
  onChange,
  onDelete,
  children,
  defaultExpanded = false,
  titleLabel,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [localTitle, setLocalTitle] = useState(fieldKey);
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  useEffect(() => {
    setLocalTitle(fieldKey);
  }, [fieldKey]);

  const commitTitleChange = () => {
    setIsEditingTitle(false);
    if (localTitle.trim() && localTitle !== fieldKey) {
      onChange(localTitle, fieldValue);
    }
  };

  const handleAccordionChange = (_event: React.SyntheticEvent, expanded: boolean) => {
    if (!isEditingTitle) {
      setIsExpanded(expanded);
    }
  };

  const handleTitleClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    setIsEditingTitle(true);
  };

  return (
    <Accordion
      expanded={isExpanded}
      onChange={handleAccordionChange}
      defaultExpanded={defaultExpanded}
      sx={{
        backgroundColor: 'transparent',
        boxShadow: 'none',
        '&:before': { display: 'none' },
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon className={styles.expandIcon} />}
        className={styles.accordionSummary}
        onClick={(e) => {
          if (isEditingTitle) {
            e.stopPropagation();
          }
        }}
      >
        <Box 
          className={styles.contentWrapper}
          onClick={(e) => {
            if (isEditingTitle) {
              e.stopPropagation();
            }
          }}
        >
          <Typography color="text.secondary" className={styles.label}>
            {titleLabel}:
          </Typography>
          {isEditingTitle ? (
            <TextField
              value={localTitle}
              onChange={(e) => setLocalTitle(e.target.value)}
              onBlur={commitTitleChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  commitTitleChange();
                }
                e.stopPropagation();
              }}
              onClick={(e) => e.stopPropagation()}
              size="small"
              variant="standard"
              autoFocus
              className={styles.titleField}
            />
          ) : (
            <Typography
              variant="h6"
              onClick={handleTitleClick}
              className={styles.titleText}
              color="primary"
            >
              {localTitle}
            </Typography>
          )}
        </Box>
        <Box 
          className={styles.buttonsGroup}
          onClick={(e) => e.stopPropagation()}
        >
          <IconButton
            size="large"
            onClick={(e) => {
              e.stopPropagation();
              handleTitleClick(e);
            }}
            className={`${styles.actionButton} editButton`}
          >
            <EditIcon className={styles.icon} />
          </IconButton>
          <IconButton
            size="large"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className={`${styles.actionButton} deleteButton`}
          >
            <DeleteIcon className={styles.icon} />
          </IconButton>
        </Box>
      </AccordionSummary>
      {/* Removed onClick stopPropagation here to allow inner interactive elements (like Select) to work properly */}
      <AccordionDetails sx={{ p: 2 }}>
        <Box sx={{ width: '100%', pointerEvents: 'auto' }}>{children}</Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default React.memo(EditableCardFormContent);
