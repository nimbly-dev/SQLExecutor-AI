import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, useMediaQuery, useTheme, CircularProgress, Alert, Snackbar } from '@mui/material';
import { getSchemaByName, updateSchemaByName } from 'services/schemaService';
import { updateByPath } from 'utils/forms/formUtils';
import {
  Schema,
  Table,
} from 'types/schema/schemaType';
import SchemaDescription from 'components/schema-manager/schema-view/schema-info/schema-description/SchemaDescription';
import SchemaTables from 'components/schema-manager/schema-view/schema-info/tables/SchemaTables';
import SchemaContextSettings from 'components/schema-manager/schema-view/schema-info/context-setting/SchemaContextSettings';
import SchemaOthers from 'components/schema-manager/schema-view/schema-info/others/SchemaOthers';
import SchemaHealthcheckView from 'components/schema-manager/schema-view/healthcheck/SchemaHealthcheckView';
import DoubleTabsLayout, { UpperTab, LeftTab } from 'components/common/tabs/DoubleTabsLayout';
import { FormUpdateProvider } from 'contexts/form/FormUpdateProvider';
import ErrorAlertModal from 'components/common/modal/ErrorAlertModal';

function SchemaView() {
  const { schema_name } = useParams<{ schema_name: string }>();
  const navigate = useNavigate();
  const [schema, setSchema] = useState<Schema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string>("");
  const [activeUpperTab, setActiveUpperTab] = useState(0);
  const [activeLeftTab, setActiveLeftTab] = useState(0);
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down('sm'));
  const [isSaving, setIsSaving] = useState(false);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [updateError, setUpdateError] = useState<unknown>(null);

  useEffect(() => {
    const fetchSchema = async () => {
      if (!schema_name) {
        navigate('/schema-manager');
        return;
      }

      try {
        setLoading(true);
        const fetchedSchema = await getSchemaByName(schema_name);
        if (!fetchedSchema) {
          throw new Error('Schema not found');
        }
        setSchema(fetchedSchema);
        setError(null);
      } catch (err) {
        console.error('Error fetching schema:', err);
        setError(err instanceof Error ? err.message : 'Failed to load schema');
        setSchema(null);
      } finally {
        setLoading(false);
      }
    };

    fetchSchema();
  }, [schema_name, navigate]);

  const genericUpdateField = useCallback((path: string, value: any) => {
    setSchema(prev => {
      if (!prev) return prev;
      return updateByPath<Schema>(prev, path, value, {
        strict: false,
        createMissing: true,
      });
    });
  }, []);

  const upperTabs: UpperTab[] = [
    { label: 'Schema Info' },
    { label: 'Healthcheck' },
  ];

  const leftTabsForSchemaInfo: LeftTab[] = [
    { label: 'Schema Info' },
    { label: 'Tables' },
    { label: 'Context Setting' },
    { label: 'Others' },
  ];

  const sampleTable: Table = {
    description: 'A sample table for testing',
    synonyms: [],
    columns: {},
    relationships: {},
    exclude_description_on_generate_sql: false
  };

  const tablesData: Record<string, Table> = (() => {
    if (!schema || !schema.tables) {
      return { sample_table: sampleTable };
    }
    return Object.keys(schema.tables).length > 0 
      ? schema.tables 
      : { sample_table: sampleTable };
  })();

  const schemaInfoContent = schema
    ? [
        <SchemaDescription key="desc" schema={schema} />,
        <SchemaTables key="tables" tables={tablesData} />,
        <SchemaContextSettings
          key="context"
          schema={schema}
        />,
        <SchemaOthers 
          key="others" 
          schema={schema}
        />,
      ]
    : [];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !schema) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/schema-manager')}>
              Return to Schema List
            </Button>
          }
        >
          {error || 'Schema not found'}
        </Alert>
      </Box>
    );
  }

  return (
    <FormUpdateProvider updateField={genericUpdateField}>
      <DoubleTabsLayout
        upperTabs={upperTabs}
        activeUpperTab={activeUpperTab}
        onUpperTabChange={setActiveUpperTab}
        leftTabs={activeUpperTab === 0 ? leftTabsForSchemaInfo : []}
        activeLeftTab={activeLeftTab}
        onLeftTabChange={setActiveLeftTab}
        upperContent={[
          // Empty content for Schema Info tab since it's handled by leftContent
          null,
          // Healthcheck content
          <SchemaHealthcheckView key="healthcheck" />,
        ]}
        leftContent={activeUpperTab === 0 ? schemaInfoContent : []}
      />
      <Box sx={{ display: 'flex', justifyContent: 'right', gap: 2, mt: 2, mr: 2 }}>
        <Button 
          variant="contained" 
          size="small" 
          color="success"
          disabled={isSaving} 
          onClick={async () => {
            if (!schema || !schema_name) return;
            
            setIsSaving(true);
            try {
              const updatedSchema = await updateSchemaByName(schema_name, schema);
              // Update local state with the returned schema
              setSchema(updatedSchema);
              setSaveMessage("Changes saved successfully");
            } catch (err) {
              setUpdateError(err);
              setErrorModalOpen(true);
            } finally {
              setIsSaving(false);
            }
          }}
        >
          {isSaving ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
        </Button>
        <Button 
          variant="outlined" 
          size="small" 
          color="error" 
          disabled={isSaving}
          onClick={() => {
            window.location.reload();
          }}
        >
          Cancel
        </Button>
      </Box>
      <Snackbar
        open={!!saveMessage}
        autoHideDuration={6000}
        onClose={() => setSaveMessage("")}
        message={saveMessage}
      />
      <ErrorAlertModal
        open={errorModalOpen}
        onClose={() => setErrorModalOpen(false)}
        title="Failed to Save Schema"
        error={updateError}
      />
    </FormUpdateProvider>
  );
}

export default SchemaView;
