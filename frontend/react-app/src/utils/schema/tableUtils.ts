import { SimpleColumnResponse } from 'types/schema/schemaType';

interface ColumnAccess {
  allow: string[];
  deny: string[];
}

/**
 * Separates columns into allow and deny lists based on sensitivity
 * @param columns - Array of column information
 * @returns Object with allow and deny arrays
 * - Sensitive columns (is_sensitive_column: true) go to deny list
 * - Non-sensitive columns (is_sensitive_column: false) go to allow list
 */
export const separateColumnsByAccess = (columns: SimpleColumnResponse[]): ColumnAccess => {
    return columns.reduce(
        (acc: ColumnAccess, column) => {
            if (column.is_sensitive_column === undefined || column.is_sensitive_column === false) {
                acc.allow.push(column.column_name);
            } else {
                acc.deny.push(column.column_name);
            }
            return acc;
        },
        { allow: [], deny: [] }
    );
};
