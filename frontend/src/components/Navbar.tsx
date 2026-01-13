import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Avatar, Container } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Assessment, Article, Compare, Analytics, CloudDownload, Login, DarkMode, LightMode, Info, PrivacyTip, AutoAwesome } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import LoginDialog from './LoginDialog';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);

  // Check if current page has dark hero (Home page) - only in dark mode
  const hasDarkHero = location.pathname === '/' && darkMode;

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Determine navbar colors based on scroll state, page, and theme
  const getNavColors = () => {
    if (!scrolled && hasDarkHero) {
      // On hero section of home page - always light text
      return {
        text: 'rgba(255, 255, 255, 0.9)',
        textActive: '#ffffff',
        bg: 'transparent',
        hoverBg: 'rgba(255, 255, 255, 0.15)',
        activeBg: 'rgba(255, 255, 255, 0.2)',
        border: 'rgba(255, 255, 255, 0.2)',
        logoText: '#ffffff',
      };
    }
    // Scrolled or other pages - use theme-aware colors
    return {
      text: darkMode ? '#94a3b8' : '#475569',
      textActive: darkMode ? '#ffffff' : '#0f172a',
      bg: darkMode ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
      hoverBg: darkMode ? 'rgba(99, 102, 241, 0.15)' : 'rgba(99, 102, 241, 0.08)',
      activeBg: darkMode ? 'rgba(99, 102, 241, 0.2)' : 'rgba(99, 102, 241, 0.12)',
      border: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
      logoText: '#4f46e5',
    };
  };

  const colors = getNavColors();

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
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        background: scrolled || !hasDarkHero ? colors.bg : 'transparent',
        backdropFilter: scrolled || !hasDarkHero ? 'blur(20px) saturate(180%)' : 'none',
        borderBottom: scrolled || !hasDarkHero ? `1px solid ${colors.border}` : 'none',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        py: scrolled ? 0.5 : 1,
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ py: 1, px: { xs: 0, sm: 2 } }}>
          {/* Logo */}
          <Box
            component={Link}
            to="/"
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              textDecoration: 'none',
              mr: 4,
            }}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-lg)',
                background: '#4f46e5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 8px rgba(79, 70, 229, 0.25)',
                overflow: 'hidden',
              }}
            >
              <img src="/logo.png" alt="Media Bias" style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '4px' }} />
            </Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 800,
                letterSpacing: '-0.02em',
                color: colors.logoText,
                display: { xs: 'none', sm: 'block' },
              }}
            >
              Media Bias
            </Typography>
          </Box>

          {/* Navigation Links */}
          <Box sx={{ display: { xs: 'none', lg: 'flex' }, gap: 0.5, flex: 1, alignItems: 'center' }}>
            {navItems.slice(0, 6).map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                sx={{
                  color: location.pathname === item.path
                    ? colors.textActive
                    : colors.text,
                  backgroundColor: location.pathname === item.path
                    ? colors.activeBg
                    : 'transparent',
                  borderRadius: 'var(--radius-lg)',
                  px: 2,
                  py: 1,
                  fontSize: '0.875rem',
                  fontWeight: location.pathname === item.path ? 600 : 500,
                  textTransform: 'none',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: colors.hoverBg,
                    color: colors.textActive,
                    transform: 'translateY(-1px)',
                  }
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {/* Theme Toggle */}
            <IconButton
              onClick={toggleDarkMode}
              sx={{
                width: 40,
                height: 40,
                borderRadius: 'var(--radius-lg)',
                color: colors.text,
                backgroundColor: scrolled || !hasDarkHero
                  ? (darkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.04)')
                  : 'rgba(255, 255, 255, 0.1)',
                border: `1px solid ${colors.border}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: colors.hoverBg,
                  color: colors.textActive,
                  transform: 'rotate(180deg)',
                }
              }}
            >
              {darkMode ? <LightMode sx={{ fontSize: 20 }} /> : <DarkMode sx={{ fontSize: 20 }} />}
            </IconButton>

            {isAuthenticated ? (
              <>
                <IconButton
                  onClick={handleUserMenuOpen}
                  sx={{
                    p: 0.5,
                    border: '2px solid',
                    borderColor: scrolled || !hasDarkHero
                      ? (darkMode ? 'rgba(99, 102, 241, 0.3)' : 'rgba(99, 102, 241, 0.2)')
                      : 'rgba(255, 255, 255, 0.3)',
                    borderRadius: 'var(--radius-full)',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: scrolled || !hasDarkHero
                        ? 'var(--color-primary-500)'
                        : 'rgba(255, 255, 255, 0.6)',
                      transform: 'scale(1.05)',
                    }
                  }}
                >
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      background: '#4f46e5',
                      fontSize: '0.95rem',
                      fontWeight: 700,
                    }}
                  >
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
                      borderRadius: 'var(--radius-xl)',
                      mt: 1.5,
                      minWidth: 180,
                      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
                      border: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.08)',
                      background: darkMode ? '#1e293b' : '#ffffff',
                      backdropFilter: 'blur(20px)',
                    }
                  }}
                >
                  <Box sx={{
                    px: 2,
                    py: 1.5,
                    borderBottom: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e8f0'
                  }}>
                    <Typography variant="body2" sx={{
                      fontWeight: 700,
                      color: darkMode ? '#f8fafc' : '#0f172a'
                    }}>
                      {user?.username}
                    </Typography>
                    <Typography variant="caption" sx={{
                      color: darkMode ? '#94a3b8' : '#64748b'
                    }}>
                      Welcome back!
                    </Typography>
                  </Box>
                  <MenuItem
                    onClick={handleLogout}
                    sx={{
                      py: 1.5,
                      color: '#ef4444',
                      '&:hover': {
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      }
                    }}
                  >
                    Logout
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <Button
                variant="contained"
                startIcon={<Login />}
                onClick={() => setLoginDialogOpen(true)}
                sx={{
                  px: 3,
                  py: 1,
                  borderRadius: 'var(--radius-lg)',
                  background: scrolled || !hasDarkHero
                    ? '#4f46e5'
                    : 'rgba(255, 255, 255, 0.95)',
                  color: scrolled || !hasDarkHero ? '#ffffff' : '#4f46e5',
                  fontWeight: 600,
                  textTransform: 'none',
                  boxShadow: scrolled || !hasDarkHero
                    ? '0 2px 8px rgba(79, 70, 229, 0.25)'
                    : '0 2px 8px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    background: scrolled || !hasDarkHero
                      ? '#4338ca'
                      : '#ffffff',
                    transform: 'translateY(-2px)',
                    boxShadow: scrolled || !hasDarkHero
                      ? '0 4px 12px rgba(79, 70, 229, 0.35)'
                      : '0 4px 12px rgba(0, 0, 0, 0.15)',
                  }
                }}
              >
                Login
              </Button>
            )}
          </Box>
        </Toolbar>
      </Container>

      <LoginDialog
        open={loginDialogOpen}
        onClose={() => setLoginDialogOpen(false)}
      />
    </AppBar>
  );
};

export default Navbar;