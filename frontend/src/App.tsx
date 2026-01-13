import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ArticleList from './pages/ArticleList';
import ArticleDetail from './pages/ArticleDetail';
import ComparisonView from './pages/ComparisonView';
import Comparison from './pages/Comparison';
import BiasAnalyzer from './pages/BiasAnalyzer';
import ManualScraper from './pages/ManualScraper';
import Contact from './pages/Contact';
import Privacy from './pages/Privacy';
import ProtectedRoute from './components/ProtectedRoute';
import { DashboardProvider } from './contexts/DashboardContext';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <DashboardProvider>
        <Box className="App" sx={{ minHeight: '100vh', bgcolor: 'var(--bg-secondary)' }}>
          <Navbar />
          <Box component="main">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/articles" element={<ArticleList />} />
              <Route path="/articles/:id" element={<ArticleDetail />} />
              <Route path="/comparison" element={<Comparison />} />
              <Route path="/comparison-advanced" element={<ComparisonView />} />
              <Route path="/analyzer" element={<BiasAnalyzer />} />
              <Route path="/scraper" element={<ManualScraper />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/privacy" element={<Privacy />} />
            </Routes>
          </Box>
        </Box>
      </DashboardProvider>
    </AuthProvider>
  );
}

export default App;