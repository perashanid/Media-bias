import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,

  Chip,
  CardContent,
} from '@mui/material';
import {
  Assessment,
  Article,
  Compare,
  Analytics,
  CloudDownload,
  CheckCircle,
  Psychology,
  TrendingUp,
  People,
  Language,
  BarChart,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface OverviewStats {
  total_articles: number;
  recent_articles: number;
  total_users: number;
  analyzed_articles: number;
  total_sources: number;
  analysis_coverage: number;
  language_stats: Array<{ _id: string; count: number }>;
  bias_distribution: Array<{ _id: string; count: number }>;
  top_sources: Array<{ _id: string; count: number }>;
}

const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch('/api/statistics/overview');
        if (response.ok) {
          const data = await response.json();
          console.log('API Response:', data); // Debug log
          
          // The API returns the stats directly, not wrapped in a success object
          setStats({
            total_articles: data.total_articles || 0,
            recent_articles: data.recent_articles || 0,
            total_users: data.total_users || 0,
            analyzed_articles: data.analyzed_articles || 0,
            total_sources: Object.keys(data.source_counts || {}).length,
            analysis_coverage: data.total_articles > 0 ? Math.round((data.analyzed_articles / data.total_articles) * 100) : 0,
            language_stats: Object.entries(data.language_distribution || {}).map(([key, value]) => ({ _id: key, count: value as number })),
            bias_distribution: Object.entries(data.bias_distribution || {}).map(([key, value]) => ({ _id: key, count: value as number })),
            top_sources: Object.entries(data.source_counts || {}).map(([key, value]) => ({ _id: key, count: value as number })).slice(0, 6)
          });
        } else {
          console.error('Failed to fetch stats:', response.status, response.statusText);
          // Set default stats if API fails
          setStats({
            total_articles: 0,
            recent_articles: 0,
            total_users: 0,
            analyzed_articles: 0,
            total_sources: 0,
            analysis_coverage: 0,
            language_stats: [],
            bias_distribution: [],
            top_sources: []
          });
        }
      } catch (error) {
        console.error('Failed to fetch home data:', error);
        // Set default stats on error
        setStats({
          total_articles: 0,
          recent_articles: 0,
          total_users: 0,
          analyzed_articles: 0,
          total_sources: 0,
          analysis_coverage: 0,
          language_stats: [],
          bias_distribution: [],
          top_sources: []
        });
      } finally {
        setStatsLoading(false);
      }
    };

    fetchHomeData();
  }, []);
  
  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', py: { xs: 6, md: 10 }, mb: 8 }}>
        <Typography 
          variant="h1" 
          component="h1" 
          sx={{ 
            fontWeight: 700, 
            mb: 3,
            background: (theme) => theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)'
              : 'linear-gradient(135deg, #1e40af 0%, #7c3aed 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Media Bias Detector
        </Typography>
        <Typography 
          variant="h5" 
          color="text.secondary" 
          paragraph 
          sx={{ 
            maxWidth: '800px', 
            mx: 'auto', 
            mb: 6,
            fontWeight: 400,
            lineHeight: 1.6,
          }}
        >
          Advanced AI-powered analysis to detect bias, sentiment, and political leanings in news articles from multiple Bangladeshi sources
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          gap: 3, 
          justifyContent: 'center', 
          flexWrap: 'wrap',
          '& .MuiButton-root': {
            px: 4,
            py: 1.5,
            fontSize: '1.1rem',
          }
        }}>
          {isAuthenticated && (
            <Button variant="contained" size="large" component={Link} to="/dashboard" startIcon={<Assessment />}>
              View Dashboard
            </Button>
          )}
          <Button variant={isAuthenticated ? "outlined" : "contained"} size="large" component={Link} to="/articles" startIcon={<Article />}>
            Browse Articles
          </Button>
          <Button variant="outlined" size="large" component={Link} to="/analyzer" startIcon={<Analytics />}>
            Analyze Text
          </Button>
        </Box>
      </Box>

      {/* Statistics Section */}
      {!statsLoading && stats && (
        <Paper sx={{ 
          p: { xs: 4, md: 6 }, 
          mb: 8, 
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'grey.200',
          borderRadius: 3,
        }}>
          <Typography variant="h2" gutterBottom sx={{ textAlign: 'center', mb: 6, color: '#0D1B2A' }}>
            Platform Statistics
          </Typography>
          
          <Grid container spacing={4} sx={{ mb: 6 }}>
            {/* Total Articles */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                textAlign: 'center', 
                p: 3,
                height: '100%',
                background: 'linear-gradient(135deg, #1B263B 0%, #415A77 100%)',
                color: '#E0E1DD',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(27, 38, 59, 0.4)',
                }
              }}>
                <CardContent>
                  <Article sx={{ fontSize: 48, mb: 2, color: '#E0E1DD' }} />
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: '#E0E1DD' }}>
                    {stats.total_articles.toLocaleString()}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#E0E1DD', opacity: 0.9 }}>
                    Total Articles
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Analyzed Articles */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                textAlign: 'center', 
                p: 3,
                height: '100%',
                background: 'linear-gradient(135deg, #415A77 0%, #778DA9 100%)',
                color: '#E0E1DD',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(65, 90, 119, 0.4)',
                }
              }}>
                <CardContent>
                  <Psychology sx={{ fontSize: 48, mb: 2, color: '#E0E1DD' }} />
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: '#E0E1DD' }}>
                    {stats.analyzed_articles.toLocaleString()}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#E0E1DD', opacity: 0.9 }}>
                    Analyzed Articles
                  </Typography>
                  <Chip 
                    label={`${stats.analysis_coverage}% Coverage`} 
                    size="small" 
                    sx={{ 
                      mt: 1, 
                      bgcolor: '#0D1B2A', 
                      color: '#E0E1DD',
                      fontWeight: 600 
                    }} 
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Total Users */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                textAlign: 'center', 
                p: 3,
                height: '100%',
                background: 'linear-gradient(135deg, #778DA9 0%, #E0E1DD 100%)',
                color: '#0D1B2A',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(119, 141, 169, 0.4)',
                }
              }}>
                <CardContent>
                  <People sx={{ fontSize: 48, mb: 2, color: '#0D1B2A' }} />
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: '#0D1B2A' }}>
                    {stats.total_users.toLocaleString()}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#0D1B2A', opacity: 0.8 }}>
                    Registered Users
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* News Sources */}
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ 
                textAlign: 'center', 
                p: 3,
                height: '100%',
                background: 'linear-gradient(135deg, #778DA9 0%, #E0E1DD 100%)',
                color: '#0D1B2A',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(119, 141, 169, 0.3)',
                }
              }}>
                <CardContent>
                  <TrendingUp sx={{ fontSize: 48, mb: 2, color: '#0D1B2A' }} />
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: '#0D1B2A' }}>
                    {stats.total_sources}
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#0D1B2A', opacity: 0.8 }}>
                    News Sources
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Additional Stats */}
          <Grid container spacing={4}>
            {/* Language Distribution */}
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                p: 3, 
                height: '100%',
                border: '2px solid #E0E1DD',
                borderRadius: 3,
                bgcolor: '#FAFAFA',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(13, 27, 42, 0.1)',
                  transform: 'translateY(-2px)'
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Language sx={{ fontSize: 32, color: '#1B263B', mr: 2 }} />
                  <Typography variant="h5" sx={{ fontWeight: 600, color: '#0D1B2A' }}>
                    Language Distribution
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {stats.language_stats.map((lang, index) => (
                    <Chip
                      key={lang._id || index}
                      label={`${lang._id || 'Unknown'}: ${lang.count.toLocaleString()}`}
                      sx={{ 
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        bgcolor: lang._id === 'bengali' ? '#415A77' : '#778DA9',
                        color: '#E0E1DD',
                        border: `2px solid ${lang._id === 'bengali' ? '#1B263B' : '#415A77'}`,
                        '&:hover': {
                          bgcolor: lang._id === 'bengali' ? '#1B263B' : '#415A77',
                          transform: 'scale(1.05)'
                        }
                      }}
                    />
                  ))}
                </Box>
              </Card>
            </Grid>

            {/* Bias Distribution */}
            <Grid item xs={12} md={6}>
              <Card sx={{ 
                p: 3, 
                height: '100%',
                border: '2px solid #E0E1DD',
                borderRadius: 3,
                bgcolor: '#FAFAFA',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(13, 27, 42, 0.1)',
                  transform: 'translateY(-2px)'
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <BarChart sx={{ fontSize: 32, color: '#1B263B', mr: 2 }} />
                  <Typography variant="h5" sx={{ fontWeight: 600, color: '#0D1B2A' }}>
                    Bias Distribution
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {stats.bias_distribution.map((bias, index) => (
                    <Chip
                      key={bias._id || index}
                      label={`${bias._id}: ${bias.count.toLocaleString()}`}
                      sx={{ 
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        bgcolor: bias._id === 'Low Bias' ? '#778DA9' : 
                                 bias._id === 'Moderate Bias' ? '#415A77' : '#1B263B',
                        color: '#E0E1DD',
                        border: `2px solid ${bias._id === 'Low Bias' ? '#415A77' : 
                                             bias._id === 'Moderate Bias' ? '#1B263B' : '#0D1B2A'}`,
                        '&:hover': {
                          transform: 'scale(1.05)',
                          bgcolor: bias._id === 'Low Bias' ? '#415A77' : 
                                   bias._id === 'Moderate Bias' ? '#1B263B' : '#0D1B2A'
                        }
                      }}
                    />
                  ))}
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* About Section */}
      <Paper sx={{ 
        p: { xs: 4, md: 6 }, 
        mb: 8, 
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'grey.200',
        borderRadius: 3,
      }}>
        <Typography variant="h2" gutterBottom sx={{ textAlign: 'center', mb: 2, color: '#0D1B2A' }}>
          About Media Bias Detector
        </Typography>
        <Typography variant="h6" paragraph sx={{ 
          textAlign: 'center', 
          mb: 6, 
          color: 'text.secondary',
          fontWeight: 400,
          maxWidth: '600px',
          mx: 'auto',
        }}>
          An AI-powered platform for analyzing media bias in Bangladeshi news sources
        </Typography>
        
        <Grid container spacing={6} sx={{ mb: 6 }}>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 2, 
                bgcolor: '#E0E1DD',
                color: '#0D1B2A',
                minWidth: 'fit-content',
              }}>
                <Assessment sx={{ fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="h5" gutterBottom sx={{ color: 'text.primary', fontWeight: 600 }}>
                  What We Do
                </Typography>
                <Typography paragraph sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                  We automatically collect and analyze news articles from major Bangladeshi media outlets to detect bias patterns, 
                  sentiment variations, and coverage differences across sources. Our platform helps readers understand how different 
                  news sources present the same stories.
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <Box sx={{ 
                p: 1.5, 
                borderRadius: 2, 
                bgcolor: '#E0E1DD',
                color: '#1B263B',
                minWidth: 'fit-content',
              }}>
                <Psychology sx={{ fontSize: 24 }} />
              </Box>
              <Box>
                <Typography variant="h5" gutterBottom sx={{ color: 'text.primary', fontWeight: 600 }}>
                  How We Do It
                </Typography>
                <Typography paragraph sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                  Using advanced Natural Language Processing (NLP) and machine learning algorithms, we analyze article content for 
                  political bias, emotional language, sentiment, and factual vs opinion content. Our AI models are specifically 
                  trained to understand both Bengali and English text patterns.
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 6 }} />

        <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 6, fontWeight: 600 }}>
          How It Works
        </Typography>
        <Grid container spacing={6}>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 3,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 3,
              }}>
                <CloudDownload sx={{ fontSize: 40, color: '#0D1B2A' }} />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Data Collection
              </Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Automatically scrapes articles from multiple Bangladeshi news sources including Prothom Alo, Daily Star, BD Pratidin, Ekattor TV, ATN News, and Jamuna TV.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 3,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 3,
              }}>
                <Psychology sx={{ fontSize: 40, color: '#1B263B' }} />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                AI Analysis
              </Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Advanced NLP algorithms analyze sentiment, political bias, emotional language, and factual vs opinion content using machine learning models trained on news data.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 3,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 3,
              }}>
                <Compare sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Comparison & Insights
              </Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Compare how different sources cover the same story, identify bias patterns, and get detailed reports on media coverage differences and similarities.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Features Section */}
      <Grid container spacing={6} sx={{ mb: 8 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 4, height: '100%', borderRadius: 3 }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
              Key Features
            </Typography>
            <List sx={{ '& .MuiListItem-root': { py: 1.5 } }}>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Multi-Source Analysis</Typography>}
                  secondary={<Typography color="text.secondary">Analyze articles from 6 major Bangladeshi news sources</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Bias Detection</Typography>}
                  secondary={<Typography color="text.secondary">Detect political bias, sentiment, and emotional language patterns</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Cross-Source Comparison</Typography>}
                  secondary={<Typography color="text.secondary">Compare how different sources cover the same story</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Real-time Scraping</Typography>}
                  secondary={<Typography color="text.secondary">Continuously collect and analyze new articles</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Multi-language Support</Typography>}
                  secondary={<Typography color="text.secondary">Analyze both Bengali and English articles</Typography>}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 4, height: '100%', borderRadius: 3 }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
              Analysis Metrics
            </Typography>
            <List sx={{ '& .MuiListItem-root': { py: 1.5, alignItems: 'flex-start' } }}>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Political Bias Score</Typography>}
                  secondary={<Typography color="text.secondary">0-40%: Left-leaning, 40-60%: Center, 60-100%: Right-leaning. Analyzes word choices, framing, and political indicators.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Sentiment Analysis</Typography>}
                  secondary={<Typography color="text.secondary">Negative: Critical/pessimistic tone, Neutral: Balanced reporting, Positive: Optimistic/supportive tone.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Emotional Language</Typography>}
                  secondary={<Typography color="text.secondary">Measures use of emotionally charged words, dramatic language, and subjective expressions vs neutral reporting.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology sx={{ fontSize: 28, color: '#1B263B' }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Factual vs Opinion</Typography>}
                  secondary={<Typography color="text.secondary">0%: Pure opinion/editorial, 50%: Mixed content, 100%: Pure factual reporting with verifiable information.</Typography>}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* News Sources Section */}
      <Paper sx={{ p: { xs: 4, md: 6 }, mb: 8, borderRadius: 3 }}>
        <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 6, fontWeight: 600 }}>
          News Sources We Monitor
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                Prothom Alo
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Leading Bengali daily newspaper
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                The Daily Star
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Premier English daily newspaper
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                BD Pratidin
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Popular Bengali news portal
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                Ekattor TV
              </Typography>
              <Typography variant="body1" color="text.secondary">
                24/7 news television channel
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                ATN News
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Satellite news channel
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ 
              textAlign: 'center', 
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
              }
            }}>
              <Typography variant="h5" sx={{ color: '#1B263B', fontWeight: 600, mb: 1 }}>
                Jamuna TV
              </Typography>
              <Typography variant="body1" color="text.secondary">
                24/7 news television channel
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Get Started Section */}
      <Paper 
        className="get-started-section"
        sx={{ 
          p: { xs: 4, md: 6 }, 
          textAlign: 'center', 
          background: (theme) => theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #415A77 0%, #778DA9 100%)'
            : 'linear-gradient(135deg, #0D1B2A 0%, #1B263B 100%)',
          color: 'white !important',
          borderRadius: 3,
          '& *': {
            color: 'white !important',
          },
          '& .MuiTypography-root': {
            color: 'white !important',
          },
          '& .MuiButton-contained': {
            backgroundColor: 'white !important',
            color: '#0D1B2A !important',
            '&:hover': {
              backgroundColor: '#f5f5f5 !important',
              color: '#0D1B2A !important',
            },
          },
          '& .MuiButton-outlined': {
            borderColor: 'white !important',
            color: 'white !important',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1) !important',
              borderColor: 'rgba(255, 255, 255, 0.8) !important',
              color: 'white !important',
            },
          },
        }}
      >
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600, color: 'white !important' }}>
          Get Started
        </Typography>
        <Typography variant="h6" paragraph sx={{ 
          opacity: 0.9, 
          maxWidth: '600px', 
          mx: 'auto',
          fontWeight: 400,
          lineHeight: 1.6,
          color: 'white !important',
        }}>
          Explore media bias patterns and make informed decisions about news consumption
        </Typography>
        <Box sx={{ 
          mt: 4, 
          display: 'flex', 
          gap: 3, 
          justifyContent: 'center', 
          flexWrap: 'wrap',
          '& .MuiButton-root': {
            px: 4,
            py: 1.5,
            fontSize: '1.1rem',
          }
        }}>
          {isAuthenticated ? (
            <Button 
              variant="contained" 
              size="large" 
              component={Link} 
              to="/dashboard" 
              sx={{ 
                bgcolor: 'white !important', 
                color: '#0D1B2A !important',
                border: 'none !important',
                '&:hover': { 
                  bgcolor: '#f5f5f5 !important',
                  color: '#0D1B2A !important',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                } 
              }}
            >
              View Dashboard
            </Button>
          ) : (
            <Button 
              variant="contained" 
              size="large" 
              component={Link} 
              to="/articles" 
              sx={{ 
                bgcolor: 'white !important', 
                color: '#0D1B2A !important',
                border: 'none !important',
                '&:hover': { 
                  bgcolor: '#f5f5f5 !important',
                  color: '#0D1B2A !important',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                } 
              }}
            >
              Browse Articles
            </Button>
          )}
          <Button 
            variant="outlined" 
            size="large" 
            component={Link} 
            to="/scraper" 
            sx={{ 
              borderColor: 'white', 
              color: 'white', 
              '&:hover': { 
                borderColor: 'rgba(255, 255, 255, 0.8)', 
                bgcolor: 'rgba(255,255,255,0.1)',
                transform: 'translateY(-2px)',
              } 
            }}
          >
            Manual Scraper
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Home;