import React from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import ContextUserCard from './ContextUserCard';
import ImpersonationModal from './ImpersonationModal';
import { useSQLExecutorContext } from '../../../pages/SQLExecutorPlayground';

const LeftPanel: React.FC = () => {
  const theme = useTheme();
  const { 
    sessionData, 
    stopImpersonation, 
    isModalOpen, 
    setIsModalOpen, 
    loadContextSession 
  } = useSQLExecutorContext();

  const handleOpenModal = () => setIsModalOpen(true);
  const handleStopImpersonation = () => {
    stopImpersonation();
    loadContextSession(); // Reload the session after stopping impersonation
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    loadContextSession(); // Reload the session after closing the modal
  };

  return (
    <>
      <Box
        sx={{
          padding: '20px',
          backgroundColor: 'transparent',
          borderRadius: '5px',
          order: { xs: 1, md: 'unset' },
          marginBottom: { xs: 2, md: 0 },
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
        <ContextUserCard
          sessionData={sessionData}
          onImpersonateClick={handleOpenModal}
          onStopImpersonation={handleStopImpersonation}
        />
      </Box>

      <ImpersonationModal 
        open={isModalOpen} 
        onClose={handleCloseModal} 
      />
    </>
  );
};

export default LeftPanel;
