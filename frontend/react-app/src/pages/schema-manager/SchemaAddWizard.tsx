import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography } from '@mui/material';
import ErrorAlertModal from 'components/common/modal/ErrorAlertModal';
import { WizardTabForm } from 'components/common/forms/WizardTabForm';
import { SchemaDescription } from 'components/schema-manager/schema-view/schema-info/schema-description/SchemaDescription';
import { SchemaContextSettings } from 'components/schema-manager/schema-view/schema-info/context-setting/SchemaContextSettings';
import SchemaTablesView from 'components/schema-manager/schema-view/schema-info/tables/SchemaTables';
import { SchemaOthers } from 'components/schema-manager/schema-view/schema-info/others/SchemaOthers';
import { Schema, ContextSetting, SchemaChatInterfaceIntegrationSetting, Table, Column } from 'types/schema/schemaType';
import { FormUpdateProvider } from 'contexts/form/FormUpdateProvider';
import { addSchema } from 'services/schemaService';

const defaultSchema: Schema = {
  tenant_id: '',
  schema_name: '',
  description: '',
  exclude_description_on_generate_sql: false,
  tables: {},
  filter_rules: [],
  synonyms: [],
  context_type: '',
  context_setting: {
    sql_context: undefined,
    api_context: undefined
  } as ContextSetting,
  schema_chat_interface_integration: {
    enabled: false,
    get_contexts_query: '',
    get_contexts_count_query: ''
  } as SchemaChatInterfaceIntegrationSetting
};

function SchemaAddWizard() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<Schema>(defaultSchema);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [updateError, setUpdateError] = useState<unknown>(null);

  const handleUpdateField = (path: string, value: any) => {
    setFormData((prev) => {
      const newData = { ...prev };
      
      // Handle special nested cases
      switch (path) {
        case 'tables': {
          const tablesRecord = value as Record<string, Table>;
          newData.tables = Object.fromEntries(
            Object.entries(tablesRecord).map(([key, table]: [string, Table]) => [
              key,
              {
                ...table,
                columns: typeof table.columns === 'object' && !Array.isArray(table.columns)
                  ? { ...table.columns }
                  : {}
              }
            ])
          );
          break;
        }
        case 'context_setting':
          newData.context_setting = { ...value } as ContextSetting;
          break;
        case 'schema_chat_interface_integration':
          newData.schema_chat_interface_integration = { 
            ...value 
          } as SchemaChatInterfaceIntegrationSetting;
          break;
        default: {
          const parts = path.split('.');
          if (parts.length > 1) {
            let current: Record<string, any> = newData as Record<string, any>;
            const lastPart = parts[parts.length - 1];
            
            for (let i = 0; i < parts.length - 1; i++) {
              const part = parts[i];
              const nextPart = parts[i + 1];
              const isNextPartArrayIndex = !isNaN(Number(nextPart));
              
              if (!(part in current)) {
                current[part] = isNextPartArrayIndex ? [] : {};
              } else {
                current[part] = isNextPartArrayIndex 
                  ? Array.from(current[part] as any[])
                  : { ...current[part] };
              }
              
              current = current[part] as Record<string, any>;
            }
            
            current[lastPart] = value;
          } else {
            const key = path as keyof Schema;
            if (key in newData) {
              (newData as any)[key] = value;
            }
          }
        }
      }
      
      return newData;
    });
  };

  const validateTable = (table: Table): boolean => {
    if (!table.columns || Object.keys(table.columns).length === 0) return false;
    
    const columns = Object.values(table.columns as Record<string, Column>);
    
    return columns.every((column: Column) => 
      column.type && 
      Array.isArray(column.constraints) && 
      column.constraints.length > 0
    );
  };

  const validateTables = (tables: Record<string, Table>): boolean => {
    if (typeof tables !== 'object' || tables === null) return false;
    const tableArray = Object.values(tables);
    return tableArray.length > 0 && tableArray.every(validateTable);
  };

  const tabs = [
    { 
      label: 'Description', 
      component: <SchemaDescription schema={formData} />,
      validationRules: [
        { path: 'schema_name', required: true },
        { path: 'description', required: true }
      ]
    },
    { 
      label: 'Context',     
      component: <SchemaContextSettings schema={formData} />,
      validationRules: [
        { path: 'context_type', required: true },
        { 
          path: 'context_setting',
          validateFn: (value: ContextSetting | undefined): boolean => {
            if (!formData.context_type) return false;
            
            if (formData.context_type === 'sql') {
              return !!(
                value?.sql_context?.table &&
                value?.sql_context?.user_identifier
              );
            }
            
            if (formData.context_type === 'api') {
              return !!(
                value?.api_context?.get_user_endpoint &&
                value?.api_context?.user_identifier &&
                value?.api_context?.auth_method
              );
            }

            return false;
          }
        }
      ]
    },
    { 
      label: 'Tables',      
      component: <SchemaTablesView tables={formData.tables} />,
      validationRules: [
        { 
          path: 'tables',
          validateFn: validateTables
        }
      ]
    },
    { 
      label: 'Others',      
      component: <SchemaOthers schema={formData} /> 
    }
  ];

  const handleSave = async () => {
    try {
      setIsSubmitting(true);
      setUpdateError(null);
      
      // Set tenant_id from cookie or context if needed
      const schemaToSubmit = {
        ...formData,
        tenant_id: formData.tenant_id || localStorage.getItem('tenant_id') || '',
      };

      await addSchema(schemaToSubmit);
      navigate('/schema-manager');
    } catch (err) {
      setUpdateError(err);
      setErrorModalOpen(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    console.log('Wizard cancelled');
    navigate('/schema-manager');
  };

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        Add New Schema
      </Typography>
      <FormUpdateProvider updateField={handleUpdateField}>
        <WizardTabForm 
          tabs={tabs} 
          onSave={handleSave} 
          onCancel={handleCancel}
          formData={formData}
          isSubmitting={isSubmitting}
        />
      </FormUpdateProvider>
      
      <ErrorAlertModal
        open={errorModalOpen}
        onClose={() => setErrorModalOpen(false)}
        title="Failed to Add Schema"
        error={updateError}
      />
    </Box>
  );
}

export default SchemaAddWizard;
