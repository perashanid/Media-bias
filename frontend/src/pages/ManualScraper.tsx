import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { ExpandMore, Settings } from '@mui/icons-material';
import { scrapingApi } from '../services/api';
import { useDashboard } from '../contexts/DashboardContext';

interface ScrapingResult {
  success: boolean;
  message?: string;
  article_id?: string;
  title?: string;
  source?: string;
  articles_count?: number;
  analyzed_count?: number;
  source_results?: {
    [source: string]: {
      scraped: number;
      stored: number;
      analyzed: number;
    };
  };
  article?: {
    title: string;
    source: string;
    content_preview: string;
    publication_date?: string;
    language: string;
  };
  bias_analysis?: {
    political_bias: number;
    sentiment_score: number;
    factual_vs_opinion: number;
    overall_bias_score: number;
  };
  error?: string;
}

const ManualScraper: React.FC = () => {
  const { triggerRefresh } = useDashboard();
  const [url, setUrl] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [comprehensiveMode, setComprehensiveMode] = useState(false);
  const [maxArticles, setMaxArticles] = useState(50);
  const [maxDepth, setMaxDepth] = useState(3);
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [testResult, setTestResult] = useState<ScrapingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadAvailableSources = useCallback(async () => {
    try {
      const data = await scrapingApi.getAvailableSources();
      setAvailableSources(data.sources || []);
    } catch (err) {
      console.error('Failed to load sources:', err);
    }
  }, []);

  useEffect(() => {
    loadAvailableSources();
  }, [loadAvailableSources]);

  const handleUrlScrape = async () => {
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await scrapingApi.manualScrape({ url: url.trim() });
      setResult(data);
      if (data.success) {
        triggerRefresh(); // Refresh dashboard after successful scraping
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to scrape URL');
    } finally {
      setLoading(false);
    }
  };

  const handleSourceScrape = async () => {
    if (!selectedSource) {
      setError('Please select a source');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestData: any = { source: selectedSource };
      
      if (comprehensiveMode) {
        requestData.comprehensive = true;
        requestData.max_articles = maxArticles;
        requestData.max_depth = maxDepth;
      }
      
      const data = await scrapingApi.manualScrape(requestData);
      setResult(data);
      if (data.success) {
        triggerRefresh(); // Refresh dashboard after successful scraping
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to scrape source');
    } finally {
      setLoading(false);
    }
  };

  const handleBatchScrape = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await scrapingApi.batchScrape({ max_articles_per_source: 5 });
      setResult(data);
      if (data.success) {
        triggerRefresh(); // Refresh dashboard after successful scraping
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to batch scrape');
    } finally {
      setLoading(false);
    }
  };

  const handleTestUrl = async () => {
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setTestLoading(true);
    setError(null);
    setTestResult(null);

    try {
      const data = await scrapingApi.testUrl(url.trim());
      setTestResult(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to test URL');
    } finally {
      setTestLoading(false);
    }
  };

  const getBiasLabel = (score: number) => {
    if (score < 0.4) return { label: 'Left-leaning', bgcolor: '#1B263B', color: '#E0E1DD' };
    if (score > 0.6) return { label: 'Right-leaning', bgcolor: '#415A77', color: '#E0E1DD' };
    return { label: 'Center', bgcolor: '#778DA9', color: '#0D1B2A' };
  };

  const getSentimentLabel = (score: number) => {
    if (score < 0.4) return { label: 'Negative', bgcolor: '#415A77', color: '#E0E1DD' };
    if (score > 0.6) return { label: 'Positive', bgcolor: '#1B263B', color: '#E0E1DD' };
    return { label: 'Neutral', bgcolor: '#778DA9', color: '#0D1B2A' };
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Manual Article Scraper
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Scrape and analyze articles manually by URL or from available news sources.
      </Typography>

      <Grid container spacing={3}>
        {/* URL Scraping Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Scrape by URL
            </Typography>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Article URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                variant="outlined"
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleUrlScrape}
                disabled={loading || !url.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                {loading ? 'Scraping...' : 'Scrape & Store'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleTestUrl}
                disabled={testLoading || !url.trim()}
                startIcon={testLoading ? <CircularProgress size={20} /> : null}
              >
                {testLoading ? 'Testing...' : 'Test Only'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Source Scraping Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Scrape by Source
            </Typography>
            <Box sx={{ mb: 2 }}>
              <FormControl fullWidth>
                <InputLabel>News Source</InputLabel>
                <Select
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  label="News Source"
                >
                  {availableSources.map((source) => (
                    <MenuItem key={source} value={source}>
                      {source}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            
            {/* Comprehensive Scraping Options */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Settings sx={{ mr: 1 }} />
                <Typography>Advanced Scraping Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <FormControlLabel
                  control={
                    <Switch
                      checked={comprehensiveMode}
                      onChange={(e) => setComprehensiveMode(e.target.checked)}
                    />
                  }
                  label="Comprehensive Scraping (crawl entire website)"
                  sx={{ mb: 2 }}
                />
                
                {comprehensiveMode && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Comprehensive scraping will crawl the entire website by following all links to find and scrape articles.
                      This may take significantly longer but will find more articles.
                    </Typography>
                    
                    <Typography gutterBottom>
                      Maximum Articles: {maxArticles}
                    </Typography>
                    <Slider
                      value={maxArticles}
                      onChange={(_, value) => setMaxArticles(value as number)}
                      min={10}
                      max={200}
                      step={10}
                      marks={[
                        { value: 10, label: '10' },
                        { value: 50, label: '50' },
                        { value: 100, label: '100' },
                        { value: 200, label: '200' }
                      ]}
                      sx={{ mb: 3 }}
                    />
                    
                    <Typography gutterBottom>
                      Crawling Depth: {maxDepth}
                    </Typography>
                    <Slider
                      value={maxDepth}
                      onChange={(_, value) => setMaxDepth(value as number)}
                      min={1}
                      max={5}
                      step={1}
                      marks={[
                        { value: 1, label: '1' },
                        { value: 2, label: '2' },
                        { value: 3, label: '3' },
                        { value: 4, label: '4' },
                        { value: 5, label: '5' }
                      ]}
                      sx={{ mb: 2 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      Higher depth means following more links but takes longer
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                onClick={handleSourceScrape}
                disabled={loading || !selectedSource}
                startIcon={loading ? <CircularProgress size={20} /> : null}
                sx={{ flex: 1 }}
              >
                {loading ? (comprehensiveMode ? 'Crawling...' : 'Scraping...') : 
                 (comprehensiveMode ? 'Comprehensive Scrape' : 'Scrape Source')}
              </Button>
              <Button
                variant="outlined"
                onClick={handleBatchScrape}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : null}
                sx={{ flex: 1 }}
              >
                {loading ? 'Scraping...' : 'Scrape All'}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Scraping Result */}
      {result && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Scraping Result
          </Typography>
          {result.success ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              {result.message}
            </Alert>
          ) : (
            <Alert severity="error" sx={{ mb: 2 }}>
              {result.error || 'Scraping failed'}
            </Alert>
          )}
          
          {result.success && result.title && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                <strong>Title:</strong> {result.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Source:</strong> {result.source}
              </Typography>
              {result.article_id && (
                <Typography variant="body2" color="text.secondary">
                  <strong>Article ID:</strong> {result.article_id}
                </Typography>
              )}
              {result.articles_count && (
                <Typography variant="body2" color="text.secondary">
                  <strong>Articles Scraped:</strong> {result.articles_count}
                </Typography>
              )}
              {result.analyzed_count && (
                <Typography variant="body2" color="text.secondary">
                  <strong>Articles Analyzed:</strong> {result.analyzed_count}
                </Typography>
              )}
              {result.source_results && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    <strong>Source Results:</strong>
                  </Typography>
                  {Object.entries(result.source_results).map(([source, stats]: [string, any]) => (
                    <Typography key={source} variant="body2" color="text.secondary">
                      {source}: {stats.scraped} scraped, {stats.stored} stored, {stats.analyzed} analyzed
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Paper>
      )}

      {/* Test Result */}
      {testResult && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            URL Test Result
          </Typography>
          {testResult.success ? (
            <>
              <Alert severity="info" sx={{ mb: 2 }}>
                Article content extracted successfully (not stored)
              </Alert>
              
              {testResult.article && (
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {testResult.article.title}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Chip 
                        label={testResult.article.source} 
                        size="small" 
                        sx={{ mr: 1 }} 
                      />
                      <Chip 
                        label={testResult.article.language} 
                        size="small" 
                        sx={{ bgcolor: '#1B263B', color: '#E0E1DD' }} 
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {testResult.article.content_preview}
                    </Typography>
                    {testResult.article.publication_date && (
                      <Typography variant="caption" color="text.secondary">
                        Published: {new Date(testResult.article.publication_date).toLocaleDateString()}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              )}

              {testResult.bias_analysis && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Bias Analysis Preview
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      <Chip
                        label={`Political: ${getBiasLabel(testResult.bias_analysis.political_bias).label}`}
                        size="small"
                        sx={{
                          bgcolor: getBiasLabel(testResult.bias_analysis.political_bias).bgcolor,
                          color: getBiasLabel(testResult.bias_analysis.political_bias).color
                        }}
                      />
                      <Chip
                        label={`Sentiment: ${getSentimentLabel(testResult.bias_analysis.sentiment_score).label}`}
                        size="small"
                        sx={{
                          bgcolor: getSentimentLabel(testResult.bias_analysis.sentiment_score).bgcolor,
                          color: getSentimentLabel(testResult.bias_analysis.sentiment_score).color
                        }}
                      />
                      <Chip
                        label={`Factual: ${(testResult.bias_analysis.factual_vs_opinion * 100).toFixed(0)}%`}
                        color="info"
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Overall Bias Score: {(testResult.bias_analysis.overall_bias_score * 100).toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Alert severity="error">
              {testResult.error || 'URL test failed'}
            </Alert>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default ManualScraper;