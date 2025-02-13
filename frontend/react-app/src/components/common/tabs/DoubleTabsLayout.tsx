
import React from 'react';
import { Tabs, Tab, List, ListItemButton, ListItemText, Box, Grid, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';

export interface UpperTab {
  label: string;
}

export interface LeftTab {
  label: string;
}

/**
 * Props for DoubleTabsLayout. 
 * Renders an upper-level Tabs row and a left vertical list of tabs.
 */
interface DoubleTabsLayoutProps {
  upperTabs: UpperTab[];
  activeUpperTab: number;
  onUpperTabChange: (newValue: number) => void;
  leftTabs: LeftTab[];
  activeLeftTab: number;
  onLeftTabChange: (newValue: number) => void;
  upperContent: React.ReactNode[];
  leftContent: React.ReactNode[];
}

/**
 * A reusable component combining an upper Tab bar and a left vertical list of tabs.
 */
export const DoubleTabsLayout: React.FC<DoubleTabsLayoutProps> = ({
  upperTabs,
  activeUpperTab,
  onUpperTabChange,
  leftTabs,
  activeLeftTab,
  onLeftTabChange,
  upperContent,
  leftContent,
}) => {
  const theme = useTheme();
  const isSm = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ p: 2 }}>
      <Tabs
        value={activeUpperTab}
        onChange={(_, newValue) => onUpperTabChange(newValue)}
        variant={isSm ? 'scrollable' : 'fullWidth'}
        scrollButtons="auto"
      >
        {upperTabs.map((tab, index) => (
          <Tab key={index} label={tab.label} />
        ))}
      </Tabs>
      {activeUpperTab < upperContent.length ? upperContent[activeUpperTab] : null}

      {/* Left and main content layout */}
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={3}>
          <List component="nav">
            {leftTabs.map((tab, index) => (
              <ListItemButton
                key={index}
                selected={activeLeftTab === index}
                onClick={() => onLeftTabChange(index)}
              >
                <ListItemText primary={tab.label} />
              </ListItemButton>
            ))}
          </List>
        </Grid>
        <Grid item xs={12} md={9}>
          {activeLeftTab < leftContent.length ? leftContent[activeLeftTab] : null}
        </Grid>
      </Grid>
    </Box>
  );
};

export default DoubleTabsLayout;