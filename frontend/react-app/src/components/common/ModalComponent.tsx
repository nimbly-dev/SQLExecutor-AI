import { Modal, Box, Typography, Button } from '@mui/material';
import React from 'react';

interface ModalComponentProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  onSubmit: () => void;
  submitDisabled: boolean;
}

export const ModalComponent: React.FC<ModalComponentProps> = ({
  open,
  onClose,
  title,
  children,
  onSubmit,
  submitDisabled,
}) => {
  return (
    <Modal open={open} onClose={onClose}>
      <Box sx={{ width: 500, margin: 'auto', mt: 5, p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {children}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
          <Button onClick={onClose} variant="outlined">
            Cancel
          </Button>
          <Button onClick={onSubmit} variant="contained" disabled={submitDisabled}>
            Submit
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};
