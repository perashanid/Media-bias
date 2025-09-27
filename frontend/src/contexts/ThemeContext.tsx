import React, { createContext, useContext, useState, useEffect } from 'react';
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

// Color scheme from the provided image
const colors = {
  primary: '#0D1B2A',    // Darkest blue
  secondary: '#1B263B',   // Dark blue
  accent: '#415A77',      // Medium blue
  light: '#778DA9',       // Light blue
  lightest: '#E0E1DD',    // Light gray
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

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: colors.primary,
        light: colors.secondary,
        dark: '#0A1520',
        contrastText: '#ffffff',
      },
      secondary: {
        main: colors.accent,
        light: colors.light,
        dark: colors.secondary,
        contrastText: '#ffffff',
      },
      background: {
        default: darkMode ? colors.primary : '#fafafa',
        paper: darkMode ? colors.secondary : '#ffffff',
      },
      text: {
        primary: darkMode ? colors.lightest : '#1a1a1a',
        secondary: darkMode ? colors.light : '#4a5568',
      },
      grey: {
        50: darkMode ? colors.secondary : '#f9fafb',
        100: darkMode ? colors.accent : '#f3f4f6',
        200: darkMode ? colors.light : '#e5e7eb',
        300: darkMode ? colors.light : '#d1d5db',
        400: darkMode ? colors.light : '#9ca3af',
        500: darkMode ? colors.lightest : colors.light,
        600: darkMode ? colors.lightest : colors.accent,
        700: darkMode ? colors.lightest : colors.secondary,
        800: darkMode ? colors.lightest : colors.primary,
        900: darkMode ? '#ffffff' : colors.primary,
      },
    },
    typography: {
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 700,
        lineHeight: 1.2,
        letterSpacing: '-0.025em',
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
        lineHeight: 1.3,
        letterSpacing: '-0.025em',
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      h3: {
        fontSize: '1.5rem',
        fontWeight: 600,
        lineHeight: 1.4,
        letterSpacing: '-0.025em',
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      h4: {
        fontSize: '1.25rem',
        fontWeight: 600,
        lineHeight: 1.4,
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      h5: {
        fontSize: '1.125rem',
        fontWeight: 500,
        lineHeight: 1.5,
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      h6: {
        fontSize: '1rem',
        fontWeight: 500,
        lineHeight: 1.5,
        color: darkMode ? colors.lightest : '#1a1a1a',
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.6,
        color: darkMode ? colors.light : '#4a5568',
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.5,
        color: darkMode ? colors.light : '#4a5568',
      },
      button: {
        textTransform: 'none',
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: 'none',
            fontWeight: 500,
            boxShadow: 'none',
            '&:hover': {
              boxShadow: darkMode 
                ? '0 4px 12px rgba(224, 225, 221, 0.1)' 
                : '0 4px 12px rgba(13, 27, 42, 0.1)',
            },
          },
          contained: {
            background: darkMode 
              ? `linear-gradient(135deg, ${colors.accent} 0%, ${colors.light} 100%)`
              : `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%)`,
            '&:hover': {
              background: darkMode 
                ? `linear-gradient(135deg, ${colors.light} 0%, ${colors.lightest} 100%)`
                : `linear-gradient(135deg, ${colors.secondary} 0%, ${colors.accent} 100%)`,
              boxShadow: darkMode 
                ? '0 4px 12px rgba(224, 225, 221, 0.15)' 
                : '0 4px 12px rgba(13, 27, 42, 0.15)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            backgroundColor: darkMode ? colors.secondary : '#ffffff',
            border: darkMode ? `1px solid ${colors.accent}` : '1px solid rgba(0, 0, 0, 0.05)',
            boxShadow: darkMode 
              ? '0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)'
              : '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
            '&:hover': {
              boxShadow: darkMode 
                ? '0 4px 6px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.3)'
                : '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            backgroundColor: darkMode ? colors.secondary : '#ffffff',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: darkMode ? colors.primary : colors.primary,
            boxShadow: darkMode 
              ? '0 1px 3px rgba(0, 0, 0, 0.3)'
              : '0 1px 3px rgba(0, 0, 0, 0.1)',
            backdropFilter: 'blur(8px)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
              backgroundColor: darkMode ? colors.secondary : '#ffffff',
              '& fieldset': {
                borderColor: darkMode ? colors.accent : '#e5e7eb',
              },
              '&:hover fieldset': {
                borderColor: darkMode ? colors.light : colors.accent,
              },
              '&.Mui-focused fieldset': {
                borderColor: darkMode ? colors.light : colors.primary,
              },
            },
            '& .MuiInputLabel-root': {
              color: darkMode ? colors.light : colors.accent,
            },
            '& .MuiOutlinedInput-input': {
              color: darkMode ? colors.lightest : colors.primary,
            },
          },
        },
      },
    },
  });

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};