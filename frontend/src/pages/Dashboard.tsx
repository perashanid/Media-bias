import React, { useState, useEffect } from 'react';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
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
  Settings,
  Visibility,
  Restore,
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
  const { user, isAuthenticated, updatePreferences, getHiddenArticles, unhideArticle } = useAuth();
  
  // Global dashboard state
  const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null);
  const [sourceComparison, setSourceComparison] = useState<any>(null);
  const [biasTrends, setBiasTrends] = useState<any>(null);
  
  // Personal dashboard state
  const [recentArticles, setRecentArticles] = useState<ArticleType[]>([]);
  const [hiddenArticles, setHiddenArticles] = useState<string[]>([]);
  const [hiddenArticleDetails, setHiddenArticleDetails] = useState<ArticleType[]>([]);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [tabValue, setTabValue] = useState(0);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [preferences, setPreferences] = useState({
    theme: 'light',
    articles_per_page: 20,
    default_time_range: 7,
  });

  const fetchDashboardData = async () => {
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
        setPreferences(user.preferences || preferences);
        
        // Load recent articles
        const articlesResponse = await articlesApi.getArticles({ limit: 10 });
        setRecentArticles(articlesResponse.articles);

        // Load hidden articles
        const hidden = await getHiddenArticles();
        setHiddenArticles(hidden);

        // Load details for hidden articles (first 5)
        const hiddenDetails = await Promise.all(
          hidden.slice(0, 5).map(async (id) => {
            try {
              return await articlesApi.getArticle(id);
            } catch (error) {
              return null;
            }
          })
        );
        setHiddenArticleDetails(hiddenDetails.filter(Boolean) as ArticleType[]);
      }

    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [refreshTrigger, isAuthenticated, user]);

  const handleRefresh = async () => {
    setLastRefresh(new Date());
    await fetchDashboardData();
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleUnhideArticle = async (articleId: string) => {
    try {
      const success = await unhideArticle(articleId);
      if (success) {
        setHiddenArticles(hiddenArticles.filter(id => id !== articleId));
        setHiddenArticleDetails(hiddenArticleDetails.filter(article => article.id !== articleId));
      }
    } catch (error) {
      console.error('Failed to unhide article:', error);
    }
  };

  const handleSavePreferences = async () => {
    try {
      const success = await updatePreferences(preferences);
      if (success) {
        setSettingsOpen(false);
      }
    } catch (error) {
      console.error('Failed to update preferences:', error);
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

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Container maxWidth="lg">
      {/* Dashboard Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {isAuthenticated ? `Welcome back, ${user?.username}!` : 'Real-time analytics and statistics'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </Typography>
          {isAuthenticated && (
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => setSettingsOpen(true)}
            >
              Settings
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Tabs for Global/Personal Views */}
      {isAuthenticated && (
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="dashboard tabs">
            <Tab icon={<Person />} label="Personal" />
            <Tab icon={<Public />} label="Global" />
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
                    <TrendingUp color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">Hidden</Typography>
                  </Box>
                  <Typography variant="h3" color="success">
                    {hiddenArticles.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Articles you've hidden
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
                                    color={article.bias_scores.overall_bias_score < 0.3 ? 'success' : 
                                           article.bias_scores.overall_bias_score < 0.6 ? 'warning' : 'error'}
                                    sx={{ mt: 0.5 }}
                                  />
                                )}
                              </Box>
                            }
                          />
                          <ListItemSecondaryAction>
                            <IconButton
                              component={Link}
                              to={`/articles/${article.id}`}
                              size="small"
                            >
                              <Visibility />
                            </IconButton>
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

            {/* Hidden Articles */}
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Hidden Articles
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  {hiddenArticleDetails.length > 0 ? (
                    <List>
                      {hiddenArticleDetails.map((article) => (
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
                              onClick={() => handleUnhideArticle(article.id)}
                              color="warning"
                            >
                              <Restore />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography color="text.secondary">No hidden articles</Typography>
                  )}
                  {hiddenArticles.length > hiddenArticleDetails.length && (
                    <Typography variant="caption" color="text.secondary">
                      And {hiddenArticles.length - hiddenArticleDetails.length} more...
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
        <Grid container spacing={3} sx={{ mb: 6 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', textAlign: 'center' }}>
            <CardContent>
              <Assessment sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography color="textSecondary" gutterBottom>
                Total Articles
              </Typography>
              <Typography variant="h4">
                {overviewStats?.total_articles?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', textAlign: 'center' }}>
            <CardContent>
              <Psychology sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography color="textSecondary" gutterBottom>
                Analyzed Articles
              </Typography>
              <Typography variant="h4">
                {overviewStats?.analyzed_articles?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {overviewStats?.analysis_coverage?.percentage?.toFixed(1) || 0}% coverage
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', textAlign: 'center' }}>
            <CardContent>
              <TrendingUp sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography color="textSecondary" gutterBottom>
                Recent Articles
              </Typography>
              <Typography variant="h4">
                {overviewStats?.recent_articles?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last 7 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', textAlign: 'center' }}>
            <CardContent>
              <Speed sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography color="textSecondary" gutterBottom>
                Pending Analysis
              </Typography>
              <Typography variant="h4">
                {overviewStats?.unanalyzed_articles?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
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
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4 }}>
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
                  <Bar dataKey="articles" fill="#1976d2" />
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
                    fill="#8884d8"
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
                      stroke="#1976d2"
                      name="Overall Bias"
                    />
                    <Line
                      type="monotone"
                      dataKey="average_sentiment"
                      stroke="#00C49F"
                      name="Sentiment"
                    />
                    <Line
                      type="monotone"
                      dataKey="average_political_bias"
                      stroke="#FF8042"
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

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>User Preferences</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.theme === 'dark'}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    theme: e.target.checked ? 'dark' : 'light'
                  })}
                />
              }
              label="Dark Theme"
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Articles per page"
              type="number"
              value={preferences.articles_per_page}
              onChange={(e) => setPreferences({
                ...preferences,
                articles_per_page: parseInt(e.target.value) || 20
              })}
              sx={{ mb: 2 }}
              inputProps={{ min: 5, max: 100 }}
            />
            
            <TextField
              fullWidth
              label="Default time range (days)"
              type="number"
              value={preferences.default_time_range}
              onChange={(e) => setPreferences({
                ...preferences,
                default_time_range: parseInt(e.target.value) || 7
              })}
              inputProps={{ min: 1, max: 365 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePreferences} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

    </Container>
  );
};

export default Dashboard;