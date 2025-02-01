import { useState } from 'react';

/**
 * Custom hook for managing pagination in the impersonation view.
 *
 * @param selectedSchema The currently selected schema.
 * @param fetchUsers Function to fetch users based on pagination.
 * @param setIsLoading Function to control the loading state.
 * @returns The current page, rowsPerPage and their change handlers.
 */
interface UseImpersonationPaginationReturn {
    page: number;
    rowsPerPage: number;
    handleChangePage: (event: unknown, newPage: number) => Promise<void>;
    handleChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const useImpersonationPagination = (
    selectedSchema: { schema_name: string } | null,
    fetchUsers: (currentPage: number, limit: number, schema: string) => Promise<void>,
    setIsLoading: (flag: boolean) => void
): UseImpersonationPaginationReturn => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const handleChangePage = async (_event: unknown, newPage: number) => {
        setPage(newPage);
        if (selectedSchema) {
            setIsLoading(true);
            try {
                await fetchUsers(newPage, rowsPerPage, selectedSchema.schema_name);
            } catch (error) {
                console.error('Error fetching users on page change:', error);
            } finally {
                setIsLoading(false);
            }
        }
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newRowsPerPage = parseInt(event.target.value, 10);
        if (!selectedSchema) return;
        setIsLoading(true);
        setPage(0);
        setRowsPerPage(newRowsPerPage);
        setTimeout(async () => {
            try {
                await fetchUsers(0, newRowsPerPage, selectedSchema.schema_name);
            } catch (error) {
                console.error('Error fetching users:', error);
            } finally {
                setIsLoading(false);
            }
        }, 500);
    };

    return { page, rowsPerPage, handleChangePage, handleChangeRowsPerPage };
};

export default useImpersonationPagination;
