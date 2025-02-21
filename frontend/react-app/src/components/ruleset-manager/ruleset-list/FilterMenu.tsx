import React from 'react';
import {
  Button,
  Menu,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Typography,
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';

export interface FilterState {
  enabled?: boolean;
  disabled?: boolean;
  hasInjectors?: boolean;
  noInjectors?: boolean;
}

interface FilterMenuProps {
  filters: FilterState;
  onChange: (newFilters: FilterState) => void;
}

export const FilterMenu: React.FC<FilterMenuProps> = ({ filters, onChange }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleFilterChange = (key: keyof FilterState) => {
    const newFilters = { ...filters };
    newFilters[key] = !filters[key];

    // Clear opposite filter when one is selected
    if (key === 'enabled') newFilters.disabled = false;
    if (key === 'disabled') newFilters.enabled = false;
    if (key === 'hasInjectors') newFilters.noInjectors = false;
    if (key === 'noInjectors') newFilters.hasInjectors = false;

    onChange(newFilters);
  };

  return (
    <>
      <Button
        startIcon={<FilterListIcon />}
        onClick={handleClick}
        variant="outlined"
        color="primary"
      >
        Filters
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem sx={{ pointerEvents: 'none' }}>
          <Typography variant="subtitle2" color="textSecondary">
            Ruleset Status
          </Typography>
        </MenuItem>
        <FormGroup sx={{ px: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.enabled}
                onChange={() => handleFilterChange('enabled')}
                disabled={filters.disabled}
              />
            }
            label="Enabled"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.disabled}
                onChange={() => handleFilterChange('disabled')}
                disabled={filters.enabled}
              />
            }
            label="Disabled"
          />
        </FormGroup>
        <Divider sx={{ my: 1 }} />
        <MenuItem sx={{ pointerEvents: 'none' }}>
          <Typography variant="subtitle2" color="textSecondary">
            Injectors
          </Typography>
        </MenuItem>
        <FormGroup sx={{ px: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.hasInjectors}
                onChange={() => handleFilterChange('hasInjectors')}
                disabled={filters.noInjectors}
              />
            }
            label="Has Injectors"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.noInjectors}
                onChange={() => handleFilterChange('noInjectors')}
                disabled={filters.hasInjectors}
              />
            }
            label="No Injectors"
          />
        </FormGroup>
      </Menu>
    </>
  );
};
