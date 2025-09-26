import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  Grid,
  Divider,
  CircularProgress,
  Alert,
  Paper,
} from '@mui/material';
import { ArrowBack, Compare, OpenInNew } from '@mui/icons-material';
import { format } from 'date-fns';
import { articlesApi, comparisonApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';

const ArticleDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [similarArticles, setSimilarArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  useEffect(() => {
    if (id) {
      fetchArticle(id);
      fetchSimilarArticles(id);
    }
  }, [id]);

  const fetchArticle = async (articleId: string) => {
    try {
      setLoading(true);
      setError(null);

      const articleData = await articlesApi.getArticle(articleId);
      setArticle(articleData);

    } catch (err) {
      setError('Failed to load article');
      console.error('Article detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilarArticles = async (articleId: string) => {
    try {
      setLoadingSimilar(true);

      const response = await comparisonApi.getSimilarArticles(articleId, 0.3);
      setSimilarArticles(response.related_articles || []);

    } catch (err) {
      console.error('Similar articles error:', err);
    } finally {
      setLoadingSimilar(false);
    }
  };

  const handleAnalyzeBias = async () => {
    if (!article) return;

    try {
      setLoading(true);
      await articlesApi.analyzeArticleBias(article.id);
      
      // Refresh article data to get updated bias scores
      await fetchArticle(article.id);

    } catch (err) {
      setError('Failed to analyze bias');
      console.error('Bias analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!article) {
    return <Alert severity="warning">Article not found</Alert>;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button
          component={Link}
          to="/articles"
          startIcon={<ArrowBack />}
          sx={{ mb: 2 }}
        >
          Back to Articles
        </Button>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h4" gutterBottom>
              {article.title}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              <Button
                variant="outlined"
                component={Link}
                to={`/comparison?article=${article.id}`}
                startIcon={<Compare />}
              >
                Compare
              </Button>
              <Button
                variant="outlined"
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                startIcon={<OpenInNew />}
              >
                Original
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {/* Article Content */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              {/* Article Metadata */}
              <Box sx={{ mb: 3 }}>
                <Grid container spacing={1} sx={{ mb: 2 }}>
                  <Grid item>
                    <Chip label={article.source} color="primary" />
                  </Grid>
                  <Grid item>
                    <Chip label={article.language} variant="outlined" />
                  </Grid>
                </Grid>

                <Typography variant="body2" color="text.secondary">
                  Published: {format(new Date(article.publication_date), 'MMMM dd, yyyy HH:mm')}
                </Typography>
                {article.author && (
                  <Typography variant="body2" color="text.secondary">
                    Author: {article.author}
                  </Typography>
                )}
                <Typography variant="body2" color="text.secondary">
                  Scraped: {format(new Date(article.scraped_at), 'MMMM dd, yyyy HH:mm')}
                </Typography>
              </Box>

              <Divider sx={{ mb: 3 }} />

              {/* Article Content */}
              <Typography variant="body1" sx={{ lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
                {article.content}
              </Typography>
            </CardContent>
          </Card>

          {/* Similar Articles */}
          {similarArticles.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Similar Articles
                </Typography>
                {loadingSimilar ? (
                  <CircularProgress size={24} />
                ) : (
                  <Grid container spacing={2}>
                    {similarArticles.slice(0, 3).map((similarArticle) => (
                      <Grid item xs={12} key={similarArticle.id}>
                        <Paper sx={{ p: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Box sx={{ flexGrow: 1 }}>
                              <Typography variant="subtitle1" gutterBottom>
                                {similarArticle.title}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" gutterBottom>
                                {similarArticle.source} • {format(new Date(similarArticle.publication_date), 'MMM dd, yyyy')}
                              </Typography>
                              <Typography variant="body2" sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}>
                                {similarArticle.content}
                              </Typography>
                            </Box>
                            <Button
                              component={Link}
                              to={`/articles/${similarArticle.id}`}
                              size="small"
                              sx={{ ml: 2 }}
                            >
                              View
                            </Button>
                          </Box>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Bias Analysis Sidebar */}
        <Grid item xs={12} md={4}>
          {article.bias_scores ? (
            <BiasScoreCard biasScore={article.bias_scores} showDetails={true} />
          ) : (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bias Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  This article hasn't been analyzed for bias yet.
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleAnalyzeBias}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Analyze Bias'}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Article Statistics */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Article Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Word Count
                  </Typography>
                  <Typography variant="h6">
                    {article.content.split(/\s+/).length}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Character Count
                  </Typography>
                  <Typography variant="h6">
                    {article.content.length}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ArticleDetail;