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
  IconButton,
  Tooltip,
  Checkbox,
  FormControlLabel,
  Fab,
  Badge,
  Divider,
  Paper,
} from '@mui/material';
import { 
  Search, 
  Visibility, 
  Analytics, 
  VisibilityOff, 
  Restore, 
  Compare,
  FilterList,
  Clear,
  CheckBox,
  CheckBoxOutlineBlank
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { articlesApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';
import { useAuth } from '../contexts/AuthContext';

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
  const [hiddenArticles, setHiddenArticles] = useState<string[]>([]);
  const [selectedArticles, setSelectedArticles] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [comparing, setComparing] = useState(false);
  
  const { isAuthenticated, hideArticle, unhideArticle, getHiddenArticles } = useAuth();

  const articlesPerPage = 15;

  const loadHiddenArticles = useCallback(async () => {
    try {
      const hidden = await getHiddenArticles();
      setHiddenArticles(hidden);
    } catch (error) {
      console.error('Failed to load hidden articles:', error);
    }
  }, [getHiddenArticles]);

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
    if (isAuthenticated) {
      loadHiddenArticles();
    }
  }, [fetchAvailableTopics, fetchArticles, loadHiddenArticles, isAuthenticated]);

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

  const handleHideArticle = async (articleId: string) => {
    try {
      const success = await hideArticle(articleId);
      if (success) {
        setHiddenArticles([...hiddenArticles, articleId]);
      }
    } catch (error) {
      console.error('Failed to hide article:', error);
    }
  };

  const handleUnhideArticle = async (articleId: string) => {
    try {
      const success = await unhideArticle(articleId);
      if (success) {
        setHiddenArticles(hiddenArticles.filter(id => id !== articleId));
      }
    } catch (error) {
      console.error('Failed to unhide article:', error);
    }
  };

  const isArticleHidden = (articleId: string) => {
    return hiddenArticles.includes(articleId);
  };

  return (
    <Box>
      <Typography variant="h2" gutterBottom sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
        News Articles
      </Typography>

      {/* Enhanced Filters and Search */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        {/* Search and Basic Filters */}
        <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
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
                  borderRadius: 2,
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
                py: 1.5,
                borderRadius: 2,
              }}
            >
              More Filters
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              startIcon={<Search />}
              sx={{ 
                py: 1.5,
                borderRadius: 2,
              }}
            >
              Search
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              onClick={clearAllFilters}
              startIcon={<Clear />}
              sx={{ 
                py: 1.5,
                borderRadius: 2,
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
          <Grid container spacing={4}>
            {articles.map((article) => (
              <Grid item xs={12} md={6} lg={4} key={article.id}>
                <Card sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'all 0.3s ease',
                  border: selectedArticles.has(article.id) ? '2px solid' : '1px solid',
                  borderColor: selectedArticles.has(article.id) ? 'primary.main' : 'grey.200',
                  bgcolor: selectedArticles.has(article.id) ? 'action.selected' : 'background.paper',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
                  }
                }}>
                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        <Chip
                          label={article.source}
                          size="small"
                          color="primary"
                          sx={{ fontWeight: 500 }}
                        />
                        <Chip
                          label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                          size="small"
                          color={getBiasLevelColor(article.bias_scores?.overall_bias_score)}
                          sx={{ fontWeight: 500 }}
                        />
                        {article.topics && article.topics.length > 0 && (
                          <Chip
                            label={article.topics[0].charAt(0).toUpperCase() + article.topics[0].slice(1)}
                            size="small"
                            variant="outlined"
                            color="info"
                            sx={{ fontWeight: 500 }}
                          />
                        )}
                      </Box>
                      <Checkbox
                        checked={selectedArticles.has(article.id)}
                        onChange={() => handleSelectArticle(article.id)}
                        size="small"
                        icon={<CheckBoxOutlineBlank />}
                        checkedIcon={<CheckBox />}
                        sx={{ p: 0.5 }}
                      />
                    </Box>

                    <Typography variant="h6" gutterBottom sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      fontWeight: 600,
                      lineHeight: 1.4,
                      mb: 2,
                    }}>
                      {article.title}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: 3,
                      lineHeight: 1.6,
                    }}>
                      {article.content}
                    </Typography>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                        {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                      </Typography>
                      {article.author && (
                        <Typography variant="body2" color="text.secondary">
                          By {article.author}
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary">
                        {article.language}
                      </Typography>
                    </Box>

                    {/* Bias Score Preview */}
                    {article.bias_scores && (
                      <Box sx={{ mb: 2 }}>
                        <BiasScoreCard biasScore={article.bias_scores} showDetails={false} />
                      </Box>
                    )}
                  </CardContent>

                  <Box sx={{ p: 3, pt: 0 }}>
                    <Grid container spacing={1.5} alignItems="center">
                      <Grid item xs={isAuthenticated ? 4 : 6}>
                        <Button
                          fullWidth
                          variant="contained"
                          size="small"
                          component={Link}
                          to={`/articles/${article.id}`}
                          startIcon={<Visibility />}
                          sx={{ borderRadius: 2 }}
                        >
                          View
                        </Button>
                      </Grid>
                      <Grid item xs={isAuthenticated ? 4 : 6}>
                        <Button
                          fullWidth
                          variant="outlined"
                          size="small"
                          component={Link}
                          to={`/comparison?article=${article.id}`}
                          startIcon={<Analytics />}
                          sx={{ borderRadius: 2 }}
                        >
                          Compare
                        </Button>
                      </Grid>
                      {isAuthenticated && (
                        <Grid item xs={4}>
                          <Tooltip title={isArticleHidden(article.id) ? "Unhide article" : "Hide article"}>
                            <IconButton
                              size="small"
                              onClick={() => 
                                isArticleHidden(article.id) 
                                  ? handleUnhideArticle(article.id)
                                  : handleHideArticle(article.id)
                              }
                              color={isArticleHidden(article.id) ? "warning" : "default"}
                              sx={{ 
                                borderRadius: 2,
                                border: '1px solid',
                                borderColor: isArticleHidden(article.id) ? 'warning.main' : 'grey.300',
                              }}
                            >
                              {isArticleHidden(article.id) ? <Restore /> : <VisibilityOff />}
                            </IconButton>
                          </Tooltip>
                        </Grid>
                      )}
                    </Grid>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination - Always show for navigation */}
          {!loading && articles.length > 0 && (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              mt: 4, 
              mb: 4,
              p: 3,
              bgcolor: '#E0E1DD',
              borderRadius: 2,
              border: '1px solid #778DA9'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
                <Typography variant="body2" sx={{ color: '#0D1B2A', fontWeight: 500 }}>
                  Page {page} of {totalPages} ({totalArticles} total articles)
                </Typography>
                
                {/* Always show pagination controls for navigation */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handlePageChange(null as any, Math.max(1, page - 1))}
                    disabled={page <= 1}
                    sx={{
                      minWidth: '80px',
                      color: '#0D1B2A',
                      borderColor: '#778DA9',
                      '&:hover': {
                        bgcolor: '#778DA9',
                        color: '#E0E1DD'
                      },
                      '&.Mui-disabled': {
                        color: '#778DA9',
                        borderColor: '#778DA9',
                        opacity: 0.5
                      }
                    }}
                  >
                    Previous
                  </Button>
                  
                  <Typography variant="body2" sx={{ 
                    color: '#1B263B', 
                    fontWeight: 600,
                    mx: 2,
                    minWidth: '60px',
                    textAlign: 'center'
                  }}>
                    {page} / {totalPages}
                  </Typography>
                  
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handlePageChange(null as any, Math.min(totalPages, page + 1))}
                    disabled={page >= totalPages}
                    sx={{
                      minWidth: '80px',
                      color: '#0D1B2A',
                      borderColor: '#778DA9',
                      '&:hover': {
                        bgcolor: '#778DA9',
                        color: '#E0E1DD'
                      },
                      '&.Mui-disabled': {
                        color: '#778DA9',
                        borderColor: '#778DA9',
                        opacity: 0.5
                      }
                    }}
                  >
                    Next
                  </Button>
                </Box>

                {/* Show full pagination for multiple pages */}
                {totalPages > 3 && (
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={handlePageChange}
                    showFirstButton
                    showLastButton
                    size="small"
                    sx={{
                      '& .MuiPaginationItem-root': {
                        color: '#0D1B2A',
                        borderColor: '#778DA9',
                        fontWeight: 500,
                        '&:hover': {
                          bgcolor: '#778DA9',
                          color: '#E0E1DD'
                        },
                        '&.Mui-selected': {
                          bgcolor: '#1B263B',
                          color: '#E0E1DD',
                          '&:hover': {
                            bgcolor: '#415A77'
                          }
                        }
                      }
                    }}
                  />
                )}
                
                {totalPages === 1 && (
                  <Typography variant="body2" sx={{ color: '#415A77', fontStyle: 'italic' }}>
                    All articles shown
                  </Typography>
                )}
              </Box>
            </Box>
          )}

          {/* No Results */}
          {articles.length === 0 && !loading && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No articles found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your search criteria or filters
              </Typography>
            </Box>
          )}
        </>
      )}

      {/* Floating Action Button for Comparison */}
      {selectedArticles.size >= 2 && (
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
          }}
          onClick={handleCompareSelected}
          disabled={comparing}
        >
          <Badge badgeContent={selectedArticles.size} color="secondary">
            {comparing ? <CircularProgress size={24} color="inherit" /> : <Compare />}
          </Badge>
        </Fab>
      )}
    </Box>
  );
};

export default ArticleList;