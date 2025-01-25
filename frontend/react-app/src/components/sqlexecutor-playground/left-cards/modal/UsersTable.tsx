import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Backdrop,
  CircularProgress,
  Fade,
} from '@mui/material';
import { ExternalContextUserRow } from '../../../../types/chat-interface/contextUsers';

interface UsersTableProps {
  users: ExternalContextUserRow[];
  identifierField: string;
  customFieldKeys: string[];
  isLoading: boolean;
  isTransitioning: boolean;
  onSelect: (user: ExternalContextUserRow) => void;
}

const UsersTable: React.FC<UsersTableProps> = ({
  users,
  identifierField,
  customFieldKeys,
  isLoading,
  isTransitioning,
  onSelect,
}) => {
  return (
    <TableContainer 
      component={Paper} 
      sx={{ 
        maxHeight: '50vh',
        overflow: 'auto',
        '& .MuiTableCell-root': { padding: '8px' },
        '& .MuiTableRow-root': {
          '&:last-child td': { borderBottom: 0 },
        },
        position: 'relative',
      }}
    >
      <Fade in={isTransitioning}>
        <Backdrop
          open={isTransitioning}
          sx={{
            position: 'absolute',
            zIndex: 1,
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress color="primary" />
        </Backdrop>
      </Fade>

      <Table>
        <TableHead>
          <TableRow>
            <TableCell>{identifierField}</TableCell>
            {customFieldKeys.map((key) => (
              <TableCell key={`header-field-${key}`}>{key}</TableCell>
            ))}
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={customFieldKeys.length + 2} align="center">
                Loading...
              </TableCell>
            </TableRow>
          ) : (
            users.map((user, index) => (
              <TableRow 
                hover 
                key={`user-row-${user.custom_fields[identifierField]}-${index}`}
              >
                <TableCell>{user.user_identifier}</TableCell>
                {customFieldKeys.map((fieldKey) => (
                  <TableCell key={`user-${user.custom_fields[identifierField]}-field-${fieldKey}`}>
                    {user.custom_fields[fieldKey]}
                  </TableCell>
                ))}
                <TableCell>
                  <Button
                    variant="contained"
                    color="info"
                    size="small"
                    onClick={() => onSelect(user)}
                  >
                    Select
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default UsersTable;
