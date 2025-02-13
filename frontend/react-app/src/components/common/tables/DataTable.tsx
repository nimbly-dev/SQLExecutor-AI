import {
  Table, TableHead, TableBody, TableRow, TableCell,
  TablePagination, CircularProgress, Typography,
  Paper
} from '@mui/material';
import { TableProps } from 'types/common/tableTypes';
import styles from 'styles/common/tables/DataTable.module.scss';

/**
 * Generic data table component with pagination and filtering support
 */
export function DataTable<T>({
  items,
  columns,
  total,
  page,
  pageSize,
  loading = false,
  onPageChange,
  onPageSizeChange,
  rowActions,
  noDataMessage = 'No data found',
  className = '',
  rowsPerPageOptions = [5, 10, 25, 50],
}: TableProps<T>) {
  // Remove filterComponent from props since it will be handled outside
  const handlePageChange = (_: any, newPage: number) => {
    onPageChange(newPage);
  };

  return (
    <Paper className={`${styles.tableContainer} ${className}`}>
      <div className={styles.tableWrapper}>
        {loading ? (
          <div className={styles.loadingContainer}>
            <CircularProgress />
          </div>
        ) : (
          <>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow className={styles.tableHeader}>
                  {columns.map((column) => (
                    <TableCell
                      key={column.id}
                      align={column.align}
                      style={{ width: column.width }}
                    >
                      {column.label}
                    </TableCell>
                  ))}
                  {rowActions && <TableCell align="right">Actions</TableCell>}
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item, index) => (
                  <TableRow key={index} className={styles.tableRow}>
                    {columns.map((column) => (
                      <TableCell
                        key={column.id}
                        align={column.align}
                      >
                        {column.render ? column.render(item) : (item as any)[column.id]}
                      </TableCell>
                    ))}
                    {rowActions && (
                      <TableCell align="right">
                        <div className={styles.actionButtons}>
                          {rowActions(item)}
                        </div>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
                {items.length === 0 && (
                  <TableRow>
                    <TableCell 
                      colSpan={columns.length + (rowActions ? 1 : 0)} 
                      align="center"
                    >
                      <Typography color="textSecondary">
                        {noDataMessage}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </>
        )}
      </div>
      {(
        <div className={styles.paginationWrapper}>
          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={handlePageChange}
            rowsPerPage={pageSize}
            onRowsPerPageChange={onPageSizeChange}
            rowsPerPageOptions={rowsPerPageOptions}
          />
        </div>
      )}
    </Paper>
  );
}
