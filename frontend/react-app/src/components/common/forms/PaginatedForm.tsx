import React, { useState, useMemo, useEffect } from 'react';
import { Box, TextField, Pagination } from '@mui/material';
import styles from 'styles/common/forms/PaginatedForm.module.scss';

interface PaginatedFormProps<T> {
  items: T[];
  searchPlaceholder?: string;
  paginationLabel?: string;
  pageSizeOptions?: number[];
  filterFunc: (item: T, searchTerm: string) => boolean;
  renderItem: (item: T, index: number) => React.ReactNode;
  renderHeader?: (searchTerm: string, setSearchTerm: (term: string) => void) => React.ReactNode;
}

function PaginatedForm<T>({
  items = [], 
  searchPlaceholder = 'Search...',
  paginationLabel = 'Items per page',
  pageSizeOptions = [5, 10, 15, 20],
  filterFunc,
  renderItem,
  renderHeader,
}: PaginatedFormProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(pageSizeOptions[0]);

  const safeItems = Array.isArray(items) ? items : [];

  const filteredItems = useMemo(() => {
    return safeItems.filter(item => filterFunc(item, searchTerm));
  }, [safeItems, searchTerm, filterFunc]);

  useEffect(() => {
    const totalPages = Math.ceil(filteredItems.length / pageSize) || 1;
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [filteredItems, page, pageSize]);

  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredItems.slice(start, start + pageSize);
  }, [filteredItems, page, pageSize]);

  return (
    <Box className={styles.container}>
      {renderHeader ? (
        renderHeader(searchTerm, setSearchTerm)
      ) : (
        <TextField
          fullWidth
          size="small"
          placeholder={searchPlaceholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 2 }}
        />
      )}
      
      {paginatedItems.map((item, index) => (
        <Box 
          key={`item-${page}-${index}-${items.length}`} 
          className={styles.contentItem}
        >
          {renderItem(item, index)}
        </Box>
      ))}

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
        <Pagination
          count={Math.ceil(filteredItems.length / pageSize)}
          page={page}
          onChange={(_, newPage) => setPage(newPage)}
        />
      </Box>
    </Box>
  );
}

export default PaginatedForm;
