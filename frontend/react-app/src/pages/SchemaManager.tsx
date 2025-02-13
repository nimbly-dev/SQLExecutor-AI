import React, { useState, useEffect } from 'react';
import { 
  Typography, Button, TextField, useTheme, useMediaQuery, 
  IconButton, Dialog, CircularProgress, MenuItem, Select,
  DialogTitle, DialogContent, DialogActions,
  DialogContentText, Alert, Snackbar, FormControl
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import { SchemaSummary } from 'types/schema/schemaType';
import { MobileSchemaCard } from 'components/schema-manager/MobileSchemaCard';
import { getSchemasPaginated, deleteSchema } from 'services/schemaService';
import styles from 'styles/schema-manager/SchemaManager.module.scss';
import { SchemaListView } from 'components/schema-manager/schema-listview/SchemaListView';
import { useNavigate } from 'react-router-dom';

function SchemaManager() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [schemas, setSchemas] = useState<SchemaSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    fetchSchemas();
  }, [page, pageSize, searchQuery, filterType]); 

  const fetchSchemas = async () => {
    try {
      setLoading(true);
      const data = await getSchemasPaginated({
        page: page + 1,
        pageSize,
        name: searchQuery || undefined,
        contextType: filterType,
      });
      setSchemas(data.schemas);
      setTotal(data.total);
    } catch (err) {
      // Only show error for actual API failures
      if (err instanceof Error && (err as any).response?.status !== 404) {
        setError('Failed to fetch schemas');
        console.error('Error fetching schemas:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (schemaName: string) => {
    setSelectedSchema(schemaName);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedSchema) return;
    
    setIsDeleting(true);
    try {
      await deleteSchema(selectedSchema);
      setSchemas(schemas.filter(schema => schema.schema_name !== selectedSchema));
      setDeleteDialogOpen(false);
    } catch (err) {
      setError('Failed to delete schema');
      console.error('Error deleting schema:', err);
    } finally {
      setIsDeleting(false);
      setSelectedSchema(null);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setPage(0);
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

  const handleView = (schema: SchemaSummary) => {
    navigate(`/schema-manager/view/${schema.schema_name}`);
  };


  const renderTopBar = (
    <div className={styles.topBar}>
      <div className={styles.searchContainer}>
        <TextField 
          className={styles.searchField}
          fullWidth
          variant="outlined" 
          placeholder="Search schemas..."
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
        <FormControl className={styles.contextSelect}>
          <Select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as string)}
            displayEmpty
          >
            <MenuItem value="all">All Context Types</MenuItem>
            <MenuItem value="api">API</MenuItem>
            <MenuItem value="sql">SQL</MenuItem>
          </Select>
        </FormControl>
      </div>
      <div className={styles.buttonGroup}>
        <Button 
          variant="contained" 
          color="info"
          startIcon={<SearchIcon />}
        >
          Discover Schema
        </Button>
        <Button 
          variant="contained" 
          color="success"
          startIcon={<AddIcon />}
          onClick={() => navigate('/schema-manager/add')}
        >
          Add Schema
        </Button>
      </div>
    </div>
  );

  return (
    <div className={styles.container}>
      <Typography 
        variant={isMobile ? 'h4' : 'h2'} 
        fontWeight="bold" 
        gutterBottom
      >
        Schema Manager {!loading && total > 0 && `(${total})`}
      </Typography>

      {renderTopBar}

      {isMobile ? (
        <div className={styles.mobileContainer}>
          {schemas?.map((schema, index) => (
            <MobileSchemaCard 
              key={index}
              schema={schema}
              onDelete={() => handleDelete(schema.schema_name)}
              onView={() => handleView(schema)}
            />
          ))}
          {schemas?.length === 0 && (
            <Typography color="textSecondary" align="center">
              No schemas found
            </Typography>
          )}
        </div>
      ) : (
        <div className={styles.tableSection}>
          <SchemaListView
            schemas={schemas}
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
      )}

      <Dialog
        open={deleteDialogOpen}
        onClose={() => !isDeleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete schema "{selectedSchema}"? 
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

export default SchemaManager;
