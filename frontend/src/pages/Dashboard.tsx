import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Container,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Chip,
  IconButton,

  Tabs,
  Tab,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ResponsiveContainer,
} from 'recharts';
import {
  Assessment,
  Article,
  Compare,
  Analytics,
  CloudDownload,
  TrendingUp,
  Psychology,
  Speed,
  Refresh,
  Visibility,
  Favorite,
  FavoriteBorder,
  Person,
  Public,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { statisticsApi, articlesApi } from '../services/api';
import { useDashboard } from '../contexts/DashboardContext';
import { useAuth } from '../contexts/AuthContext';
import { Article as ArticleType } from '../types/Article';

interface OverviewStats {
  total_articles: number;
  analyzed_articles: number;
  unanalyzed_articles: number;
  recent_articles: number;
  language_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  analysis_coverage: { percentage: number };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const Dashboard: React.FC = () => {
  const { refreshTrigger } = useDashboard();
  const { user, isAuthenticated } = useAuth();
  
  // Global dashboard state
  const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null);
  const [sourceComparison, setSourceComparison] = useState<any>(null);
  const [biasTrends, setBiasTrends] = useState<any>(null);
  
  // Personal dashboard state
  const [recentArticles, setRecentArticles] = useState<ArticleType[]>([]);
  const [favoriteArticles, setFavoriteArticles] = useState<string[]>([]);
  const [favoriteArticleDetails, setFavoriteArticleDetails] = useState<ArticleType[]>([]);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [tabValue, setTabValue] = useState(0);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch global statistics
      const overviewData = await statisticsApi.getOverview();
      setOverviewStats(overviewData);

      const comparisonData = await statisticsApi.getComparisonSummary(30);
      setSourceComparison(comparisonData);

      const trendsData = await statisticsApi.getBiasTrends({ days: 7 });
      setBiasTrends(trendsData);

      // Fetch personal data if authenticated
      if (isAuthenticated && user) {
        // Load recent articles
        const articlesResponse = await articlesApi.getArticles({ limit: 10 });
        setRecentArticles(articlesResponse.articles);

        // Load favorite articles (placeholder for now)
        // TODO: Implement getFavoriteArticles API call
        const favorites: string[] = []; // await getFavoriteArticles();
        setFavoriteArticles(favorites);

        // Load details for favorite articles (first 5)
        const favoriteDetails = await Promise.all(
          favorites.slice(0, 5).map(async (id) => {
            try {
              return await articlesApi.getArticle(id);
            } catch (error) {
              return null;
            }
          })
        );
        setFavoriteArticleDetails(favoriteDetails.filter(Boolean) as ArticleType[]);
      }

    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    fetchDashboardData();
  }, [refreshTrigger, fetchDashboardData]);

  const handleRefresh = async () => {
    setLastRefresh(new Date());
    await fetchDashboardData();
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleToggleFavorite = async (articleId: string) => {
    try {
      // TODO: Implement favorite/unfavorite API calls
      const isFavorite = favoriteArticles.includes(articleId);
      if (isFavorite) {
        // Remove from favorites
        setFavoriteArticles(favoriteArticles.filter(id => id !== articleId));
        setFavoriteArticleDetails(favoriteArticleDetails.filter(article => article.id !== articleId));
      } else {
        // Add to favorites
        setFavoriteArticles([...favoriteArticles, articleId]);
        // Load article details
        try {
          const article = await articlesApi.getArticle(articleId);
          setFavoriteArticleDetails([...favoriteArticleDetails, article]);
        } catch (error) {
          console.error('Failed to load article details:', error);
        }
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        sx={{
          background: 'var(--color-background)',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress 
            size={60} 
            sx={{ 
              color: 'var(--color-primary-500)',
              mb: 3,
            }} 
          />
          <Typography variant="h6" sx={{ color: 'var(--color-text-secondary)' }}>
            Loading dashboard...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ pt: 16, px: 4 }}>
        <Alert 
          severity="error"
          sx={{ 
            borderRadius: 'var(--radius-xl)',
            maxWidth: 600,
            mx: 'auto',
          }}
        >
          {error}
        </Alert>
      </Box>
    );
  }

  // Prepare data for charts
  const sourceData = overviewStats?.source_distribution
    ? Object.entries(overviewStats.source_distribution).map(([source, count]) => ({
        source,
        articles: count,
      }))
    : [];

  const languageData = overviewStats?.language_distribution
    ? Object.entries(overviewStats.language_distribution).map(([language, count]) => ({
        name: language,
        value: count,
      }))
    : [];

  const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'];

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
        {/* Background decorations */}
        <Box
          sx={{
            position: 'absolute',
            top: '-30%',
            right: '-10%',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: '#0891b2',
            filter: 'blur(100px)',
            opacity: 0.1,
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: '-20%',
            left: '5%',
            width: 300,
            height: 300,
            borderRadius: '50%',
            background: '#4f46e5',
            filter: 'blur(100px)',
            opacity: 0.1,
          }}
        />
        
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: { xs: 'flex-start', md: 'center' },
            flexDirection: { xs: 'column', md: 'row' },
            gap: 3,
          }}>
            <Box>
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
                  <Assessment sx={{ color: '#fbbf24', fontSize: 28 }} />
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
                  Dashboard
                </Typography>
              </Box>
              <Typography
                variant="h6"
                sx={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontWeight: 400,
                }}
              >
                {isAuthenticated ? `Welcome back, ${user?.username}!` : 'Real-time analytics and insights'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.6)',
                  display: { xs: 'none', sm: 'block' },
                }}
              >
                Last updated: {lastRefresh.toLocaleTimeString()}
              </Typography>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={handleRefresh}
                disabled={loading}
                sx={{
                  px: 3,
                  py: 1.25,
                  borderRadius: 'var(--radius-xl)',
                  background: 'rgba(255, 255, 255, 0.15)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: '#ffffff',
                  fontWeight: 600,
                  textTransform: 'none',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.25)',
                  },
                }}
              >
                Refresh
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">

      {/* Tabs for Global/Personal Views */}
      {isAuthenticated && (
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="dashboard tabs"
            sx={{
              '& .MuiTab-root': {
                color: 'text.primary',
                fontWeight: 500,
                fontSize: '1rem',
                minHeight: 64,
                '&.Mui-selected': {
                  color: 'primary.main',
                  fontWeight: 600,
                },
                '& .MuiSvgIcon-root': {
                  color: 'inherit',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: 'primary.main',
                height: 3,
              },
            }}
          >
            <Tab 
              icon={<Person sx={{ fontSize: 24 }} />} 
              label="Personal" 
              sx={{ 
                color: 'text.primary !important',
                '&.Mui-selected': {
                  color: 'primary.main !important',
                },
                '& .MuiSvgIcon-root': {
                  color: 'inherit !important',
                },
              }} 
            />
            <Tab 
              icon={<Public sx={{ fontSize: 24 }} />} 
              label="Global" 
              sx={{ 
                color: 'text.primary !important',
                '&.Mui-selected': {
                  color: 'primary.main !important',
                },
                '& .MuiSvgIcon-root': {
                  color: 'inherit !important',
                },
              }} 
            />
          </Tabs>
        </Box>
      )}

      {/* Personal Dashboard Tab */}
      {isAuthenticated && (
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Personal Statistics Cards */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Article color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Articles Available</Typography>
                  </Box>
                  <Typography variant="h3" color="primary">
                    {overviewStats?.total_articles || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total articles in system
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Analytics color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Analyzed</Typography>
                  </Box>
                  <Typography variant="h3" color="secondary">
                    {overviewStats?.analyzed_articles || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Articles with bias analysis
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Favorite sx={{ mr: 1, color: '#415A77' }} />
                    <Typography variant="h6">Favorites</Typography>
                  </Box>
                  <Typography variant="h3" sx={{ color: '#415A77' }}>
                    {favoriteArticles.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Articles you've favorited
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Recent Articles */}
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Articles
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {recentArticles.length > 0 ? (
                    <List>
                      {recentArticles.slice(0, 5).map((article) => (
                        <ListItem key={article.id} divider>
                          <ListItemText
                            primary={article.title}
                            secondary={
                              <Box>
                                <Typography variant="caption" display="block">
                                  {article.source} • {format(new Date(article.publication_date), 'MMM dd, yyyy')}
                                </Typography>
                                {article.bias_scores && (
                                  <Chip
                                    size="small"
                                    label={`Bias: ${(article.bias_scores.overall_bias_score * 100).toFixed(0)}%`}
                                    sx={{ 
                                      mt: 0.5,
                                      bgcolor: article.bias_scores.overall_bias_score < 0.4 ? '#E0E1DD' : 
                                               article.bias_scores.overall_bias_score < 0.7 ? '#778DA9' : '#415A77',
                                      color: article.bias_scores.overall_bias_score < 0.4 ? '#0D1B2A' : 
                                             article.bias_scores.overall_bias_score < 0.7 ? '#0D1B2A' : '#E0E1DD'
                                    }}
                                  />
                                )}
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <IconButton
                                size="small"
                                onClick={() => handleToggleFavorite(article.id)}
                                sx={{ color: favoriteArticles.includes(article.id) ? '#e91e63' : '#ccc' }}
                              >
                                {favoriteArticles.includes(article.id) ? <Favorite /> : <FavoriteBorder />}
                              </IconButton>
                              <IconButton
                                component={Link}
                                to={`/articles/${article.id}`}
                                size="small"
                              >
                                <Visibility />
                              </IconButton>
                            </Box>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No recent articles</Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button component={Link} to="/articles" variant="outlined" fullWidth>
                      View All Articles
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Favorite Articles */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Favorite Articles
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {favoriteArticleDetails.length > 0 ? (
                    <List>
                      {favoriteArticleDetails.map((article) => (
                        <ListItem key={article.id} divider>
                          <ListItemText
                            primary={article.title}
                            secondary={article.source}
                            primaryTypographyProps={{
                              sx: {
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }
                            }}
                          />
                          <ListItemSecondaryAction>
                            <IconButton
                              size="small"
                              onClick={() => handleToggleFavorite(article.id)}
                              sx={{ color: '#e91e63' }}
                            >
                              <Favorite />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No favorite articles yet</Typography>
                  )}
                  {favoriteArticles.length > favoriteArticleDetails.length && (
                    <Typography variant="caption" color="text.secondary">
                      And {favoriteArticles.length - favoriteArticleDetails.length} more...
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      )}

      {/* Global Dashboard Tab */}
      <TabPanel value={tabValue} index={isAuthenticated ? 1 : 0}>
        {/* Overview Cards */}
        <Grid container spacing={4} sx={{ mb: 8 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            textAlign: 'center',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 2,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 2,
              }}>
                <Assessment sx={{ fontSize: 32, color: '#0D1B2A' }} />
              </Box>
              <Typography variant="h6" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                Total Articles
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {overviewStats?.total_articles?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            textAlign: 'center',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 2,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 2,
              }}>
                <Psychology sx={{ fontSize: 32, color: '#1B263B' }} />
              </Box>
              <Typography variant="h6" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                Analyzed Articles
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {overviewStats?.analyzed_articles?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {overviewStats?.analysis_coverage?.percentage?.toFixed(1) || 0}% coverage
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            textAlign: 'center',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 2,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 2,
              }}>
                <TrendingUp sx={{ fontSize: 32, color: '#415A77' }} />
              </Box>
              <Typography variant="h6" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                Recent Articles
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {overviewStats?.recent_articles?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Last 7 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            height: '100%', 
            textAlign: 'center',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)',
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 2,
                borderRadius: '50%',
                bgcolor: '#E0E1DD',
                mb: 2,
              }}>
                <Speed sx={{ fontSize: 32, color: '#778DA9' }} />
              </Box>
              <Typography variant="h6" color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                Pending Analysis
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'text.primary' }}>
                {overviewStats?.unanalyzed_articles?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 4, mb: 6, borderRadius: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          Quick Actions
        </Typography>
        <Box sx={{ 
          display: 'flex', 
          gap: 3, 
          flexWrap: 'wrap',
          '& .MuiButton-root': {
            px: 3,
            py: 1.5,
            borderRadius: 2,
            fontSize: '1rem',
          }
        }}>
          <Button variant="contained" component={Link} to="/articles" startIcon={<Article />}>
            Browse Articles
          </Button>
          <Button variant="outlined" component={Link} to="/analyzer" startIcon={<Analytics />}>
            Analyze Text
          </Button>
          <Button variant="outlined" component={Link} to="/comparison" startIcon={<Compare />}>
            Compare Sources
          </Button>
          <Button variant="outlined" component={Link} to="/scraper" startIcon={<CloudDownload />}>
            Manual Scraper
          </Button>
        </Box>
      </Paper>

      {/* Charts Section */}
      <Typography variant="h3" gutterBottom sx={{ textAlign: 'center', mb: 6, fontWeight: 600 }}>
        Current Statistics
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {/* Articles by Source */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Articles by Source
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sourceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="source" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="articles" fill="#1B263B" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Language Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Language Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={languageData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#415A77"
                    dataKey="value"
                  >
                    {languageData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Bias Trends */}
        {biasTrends?.trend_data && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bias Trends (Last 7 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={biasTrends.trend_data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="average_overall_bias"
                      stroke="#0D1B2A"
                      name="Overall Bias"
                    />
                    <Line
                      type="monotone"
                      dataKey="average_sentiment"
                      stroke="#1B263B"
                      name="Sentiment"
                    />
                    <Line
                      type="monotone"
                      dataKey="average_political_bias"
                      stroke="#415A77"
                      name="Political Bias"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Source Comparison Summary */}
        {sourceComparison?.source_comparison && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Source Bias Comparison (Last 30 Days)
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(sourceComparison.source_comparison).map(([source, data]: [string, any]) => (
                    <Grid item xs={12} sm={6} md={4} key={source}>
                      <Box p={2} border={1} borderColor="grey.300" borderRadius={1}>
                        <Typography variant="subtitle1" gutterBottom>
                          {source}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Articles: {data.article_count}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Avg Bias: {(data.average_overall_bias * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Sentiment: {data.average_sentiment > 0 ? 'Positive' : data.average_sentiment < 0 ? 'Negative' : 'Neutral'}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Factual Content: {(data.average_factual_content * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
      </TabPanel>
      </Container>
    </Box>
  );
};

export default Dashboard;