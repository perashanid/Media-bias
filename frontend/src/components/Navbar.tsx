import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Avatar } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Assessment, Article, Compare, Analytics, CloudDownload, Login, DarkMode, LightMode, Info, PrivacyTip } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import LoginDialog from './LoginDialog';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const navItems = [
    { path: '/', label: 'Home', icon: <Assessment /> },
    ...(isAuthenticated ? [{ path: '/dashboard', label: 'Dashboard', icon: <Assessment /> }] : []),
    { path: '/articles', label: 'Articles', icon: <Article /> },
    { path: '/comparison', label: 'Comparison', icon: <Compare /> },
    { path: '/analyzer', label: 'Analyzer', icon: <Analytics /> },
    { path: '/scraper', label: 'Scraper', icon: <CloudDownload /> },
    { path: '/contact', label: 'Contact', icon: <Info /> },
    { path: '/privacy', label: 'Privacy', icon: <PrivacyTip /> },
  ];

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ py: 1 }}>
        <Typography 
          variant="h5" 
          component={Link} 
          to="/" 
          sx={{ 
            flexGrow: 1, 
            textDecoration: 'none', 
            color: 'white',
            cursor: 'pointer',
            fontWeight: 700,
            '&:hover': {
              opacity: 0.8
            }
          }}
        >
          Media Bias Detector
        </Typography>
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 0.5, alignItems: 'center' }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              startIcon={item.icon}
              sx={{
                color: location.pathname === item.path ? 'white' : 'rgba(255, 255, 255, 0.7)',
                backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                borderRadius: 2,
                px: 2,
                py: 1,
                fontWeight: location.pathname === item.path ? 600 : 500,
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                }
              }}
            >
              {item.label}
            </Button>
          ))}
          
          <IconButton
            onClick={toggleDarkMode}
            sx={{
              ml: 1,
              color: 'rgba(255, 255, 255, 0.7)',
              '&:hover': {
                color: 'white',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            {darkMode ? <LightMode /> : <DarkMode />}
          </IconButton>
          
          {isAuthenticated ? (
            <>
              <IconButton
                size="large"
                edge="end"
                aria-label="account of current user"
                aria-controls="user-menu"
                aria-haspopup="true"
                onClick={handleUserMenuOpen}
                sx={{ ml: 2 }}
              >
                <Avatar sx={{ 
                  width: 36, 
                  height: 36, 
                  bgcolor: 'primary.main',
                  fontSize: '1rem',
                  fontWeight: 600,
                }}>
                  {user?.username.charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>
              <Menu
                id="user-menu"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleUserMenuClose}
                sx={{
                  '& .MuiPaper-root': {
                    borderRadius: 2,
                    mt: 1,
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  }
                }}
              >
                <MenuItem disabled>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    {user?.username}
                  </Typography>
                </MenuItem>
                <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button
              variant="contained"
              startIcon={<Login />}
              onClick={() => setLoginDialogOpen(true)}
              sx={{ ml: 2, borderRadius: 2 }}
            >
              Login
            </Button>
          )}
        </Box>
        
        <LoginDialog
          open={loginDialogOpen}
          onClose={() => setLoginDialogOpen(false)}
        />
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;