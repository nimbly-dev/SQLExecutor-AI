import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import { SettingDetail } from 'types/settings/tenantSettingType';
import { updateSettingDetail } from 'services/tenantSetting';

interface TenantSettingsDetailFormFieldProps {
  open: boolean;
  onClose: () => void;
  onSave: () => void;
  settingKey: string;
  categoryKey: string;
  settingDetail: SettingDetail;
}

export function TenantSettingsDetailFormField({
  open,
  onClose,
  onSave,
  settingKey,
  categoryKey,
  settingDetail,
}: TenantSettingsDetailFormFieldProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<SettingDetail>(settingDetail);

  const handleChange = (field: keyof SettingDetail) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    try {
      await updateSettingDetail(categoryKey, settingKey, formData);
      onSave();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update setting');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Edit Setting: {settingKey}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          {error && <Alert severity="error">{error}</Alert>}
          
          <TextField
            label="Basic Name"
            value={formData.setting_basic_name}
            fullWidth
            disabled
          />

          <TextField
            label="Description"
            value={formData.setting_description}
            onChange={handleChange('setting_description')}
            fullWidth
            multiline
            rows={3}
          />

          <TextField
            label="Default Value"
            value={formData.setting_default_value}
            fullWidth
            disabled
          />

          <TextField
            label="Value"
            value={formData.setting_value}
            onChange={handleChange('setting_value')}
            fullWidth
          />

          <TextField
            label="Custom Setting"
            value={formData.is_custom_setting ? 'Yes' : 'No'}
            fullWidth
            disabled
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
}
