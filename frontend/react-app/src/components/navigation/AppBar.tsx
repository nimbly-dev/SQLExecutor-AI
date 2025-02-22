// AppBar.tsx
import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import MyAccount from 'components/account/MyAccount';

interface AppBarProps {
  open: boolean;
  handleDrawerOpen: () => void;
  darkMode: boolean;
  toggleTheme: () => void;
}

const drawerWidth = 240;

const AppBarComponent: React.FC<AppBarProps> = ({
  open,
  handleDrawerOpen,
  darkMode,
  toggleTheme,
}) => {
  return (
    <AppBar
      position="fixed"
      sx={(theme) => ({
        // Use the custom property from the theme for background color.
        backgroundColor: theme.custom.appBarBg,
        opacity: 1,
        borderRadius: 0,
        border: 'none',
        boxSizing: 'border-box',
        left: open ? `${drawerWidth}px` : 0,
        width: open ? `calc(100% - ${drawerWidth}px)` : '100%',
        transition: theme.transitions.create(['left', 'width'], {
          easing: open ? theme.transitions.easing.easeOut : theme.transitions.easing.sharp,
          duration: open
            ? theme.transitions.duration.enteringScreen
            : theme.transitions.duration.leavingScreen,
        }),
      })}
    >
      <Toolbar
        sx={{
          // Remove any hard-coded background; let the AppBar's background show through.
          backgroundColor: 'transparent',
          opacity: 1,
          position: 'relative',
          minHeight: 64,
          px: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {!open && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={handleDrawerOpen}
              edge="start"
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div">
            SQLExecutor
          </Typography>
        </Box>
        <Box
          sx={{
            position: 'absolute',
            right: 16,
            top: '50%',
            transform: 'translateY(-50%)',
          }}
        >
          <MyAccount darkMode={darkMode} toggleTheme={toggleTheme} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default AppBarComponent;
