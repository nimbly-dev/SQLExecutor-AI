import React, { useMemo, useState } from 'react';
import { TextField, Box, Paper } from '@mui/material';
import { UserSpecificAccessPolicy } from 'types/ruleset/rulesetType';
import { createDebouncedUpdate } from 'utils/forms/formUtils';

interface UserPolicyInfoProps {
  selectedUser: string;
  policy: UserSpecificAccessPolicy;
  onUpdate: (userId: string, policy: UserSpecificAccessPolicy) => void;
}

const UserPolicyInfo: React.FC<UserPolicyInfoProps> = ({
  selectedUser,
  policy,
  onUpdate,
}) => {
  // Local state for immediate updates
  const [localIdentifier, setLocalIdentifier] = useState(policy.user_identifier || '');
  
  // Create debounced update
  const debouncedUpdate = useMemo(() => createDebouncedUpdate(300), []);

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 2 }}>
        <TextField
          fullWidth
          label="User Identifier"
          value={localIdentifier}
          onChange={(e) => {
            setLocalIdentifier(e.target.value);
            
            debouncedUpdate(
              () => {
                onUpdate(selectedUser, {
                  ...policy,
                  user_identifier: e.target.value
                });
              },
              'user_identifier',
              e.target.value
            );
          }}
          helperText="Email or unique identifier for the user"
        />
      </Paper>
    </Box>
  );
};

export default UserPolicyInfo;
