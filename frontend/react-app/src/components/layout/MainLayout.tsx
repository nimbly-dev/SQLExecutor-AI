// MainLayout.tsx

import React, { ReactNode } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Toolbar } from '@mui/material';
import AppBarComponent from '../navigation/AppBar';
import LeftSideNavigation from '../navigation/LeftSideNavigation';

interface MainLayoutProps {
  darkMode: boolean;
  toggleTheme: () => void;
  children?: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ darkMode, toggleTheme, children }) => {
  const [open, setOpen] = React.useState(true);
  const handleDrawerOpen = () => setOpen(true);
  const handleDrawerClose = () => setOpen(false);

  return (
    // Use 100% width (not 100vw) to avoid scrollbar-induced differences
    <Box sx={{ display: 'flex', height: '100vh', width: '100%', bgcolor: 'background.default' }}>
      <AppBarComponent
        open={open}
        handleDrawerOpen={handleDrawerOpen}
        darkMode={darkMode}
        toggleTheme={toggleTheme}
      />
      <LeftSideNavigation open={open} handleDrawerClose={handleDrawerClose} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          minHeight: '80vh',
          bgcolor: 'background.default',
          transition: (theme) =>
            theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <Toolbar />
        {children || <Outlet />}
      </Box>
    </Box>
  );
};

export default MainLayout;
