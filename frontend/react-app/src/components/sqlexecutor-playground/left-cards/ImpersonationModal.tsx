import React, { useState, useEffect } from 'react';
import {
  Modal,
  Box,
  Typography,
  Card,
  CardContent,
  Fade,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useImpersonation } from '../../../hooks/sqlexecutor-playground/left-cards/useImpersonation';
import { getUsersContext } from '../../../services/chatInterface'; // Add this import
import SearchSection from './modal/SearchSection';
import UsersTable from './modal/UsersTable';
import ModalFooter from './modal/ModalFooter';

interface ImpersonationModalProps {
  open: boolean;
  onClose: () => void;
}

const ImpersonationModal: React.FC<ImpersonationModalProps> = ({ open, onClose }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedField, setSelectedField] = useState('');
  const theme = useTheme();

  const {
    users,
    identifierField,
    isLoading,
    isTransitioning,
    totalCount,
    fetchUsers,
    handleUserSelect,
    fetchIdentifierField,
    setIsTransitioning,
    setIsLoading,
    setUsers
  } = useImpersonation(onClose);

  useEffect(() => {
    if (open) {
      fetchIdentifierField();
      fetchUsers(page, rowsPerPage);
    }
  }, [open, fetchUsers, page, rowsPerPage]);

  useEffect(() => {
    if (isLoading) {
      setIsTransitioning(true);
    } else {
      const timeoutId = setTimeout(() => {
        setIsTransitioning(false);
      }, 300);
      return () => clearTimeout(timeoutId);
    }
  }, [isLoading, setIsTransitioning]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setIsLoading(true);
    
    setPage(0);
    setRowsPerPage(newRowsPerPage);
    
    setTimeout(async () => {
      try {
        const response = await getUsersContext(1, 'ASC', newRowsPerPage);
        if (response && response.data) {  // Add null check
          setUsers(response.data);
        }
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        setIsLoading(false);
      }
    }, 500);
  };

  const getCustomFieldKeys = () => {
    if (users.length === 0) return [];
    return Object.keys(users[0].custom_fields);
  };

  const customFieldKeys = getCustomFieldKeys();

  const handleSearch = () => {
    console.log('Searching for:', searchQuery, 'in field:', selectedField);
  };

  const allFields = identifierField ? [identifierField, ...customFieldKeys] : customFieldKeys;

  return (
    <Modal 
      open={open} 
      onClose={onClose}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Fade in={open}>
        <Box sx={{ 
          width: '60%', 
          maxHeight: '80vh',
          backgroundColor: theme.palette.background.paper, 
          borderRadius: 1,
          boxShadow: 24,
          position: 'relative',
        }}>
          <Card>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Impersonate User
              </Typography>
              
              <SearchSection
                searchQuery={searchQuery}
                selectedField={selectedField}
                allFields={allFields}
                onSearchChange={setSearchQuery}
                onFieldChange={setSelectedField}
                onSearch={handleSearch}
              />

              <UsersTable
                users={users}
                identifierField={identifierField}
                customFieldKeys={customFieldKeys}
                isLoading={isLoading}
                isTransitioning={isTransitioning}
                onSelect={handleUserSelect}
              />

              <ModalFooter
                totalCount={totalCount}
                page={page}
                rowsPerPage={rowsPerPage}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                onClose={onClose}
              />
            </CardContent>
          </Card>
        </Box>
      </Fade>
    </Modal>
  );
};

export default ImpersonationModal;

