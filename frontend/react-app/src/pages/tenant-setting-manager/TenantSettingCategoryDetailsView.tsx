import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Button, TextField, Typography, useTheme, useMediaQuery,
  Stack, Paper
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { DataTable } from 'components/common/tables/DataTable';
import { getSettingDetailsByCategory } from 'services/tenantSetting';
import { Column } from 'types/common/tableTypes';
import { TenantSettingCategoryDetails } from 'types/settings/tenantSettingType';
import styles from 'styles/tenant-setting-manager/TenantSettingsManager.module.scss';
import { TenantSettingsDetailFormField } from 'components/tenant-settings-manager/TenantSettingsDetailFormField';

interface SettingRow {
  key: string;
  basicName: string;
  description: string;
  defaultValue: string;
  value: string;
  isCustomSetting: boolean;
}

function TenantSettingCategoryDetailsView() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { categoryKey } = useParams<{ categoryKey: string }>();
  
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState<SettingRow[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedSetting, setSelectedSetting] = useState<SettingRow | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const columns: Column<SettingRow>[] = [
    {
      id: 'key',
      label: 'Setting Key',
      render: (item: SettingRow) => item.key,
    },
    {
      id: 'basicName',
      label: 'Name',
      render: (item: SettingRow) => item.basicName,
    },
    {
      id: 'description',
      label: 'Description',
      render: (item: SettingRow) => item.description,
    },
    {
      id: 'value',
      label: 'Value',
      render: (item: SettingRow) => item.value || item.defaultValue,
    },
  ];

  useEffect(() => {
    if (categoryKey) {
      fetchSettings();
    }
  }, [categoryKey, searchQuery, page, pageSize]);

  const fetchSettings = async () => {
    if (!categoryKey) return;

    setLoading(true);
    try {
      const response = await getSettingDetailsByCategory(categoryKey);
      // The response is a single object, not an array, so we don't need to access [0]
      const settingRows = Object.entries(response.settings).map(([key, details]) => ({
        key,
        basicName: details.setting_basic_name,
        description: details.setting_description,
        defaultValue: details.setting_default_value,
        value: details.setting_value,
        isCustomSetting: details.is_custom_setting,
      }));

      const filteredSettings = settingRows.filter(setting => 
        setting.key.toUpperCase().includes(searchQuery.toUpperCase()) ||
        setting.basicName.toUpperCase().includes(searchQuery.toUpperCase())
      );

      setTotal(filteredSettings.length);
      
      // Handle pagination
      const startIndex = page * pageSize;
      const endIndex = startIndex + pageSize;
      setSettings(filteredSettings.slice(startIndex, endIndex));
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      setError('Failed to fetch category settings');
      setSettings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const handleView = (setting: SettingRow) => {
    setSelectedSetting(setting);
    setIsDetailModalOpen(true);
  };

  const handleDetailModalClose = () => {
    setIsDetailModalOpen(false);
    setSelectedSetting(null);
  };

  const handleSettingSaved = () => {
    fetchSettings(); // Refresh the settings list
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleBack = () => {
    navigate('/tenant-settings-manager');
  };

  const renderActions = (setting: SettingRow) => (
    <Button
      startIcon={<VisibilityIcon />}
      variant="outlined"
      size="small"
      onClick={() => handleView(setting)}
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
      <Paper
        elevation={0}
        sx={{
          p: 2,
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          variant="outlined"
          size="small"
        >
          Back
        </Button>
        <Typography 
          variant="h6"
          fontWeight="medium"
          sx={{ color: theme.palette.text.primary }}
        >
          {categoryKey} Settings
        </Typography>
      </Paper>

      <Paper 
        elevation={0}
        sx={{ 
          p: 1.5,
          border: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.paper
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search settings..."
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
          items={settings}
          columns={columns}
          loading={loading}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          rowActions={renderActions}
          noDataMessage="No settings found"
        />
      </Paper>

      {selectedSetting && (
        <TenantSettingsDetailFormField
          open={isDetailModalOpen}
          onClose={handleDetailModalClose}
          onSave={handleSettingSaved}
          settingKey={selectedSetting.key}
          categoryKey={categoryKey || ''}
          settingDetail={{
            setting_description: selectedSetting.description,
            setting_basic_name: selectedSetting.basicName,
            setting_default_value: selectedSetting.defaultValue,
            setting_value: selectedSetting.value,
            is_custom_setting: selectedSetting.isCustomSetting,
          }}
        />
      )}
    </Stack>
  );
}

export default TenantSettingCategoryDetailsView;
