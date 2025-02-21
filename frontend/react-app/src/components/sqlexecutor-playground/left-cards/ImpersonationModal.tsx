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
import { useImpersonation } from 'hooks/sqlexecutor-playground/left-cards/useImpersonation';
import SearchSection from 'components/sqlexecutor-playground/left-cards/modal/SearchSection';
import UsersTable from 'components/sqlexecutor-playground/left-cards/modal/UsersTable';
import ModalFooter from 'components/sqlexecutor-playground/left-cards/modal/ModalFooter';
import useImpersonationPagination from 'hooks/sqlexecutor-playground/left-cards/useImpersonationPagination';
import { SchemaSummary } from 'types/schema/schemaType';

interface ImpersonationModalProps {
  open: boolean;
  onClose: () => void;
  selectedSchema: SchemaSummary | null; // updated type using SchemaSummary with user_identifier
}

const ImpersonationModal: React.FC<ImpersonationModalProps> = ({ open, onClose, selectedSchema }) => {
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
    setUsers,
  } = useImpersonation(onClose);

  useEffect(() => {
    if (open && selectedSchema) {
      fetchIdentifierField();
      fetchUsers(0, 10, selectedSchema.schema_name);
    }
  }, [open, selectedSchema, fetchUsers]);

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

  const {
    page,
    rowsPerPage,
    handleChangePage,
    handleChangeRowsPerPage,
  } = useImpersonationPagination(selectedSchema, fetchUsers, setIsLoading);

  const getCustomFieldKeys = () => {
    if (users.length === 0) return [];
    return Object.keys(users[0].custom_fields);
  };

  const customFieldKeys = getCustomFieldKeys();
  const allFields = identifierField ? [identifierField, ...customFieldKeys] : customFieldKeys;

  const handleSearch = () => {
    console.log('Searching for:', searchQuery, 'in field:', selectedField);
  };


  const handleUserSelectWrapper = (user: any) => {
    if (selectedSchema) {
      // Pass the entire schema object instead of just the name
      handleUserSelect(user, selectedSchema);
    }
  };

  return (
    <Modal 
      open={open} 
      onClose={onClose}
      sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
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
          {selectedSchema ? (
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
                  onSelect={handleUserSelectWrapper} 
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
          ) : (
            <Box sx={{ p: 3, backgroundColor: theme.palette.background.paper, borderRadius: 1 }}>
              <Typography variant="body1" color="error">
                A schema must be selected before impersonation is available.
              </Typography>
            </Box>
          )}
        </Box>
      </Fade>
    </Modal>
  );
};

export default ImpersonationModal;

