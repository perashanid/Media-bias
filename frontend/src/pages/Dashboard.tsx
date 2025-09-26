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
  ListItemIcon,
  ListItemText,
  Divider,
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
  CheckCircle,
  TrendingUp,
  Language,
  Psychology,
  Speed,
  Security,
  Refresh,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { statisticsApi } from '../services/api';
import { useDashboard } from '../contexts/DashboardContext';

interface OverviewStats {
  total_articles: number;
  analyzed_articles: number;
  unanalyzed_articles: number;
  recent_articles: number;
  language_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  analysis_coverage: { percentage: number };
}

const Dashboard: React.FC = () => {
  const { refreshTrigger } = useDashboard();
  const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null);
  const [sourceComparison, setSourceComparison] = useState<any>(null);
  const [biasTrends, setBiasTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch overview statistics
        const overviewData = await statisticsApi.getOverview();
        setOverviewStats(overviewData);

        // Fetch source comparison
        const comparisonData = await statisticsApi.getComparisonSummary(30);
        setSourceComparison(comparisonData);

        // Fetch bias trends
        const trendsData = await statisticsApi.getBiasTrends({ days: 7 });
        setBiasTrends(trendsData);

      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchDashboardData();
  }, [refreshTrigger]);

  const handleRefresh = async () => {
    setLastRefresh(new Date());
    await fetchDashboardData();
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Real-time analytics and statistics
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </Typography>
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
                    {languageData.map((entry, index) => (
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


    </Container>
  );
};

export default Dashboard;