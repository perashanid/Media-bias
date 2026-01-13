import React, { useState, useEffect, useCallback } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Button,
  Avatar,
} from '@mui/material';
import { useSearchParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import { articlesApi } from '../services/api';
import { Article } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';
import {
  ArrowBack,
  Visibility,
  Compare,
  TrendingUp,
  Assessment,
  Insights,
  AutoAwesome,
  Article as ArticleIcon,
} from '@mui/icons-material';

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

  const calculateBiasComparison = useCallback((articles: Article[]) => {
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
  }, []);

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
  }, [searchParams, calculateBiasComparison]);



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
    if (!score) return 'var(--color-neutral-400)';
    if (score < 0.4) return 'var(--color-success)';
    if (score < 0.7) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  const getBiasLevelLabel = (score?: number): string => {
    if (!score) return 'Not Analyzed';
    if (score < 0.4) return 'Low Bias';
    if (score < 0.7) return 'Moderate Bias';
    return 'High Bias';
  };

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0f172a',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress
            size={60}
            sx={{
              color: 'var(--color-accent)',
              mb: 3,
            }}
          />
          <Typography
            variant="h6"
            sx={{
              color: 'white',
              fontWeight: 600,
            }}
          >
            Loading comparison data...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ py: 8 }}>
        <Container maxWidth="md">
          <Box
            sx={{
              textAlign: 'center',
              p: 6,
              borderRadius: 4,
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
            }}
          >
            <Typography variant="h5" sx={{ color: 'var(--color-error)', fontWeight: 700, mb: 2 }}>
              {error}
            </Typography>
            <Button
              component={Link}
              to="/articles"
              startIcon={<ArrowBack />}
              variant="contained"
              sx={{
                mt: 2,
                background: '#4f46e5',
                borderRadius: 3,
                px: 4,
                py: 1.5,
                '&:hover': { background: '#4338ca' },
              }}
            >
              Back to Articles
            </Button>
          </Box>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', pb: 8 }}>
      {/* ============ HERO SECTION ============ */}
      <Box
        sx={{
          position: 'relative',
          py: { xs: 10, md: 14 },
          px: { xs: 2, md: 4 },
          background: '#0f172a',
          overflow: 'hidden',
          mb: 6,
        }}
      >
        {/* Background Shapes */}
        <Box
          sx={{
            position: 'absolute',
            width: { xs: 200, md: 400 },
            height: { xs: 200, md: 400 },
            borderRadius: '50%',
            background: '#4f46e5',
            filter: 'blur(100px)',
            opacity: 0.15,
            top: -100,
            right: -100,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            width: { xs: 150, md: 300 },
            height: { xs: 150, md: 300 },
            borderRadius: '50%',
            background: '#0891b2',
            filter: 'blur(100px)',
            opacity: 0.1,
            bottom: -50,
            left: -50,
          }}
        />

        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Button
            component={Link}
            to="/articles"
            startIcon={<ArrowBack />}
            sx={{
              mb: 4,
              color: 'rgba(255, 255, 255, 0.8)',
              '&:hover': {
                color: 'white',
                bgcolor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Back to Articles
          </Button>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Avatar
              sx={{
                width: 64,
                height: 64,
                background: '#4f46e5',
                boxShadow: '0 4px 16px rgba(79, 70, 229, 0.3)',
              }}
            >
              <Compare sx={{ fontSize: 32 }} />
            </Avatar>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  color: 'white',
                  mb: 0.5,
                }}
              >
                Article{' '}
                <Box
                  component="span"
                  sx={{
                    color: '#06b6d4',
                  }}
                >
                  Comparison
                </Box>
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontWeight: 400,
                }}
              >
                Analyzing {articles.length} articles for bias patterns and coverage differences
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Comparison Summary */}
        {comparisonData && (
          <Box
            sx={{
              mb: 5,
              p: 4,
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  background: '#0891b2',
                }}
              >
                <Assessment />
              </Avatar>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Comparison Summary
              </Typography>
            </Box>

            <Grid container spacing={3} sx={{ mb: 4 }}>
              {[
                {
                  value: `${(comparisonData.bias_comparison.average_bias * 100).toFixed(1)}%`,
                  label: 'Average Bias Score',
                  color: '#4f46e5',
                  icon: <TrendingUp />,
                },
                {
                  value: `${(comparisonData.bias_comparison.bias_variance * 100).toFixed(1)}%`,
                  label: 'Bias Variance',
                  color: '#0891b2',
                  icon: <Assessment />,
                },
                {
                  value: `${(comparisonData.bias_comparison.coverage_similarity * 100).toFixed(1)}%`,
                  label: 'Coverage Similarity',
                  color: '#059669',
                  icon: <Compare />,
                },
                {
                  value: articles.length,
                  label: 'Articles Compared',
                  color: '#d97706',
                  icon: <ArticleIcon />,
                },
              ].map((stat, index) => (
                <Grid item xs={6} md={3} key={index}>
                  <Box
                    sx={{
                      p: 3,
                      borderRadius: 3,
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      textAlign: 'center',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        background: 'rgba(255, 255, 255, 0.08)',
                        boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
                      },
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 40,
                        height: 40,
                        background: stat.color,
                        mx: 'auto',
                        mb: 2,
                      }}
                    >
                      {stat.icon}
                    </Avatar>
                    <Typography
                      variant="h4"
                      sx={{
                        fontWeight: 800,
                        background: stat.color,
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        mb: 0.5,
                      }}
                    >
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {/* Insights */}
            {comparisonData.insights.length > 0 && (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Insights sx={{ color: 'var(--color-accent)' }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Key Insights
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {comparisonData.insights.map((insight, index) => (
                    <Box
                      key={index}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        background: 'rgba(8, 145, 178, 0.08)',
                        border: '1px solid rgba(8, 145, 178, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                      }}
                    >
                      <AutoAwesome sx={{ color: 'var(--color-accent)', fontSize: 20 }} />
                      <Typography variant="body2" sx={{ color: 'text.primary' }}>
                        {insight}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        )}

        {/* Detailed Comparison Table */}
        <Box
          sx={{
            mb: 5,
            borderRadius: 4,
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <Box sx={{ p: 3, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Detailed Analysis
            </Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ background: 'rgba(99, 102, 241, 0.1)' }}>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Article</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Source</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Language</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Bias Level</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Sentiment</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: 'var(--color-primary-400)' }}>Published</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {articles.map((article, index) => (
                  <TableRow
                    key={article.id}
                    sx={{
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        background: 'rgba(99, 102, 241, 0.05)',
                      },
                      borderBottom: index === articles.length - 1 ? 'none' : '1px solid rgba(255, 255, 255, 0.05)',
                    }}
                  >
                    <TableCell>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                        {article.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {article.content}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={article.source}
                        size="small"
                        sx={{
                          background: '#4f46e5',
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={article.language}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: 'var(--color-accent)',
                          color: 'var(--color-accent)',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Chip
                          label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                          size="small"
                          sx={{
                            bgcolor: getBiasLevelColor(article.bias_scores?.overall_bias_score),
                            color: 'white',
                            fontWeight: 600,
                          }}
                        />
                        {article.bias_scores?.overall_bias_score && (
                          <LinearProgress
                            variant="determinate"
                            value={article.bias_scores.overall_bias_score * 100}
                            sx={{
                              mt: 1,
                              height: 6,
                              borderRadius: 3,
                              bgcolor: 'rgba(255, 255, 255, 0.1)',
                              '& .MuiLinearProgress-bar': {
                                background: '#4f46e5',
                                borderRadius: 3,
                              },
                            }}
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {article.bias_scores?.sentiment_score !== undefined && (
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: 'var(--color-accent)' }}>
                            {(article.bias_scores.sentiment_score * 100).toFixed(1)}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={article.bias_scores.sentiment_score * 100}
                            sx={{
                              mt: 1,
                              height: 6,
                              borderRadius: 3,
                              bgcolor: 'rgba(255, 255, 255, 0.1)',
                              '& .MuiLinearProgress-bar': {
                                background: '#0891b2',
                                borderRadius: 3,
                              },
                            }}
                          />
                        </Box>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>

        {/* Individual Article Cards */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
            Individual Articles
          </Typography>
        </Box>
        <Grid container spacing={4}>
          {articles.map((article, index) => (
            <Grid item xs={12} md={6} key={article.id}>
              <Card
                className="card-modern"
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  background: 'rgba(255, 255, 255, 0.03)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: 4,
                  transition: 'all 0.3s ease',
                  animation: `fadeInUp 0.6s ease ${index * 0.1}s backwards`,
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 20px 60px rgba(99, 102, 241, 0.2)',
                    border: '1px solid rgba(99, 102, 241, 0.3)',
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    <Chip
                      label={article.source}
                      size="small"
                      sx={{
                        background: '#4f46e5',
                        color: 'white',
                        fontWeight: 600,
                      }}
                    />
                    <Chip
                      label={getBiasLevelLabel(article.bias_scores?.overall_bias_score)}
                      size="small"
                      sx={{
                        bgcolor: getBiasLevelColor(article.bias_scores?.overall_bias_score),
                        color: 'white',
                        fontWeight: 600,
                      }}
                    />
                    <Chip
                      label={article.language}
                      size="small"
                      variant="outlined"
                      sx={{
                        borderColor: 'var(--color-accent)',
                        color: 'var(--color-accent)',
                      }}
                    />
                  </Box>

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
                    }}
                  >
                    {article.title}
                  </Typography>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: 3,
                      lineHeight: 1.7,
                    }}
                  >
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
                    variant="contained"
                    component={Link}
                    to={`/articles/${article.id}`}
                    startIcon={<Visibility />}
                    sx={{
                      background: '#4f46e5',
                      borderRadius: 3,
                      py: 1.5,
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': {
                        background: '#4338ca',
                        transform: 'scale(1.02)',
                        boxShadow: '0 4px 16px rgba(79, 70, 229, 0.3)',
                      },
                    }}
                  >
                    View Full Article
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default Comparison;