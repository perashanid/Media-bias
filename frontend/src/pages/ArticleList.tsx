import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import { Search, Visibility, Analytics, VisibilityOff, Restore } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { articlesApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';
import { useAuth } from '../contexts/AuthContext';

const ArticleList: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [availableSources, setAvailableSources] = useState<string[]>([]);
  const [hiddenArticles, setHiddenArticles] = useState<string[]>([]);
  
  const { isAuthenticated, hideArticle, unhideArticle, getHiddenArticles } = useAuth();

  const articlesPerPage = 12;

  useEffect(() => {
    fetchArticles();
    if (isAuthenticated) {
      loadHiddenArticles();
    }
  }, [page, sourceFilter, isAuthenticated]);

  const loadHiddenArticles = async () => {
    try {
      const hidden = await getHiddenArticles();
      setHiddenArticles(hidden);
    } catch (error) {
      console.error('Failed to load hidden articles:', error);
    }
  };

  const fetchArticles = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        limit: articlesPerPage,
        skip: (page - 1) * articlesPerPage,
        ...(sourceFilter && { source: sourceFilter }),
      };

      const response = await articlesApi.getArticles(params);
      setArticles(response.articles);
      
      // Calculate total pages (this is a rough estimate)
      setTotalPages(Math.ceil(response.count / articlesPerPage) || 1);

      // Extract unique sources for filter
      const sources = Array.from(new Set(response.articles.map((article: Article) => article.source))) as string[];
      setAvailableSources(sources);

    } catch (err) {
      setError('Failed to load articles');
      console.error('Articles error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchArticles();
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await articlesApi.searchArticles(searchQuery, articlesPerPage);
      setArticles(response.articles);
      setTotalPages(1); // Search results are typically single page

    } catch (err) {
      setError('Failed to search articles');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const getBiasLevelColor = (score?: number): 'success' | 'warning' | 'error' | 'default' => {
    if (!score) return 'default';
    if (score < 0.3) return 'success';
    if (score < 0.6) return 'warning';
    return 'error';
  };

  const getBiasLevelLabel = (score?: number): string => {
    if (!score) return 'Not Analyzed';
    if (score < 0.3) return 'Low Bias';
    if (score < 0.6) return 'Moderate Bias';
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
      <Typography variant="h4" gutterBottom>
        News Articles
      </Typography>

      {/* Filters and Search */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              select
              label="Source"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
            >
              <MenuItem value="">All Sources</MenuItem>
              {availableSources.map((source) => (
                <MenuItem key={source} value={source}>
                  {source}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              startIcon={<Search />}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Articles Grid */}
      {!loading && !error && (
        <>
          <Grid container spacing={3}>
            {articles.map((article) => (
              <Grid item xs={12} md={6} lg={4} key={article.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={article.source}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                      <Chip
                        label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                        size="small"
                        color={getBiasLevelColor(article.bias_scores?.overall_bias_score)}
                        sx={{ mb: 1, ml: 1 }}
                      />
                    </Box>

                    <Typography variant="h6" gutterBottom sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}>
                      {article.title}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: 2,
                    }}>
                      {article.content}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Published: {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                      </Typography>
                      {article.author && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          By: {article.author}
                        </Typography>
                      )}
                      <Typography variant="caption" color="text.secondary" display="block">
                        Language: {article.language}
                      </Typography>
                    </Box>

                    {/* Bias Score Preview */}
                    {article.bias_scores && (
                      <Box sx={{ mb: 2 }}>
                        <BiasScoreCard biasScore={article.bias_scores} showDetails={false} />
                      </Box>
                    )}
                  </CardContent>

                  <Box sx={{ p: 2, pt: 0 }}>
                    <Grid container spacing={1} alignItems="center">
                      <Grid item xs={isAuthenticated ? 4 : 6}>
                        <Button
                          fullWidth
                          variant="outlined"
                          size="small"
                          component={Link}
                          to={`/articles/${article.id}`}
                          startIcon={<Visibility />}
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

          {/* Pagination */}
          {articles.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
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
    </Box>
  );
};

export default ArticleList;