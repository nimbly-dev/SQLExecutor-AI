import React, { useCallback } from 'react';
import { Grid, TextField, FormControlLabel, Switch, Paper } from '@mui/material';
import { Ruleset } from 'types/ruleset/rulesetType';
import { useFormUpdate } from 'contexts/form/FormUpdateProvider';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import DescriptionTextFormField from 'components/common/forms/field-forms/DescriptionTextFormField';
import AsyncPaginatedDropdownFormField from 'components/common/forms/field-forms/AsyncPaginatedDropdownFormField';
import { getSchemasPaginated } from 'services/schemaService';
import { debounceAsync } from 'utils/common/debounceUtils';

export interface RulesetInfoProps {
  ruleset: Ruleset;
}

type RulesetInfoState = Pick<
  Ruleset,
  'ruleset_name' | 'description' | 'connected_schema_name' | 'is_ruleset_enabled'
>;

export const RulesetInfo: React.FC<RulesetInfoProps> = ({ ruleset }) => {
  const { updateField } = useFormUpdate();

  const [localState, setField] = useLocalFormState<RulesetInfoState>({
    ruleset_name: ruleset.ruleset_name,
    description: ruleset.description,
    connected_schema_name: ruleset.connected_schema_name,
    is_ruleset_enabled: ruleset.is_ruleset_enabled,
  });

  const handleChange = (field: keyof RulesetInfoState) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value =
      event.target.type === 'checkbox'
        ? event.target.checked
        : event.target.value;

    setField(field, value);
    updateField(field, value);
  };

  const handleDescriptionChange = (value: string) => {
    setField('description', value);
    updateField('description', value);
  };

  const handleSchemaSearch = debounceAsync(async (
    searchTerm: string,
    page: number,
    pageSize: number
  ) => {
    try {
      const result = await getSchemasPaginated({
        name: searchTerm,
        page,
        pageSize,
      });

      return {
        options: result.schemas.map((schema) => ({
          value: schema.schema_name,
          label: `${schema.schema_name} (${schema.context_type})`,
        })),
        total: result.total,
      };
    } catch (error) {
      console.error('Error fetching schemas:', error);
      throw new Error('Failed to fetch schemas');
    }
  }, 300);

  const handleSchemaChange = (value: string) => {
    const newValue = value || '';
    setField('connected_schema_name', newValue);
    updateField('connected_schema_name', newValue);
  };

  const getCurrentSchemaLabel = useCallback(
    () => ruleset.connected_schema_name,
    [ruleset.connected_schema_name]
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Ruleset Name"
                value={localState.ruleset_name}
                onChange={handleChange('ruleset_name')}
                variant="outlined"
                helperText="Changing the ruleset name will affect references to this ruleset"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <AsyncPaginatedDropdownFormField
                label="Connected Schema"
                value={localState.connected_schema_name}
                onChange={handleSchemaChange}
                onSearch={handleSchemaSearch}
                placeholder="Search schemas..."
                defaultPageSize={10}
                pageSizeOptions={[5, 10, 25, 50]}
                renderValue={getCurrentSchemaLabel}
              />
            </Grid>
            <Grid item xs={12}>
              <DescriptionTextFormField
                description={localState.description}
                onChange={handleDescriptionChange}
                label="Description"
                minRows={4}
                maxRows={4}
                size="medium"
                placeholder="Enter ruleset description"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={localState.is_ruleset_enabled}
                    onChange={handleChange('is_ruleset_enabled')}
                    color="primary"
                  />
                }
                label="Enable Ruleset"
              />
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default RulesetInfo;
