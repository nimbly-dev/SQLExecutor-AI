import React, { useMemo, useCallback, useState, useEffect } from 'react';
import { Box, TextField } from '@mui/material';
import { GroupAccessPolicy } from 'types/ruleset/rulesetType';
import { useLocalFormState } from 'hooks/common/forms/useLocalFormState';
import { createDebouncedUpdate } from 'utils/forms/formUtils';

interface RulesetFormGroupInfoProps {
  group: GroupAccessPolicy;
  groupKey: string;
  onUpdate: (key: string, value: GroupAccessPolicy) => void;
  onRename: (oldKey: string, newKey: string, value: GroupAccessPolicy) => void;
}

const RulesetFormGroupInfo: React.FC<RulesetFormGroupInfoProps> = ({
  group,
  groupKey,
  onUpdate,
  onRename,
}) => {
  const [localGroup, setField] = useLocalFormState<GroupAccessPolicy>(group);
  const [localName, setLocalName] = useState(groupKey);

  // Sync localName when groupKey changes externally
  useEffect(() => {
    setLocalName(groupKey);
  }, [groupKey]);

  const debouncedUpdate = useMemo(
    () => createDebouncedUpdate<GroupAccessPolicy>(300),
    []
  );

  const handleDescriptionChange = (value: string): void => {
    setField('description', value);
    debouncedUpdate(
      () => onUpdate(groupKey, { ...group, description: value }),
      'description',
      value
    );
  };

  const handleNameChange = (value: string): void => {
    if (value === groupKey) return;
    setLocalName(value);  
    debouncedUpdate(
      () => onRename(groupKey, value, group),
      'name' as keyof GroupAccessPolicy,
      value
    );
  };

  return (
    <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
      <TextField
        fullWidth
        label="Name"
        value={localName}  
        onChange={(e) => handleNameChange(e.target.value)}
      />
      <TextField
        fullWidth
        multiline
        rows={4}
        label="Description"
        value={localGroup.description}
        onChange={(e) => handleDescriptionChange(e.target.value)}
      />
    </Box>
  );
};

export default RulesetFormGroupInfo;
