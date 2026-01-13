import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  TextField,
  MenuItem,
  Pagination,
  CircularProgress,
  Alert,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Fab,
  Badge,
  Divider,
  Paper,
  Container,
  Avatar,
} from '@mui/material';
import { 
  Search, 
  Visibility, 
  Analytics, 
  Compare,
  FilterList,
  Clear,
  CheckBox,
  CheckBoxOutlineBlank,
  CalendarMonth,
  TrendingUp,
  AutoAwesome,
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { articlesApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';


const ArticleList: React.FC = () => {
  const navigate = useNavigate();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [topicFilter, setTopicFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [biasFilter, setBiasFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalArticles, setTotalArticles] = useState(0);
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const [selectedArticles, setSelectedArticles] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [comparing, setComparing] = useState(false);
  


  const articlesPerPage = 15;



  const fetchAvailableTopics = useCallback(async () => {
    try {
      const response = await articlesApi.getAvailableTopics();
      setAvailableTopics(response.topics || []);
    } catch (error) {
      console.error('Failed to fetch available topics:', error);
    }
  }, []);

  const fetchArticles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        limit: articlesPerPage,
        skip: (page - 1) * articlesPerPage,
      };

      // Add filters
      if (sourceFilter) params.source = sourceFilter;
      if (topicFilter) params.topic = topicFilter;

      const response = await articlesApi.getArticles(params);
      let filteredArticles = response.articles;

      if (languageFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => 
          article.language?.toLowerCase() === languageFilter.toLowerCase()
        );
      }

      if (biasFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => {
          if (!article.bias_scores?.overall_bias_score) return false;
          const score = article.bias_scores.overall_bias_score;
          switch (biasFilter) {
            case 'low': return score < 0.4;
            case 'moderate': return score >= 0.4 && score < 0.7;
            case 'high': return score >= 0.7;
            default: return true;
          }
        });
      }

      setArticles(filteredArticles);
      
      // Use server-provided total count for pagination
      const totalCount = response.total_count || response.count || filteredArticles.length;
      setTotalArticles(totalCount);
      
      // Calculate total pages based on actual total count
      let calculatedPages = Math.ceil(totalCount / articlesPerPage);
      
      // Ensure we always have at least 1 page if there are articles
      if (filteredArticles.length > 0 && calculatedPages === 0) {
        calculatedPages = 1;
      }
      
      // If we have a full page of articles but no total count, estimate there might be more
      if (!response.total_count && filteredArticles.length === articlesPerPage && response.has_more !== false) {
        // Estimate there are more pages available
        const estimatedTotal = Math.max(totalCount, (page * articlesPerPage) + 1);
        setTotalArticles(estimatedTotal);
        calculatedPages = Math.ceil(estimatedTotal / articlesPerPage);
      }
      
      setTotalPages(calculatedPages);
      
      // Debug logging
      console.log('Pagination Debug:', {
        totalCount,
        articlesPerPage,
        calculatedPages,
        currentPage: page,
        responseCount: response.count,
        responseTotalCount: response.total_count,
        hasMore: response.has_more,
        articlesLength: filteredArticles.length
      });

      // Extract unique sources for filters
      const sources = Array.from(new Set(response.articles.map((article: Article) => article.source))) as string[];
      setAvailableSources(sources);

    } catch (err) {
      setError('Failed to load articles');
      console.error('Articles error:', err);
    } finally {
      setLoading(false);
    }
  }, [page, sourceFilter, topicFilter, languageFilter, biasFilter, articlesPerPage]);

  useEffect(() => {
    fetchAvailableTopics();
    fetchArticles();
  }, [fetchAvailableTopics, fetchArticles]);

  // Multi-select handlers
  const handleSelectArticle = (articleId: string) => {
    const newSelected = new Set(selectedArticles);
    if (newSelected.has(articleId)) {
      newSelected.delete(articleId);
    } else {
      newSelected.add(articleId);
    }
    setSelectedArticles(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedArticles.size === articles.length) {
      setSelectedArticles(new Set());
    } else {
      setSelectedArticles(new Set(articles.map(article => article.id)));
    }
  };

  const handleClearSelection = () => {
    setSelectedArticles(new Set());
  };

  const handleCompareSelected = async () => {
    if (selectedArticles.size < 2) {
      setError('Please select at least 2 articles to compare');
      return;
    }

    if (selectedArticles.size > 5) {
      setError('Please select no more than 5 articles to compare');
      return;
    }

    setComparing(true);
    try {
      // Navigate to comparison page with selected articles
      const articleIds = Array.from(selectedArticles);
      const params = new URLSearchParams();
      params.set('articles', articleIds.join(','));
      navigate(`/comparison?${params.toString()}`);
    } catch (err) {
      setError('Failed to create comparison');
      console.error('Comparison error:', err);
    } finally {
      setComparing(false);
    }
  };

  const clearAllFilters = () => {
    setSourceFilter('');
    setTopicFilter('');
    setLanguageFilter('');
    setBiasFilter('');
    setSearchQuery('');
    setPage(1);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchArticles();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setPage(1); // Reset to first page for search

      const response = await articlesApi.searchArticles(searchQuery, articlesPerPage * 5); // Get more results for search
      let filteredArticles = response.articles;

      // Apply client-side filters for features not supported by search API
      if (sourceFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => article.source === sourceFilter);
      }
      if (topicFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => 
          article.topics?.includes(topicFilter) ||
          article.title.toLowerCase().includes(topicFilter.toLowerCase()) ||
          article.content.toLowerCase().includes(topicFilter.toLowerCase())
        );
      }
      if (languageFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => 
          article.language?.toLowerCase() === languageFilter.toLowerCase()
        );
      }
      if (biasFilter) {
        filteredArticles = filteredArticles.filter((article: Article) => {
          if (!article.bias_scores?.overall_bias_score) return false;
          const score = article.bias_scores.overall_bias_score;
          switch (biasFilter) {
            case 'low': return score < 0.4;
            case 'moderate': return score >= 0.4 && score < 0.7;
            case 'high': return score >= 0.7;
            default: return true;
          }
        });
      }

      setArticles(filteredArticles);
      setTotalArticles(filteredArticles.length);
      setTotalPages(Math.ceil(filteredArticles.length / articlesPerPage) || 1);

    } catch (err) {
      setError('Failed to search articles');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    setSelectedArticles(new Set()); // Clear selection when changing pages
  };

  const getBiasLevelColor = (score?: number): 'success' | 'warning' | 'error' | 'default' => {
    if (!score) return 'default';
    if (score < 0.4) return 'success';
    if (score < 0.7) return 'warning';
    return 'error';
  };

  const getBiasLevelLabel = (score?: number): string => {
    if (!score) return 'Not Analyzed';
    if (score < 0.4) return 'Low Bias';
    if (score < 0.7) return 'Moderate Bias';
    return 'High Bias';
  };



  return (
    <Box sx={{ minHeight: '100vh', pt: 12, pb: 8 }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: '#0f172a',
          py: { xs: 6, md: 8 },
          mb: 6,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background decoration */}
        <Box
          sx={{
            position: 'absolute',
            top: '-50%',
            right: '-20%',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: '#4f46e5',
            filter: 'blur(100px)',
            opacity: 0.12,
          }}
        />
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 'var(--radius-lg)',
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AutoAwesome sx={{ color: '#fbbf24', fontSize: 28 }} />
            </Box>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                color: '#ffffff',
                fontSize: { xs: '2rem', md: '2.5rem' },
                letterSpacing: '-0.02em',
              }}
            >
              News Articles
            </Typography>
          </Box>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: 400,
              maxWidth: 600,
            }}
          >
            Explore and analyze articles from Bangladesh's leading news sources. 
            Filter, search, and compare coverage across outlets.
          </Typography>

          {/* Quick Stats */}
          <Box sx={{ display: 'flex', gap: 4, mt: 4, flexWrap: 'wrap' }}>
            {[
              { value: totalArticles, label: 'Total Articles' },
              { value: availableSources.length, label: 'Sources' },
              { value: selectedArticles.size, label: 'Selected' },
            ].map((stat, index) => (
              <Box key={index}>
                <Typography
                  variant="h4"
                  sx={{ fontWeight: 800, color: '#ffffff' }}
                >
                  {stat.value.toLocaleString()}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{ color: 'rgba(255, 255, 255, 0.6)', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                >
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Enhanced Filters and Search */}
        <Paper
          sx={{
            p: 4,
            mb: 4,
            borderRadius: 'var(--radius-2xl)',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-lg)',
          }}
        >
        {/* Search and Basic Filters */}
        <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search articles by title or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: 'var(--color-text-muted)' }} />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 'var(--radius-xl)',
                  backgroundColor: 'var(--color-background)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: 'var(--color-primary-300)',
                  },
                  '&.Mui-focused': {
                    boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.15)',
                  },
                }
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              select
              label="Source"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 'var(--radius-xl)',
                  backgroundColor: 'var(--color-background)',
                }
              }}
            >
              <MenuItem value="">All Sources</MenuItem>
              {availableSources.map((source) => (
                <MenuItem key={source} value={source}>
                  {source}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => setShowFilters(!showFilters)}
              startIcon={<FilterList />}
              sx={{ 
                py: 1.75,
                borderRadius: 'var(--radius-xl)',
                borderColor: 'var(--color-border)',
                color: 'var(--color-text-secondary)',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': {
                  borderColor: 'var(--color-primary-500)',
                  backgroundColor: 'var(--color-primary-50)',
                },
              }}
            >
              {showFilters ? 'Hide' : 'More'} Filters
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              startIcon={<Search />}
              sx={{ 
                py: 1.75,
                borderRadius: 'var(--radius-xl)',
                background: '#4f46e5',
                fontWeight: 600,
                textTransform: 'none',
                boxShadow: '0 2px 8px rgba(79, 70, 229, 0.25)',
                '&:hover': {
                  background: '#4338ca',
                  boxShadow: '0 4px 12px rgba(79, 70, 229, 0.35)',
                  transform: 'translateY(-1px)',
                },
              }}
            >
              Search
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="text"
              onClick={clearAllFilters}
              startIcon={<Clear />}
              sx={{ 
                py: 1.75,
                borderRadius: 'var(--radius-xl)',
                color: 'var(--color-text-muted)',
                fontWeight: 500,
                textTransform: 'none',
                '&:hover': {
                  color: 'var(--color-error)',
                  backgroundColor: 'rgba(239, 68, 68, 0.1)',
                },
              }}
            >
              Clear All
            </Button>
          </Grid>
        </Grid>

        {/* Advanced Filters */}
        {showFilters && (
          <>
            <Divider sx={{ mb: 3 }} />
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  select
                  label="Language"
                  value={languageFilter}
                  onChange={(e) => setLanguageFilter(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  <MenuItem value="">All Languages</MenuItem>
                  <MenuItem value="bengali">Bengali</MenuItem>
                  <MenuItem value="english">English</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  select
                  label="Bias Level"
                  value={biasFilter}
                  onChange={(e) => setBiasFilter(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  <MenuItem value="">All Bias Levels</MenuItem>
                  <MenuItem value="low">Low Bias</MenuItem>
                  <MenuItem value="moderate">Moderate Bias</MenuItem>
                  <MenuItem value="high">High Bias</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  select
                  label="Topic"
                  value={topicFilter}
                  onChange={(e) => setTopicFilter(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  <MenuItem value="">All Topics</MenuItem>
                  {availableTopics.map((topic) => (
                    <MenuItem key={topic} value={topic}>
                      {topic.charAt(0).toUpperCase() + topic.slice(1)}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">
                    {totalArticles} articles found
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </>
        )}

        {/* Multi-select Controls */}
        {selectedArticles.size > 0 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {selectedArticles.size} article{selectedArticles.size !== 1 ? 's' : ''} selected
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleClearSelection}
                startIcon={<Clear />}
              >
                Clear Selection
              </Button>
              <Button
                variant="contained"
                size="small"
                onClick={handleCompareSelected}
                disabled={selectedArticles.size < 2 || comparing}
                startIcon={comparing ? <CircularProgress size={16} /> : <Compare />}
              >
                {comparing ? 'Creating Comparison...' : `Compare Selected (${selectedArticles.size})`}
              </Button>
            </Box>
          </>
        )}
      </Paper>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Select All Controls */}
      {!loading && !error && articles.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={selectedArticles.size === articles.length && articles.length > 0}
                indeterminate={selectedArticles.size > 0 && selectedArticles.size < articles.length}
                onChange={handleSelectAll}
                icon={<CheckBoxOutlineBlank />}
                checkedIcon={<CheckBox />}
              />
            }
            label={`Select All (${articles.length} articles)`}
          />
          <Typography variant="body2" color="text.secondary">
            Page {page} of {totalPages} • {totalArticles} total articles
          </Typography>
        </Box>
      )}

      {/* Articles Grid */}
      {!loading && !error && (
        <>
          <Grid container spacing={3}>
            {articles.map((article, index) => (
              <Grid item xs={12} md={6} lg={4} key={article.id}>
                <Card 
                  className="card-modern"
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    border: selectedArticles.has(article.id) ? '2px solid var(--color-primary-500)' : '1px solid var(--color-border)',
                    bgcolor: selectedArticles.has(article.id) ? 'var(--color-primary-50)' : 'var(--color-surface)',
                    borderRadius: 'var(--radius-2xl)',
                    overflow: 'hidden',
                    position: 'relative',
                    animation: `fadeInUp 0.5s ease ${index * 0.05}s both`,
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 'var(--shadow-xl)',
                    },
                    '&:hover .card-gradient-bar': {
                      transform: 'scaleX(1)',
                    },
                  }}
                >
                  {/* Gradient top bar */}
                  <Box
                    className="card-gradient-bar"
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 4,
                      background: article.bias_scores?.overall_bias_score 
                        ? article.bias_scores.overall_bias_score < 0.4 
                          ? '#10b981'
                          : article.bias_scores.overall_bias_score < 0.7
                            ? '#f59e0b'
                            : '#ef4444'
                        : '#4f46e5',
                      transform: 'scaleX(0)',
                      transformOrigin: 'left',
                      transition: 'transform 0.4s ease',
                    }}
                  />

                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    {/* Header with chips and checkbox */}
                    <Box sx={{ mb: 3, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        <Chip
                          avatar={
                            <Avatar sx={{ bgcolor: 'var(--color-primary-500) !important', width: 24, height: 24, fontSize: '0.7rem' }}>
                              {article.source?.substring(0, 2).toUpperCase()}
                            </Avatar>
                          }
                          label={article.source}
                          size="small"
                          sx={{ 
                            fontWeight: 600,
                            borderRadius: 'var(--radius-lg)',
                            bgcolor: 'var(--color-primary-50)',
                            color: 'var(--color-primary-700)',
                          }}
                        />
                        <Chip
                          icon={<TrendingUp sx={{ fontSize: 14 }} />}
                          label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                          size="small"
                          sx={{
                            fontWeight: 600,
                            borderRadius: 'var(--radius-lg)',
                            bgcolor: article.bias_scores?.overall_bias_score
                              ? article.bias_scores.overall_bias_score < 0.4
                                ? 'rgba(16, 185, 129, 0.1)'
                                : article.bias_scores.overall_bias_score < 0.7
                                  ? 'rgba(245, 158, 11, 0.1)'
                                  : 'rgba(239, 68, 68, 0.1)'
                              : 'var(--color-surface-elevated)',
                            color: article.bias_scores?.overall_bias_score
                              ? article.bias_scores.overall_bias_score < 0.4
                                ? 'var(--color-success)'
                                : article.bias_scores.overall_bias_score < 0.7
                                  ? 'var(--color-warning)'
                                  : 'var(--color-error)'
                              : 'var(--color-text-muted)',
                          }}
                        />
                      </Box>
                      <Checkbox
                        checked={selectedArticles.has(article.id)}
                        onChange={() => handleSelectArticle(article.id)}
                        size="small"
                        icon={<CheckBoxOutlineBlank sx={{ color: 'var(--color-border)' }} />}
                        checkedIcon={<CheckBox sx={{ color: 'var(--color-primary-500)' }} />}
                        sx={{ p: 0.5 }}
                      />
                    </Box>

                    {/* Title */}
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        fontWeight: 700,
                        lineHeight: 1.4,
                        mb: 2,
                        fontSize: '1rem',
                        color: 'var(--color-text)',
                      }}
                    >
                      {article.title}
                    </Typography>

                    {/* Content preview */}
                    <Typography 
                      variant="body2" 
                      sx={{
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        mb: 3,
                        lineHeight: 1.7,
                        color: 'var(--color-text-secondary)',
                      }}
                    >
                      {article.content}
                    </Typography>

                    {/* Meta info */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <CalendarMonth sx={{ fontSize: 16, color: 'var(--color-text-muted)' }} />
                        <Typography variant="caption" sx={{ color: 'var(--color-text-muted)' }}>
                          {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                        </Typography>
                      </Box>
                      <Chip
                        label={article.language}
                        size="small"
                        variant="outlined"
                        sx={{ 
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.65rem',
                          height: 20,
                          borderColor: 'var(--color-border)',
                          color: 'var(--color-text-muted)',
                        }}
                      />
                    </Box>

                    {/* Bias Score Preview */}
                    {article.bias_scores && (
                      <Box sx={{ mb: 2 }}>
                        <BiasScoreCard biasScore={article.bias_scores} showDetails={false} />
                      </Box>
                    )}
                  </CardContent>

                  {/* Actions */}
                  <Box sx={{ p: 3, pt: 0 }}>
                    <Grid container spacing={1.5}>
                      <Grid item xs={6}>
                        <Button
                          fullWidth
                          variant="contained"
                          size="small"
                          component={Link}
                          to={`/articles/${article.id}`}
                          startIcon={<Visibility />}
                          sx={{ 
                            borderRadius: 'var(--radius-lg)',
                            py: 1,
                            background: '#4f46e5',
                            fontWeight: 600,
                            textTransform: 'none',
                            boxShadow: 'none',
                            '&:hover': {
                              background: '#4338ca',
                              boxShadow: '0 2px 8px rgba(79, 70, 229, 0.25)',
                            },
                          }}
                        >
                          View
                        </Button>
                      </Grid>
                      <Grid item xs={6}>
                        <Button
                          fullWidth
                          variant="outlined"
                          size="small"
                          component={Link}
                          to={`/comparison?article=${article.id}`}
                          startIcon={<Analytics />}
                          sx={{ 
                            borderRadius: 'var(--radius-lg)',
                            py: 1,
                            borderColor: 'var(--color-border)',
                            color: 'var(--color-text-secondary)',
                            fontWeight: 600,
                            textTransform: 'none',
                            '&:hover': {
                              borderColor: 'var(--color-primary-500)',
                              color: 'var(--color-primary-600)',
                              bgcolor: 'var(--color-primary-50)',
                            },
                          }}
                        >
                          Compare
                        </Button>
                      </Grid>
                    </Grid>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {!loading && articles.length > 0 && (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              mt: 6, 
              mb: 4,
              p: 4,
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-2xl)',
              border: '1px solid var(--color-border)',
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap', justifyContent: 'center' }}>
                <Typography variant="body2" sx={{ color: 'var(--color-text-secondary)', fontWeight: 500 }}>
                  Page {page} of {totalPages} • {totalArticles.toLocaleString()} total articles
                </Typography>
                
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={handlePageChange}
                  showFirstButton
                  showLastButton
                  sx={{
                    '& .MuiPaginationItem-root': {
                      color: 'var(--color-text)',
                      borderRadius: 'var(--radius-lg)',
                      fontWeight: 500,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: 'var(--color-primary-50)',
                        color: 'var(--color-primary-600)',
                        transform: 'translateY(-1px)',
                      },
                      '&.Mui-selected': {
                        background: '#4f46e5',
                        color: '#ffffff',
                        boxShadow: '0 2px 8px rgba(79, 70, 229, 0.25)',
                        '&:hover': {
                          background: '#4338ca',
                          opacity: 0.9,
                        }
                      },
                    }
                  }}
                />
              </Box>
            </Box>
          )}

          {/* No Results */}
          {articles.length === 0 && !loading && (
            <Box 
              sx={{ 
                textAlign: 'center', 
                py: 12,
                px: 4,
                background: 'var(--color-surface)',
                borderRadius: 'var(--radius-2xl)',
                border: '1px solid var(--color-border)',
              }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: 'var(--color-surface-elevated)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                }}
              >
                <Search sx={{ fontSize: 40, color: 'var(--color-text-muted)' }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, color: 'var(--color-text)' }}>
                No articles found
              </Typography>
              <Typography variant="body1" sx={{ color: 'var(--color-text-secondary)', mb: 4 }}>
                Try adjusting your search criteria or filters
              </Typography>
              <Button
                variant="contained"
                onClick={clearAllFilters}
                sx={{
                  background: '#4f46e5',
                  borderRadius: 'var(--radius-xl)',
                  px: 4,
                  py: 1.5,
                  fontWeight: 600,
                  textTransform: 'none',
                  '&:hover': { background: '#4338ca' },
                }}
              >
                Clear All Filters
              </Button>
            </Box>
          )}
        </>
      )}

      {/* Floating Action Button for Comparison */}
      {selectedArticles.size >= 2 && (
        <Fab
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            zIndex: 1000,
            background: '#4f46e5',
            boxShadow: '0 4px 16px rgba(79, 70, 229, 0.35)',
            '&:hover': {
              background: '#4338ca',
              transform: 'scale(1.05)',
              boxShadow: '0 6px 20px rgba(79, 70, 229, 0.45)',
            },
          }}
          onClick={handleCompareSelected}
          disabled={comparing}
        >
          <Badge 
            badgeContent={selectedArticles.size} 
            sx={{
              '& .MuiBadge-badge': {
                background: 'var(--color-accent-500)',
                color: '#ffffff',
                fontWeight: 700,
              }
            }}
          >
            {comparing ? <CircularProgress size={24} color="inherit" /> : <Compare sx={{ color: '#ffffff' }} />}
          </Badge>
        </Fab>
      )}
      </Container>
    </Box>
  );
};

export default ArticleList;