import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import '@fontsource/inter/300.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import './styles/modern.css';
import App from './App';
import { CustomThemeProvider } from './contexts/ThemeContext';

const AppWithTheme: React.FC = () => {
  useEffect(() => {
    // Set theme attribute on document for CSS variables
    const updateThemeAttribute = () => {
      const isDark = localStorage.getItem('darkMode') === 'true';
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    };

    updateThemeAttribute();
    
    // Listen for theme changes
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'darkMode') {
        updateThemeAttribute();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return <App />;
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <CustomThemeProvider>
        <AppWithTheme />
      </CustomThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);