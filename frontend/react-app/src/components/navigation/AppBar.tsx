// AppBar.tsx

import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import MyAccount from '../account/MyAccount';

interface AppBarProps {
  open: boolean;
  handleDrawerOpen: () => void;
  darkMode: boolean;
  toggleTheme: () => void;
}

const AppBarComponent: React.FC<AppBarProps> = ({ open, handleDrawerOpen, darkMode, toggleTheme }) => {
  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        transition: (theme) =>
          theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        ...(open && {
          marginLeft: 240, // Ensure this matches Drawer width
          width: `calc(100% - 240px)`,
          transition: (theme) =>
            theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
        }),
      }}
    >
      <Toolbar
        sx={{
          minHeight: 64,
          display: 'flex',
          alignItems: 'center', 
        }}
      >
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={handleDrawerOpen}
          edge="start"
          sx={{
            marginRight: 2,
            ...(open && { display: 'none' }), // Hide if drawer is open
          }}
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" noWrap component="div">
          SQLExecutor
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <MyAccount darkMode={darkMode} toggleTheme={toggleTheme} />
      </Toolbar>
    </AppBar>
  );
};

export default AppBarComponent;
