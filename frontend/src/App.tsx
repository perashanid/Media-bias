import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ArticleList from './pages/ArticleList';
import ArticleDetail from './pages/ArticleDetail';
import ComparisonView from './pages/ComparisonView';
import BiasAnalyzer from './pages/BiasAnalyzer';
import ManualScraper from './pages/ManualScraper';

function App() {
  return (
    <div className="App">
      <Navbar />
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/articles" element={<ArticleList />} />
          <Route path="/articles/:id" element={<ArticleDetail />} />
          <Route path="/comparison" element={<ComparisonView />} />
          <Route path="/analyzer" element={<BiasAnalyzer />} />
          <Route path="/scraper" element={<ManualScraper />} />
        </Routes>
      </Container>
    </div>
  );
}

export default App;