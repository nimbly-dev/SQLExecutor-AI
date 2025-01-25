import React from 'react';
import {
  Box,
  Button,
  TablePagination,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

interface ModalFooterProps {
  totalCount: number;
  page: number;
  rowsPerPage: number;
  onPageChange: (event: unknown, newPage: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onClose: () => void;
}

const ModalFooter: React.FC<ModalFooterProps> = ({
  totalCount,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  onClose,
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ 
      mt: 2, 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      borderTop: `1px solid ${theme.palette.divider}`,
      pt: 2,
    }}>
      <TablePagination
        component="div"
        count={totalCount}
        page={page}
        onPageChange={onPageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={onRowsPerPageChange}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
      <Button
        variant="outlined"
        color="warning"  
        onClick={onClose}
      >
        Cancel
      </Button>
    </Box>
  );
};

export default ModalFooter;
