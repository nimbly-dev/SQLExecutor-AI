import React from 'react';
import { Box, TextField, FormControlLabel, Switch } from '@mui/material';
import { Injector } from 'types/ruleset/rulesetType';

interface RulesetFormInjectorDetailsProps {
  injector: Injector;
  injectorKey: string;  // Added to handle the name as key
  onChange: <K extends keyof Injector>(field: K, value: Injector[K]) => void;
  onKeyChange: (newKey: string) => void;  // Added to handle key changes
}

const RulesetFormInjectorDetails: React.FC<RulesetFormInjectorDetailsProps> = ({ 
  injector, 
  injectorKey,
  onChange,
  onKeyChange 
}) => {
  return (
    <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
      <TextField
        fullWidth
        label="Name"
        value={injectorKey}
        onChange={(e) => onKeyChange(e.target.value)}
      />
      <FormControlLabel
        control={
          <Switch
            checked={injector.enabled}
            onChange={(e) => onChange('enabled', e.target.checked)}
          />
        }
        label="Enabled"
      />
      <TextField
        fullWidth
        multiline
        rows={4}
        label="Condition"
        value={injector.condition}
        onChange={(e) => onChange('condition', e.target.value)}
      />
    </Box>
  );
};

export default RulesetFormInjectorDetails;
