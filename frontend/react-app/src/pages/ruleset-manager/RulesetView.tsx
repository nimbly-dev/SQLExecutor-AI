import React, { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, useTheme, CircularProgress, Alert, Snackbar, Paper, Typography, Chip, Grid } from '@mui/material';
import { getRulesetByName, updateRuleset } from 'services/rulesetService';
import { updateByPath } from 'utils/forms/formUtils';
import { Ruleset } from 'types/ruleset/rulesetType';
import { FormUpdateProvider } from 'contexts/form/FormUpdateProvider';
import ErrorAlertModal from 'components/common/modal/ErrorAlertModal';
import { TabLayout, TabInfo } from 'components/common/tabs/TabLayout';
import RulesetInfo from 'components/ruleset-manager/ruleset-view/ruleset-info/RulesetInfo';
import RulesetInterpolatedConditions from 'components/ruleset-manager/ruleset-view/conditions/RulesetInterpolatedConditions';
import RulesetInjectors from 'components/ruleset-manager/ruleset-view/injectors/RulesetInjectors';
import RulesetGlobalAccessPolicy from 'components/ruleset-manager/ruleset-view/global_access_policy/RulesetGlobalAccessPolicy';
import RulesetGroupAccessPolicy from 'components/ruleset-manager/ruleset-view/group_access_policy/RulesetGroupAccessPolicy';
import  RulesetUserSpecificAccessPolicy  from 'components/ruleset-manager/ruleset-view/user_specific_access_policy/RulesetUserSpecificAccessPolicy';
import { getSchemaTables } from 'services/schemaService';
import { SimpleTablesResponse } from 'types/schema/schemaType';

const RulesetView: React.FC = () => {
  const { ruleset_name } = useParams<{ ruleset_name: string }>();
  const navigate = useNavigate();
  const [ruleset, setRuleset] = useState<Ruleset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string>("");
  const [activeLeftTab, setActiveLeftTab] = useState(0);
  const theme = useTheme();
  const [isSaving, setIsSaving] = useState(false);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [updateError, setUpdateError] = useState<unknown>(null);
  const [availableTables, setAvailableTables] = useState<SimpleTablesResponse>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!ruleset_name) {
        navigate('/ruleset-manager');
        return;
      }

      try {
        setLoading(true);
        // First fetch ruleset
        const fetchedRuleset = await getRulesetByName(ruleset_name);
        
        if (!fetchedRuleset) {
          throw new Error('Ruleset not found');
        }

        setRuleset(fetchedRuleset);

        const tablesResponse = await getSchemaTables(fetchedRuleset.connected_schema_name);
        setAvailableTables(tablesResponse); // Store full table response
        
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setRuleset(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [ruleset_name, navigate]);

  const genericUpdateField = useCallback((path: string, value: any) => {
    setRuleset(prev => {
      if (!prev) return prev;
      return updateByPath<Ruleset>(prev, path, value, {
        strict: false,
        createMissing: true,
      });
    });
  }, []);

  const tabs: TabInfo[] = [
    { label: 'Ruleset Info' },
    { label: 'Interpolated Conditions' },
    { label: 'Global Access Policy' },
    { label: 'Group Access Policy' },
    { label: 'User Specific Access Policy' },
    { label: 'Injectors' },
  ];

  const content = ruleset
    ? [
        <RulesetInfo key="info" ruleset={ruleset} />,
        <RulesetInterpolatedConditions key="interpolated-conditions" ruleset={ruleset} />,
        <RulesetGlobalAccessPolicy 
          key="global" 
          ruleset={ruleset} 
          availableTables={availableTables}
        />,
        <RulesetGroupAccessPolicy 
          key="group" 
          ruleset={ruleset}
          availableTables={availableTables}
        />,
        <RulesetUserSpecificAccessPolicy 
          key="user" 
          ruleset={ruleset}
          tables={availableTables}  // Changed from availableTables to tables to match child props
        />,
        <RulesetInjectors 
          key="injectors" 
          ruleset={ruleset} 
          availableTables={availableTables}
        />
      ]
    : [];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !ruleset) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/ruleset-manager')}>
              Return to Ruleset List
            </Button>
          }
        >
          {error || 'Ruleset not found'}
        </Alert>
      </Box>
    );
  }

  return (
    <FormUpdateProvider updateField={genericUpdateField}>
      <Box sx={{ width: '100%', p: 2 }}>
        {/* Title Card */}
        <Paper 
          sx={{ 
            p: 2,
            mb: 2,
            borderRadius: 1,
          }}
        >
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs>
              <Typography variant="h5">
                {ruleset?.ruleset_name}
              </Typography>
              <Typography 
                variant="body2" 
                color="text.secondary"
              >
                Connected to schema: {ruleset?.connected_schema_name}
              </Typography>
            </Grid>
            <Grid item>
              <Chip
                label={ruleset?.is_ruleset_enabled ? 'Enabled' : 'Disabled'}
                color={ruleset?.is_ruleset_enabled ? 'success' : 'default'}
                size="small"
              />
            </Grid>
          </Grid>
        </Paper>

        {/* Tab Layout */}
        <TabLayout
          tabs={tabs}
          activeTab={activeLeftTab}
          onTabChange={setActiveLeftTab}
          content={content}
        />

        {/* Action Buttons */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          gap: 1,
          mt: 2,
          position: 'sticky',
          bottom: theme.spacing(2),
          backgroundColor: 'background.default',
          py: 1,
        }}>
          <Button 
            variant="contained" 
            size="small" 
            color="success"
            disabled={isSaving} 
            onClick={async () => {
              if (!ruleset || !ruleset_name) return;
            
              setIsSaving(true);
              try {
                // Prepare body of type AddUpdateRulesetRequest
                const updateBody = {
                  ruleset_name: ruleset.ruleset_name,
                  connected_schema_name: ruleset.connected_schema_name,
                  description: ruleset.description,
                  is_ruleset_enabled: ruleset.is_ruleset_enabled,
                  conditions: ruleset.conditions,
                  global_access_policy: ruleset.global_access_policy,
                  group_access_policy: ruleset.group_access_policy,
                  user_specific_access_policy: ruleset.user_specific_access_policy,
                  injectors: ruleset.injectors,
                };
                
                const updatedRuleset = await updateRuleset(ruleset_name, updateBody);
                setRuleset(updatedRuleset);
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
            onClick={() => window.location.reload()}
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
          title="Failed to Save Ruleset"
          error={updateError}
        />
      </Box>
    </FormUpdateProvider>
  );
}

export default RulesetView;
