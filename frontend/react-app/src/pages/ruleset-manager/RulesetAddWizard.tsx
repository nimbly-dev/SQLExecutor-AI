import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { WizardTabForm } from 'components/common/forms/WizardTabForm';
import { RulesetInfo } from 'components/ruleset-manager/ruleset-view/ruleset-info/RulesetInfo';
import { RulesetInterpolatedConditions } from 'components/ruleset-manager/ruleset-view/conditions/RulesetInterpolatedConditions';
import { RulesetGlobalAccessPolicy } from 'components/ruleset-manager/ruleset-view/global_access_policy/RulesetGlobalAccessPolicy';
import { RulesetGroupAccessPolicy } from 'components/ruleset-manager/ruleset-view/group_access_policy/RulesetGroupAccessPolicy';
import { RulesetUserSpecificAccessPolicy } from 'components/ruleset-manager/ruleset-view/user_specific_access_policy/RulesetUserSpecificAccessPolicy';
import { RulesetInjectors } from 'components/ruleset-manager/ruleset-view/injectors/RulesetInjectors';
import { FormUpdateProvider } from 'contexts/form/FormUpdateProvider';
import { GlobalAccessPolicy, Ruleset } from 'types/ruleset/rulesetType';
import { addRuleset } from 'services/rulesetService';
import { getSchemaTables } from 'services/schemaService';
import { SimpleTablesResponse } from 'types/schema/schemaType';
import ErrorAlertModal from 'components/common/modal/ErrorAlertModal';


const initialRuleset: Ruleset = {
  tenant_id: '',
  ruleset_name: '',
  connected_schema_name: '',
  description: '',
  is_ruleset_enabled: true,
  conditions: {}, // Initialize as empty object
  global_access_policy: {
    tables: {}
  },
  // Add default empty values for optional policies
  group_access_policy: {},
  user_specific_access_policy: [],
  injectors: {}
};

export const RulesetAddWizard: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<Ruleset>(initialRuleset);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [availableTables, setAvailableTables] = useState<SimpleTablesResponse>([]);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    const fetchTables = async () => {
      if (formData.connected_schema_name) {
        try {
          const tablesResponse = await getSchemaTables(formData.connected_schema_name);
          setAvailableTables(tablesResponse);
        } catch (error) {
          console.error('Error fetching schema tables:', error);
        }
      }
    };

    fetchTables();
  }, [formData.connected_schema_name]);

  const genericUpdateField = (path: string, value: any) => {
    setFormData(prev => {
      // Create a deep copy of the previous state
      const newData = JSON.parse(JSON.stringify(prev)) as Ruleset;
      
      const pathParts = path.split('.');
      let current = newData as any;

      // Handle arrays and nested objects properly
      for (let i = 0; i < pathParts.length - 1; i++) {
        const part = pathParts[i];
        // If the next part doesn't exist or is null, initialize it
        if (!current[part]) {
          // Check if the next path part is a number (array index)
          const nextPart = pathParts[i + 1];
          current[part] = isNaN(Number(nextPart)) ? {} : [];
        }
        current = current[part];
      }

      // Set the final value
      const lastPart = pathParts[pathParts.length - 1];
      current[lastPart] = value;

      // For conditions specifically, ensure it's always an object
      if (path === 'conditions' && !value) {
        newData.conditions = {};
      }

      return newData;
    });
  };

  const handleSave = async () => {
    try {
      setIsSubmitting(true);
      
      // Create the base request with required fields only
      const rulesetRequest = {
        ruleset_name: formData.ruleset_name,
        connected_schema_name: formData.connected_schema_name,
        description: formData.description,
        is_ruleset_enabled: formData.is_ruleset_enabled,
        conditions: formData.conditions,
        global_access_policy: formData.global_access_policy,
        group_access_policy: formData.group_access_policy || {},
        user_specific_access_policy: formData.user_specific_access_policy || [],
        injectors: formData.injectors || {}
      };
      
      console.log('Sending request:', JSON.stringify(rulesetRequest, null, 2));
      await addRuleset(rulesetRequest);
      navigate('/ruleset-manager');
    } catch (err) {
      console.error('Failed to create ruleset:', err);
      setError(err);
      setErrorModalOpen(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate('/ruleset-manager');
  };

  const tabs = [
    {
      label: 'Ruleset Info',
      component: <RulesetInfo ruleset={formData} />,
      validationRules: [
        { 
          path: 'ruleset_name',
          required: true
        },
        {
          path: 'connected_schema_name',
          required: true
        },
        {
          path: 'description',
          required: true
        }
      ]
    },
    {
      label: 'Conditions',
      component: <RulesetInterpolatedConditions ruleset={formData} />,
      validationRules: [
        {
          path: 'conditions',
          required: true,
          validateFn: (value: Record<string, string> | undefined) => 
            Object.keys(value || {}).length > 0
        }
      ]
    },
    {
      label: 'Global Access Policy',
      component: <RulesetGlobalAccessPolicy 
        ruleset={formData}
        availableTables={availableTables}
      />,
      validationRules: [
        {
          path: 'global_access_policy',
          required: true,
          validateFn: (value: GlobalAccessPolicy | undefined) => 
            Object.keys(value?.tables || {}).length > 0
        }
      ]
    },
    {
      label: 'Group Access Policy',
      component: <RulesetGroupAccessPolicy 
        ruleset={formData}
        availableTables={availableTables}
      />,
    },
    {
      label: 'User Specific Access Policy',
      component: <RulesetUserSpecificAccessPolicy 
        ruleset={formData}
        tables={availableTables}
      />,
    },
    {
      label: 'Injectors',
      component: <RulesetInjectors 
        ruleset={formData}
        availableTables={availableTables}
      />,
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <FormUpdateProvider updateField={genericUpdateField}>
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
        title="Failed to Create Ruleset"
        error={error}
      />
    </Box>
  );
};

export default RulesetAddWizard;
