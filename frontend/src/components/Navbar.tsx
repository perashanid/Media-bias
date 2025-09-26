import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Assessment, Article, Compare, Analytics, CloudDownload } from '@mui/icons-material';

const Navbar: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <Assessment /> },
    { path: '/articles', label: 'Articles', icon: <Article /> },
    { path: '/comparison', label: 'Comparison', icon: <Compare /> },
    { path: '/analyzer', label: 'Analyzer', icon: <Analytics /> },
    { path: '/scraper', label: 'Scraper', icon: <CloudDownload /> },
  ];

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography 
          variant="h6" 
          component={Link} 
          to="/" 
          sx={{ 
            flexGrow: 1, 
            textDecoration: 'none', 
            color: 'inherit',
            cursor: 'pointer',
            '&:hover': {
              opacity: 0.8
            }
          }}
        >
          Media Bias Detector
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              component={Link}
              to={item.path}
              startIcon={item.icon}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;