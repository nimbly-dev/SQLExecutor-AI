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

const MyAccount: React.FC<{ darkMode: boolean; toggleTheme: () => void }> = ({
  darkMode,
  toggleTheme,
}) => {
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
    logout(); 
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  return (
    <>
      <IconButton onClick={handleMenuOpen} sx={{ marginRight: 1 }}>
        <Avatar alt="Profile" src="/placeholder-profile.png" />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem disableRipple>
          <FormControlLabel
            control={<Switch checked={darkMode} onChange={toggleTheme} />}
            label={<Typography variant="body2">Dark Mode</Typography>}
          />
        </MenuItem>
        <Divider />
        {isLoggedIn ? (
          <MenuItem onClick={handleLogout}>
            <Typography variant="body2">Log Out</Typography>
          </MenuItem>
        ) : (
          <MenuItem onClick={handleLoginRedirect}>
            <Typography variant="body2">Login</Typography>
          </MenuItem>
        )}
      </Menu>
    </>
  );
};

export default MyAccount;
