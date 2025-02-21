import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Button, TextField, Typography, useTheme, useMediaQuery,
  Stack, Paper
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { DataTable } from 'components/common/tables/DataTable';
import { getSettingCategoryKeys } from 'services/tenantSetting';
import { Column } from 'types/common/tableTypes';
import styles from 'styles/tenant-setting-manager/TenantSettingsManager.module.scss';

function TenantSettingsManager() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [categoryKeys, setCategoryKeys] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const columns: Column<string>[] = [
    {
      id: 'category',
      label: 'Category Key',
      render: (item: string) => item,
    },
  ];

  useEffect(() => {
    fetchCategoryKeys();
  }, [searchQuery, page, pageSize]);

  const fetchCategoryKeys = async () => {
    setLoading(true);
    try {
      const allKeys = await getSettingCategoryKeys();
      const filteredKeys = allKeys.filter(key => 
        key.includes(searchQuery.toUpperCase())
      );
      
      setTotal(filteredKeys.length);
      
      // Calculate pagination
      const startIndex = page * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedKeys = filteredKeys.slice(startIndex, endIndex);
      
      setCategoryKeys(paginatedKeys);
    } catch (error) {
      console.error('Failed to fetch category keys:', error);
      setError('Failed to fetch settings categories');
      setCategoryKeys([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value.toUpperCase().replace(/\s/g, '_');
    setSearchQuery(value);
    setPage(0);
  };

  const handleView = (categoryKey: string) => {
    navigate(`/tenant-settings-manager/${categoryKey}`);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setPage(0);
  };

  const renderActions = (categoryKey: string) => (
    <Button
      startIcon={<VisibilityIcon />}
      variant="outlined"
      size="small"
      onClick={() => handleView(categoryKey)}
      sx={{
        borderRadius: theme.shape.borderRadius,
        borderColor: theme.palette.primary.main,
        color: theme.palette.primary.main,
        '&:hover': {
          backgroundColor: theme.palette.primary.main + '1A',
          borderColor: theme.palette.primary.main,
        },
      }}
    >
      View
    </Button>
  );

  return (
    <Stack spacing={2} className={styles.container}>
      <Typography 
        variant={isMobile ? 'h4' : 'h2'} 
        fontWeight="bold"
        sx={{ color: theme.palette.text.primary }}
      >
        Tenant Settings Manager
      </Typography>

      <Paper 
        elevation={0}
        sx={{ 
          p: 1.5, // Reduced padding from 2 to 1.5
          border: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.paper
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search category..."
          value={searchQuery}
          onChange={handleSearchChange}
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: theme.palette.divider,
              },
              '&:hover fieldset': {
                borderColor: theme.palette.primary.main,
              },
            },
          }}
        />
      </Paper>

      <Paper 
        elevation={0}
        sx={{ 
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <DataTable
          items={categoryKeys}
          columns={columns}
          loading={loading}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          rowActions={renderActions}
          noDataMessage="No settings categories found"
        />
      </Paper>
    </Stack>
  );
}

export default TenantSettingsManager;
