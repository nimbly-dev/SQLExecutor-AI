// MyAccount.tsx

import React, { useState } from 'react';
import {
  Menu,
  MenuItem,
  IconButton,
  Avatar,
  Divider,
  Switch,
  FormControlLabel,
  Typography,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import '../../styles/my_account/my_account.scss'; // Existing SCSS import

interface MyAccountProps {
  darkMode: boolean;
  toggleTheme: () => void;
}

const MyAccount: React.FC<MyAccountProps> = ({ darkMode, toggleTheme }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const navigate = useNavigate();
  const { isLoggedIn, logout } = useAuth();

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout(); // Ensure logout completes
    handleMenuClose();
  };

  const handleLoginRedirect = () => {
    navigate('/login');
    handleMenuClose();
  };

  return (
    <>
      <IconButton onClick={handleMenuOpen} className="account-button">
        <Avatar alt="Theo" src="/placeholder-profile.png" />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        className="menu"
      >
        <MenuItem disableRipple className="menu-item">
          <FormControlLabel
            className="theme-switch"
            control={<Switch checked={darkMode} onChange={toggleTheme} />}
            label={<Typography variant="body2">Dark Mode</Typography>}
          />
        </MenuItem>
        <Divider />
        {isLoggedIn ? (
          <MenuItem onClick={handleLogout} className="menu-item">
            <Typography variant="body2">Log Out</Typography>
          </MenuItem>
        ) : (
          <MenuItem onClick={handleLoginRedirect} className="menu-item">
            <Typography variant="body2">Login</Typography>
          </MenuItem>
        )}
      </Menu>
    </>
  );
};

export default MyAccount;
