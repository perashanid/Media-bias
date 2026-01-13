import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface CustomThemeProviderProps {
  children: React.ReactNode;
}

export const CustomThemeProvider: React.FC<CustomThemeProviderProps> = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const theme = useMemo(() => createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#6366f1',
        light: '#818cf8',
        dark: '#4f46e5',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#06b6d4',
        light: '#22d3ee',
        dark: '#0891b2',
        contrastText: '#ffffff',
      },
      background: {
        default: darkMode ? '#0f172a' : '#f8fafc',
        paper: darkMode ? '#1e293b' : '#ffffff',
      },
      text: {
        primary: darkMode ? '#f8fafc' : '#0f172a',
        secondary: darkMode ? '#94a3b8' : '#475569',
      },
      success: {
        main: '#10b981',
        light: '#34d399',
        dark: '#059669',
      },
      warning: {
        main: '#f59e0b',
        light: '#fbbf24',
        dark: '#d97706',
      },
      error: {
        main: '#ef4444',
        light: '#f87171',
        dark: '#dc2626',
      },
      divider: darkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
    },
    typography: {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 700,
        lineHeight: 1.2,
        letterSpacing: '-0.025em',
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
        lineHeight: 1.3,
        letterSpacing: '-0.025em',
      },
      h3: {
        fontSize: '1.5rem',
        fontWeight: 600,
        lineHeight: 1.4,
        letterSpacing: '-0.025em',
      },
      h4: {
        fontSize: '1.25rem',
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h5: {
        fontSize: '1.125rem',
        fontWeight: 500,
        lineHeight: 1.5,
      },
      h6: {
        fontSize: '1rem',
        fontWeight: 500,
        lineHeight: 1.5,
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.6,
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.5,
      },
      button: {
        textTransform: 'none',
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: darkMode ? '#0f172a' : '#f8fafc',
            color: darkMode ? '#f8fafc' : '#0f172a',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            textTransform: 'none',
            fontWeight: 600,
            boxShadow: 'none',
            transition: 'all 0.2s ease',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            },
          },
          contained: {
            background: '#4f46e5',
            '&:hover': {
              background: '#4338ca',
            },
          },
          outlined: {
            borderWidth: 2,
            borderColor: darkMode ? 'rgba(99, 102, 241, 0.5)' : '#4f46e5',
            color: darkMode ? '#a5b4fc' : '#4f46e5',
            '&:hover': {
              borderWidth: 2,
              borderColor: '#4f46e5',
              backgroundColor: darkMode ? 'rgba(99, 102, 241, 0.1)' : 'rgba(79, 70, 229, 0.08)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundColor: darkMode ? '#1e293b' : '#ffffff',
            border: darkMode ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(0, 0, 0, 0.06)',
            boxShadow: darkMode 
              ? '0 4px 24px rgba(0, 0, 0, 0.2)'
              : '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04)',
            transition: 'all 0.3s ease',
            '&:hover': {
              boxShadow: darkMode 
                ? '0 12px 40px rgba(0, 0, 0, 0.3)'
                : '0 10px 40px rgba(0, 0, 0, 0.12)',
              transform: 'translateY(-4px)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            backgroundColor: darkMode ? '#1e293b' : '#ffffff',
            backgroundImage: 'none',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: 'transparent',
            boxShadow: 'none',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 12,
              backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.03)' : '#ffffff',
              '& fieldset': {
                borderColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : '#e2e8f0',
                transition: 'all 0.2s ease',
              },
              '&:hover fieldset': {
                borderColor: darkMode ? 'rgba(99, 102, 241, 0.5)' : '#6366f1',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#6366f1',
                borderWidth: 2,
              },
            },
            '& .MuiInputLabel-root': {
              color: darkMode ? '#94a3b8' : '#64748b',
            },
            '& .MuiOutlinedInput-input': {
              color: darkMode ? '#f8fafc' : '#0f172a',
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 9999,
            fontWeight: 600,
          },
          outlined: {
            borderColor: darkMode ? 'rgba(255, 255, 255, 0.15)' : '#e2e8f0',
            color: darkMode ? '#94a3b8' : '#475569',
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderColor: darkMode ? 'rgba(255, 255, 255, 0.06)' : '#f1f5f9',
          },
          head: {
            backgroundColor: darkMode ? 'rgba(99, 102, 241, 0.1)' : '#f8fafc',
            fontWeight: 600,
            color: darkMode ? '#a5b4fc' : '#4f46e5',
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 20,
            backgroundColor: darkMode ? '#1e293b' : '#ffffff',
            border: darkMode ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
          },
        },
      },
      MuiMenu: {
        styleOverrides: {
          paper: {
            borderRadius: 12,
            backgroundColor: darkMode ? '#1e293b' : '#ffffff',
            border: darkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid #e2e8f0',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
          },
        },
      },
      MuiMenuItem: {
        styleOverrides: {
          root: {
            color: darkMode ? '#f8fafc' : '#0f172a',
            '&:hover': {
              backgroundColor: darkMode ? 'rgba(99, 102, 241, 0.1)' : '#f1f5f9',
            },
          },
        },
      },
      MuiSelect: {
        styleOverrides: {
          icon: {
            color: darkMode ? '#94a3b8' : '#64748b',
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 9999,
            backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : '#e2e8f0',
          },
          bar: {
            borderRadius: 9999,
            background: '#4f46e5',
          },
        },
      },
      MuiCircularProgress: {
        styleOverrides: {
          root: {
            color: '#6366f1',
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 12,
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            borderRadius: 8,
            backgroundColor: darkMode ? '#334155' : '#1e293b',
            fontSize: '0.75rem',
            fontWeight: 500,
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            color: darkMode ? '#94a3b8' : '#64748b',
            '&.Mui-selected': {
              color: '#6366f1',
            },
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          indicator: {
            backgroundColor: '#6366f1',
            height: 3,
            borderRadius: 3,
          },
        },
      },
    },
  }), [darkMode]);

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};