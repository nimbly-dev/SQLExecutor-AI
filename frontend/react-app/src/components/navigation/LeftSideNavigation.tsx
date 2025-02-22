// LeftSideNavigation.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Box,
} from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import InfoIcon from '@mui/icons-material/Info';
import SchemaIcon from '@mui/icons-material/Schema';
import RuleIcon from '@mui/icons-material/Rule';
import ApiIcon from '@mui/icons-material/Api';

interface LeftSideNavigationProps {
  open: boolean;
  handleDrawerClose: () => void;
}

const LeftSideNavigation: React.FC<LeftSideNavigationProps> = ({ open, handleDrawerClose }) => {
  const navigate = useNavigate();
  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Playground', icon: <ApiIcon />, path: '/sqlexecutor-playground' },
    { text: 'Schema Management', icon: <SchemaIcon />, path: '/schema-manager' },
    { text: 'Ruleset Management', icon: <RuleIcon />, path: '/ruleset-manager' },
    { text: 'Tenant Settings Management', icon: <SettingsIcon />, path: '/tenant-settings-manager' },
    { text: 'Docs', icon: <MenuBookIcon />, path: '/docs' },
    { text: 'About', icon: <InfoIcon />, path: '/about' },
  ];

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: open ? 240 : 60,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 240 : 60,
          boxSizing: 'border-box',
          transition: 'width 0.3s',
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', p: 1 }}>
        <IconButton onClick={handleDrawerClose}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => navigate(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              {open && <ListItemText primary={item.text} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default LeftSideNavigation;
