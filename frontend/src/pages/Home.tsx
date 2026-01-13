import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  Paper,
  Chip,
  CardContent,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  Assessment,
  Article,
  Compare,
  Analytics,
  CloudDownload,
  Psychology,
  TrendingUp,
  People,
  Language,
  BarChart,
  Speed,
  Security,
  AutoAwesome,
  Verified,
  ArrowForward,
  PlayArrow,
  CheckCircle,
  Bolt,
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

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
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch('/api/statistics/overview');
        if (response.ok) {
          const data = await response.json();
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
          setStats({
            total_articles: 0, recent_articles: 0, total_users: 0, analyzed_articles: 0,
            total_sources: 0, analysis_coverage: 0, language_stats: [], bias_distribution: [], top_sources: []
          });
        }
      } catch (error) {
        console.error('Failed to fetch home data:', error);
        setStats({
          total_articles: 0, recent_articles: 0, total_users: 0, analyzed_articles: 0,
          total_sources: 0, analysis_coverage: 0, language_stats: [], bias_distribution: [], top_sources: []
        });
      } finally {
        setStatsLoading(false);
      }
    };
    fetchHomeData();
  }, []);

  const features = [
    {
      icon: <Psychology sx={{ fontSize: 32 }} />,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning algorithms analyze sentiment, bias, and political leanings in real-time.',
      color: '#4f46e5',
    },
    {
      icon: <Compare sx={{ fontSize: 32 }} />,
      title: 'Cross-Source Comparison',
      description: 'Compare how different news outlets cover the same story to identify bias patterns.',
      color: '#0891b2',
    },
    {
      icon: <Speed sx={{ fontSize: 32 }} />,
      title: 'Real-Time Scraping',
      description: 'Continuously collect and analyze articles from 6+ major Bangladeshi news sources.',
      color: '#059669',
    },
    {
      icon: <Language sx={{ fontSize: 32 }} />,
      title: 'Multi-Language Support',
      description: 'Analyze both Bengali and English articles with specialized NLP models.',
      color: '#d97706',
    },
    {
      icon: <Security sx={{ fontSize: 32 }} />,
      title: 'Factual Analysis',
      description: 'Distinguish between factual reporting and opinion-based content automatically.',
      color: '#dc2626',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 32 }} />,
      title: 'Trend Insights',
      description: 'Track bias trends over time and identify patterns in media coverage.',
      color: '#db2777',
    },
  ];

  const newsSources = [
    { name: 'Prothom Alo', type: 'Bengali Daily', color: '#e11d48', language: 'Bengali', description: 'Bangladesh\'s largest circulating daily newspaper, providing comprehensive coverage of national and international news.', logoUrl: 'https://logo.clearbit.com/prothomalo.com' },
    { name: 'The Daily Star', type: 'English Daily', color: '#0ea5e9', language: 'English', description: 'Leading English-language newspaper in Bangladesh, known for independent journalism and in-depth analysis.', logoUrl: 'https://logo.clearbit.com/thedailystar.net' },
    { name: 'BD Pratidin', type: 'Bengali Portal', color: '#8b5cf6', language: 'Bengali', description: 'Popular Bengali news portal offering breaking news, politics, sports, and entertainment coverage.', logoUrl: 'https://logo.clearbit.com/bd-pratidin.com' },
    { name: 'Ekattor TV', type: 'TV Channel', color: '#f59e0b', language: 'Bengali', description: 'Prominent 24-hour Bengali news channel covering current affairs and live political events.', logoUrl: 'https://logo.clearbit.com/ekattor.tv' },
    { name: 'ATN News', type: 'Satellite News', color: '#10b981', language: 'Bengali', description: 'Satellite news channel providing round-the-clock news, talk shows, and investigative reports.', logoUrl: 'https://logo.clearbit.com/atnnews.tv' },
    { name: 'Jamuna TV', type: 'TV Channel', color: '#6366f1', language: 'Bengali', description: 'Private television channel known for its news programming and entertainment content.', logoUrl: 'https://logo.clearbit.com/jamuna.tv' },
  ];

  return (
    <Box sx={{ overflow: 'hidden' }}>
      {/* ============ HERO SECTION ============ */}
      <Box
        className="hero-section"
        sx={{
          position: 'relative',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
          overflow: 'hidden',
          mx: { xs: 0, md: -3 },
          mt: -4,
          px: { xs: 2, md: 4 },
        }}
      >
        {/* Subtle Background Shapes */}
        <Box
          sx={{
            position: 'absolute',
            width: { xs: 300, md: 600 },
            height: { xs: 300, md: 600 },
            borderRadius: '50%',
            background: '#4f46e5',
            filter: 'blur(120px)',
            opacity: darkMode ? 0.15 : 0.05,
            top: { xs: -100, md: -200 },
            right: { xs: -100, md: -200 },
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            width: { xs: 250, md: 400 },
            height: { xs: 250, md: 400 },
            borderRadius: '50%',
            background: '#0891b2',
            filter: 'blur(120px)',
            opacity: darkMode ? 0.1 : 0.05,
            bottom: { xs: -50, md: -100 },
            left: { xs: -50, md: -100 },
          }}
        />

        {/* Hero Content */}
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 10, textAlign: 'center', py: 8 }}>
          {/* Badge */}
          <Box
            className="animate-fade-in-down"
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 1,
              px: 2.5,
              py: 1,
              mb: 4,
              borderRadius: 'var(--radius-full)',
              background: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(79, 70, 229, 0.1)',
              backdropFilter: 'blur(10px)',
              border: darkMode ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(79, 70, 229, 0.2)',
            }}
          >
            <AutoAwesome sx={{ fontSize: 18, color: '#fbbf24' }} />
            <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.9)' : 'text.primary', fontWeight: 600 }}>
              AI-Powered Media Analysis Platform
            </Typography>
          </Box>

          {/* Main Title */}
          <Typography
            variant="h1"
            component="h1"
            className="animate-fade-in-up stagger-1"
            sx={{
              fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4.5rem', lg: '5rem' },
              fontWeight: 800,
              lineHeight: 1.1,
              letterSpacing: '-0.03em',
              mb: 3,
              color: 'text.primary',
            }}
          >
            Uncover the{' '}
            <Box
              component="span"
              sx={{
                color: darkMode ? '#67e8f9' : '#0891b2',
              }}
            >
              Truth
            </Box>
            <br />
            Behind the News
          </Typography>

          {/* Subtitle */}
          <Typography
            variant="h5"
            className="animate-fade-in-up stagger-2"
            sx={{
              color: 'text.secondary',
              maxWidth: 700,
              mx: 'auto',
              mb: 6,
              fontWeight: 400,
              lineHeight: 1.6,
              fontSize: { xs: '1rem', md: '1.25rem' },
            }}
          >
            Advanced AI-powered analysis to detect bias, sentiment, and political leanings
            in news articles from multiple Bangladeshi media sources
          </Typography>

          {/* CTA Buttons */}
          <Box
            className="animate-fade-in-up stagger-3"
            sx={{
              display: 'flex',
              gap: 2,
              justifyContent: 'center',
              flexWrap: 'wrap',
              mb: 8,
            }}
          >
            <Button
              variant="contained"
              size="large"
              component={Link}
              to={isAuthenticated ? "/dashboard" : "/articles"}
              endIcon={<ArrowForward />}
              sx={{
                px: 4,
                py: 1.75,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 'var(--radius-xl)',
                background: '#4f46e5',
                boxShadow: '0 4px 16px rgba(79, 70, 229, 0.3)',
                '&:hover': {
                  background: '#4338ca',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(79, 70, 229, 0.4)',
                },
              }}
            >
              {isAuthenticated ? 'Go to Dashboard' : 'Explore Articles'}
            </Button>
            <Button
              variant="outlined"
              size="large"
              component={Link}
              to="/analyzer"
              startIcon={<PlayArrow />}
              sx={{
                px: 4,
                py: 1.75,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 'var(--radius-xl)',
                borderColor: darkMode ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.2)',
                borderWidth: 2,
                color: 'text.primary',
                backdropFilter: 'blur(10px)',
                '&:hover': {
                  borderColor: darkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.4)',
                  background: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              Try Analyzer
            </Button>
          </Box>

          {/* Stats Preview */}
          {!statsLoading && stats && (
            <Box
              className="animate-fade-in-up stagger-4"
              sx={{
                display: 'flex',
                justifyContent: 'center',
                gap: { xs: 3, md: 6 },
                flexWrap: 'wrap',
              }}
            >
              {[
                { value: stats.total_articles, label: 'Articles Analyzed' },
                { value: stats.total_sources || 6, label: 'News Sources' },
                { value: stats.analysis_coverage, label: '% AI Coverage', suffix: '%' },
              ].map((stat, index) => (
                <Box key={index} sx={{ textAlign: 'center' }}>
                  <Typography
                    variant="h3"
                    sx={{
                      fontWeight: 800,
                      color: darkMode ? '#a5b4fc' : '#4f46e5',
                      fontSize: { xs: '2rem', md: '2.5rem' },
                    }}
                  >
                    {stat.value.toLocaleString()}{stat.suffix || '+'}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'text.secondary',
                      fontWeight: 500,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      fontSize: '0.75rem',
                    }}
                  >
                    {stat.label}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Container>

        {/* Scroll Indicator */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 32,
            left: '50%',
            transform: 'translateX(-50%)',
            animation: 'bounce 2s infinite',
          }}
        >
          <Box
            sx={{
              width: 24,
              height: 40,
              borderRadius: 12,
              border: darkMode ? '2px solid rgba(255, 255, 255, 0.3)' : '2px solid rgba(0, 0, 0, 0.2)',
              display: 'flex',
              justifyContent: 'center',
              pt: 1,
            }}
          >
            <Box
              sx={{
                width: 4,
                height: 8,
                borderRadius: 2,
                background: darkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.4)',
                animation: 'float 1.5s ease-in-out infinite',
              }}
            />
          </Box>
        </Box>
      </Box>

      {/* ============ FEATURES SECTION ============ */}
      <Box sx={{ py: { xs: 10, md: 16 }, px: { xs: 2, md: 4 }, bgcolor: 'background.default' }}>
        <Container maxWidth="lg">
          {/* Section Header */}
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Typography
              variant="overline"
              sx={{
                color: 'var(--color-primary-500)',
                fontWeight: 700,
                letterSpacing: '0.1em',
                mb: 2,
                display: 'block',
              }}
            >
              POWERFUL FEATURES
            </Typography>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                mb: 3,
                fontSize: { xs: '2rem', md: '3rem' },
                letterSpacing: '-0.02em',
                color: 'text.primary',
              }}
            >
              Everything You Need to
              <Box
                component="span"
                sx={{
                  color: '#4f46e5',
                  ml: 1,
                }}
              >
                Analyze Media
              </Box>
            </Typography>
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{ maxWidth: 600, mx: 'auto', fontWeight: 400, lineHeight: 1.7 }}
            >
              Our platform combines cutting-edge AI with comprehensive data collection
              to give you deep insights into media bias patterns.
            </Typography>
          </Box>

          {/* Features Grid */}
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  className="card-feature"
                  sx={{
                    height: '100%',
                    p: 4,
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    bgcolor: 'background.paper',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 4,
                      background: feature.color,
                      transform: 'scaleX(0)',
                      transformOrigin: 'left',
                      transition: 'transform 0.4s ease',
                    },
                    '&:hover::before': {
                      transform: 'scaleX(1)',
                    },
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 'var(--shadow-xl)',
                    },
                    '&:hover .feature-icon-box': {
                      transform: 'scale(1.1) rotate(5deg)',
                    },
                  }}
                >
                  <Box
                    className="feature-icon-box"
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 'var(--radius-xl)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: feature.color,
                      color: '#ffffff',
                      mb: 3,
                      transition: 'all 0.4s ease',
                      boxShadow: `0 4px 12px ${feature.color}40`,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: 'text.primary' }}>
                    {feature.title}
                  </Typography>
                  <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    {feature.description}
                  </Typography>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ============ STATISTICS SECTION ============ */}
      {!statsLoading && stats && (
        <Box
          sx={{
            py: { xs: 10, md: 16 },
            px: { xs: 2, md: 4 },
            background: darkMode ? '#0f172a' : '#f1f5f9',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Background decoration */}
          <Box
            sx={{
              position: 'absolute',
              top: '20%',
              right: '10%',
              width: 300,
              height: 300,
              borderRadius: '50%',
              background: '#4f46e5',
              filter: 'blur(100px)',
              opacity: 0.15,
            }}
          />
          <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                color: 'text.primary',
                textAlign: 'center',
                mb: 2,
                fontSize: { xs: '2rem', md: '3rem' },
              }}
            >
              Platform Statistics
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'text.secondary',
                textAlign: 'center',
                mb: 8,
                maxWidth: 500,
                mx: 'auto',
                fontWeight: 400,
              }}
            >
              Real-time insights into our media analysis platform
            </Typography>

            <Grid container spacing={4}>
              {[
                { icon: <Article sx={{ fontSize: 40 }} />, value: stats.total_articles, label: 'Total Articles', color: '#6366f1' },
                { icon: <Psychology sx={{ fontSize: 40 }} />, value: stats.analyzed_articles, label: 'AI Analyzed', color: '#06b6d4' },
                { icon: <People sx={{ fontSize: 40 }} />, value: stats.total_users, label: 'Active Users', color: '#10b981' },
                { icon: <Assessment sx={{ fontSize: 40 }} />, value: `${stats.analysis_coverage}%`, label: 'Coverage Rate', color: '#f59e0b' },
              ].map((stat, index) => (
                <Grid item xs={6} md={3} key={index}>
                  <Box
                    sx={{
                      textAlign: 'center',
                      p: 4,
                      borderRadius: 'var(--radius-2xl)',
                      background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.6)',
                      backdropFilter: 'blur(10px)',
                      border: darkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.05)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.9)',
                        transform: 'translateY(-4px)',
                      },
                    }}
                  >
                    <Box sx={{ color: stat.color, mb: 2 }}>{stat.icon}</Box>
                    <Typography
                      variant="h3"
                      sx={{
                        fontWeight: 800,
                        color: 'text.primary',
                        mb: 1,
                        fontSize: { xs: '2rem', md: '2.5rem' },
                      }}
                    >
                      {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'text.secondary',
                        fontWeight: 500,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      {stat.label}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {/* Bias Distribution */}
            {stats.bias_distribution.length > 0 && (
              <Box sx={{ mt: 8 }}>
                <Typography
                  variant="h5"
                  sx={{ color: 'text.primary', textAlign: 'center', mb: 4, fontWeight: 600 }}
                >
                  Bias Distribution Analysis
                </Typography>
                <Grid container spacing={3} justifyContent="center">
                  {stats.bias_distribution.map((bias, index) => (
                    <Grid item xs={12} sm={4} key={index}>
                      <Box
                        sx={{
                          p: 3,
                          borderRadius: 'var(--radius-xl)',
                          background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.6)',
                          border: darkMode ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid rgba(0, 0, 0, 0.05)',
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Typography sx={{ color: 'text.primary', fontWeight: 600 }}>
                            {bias._id}
                          </Typography>
                          <Typography sx={{ color: 'text.secondary' }}>
                            {bias.count.toLocaleString()}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={stats.total_articles > 0 ? (bias.count / stats.total_articles) * 100 : 0}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              background: bias._id === 'Low Bias' ? '#10b981' :
                                bias._id === 'Moderate Bias' ? '#f59e0b' :
                                  '#ef4444',
                              borderRadius: 4,
                            },
                          }}
                        />
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Container>
        </Box>
      )}

      {/* ============ NEWS SOURCES SECTION ============ */}
      <Box sx={{ py: { xs: 10, md: 16 }, px: { xs: 2, md: 4 }, bgcolor: 'background.paper' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Typography
              variant="overline"
              sx={{
                color: 'var(--color-accent-500)',
                fontWeight: 700,
                letterSpacing: '0.1em',
                mb: 2,
                display: 'block',
              }}
            >
              TRUSTED SOURCES
            </Typography>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 800,
                mb: 3,
                fontSize: { xs: '2rem', md: '3rem' },
                color: 'text.primary',
              }}
            >
              Bangladeshi News Sources
              <Box
                component="span"
                sx={{
                  color: '#0891b2',
                  ml: 1,
                }}
              >
                We Monitor
              </Box>
            </Typography>
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{ maxWidth: 600, mx: 'auto', fontWeight: 400, lineHeight: 1.7 }}
            >
              We continuously collect and analyze articles from Bangladesh's leading news outlets
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {newsSources.map((source, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Box
                  sx={{
                    p: 4,
                    borderRadius: 'var(--radius-xl)',
                    bgcolor: 'var(--color-surface)',
                    border: '2px solid var(--color-border)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    '&:hover': {
                      borderColor: 'var(--color-primary-500)',
                      transform: 'translateY(-4px)',
                      boxShadow: 'var(--shadow-lg)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar
                      src={source.logoUrl}
                      alt={source.name}
                      sx={{
                        width: 64,
                        height: 64,
                        bgcolor: source.logoUrl ? 'transparent' : source.color,
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        mr: 2,
                        '& img': {
                          objectFit: 'contain',
                          width: '100%',
                          height: '100%'
                        }
                      }}
                    >
                      {!source.logoUrl && source.name.substring(0, 2).toUpperCase()}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary' }}>
                        {source.name}
                      </Typography>
                      <Chip
                        size="small"
                        label={source.language}
                        sx={{
                          bgcolor: source.language === 'English' ? 'var(--color-primary-100)' : 'var(--color-accent-100)',
                          color: source.language === 'English' ? 'var(--color-primary-700)' : 'var(--color-accent-700)',
                          fontWeight: 600,
                          fontSize: '0.7rem',
                        }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    {source.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ============ CTA SECTION ============ */}
      <Box
        className="cta-section"
        sx={{
          py: { xs: 12, md: 20 },
          px: { xs: 2, md: 4 },
          position: 'relative',
          overflow: 'hidden',
          background: '#1e1b4b',
        }}
      >
        <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 1,
              bgcolor: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              borderRadius: 'var(--radius-full)',
              px: 3,
              py: 1,
              mb: 4,
            }}
          >
            <Bolt sx={{ color: '#fbbf24' }} />
            <Typography sx={{ color: '#ffffff', fontWeight: 600 }}>
              Start Analyzing Today
            </Typography>
          </Box>

          <Typography
            variant="h2"
            sx={{
              fontWeight: 800,
              color: '#ffffff',
              mb: 3,
              fontSize: { xs: '2.5rem', md: '4rem' },
              lineHeight: 1.1,
            }}
          >
            Ready to Uncover
            <br />
            Media Bias?
          </Typography>

          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.8)',
              mb: 6,
              maxWidth: 500,
              mx: 'auto',
              fontWeight: 400,
              lineHeight: 1.7,
            }}
          >
            Join thousands of users who trust our platform for unbiased news analysis.
            Make informed decisions based on facts.
          </Typography>

          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/analyzer')}
              sx={{
                px: 5,
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 700,
                bgcolor: '#ffffff',
                color: 'var(--color-primary-600)',
                borderRadius: 'var(--radius-xl)',
                textTransform: 'none',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
                '&:hover': {
                  bgcolor: '#f0f0f0',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 40px rgba(0, 0, 0, 0.3)',
                },
              }}
              endIcon={<ArrowForward />}
            >
              Get Started Free
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/articles')}
              sx={{
                px: 5,
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 700,
                color: '#ffffff',
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderRadius: 'var(--radius-xl)',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#ffffff',
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Browse Articles
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;