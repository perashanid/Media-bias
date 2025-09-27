import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Button,
} from '@mui/material';
import { useSearchParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { articlesApi, comparisonApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';
import { ArrowBack, Analytics, Visibility } from '@mui/icons-material';

interface ComparisonData {
  articles: Article[];
  bias_comparison: {
    average_bias: number;
    bias_variance: number;
    sentiment_variance: number;
    coverage_similarity: number;
  };
  insights: string[];
}

const Comparison: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [articles, setArticles] = useState<Article[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComparisonData = async () => {
      try {
        setLoading(true);
        setError(null);

        const articleIds = searchParams.get('articles')?.split(',') || [];
        
        if (articleIds.length < 2) {
          setError('At least 2 articles are required for comparison');
          return;
        }

        // Fetch all articles
        const articlePromises = articleIds.map(id => articlesApi.getArticle(id));
        const fetchedArticles = await Promise.all(articlePromises);
        setArticles(fetchedArticles);

        // Create comparison data
        const comparison: ComparisonData = {
          articles: fetchedArticles,
          bias_comparison: calculateBiasComparison(fetchedArticles),
          insights: generateInsights(fetchedArticles)
        };

        setComparisonData(comparison);

      } catch (err) {
        setError('Failed to load comparison data');
        console.error('Comparison error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchComparisonData();
  }, [searchParams]);

  const calculateBiasComparison = (articles: Article[]) => {
    const biasScores = articles
      .map(article => article.bias_scores?.overall_bias_score)
      .filter(score => score !== undefined) as number[];

    if (biasScores.length === 0) {
      return {
        average_bias: 0,
        bias_variance: 0,
        sentiment_variance: 0,
        coverage_similarity: 0
      };
    }

    const average_bias = biasScores.reduce((sum, score) => sum + score, 0) / biasScores.length;
    const bias_variance = biasScores.reduce((sum, score) => sum + Math.pow(score - average_bias, 2), 0) / biasScores.length;

    const sentimentScores = articles
      .map(article => article.bias_scores?.sentiment_score)
      .filter(score => score !== undefined) as number[];
    
    const avgSentiment = sentimentScores.reduce((sum, score) => sum + score, 0) / sentimentScores.length;
    const sentiment_variance = sentimentScores.reduce((sum, score) => sum + Math.pow(score - avgSentiment, 2), 0) / sentimentScores.length;

    // Simple coverage similarity based on title word overlap
    const coverage_similarity = calculateCoverageSimilarity(articles);

    return {
      average_bias,
      bias_variance,
      sentiment_variance,
      coverage_similarity
    };
  };

  const calculateCoverageSimilarity = (articles: Article[]): number => {
    if (articles.length < 2) return 0;

    const titleWords = articles.map(article => 
      article.title.toLowerCase().split(' ').filter(word => word.length > 3)
    );

    let totalSimilarity = 0;
    let comparisons = 0;

    for (let i = 0; i < titleWords.length; i++) {
      for (let j = i + 1; j < titleWords.length; j++) {
        const words1 = new Set(titleWords[i]);
        const words2 = new Set(titleWords[j]);
        const intersection = new Set([...words1].filter(x => words2.has(x)));
        const union = new Set([...words1, ...words2]);
        
        const similarity = intersection.size / union.size;
        totalSimilarity += similarity;
        comparisons++;
      }
    }

    return comparisons > 0 ? totalSimilarity / comparisons : 0;
  };

  const generateInsights = (articles: Article[]): string[] => {
    const insights: string[] = [];
    
    if (articles.length === 0) return insights;

    // Source diversity
    const sources = new Set(articles.map(article => article.source));
    if (sources.size === 1) {
      insights.push(`All articles are from the same source (${Array.from(sources)[0]}), which may limit perspective diversity.`);
    } else {
      insights.push(`Articles span ${sources.size} different sources, providing diverse perspectives.`);
    }

    // Language diversity
    const languages = new Set(articles.map(article => article.language));
    if (languages.size > 1) {
      insights.push(`Articles are in ${languages.size} different languages: ${Array.from(languages).join(', ')}.`);
    }

    // Bias analysis
    const biasScores = articles
      .map(article => article.bias_scores?.overall_bias_score)
      .filter(score => score !== undefined) as number[];

    if (biasScores.length > 0) {
      const maxBias = Math.max(...biasScores);
      const minBias = Math.min(...biasScores);
      const biasRange = maxBias - minBias;

      if (biasRange < 0.2) {
        insights.push('Articles show similar bias levels, indicating consistent perspective.');
      } else if (biasRange > 0.5) {
        insights.push('Articles show significant bias variation, representing different viewpoints.');
      }
    }

    return insights;
  };

  const getBiasLevelColor = (score?: number): string => {
    if (!score) return '#778DA9';
    if (score < 0.4) return '#1B263B';
    if (score < 0.7) return '#415A77';
    return '#0D1B2A';
  };

  const getBiasLevelLabel = (score?: number): string => {
    if (!score) return 'Not Analyzed';
    if (score < 0.4) return 'Low Bias';
    if (score < 0.7) return 'Moderate Bias';
    return 'High Bias';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button component={Link} to="/articles" startIcon={<ArrowBack />}>
          Back to Articles
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button component={Link} to="/articles" startIcon={<ArrowBack />} sx={{ mb: 2 }}>
          Back to Articles
        </Button>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
          Article Comparison
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comparing {articles.length} articles for bias patterns and coverage differences
        </Typography>
      </Box>

      {/* Comparison Summary */}
      {comparisonData && (
        <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            Comparison Summary
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>
                  {(comparisonData.bias_comparison.average_bias * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average Bias Score
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="secondary" sx={{ fontWeight: 700 }}>
                  {(comparisonData.bias_comparison.bias_variance * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Bias Variance
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main" sx={{ fontWeight: 700 }}>
                  {(comparisonData.bias_comparison.coverage_similarity * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Coverage Similarity
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#1B263B', fontWeight: 700 }}>
                  {articles.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Articles Compared
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Insights */}
          {comparisonData.insights.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Key Insights
              </Typography>
              {comparisonData.insights.map((insight, index) => (
                <Alert key={index} severity="info" sx={{ mb: 1 }}>
                  {insight}
                </Alert>
              ))}
            </Box>
          )}
        </Paper>
      )}

      {/* Detailed Comparison Table */}
      <Paper sx={{ mb: 4, borderRadius: 2 }}>
        <Box sx={{ p: 3, pb: 0 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            Detailed Analysis
          </Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Article</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Language</TableCell>
                <TableCell>Bias Level</TableCell>
                <TableCell>Sentiment</TableCell>
                <TableCell>Published</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {articles.map((article) => (
                <TableRow key={article.id}>
                  <TableCell>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      {article.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}>
                      {article.content}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={article.source} size="small" color="primary" />
                  </TableCell>
                  <TableCell>
                    <Chip label={article.language} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Chip
                        label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                        size="small"
                        sx={{
                          bgcolor: getBiasLevelColor(article.bias_scores?.overall_bias_score),
                          color: '#E0E1DD'
                        }}
                      />
                      {article.bias_scores?.overall_bias_score && (
                        <LinearProgress
                          variant="determinate"
                          value={article.bias_scores.overall_bias_score * 100}
                          sx={{ mt: 1, height: 4, borderRadius: 2 }}
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {article.bias_scores?.sentiment_score && (
                      <Box>
                        <Typography variant="body2">
                          {(article.bias_scores.sentiment_score * 100).toFixed(1)}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={article.bias_scores.sentiment_score * 100}
                          color="secondary"
                          sx={{ mt: 1, height: 4, borderRadius: 2 }}
                        />
                      </Box>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Individual Article Cards */}
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Individual Articles
      </Typography>
      <Grid container spacing={4}>
        {articles.map((article) => (
          <Grid item xs={12} md={6} key={article.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Chip label={article.source} size="small" color="primary" />
                  <Chip
                    label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                    size="small"
                    sx={{
                      bgcolor: getBiasLevelColor(article.bias_scores?.overall_bias_score),
                      color: '#E0E1DD'
                    }}
                  />
                  <Chip label={article.language} size="small" variant="outlined" />
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

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                    {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                  </Typography>
                  {article.author && (
                    <Typography variant="body2" color="text.secondary">
                      By {article.author}
                    </Typography>
                  )}
                </Box>

                {/* Bias Score Preview */}
                {article.bias_scores && (
                  <Box sx={{ mb: 2 }}>
                    <BiasScoreCard biasScore={article.bias_scores} showDetails={false} />
                  </Box>
                )}
              </CardContent>

              <Box sx={{ p: 3, pt: 0 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  component={Link}
                  to={`/articles/${article.id}`}
                  startIcon={<Visibility />}
                  sx={{ borderRadius: 2 }}
                >
                  View Full Article
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Comparison;