import { ReactNode } from 'react';

export interface Column<T> {
  id: string;
  label: string;
  render?: (item: T) => ReactNode;
  align?: 'left' | 'right' | 'center';
  width?: string | number;
}

export interface TableProps<T> {
  items: T[];
  columns: Column<T>[];
  total: number;
  page: number;
  pageSize: number;
  loading?: boolean;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (event: React.ChangeEvent<HTMLInputElement>) => void;  // Update this line
  onRowClick?: (item: T) => void;
  rowActions?: (item: T) => ReactNode;
  noDataMessage?: string;
  filterComponent?: ReactNode;
  className?: string;
  rowsPerPageOptions?: number[];
}

export interface PaginationConfig {
  pageSizeOptions?: number[];
  defaultPageSize?: number;
}
