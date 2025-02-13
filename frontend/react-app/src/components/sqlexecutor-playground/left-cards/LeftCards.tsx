import React from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import ContextUserCard from 'components/sqlexecutor-playground/left-cards/ContextUserCard';
import ImpersonationModal from 'components/sqlexecutor-playground/left-cards/ImpersonationModal';
import { useSQLExecutorContext } from 'pages/SQLExecutorPlayground';

const LeftPanel: React.FC = () => {
  const theme = useTheme();
  const { 
    stopImpersonation, 
    isModalOpen, 
    setIsModalOpen, 
    loadContextSession,
    selectedSchema 
  } = useSQLExecutorContext();


  const handleCloseModal = () => {
    setIsModalOpen(false);
    loadContextSession(); 
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
        <ContextUserCard />
      </Box>

      <ImpersonationModal 
        open={isModalOpen}
        onClose={handleCloseModal} 
        selectedSchema={selectedSchema}  
      />
    </>
  );
};

export default LeftPanel;
