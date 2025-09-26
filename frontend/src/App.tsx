import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from '@mui/material';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ArticleList from './pages/ArticleList';
import ArticleDetail from './pages/ArticleDetail';
import ComparisonView from './pages/ComparisonView';
import BiasAnalyzer from './pages/BiasAnalyzer';
import ManualScraper from './pages/ManualScraper';
import { DashboardProvider } from './contexts/DashboardContext';

function App() {
  return (
    <DashboardProvider>
      <div className="App">
        <Navbar />
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/articles" element={<ArticleList />} />
            <Route path="/articles/:id" element={<ArticleDetail />} />
            <Route path="/comparison" element={<ComparisonView />} />
            <Route path="/analyzer" element={<BiasAnalyzer />} />
            <Route path="/scraper" element={<ManualScraper />} />
          </Routes>
        </Container>
      </div>
    </DashboardProvider>
  );
}

export default App;