import React from 'react';
import { Dialog, DialogContent, DialogActions, Tabs, Tab, Box, useTheme } from '@mui/material';
import styles from 'styles/common/modal/MultiTabModal.module.scss';

export interface TabItem<T> {
  value: T;
  label: string;
  content: React.ReactNode;
}

export interface MultiTabModalProps<T> {
  open: boolean;
  onClose: () => void;
  value: T;
  onTabChange: (newValue: T) => void;
  tabs: TabItem<T>[];
  footer?: React.ReactNode;
}

function MultiTabModal<T>({ open, onClose, value, onTabChange, tabs, footer }: MultiTabModalProps<T>) {
  const theme = useTheme();
  const handleTabChange = (_event: React.SyntheticEvent, newValue: T) => {
    onTabChange(newValue);
  };

  const currentTab = tabs.find(tab => tab.value === value);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{ 
        sx: { 
          m: 0, 
          p: 0, 
          width: '100%',
          zIndex: theme.zIndex.modal
        } 
      }}
    >
      <DialogContent className={styles.dialogContent} sx={{ p: 0, m: 0, width: '100%' }}>
        <Box className={styles.tabHeader} sx={{ width: '100%', m: 0, p: 0 }}>
          <Tabs
            value={value}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ width: '100%', m: 0, p: 0 }}
          >
            {tabs.map(tab => (
              <Tab
                key={String(tab.value)}
                label={tab.label}
                value={tab.value}
                sx={{ flex: 1, m: 0, p: 0 }}
              />
            ))}
          </Tabs>
        </Box>
        <Box className={styles.tabContent}>
          {currentTab && currentTab.content}
        </Box>
      </DialogContent>
      {footer && (
        <DialogActions className={styles.dialogActions}>
          {footer}
        </DialogActions>
      )}
    </Dialog>
  );
}

export default MultiTabModal;
