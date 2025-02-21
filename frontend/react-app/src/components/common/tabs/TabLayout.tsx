import React from 'react';
import { Grid, List, ListItemButton, ListItemText, Box, useMediaQuery, useTheme } from '@mui/material';

export interface TabInfo {
  label: string;
}

interface TabLayoutProps {
  tabs: TabInfo[];
  activeTab: number;
  onTabChange: (newValue: number) => void;
  content: React.ReactNode[];
}

export const TabLayout: React.FC<TabLayoutProps> = ({
  tabs,
  activeTab,
  onTabChange,
  content,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={3}>
          <List 
            component="nav"
            sx={{
              bgcolor: 'background.default',
              borderRight: isMobile ? 0 : 1,
              borderColor: 'divider',
              height: '100%',
            }}
          >
            {tabs.map((tab, index) => (
              <ListItemButton
                key={index}
                selected={activeTab === index}
                onClick={() => onTabChange(index)}
                sx={{
                  borderLeft: activeTab === index ? 2 : 0,
                  borderColor: 'primary.main',
                  '&.Mui-selected': {
                    bgcolor: 'action.selected',
                  }
                }}
              >
                <ListItemText 
                  primary={tab.label}
                  primaryTypographyProps={{
                    sx: {
                      fontWeight: activeTab === index ? 'medium' : 'regular',
                    }
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        </Grid>
        <Grid item xs={12} md={9}>
          {content[activeTab]}
        </Grid>
      </Grid>
    </Box>
  );
};
