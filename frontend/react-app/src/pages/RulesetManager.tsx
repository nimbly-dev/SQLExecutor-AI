import React, { useState, useEffect } from 'react';
import { 
  Typography, Button, TextField, useTheme, useMediaQuery, 
  IconButton, Dialog, CircularProgress, MenuItem, Select,
  DialogTitle, DialogContent, DialogActions,
  DialogContentText, Alert, Snackbar, FormControl,
  Chip, Stack
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { useNavigate } from 'react-router-dom';
import { RulesetSummary } from 'types/ruleset/rulesetType';
import { RulesetListView } from 'components/ruleset-manager/ruleset-list/RulesetListView';
import { getRulesetsPaginated, deleteRuleset } from 'services/rulesetService';
import { FilterMenu, FilterState } from 'components/ruleset-manager/ruleset-list/FilterMenu';
import styles from 'styles/schema-manager/SchemaManager.module.scss';

function RulesetManager() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [rulesets, setRulesets] = useState<RulesetSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedRuleset, setSelectedRuleset] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterState>({});
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    fetchRulesets();
  }, [page, pageSize, searchQuery, filters]);

  const fetchRulesets = async () => {
    try {
      setLoading(true);
      const data = await getRulesetsPaginated({
        page: page + 1,
        pageSize,
        name: searchQuery || undefined,
        isRulesetEnabled: filters.enabled ? true : filters.disabled ? false : undefined,
        hasInjectors: filters.hasInjectors ? true : filters.noInjectors ? false : undefined,
      });
      setRulesets(data.rulesets);
      setTotal(data.total);
    } catch (err) {
      if (err instanceof Error && (err as any).response?.status !== 404) {
        setError('Failed to fetch rulesets');
        console.error('Error fetching rulesets:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setSearchQuery(searchTerm);
    setPage(0);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleDelete = (rulesetName: string) => {
    setSelectedRuleset(rulesetName);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedRuleset) return;
    
    setIsDeleting(true);
    try {
      await deleteRuleset(selectedRuleset);
      setRulesets(rulesets.filter(ruleset => ruleset.ruleset_name !== selectedRuleset));
      setDeleteDialogOpen(false);
    } catch (err) {
      setError('Failed to delete ruleset');
      console.error('Error deleting ruleset:', err);
    } finally {
      setIsDeleting(false);
      setSelectedRuleset(null);
    }
  };

  const handleView = (ruleset: RulesetSummary) => {
    navigate(`/ruleset-manager/view/${ruleset.ruleset_name}`);
  };

  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handleFilterDelete = (filterKey: keyof FilterState) => {
    const newFilters = { ...filters };
    delete newFilters[filterKey];
    setFilters(newFilters);
  };

  const handleAddRuleset = () => {
    navigate('/ruleset-manager/add');
  };

  const renderActiveFilters = () => {
    const activeFilters = Object.entries(filters).filter(([_, value]) => value);
    if (activeFilters.length === 0) return null;

    return (
      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        {activeFilters.map(([key]) => (
          <Chip
            key={key}
            label={key.replace(/([A-Z])/g, ' $1').toLowerCase()}
            onDelete={() => handleFilterDelete(key as keyof FilterState)}
            color="primary"
            variant="outlined"
          />
        ))}
      </Stack>
    );
  };

  const renderTopBar = (
    <div className={styles.topBar}>
      <div className={styles.searchContainer}>
        <TextField 
          className={styles.searchField}
          fullWidth
          variant="outlined" 
          placeholder="Search rulesets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
          InputProps={{
            endAdornment: (
              <IconButton onClick={handleSearch}>
                <SearchIcon />
              </IconButton>
            )
          }}
        />
        <FilterMenu
          filters={filters}
          onChange={handleFilterChange}
        />
      </div>
      <Button 
        variant="contained" 
        color="primary"
        startIcon={<AddIcon />}
        onClick={handleAddRuleset}
      >
        Add Ruleset
      </Button>
    </div>
  );

  return (
    <div className={styles.container}>
      <Typography 
        variant={isMobile ? 'h4' : 'h2'} 
        fontWeight="bold" 
        gutterBottom
      >
        Ruleset Manager {!loading && total > 0 && `(${total})`}
      </Typography>

      {renderTopBar}
      {renderActiveFilters()}

      <div className={styles.tableSection}>
        <RulesetListView
          rulesets={rulesets}
          total={total}
          page={page}
          pageSize={pageSize}
          loading={loading}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          onDelete={handleDelete}
          onView={handleView}
        />
      </div>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => !isDeleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete ruleset "{selectedRuleset}"? 
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setDeleteDialogOpen(false)} 
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDelete}
            color="error"
            disabled={isDeleting}
            startIcon={isDeleting ? <CircularProgress size={20} /> : null}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </div>
  );
}

export default RulesetManager;
