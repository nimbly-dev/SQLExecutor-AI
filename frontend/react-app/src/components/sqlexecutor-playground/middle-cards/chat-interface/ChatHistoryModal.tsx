import React from 'react';
import { Modal, Box, Typography, List, ListItem, ListItemText, Divider, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useTheme } from '@mui/material/styles';

interface QueryHistoryItem {
  prompt: string;
  sql: string;
}

interface ChatHistoryModalProps {
  open: boolean;
  onClose: () => void;
  history: QueryHistoryItem[]; // Update the type to match the new format
}

const ChatHistoryModal: React.FC<ChatHistoryModalProps> = ({ open, onClose, history }) => {
  const theme = useTheme();

  return (
    <Modal open={open} onClose={onClose} aria-labelledby="chat-history-modal-title">
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: { xs: '90%', sm: '600px' },
          maxHeight: '80vh',
          backgroundColor: 'transparent',
          border: 'none',
          boxShadow: 'none',
          '& .MuiTypography-root': {
            color: 'inherit',
          },
          '& .MuiDivider-root': {
            borderColor: theme.palette.mode === 'dark' ? '#444444' : 'divider',
          },
          '&::-webkit-scrollbar': {
            width: '8px',
            backgroundColor: theme.palette.mode === 'dark' ? '#1e1e1e' : '#f1f1f1',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: theme.palette.mode === 'dark' ? '#444444' : '#888888',
            borderRadius: '4px',
          },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography id="chat-history-modal-title" variant="h6" sx={{
            fontSize: '18px',
            fontWeight: 'bold',
            marginBottom: '10px',
            borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0'}`,
            paddingBottom: '10px',
          }}>
            Query History
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider sx={{ mb: 2, borderColor: theme.palette.mode === 'dark' ? '#444444' : '#e0e0e0' }} />
        {history.length > 0 ? (
          <List>
            {history.map((item, index) => (
              <ListItem key={index} divider>
                <ListItemText
                  primary={`Prompt: ${item.prompt}`}
                  secondary={`SQL: ${item.sql}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2">No queries executed yet.</Typography>
        )}
      </Box>
    </Modal>
  );
};

export default ChatHistoryModal;
