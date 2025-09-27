import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Assessment,
  Article,
  Compare,
  Analytics,
  CloudDownload,
  CheckCircle,
  Psychology,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
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
          <Button variant="contained" size="large" component={Link} to="/dashboard" startIcon={<Assessment />}>
            View Dashboard
          </Button>
          <Button variant="outlined" size="large" component={Link} to="/articles" startIcon={<Article />}>
            Browse Articles
          </Button>
          <Button variant="outlined" size="large" component={Link} to="/analyzer" startIcon={<Analytics />}>
            Analyze Text
          </Button>
        </Box>
      </Box>

      {/* About Section */}
      <Paper sx={{ 
        p: { xs: 4, md: 6 }, 
        mb: 8, 
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'grey.200',
        borderRadius: 3,
      }}>
        <Typography variant="h2" gutterBottom sx={{ textAlign: 'center', mb: 2, color: 'primary.main' }}>
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
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(65, 90, 119, 0.2)' : 'rgba(13, 27, 42, 0.1)',
                color: 'primary.main',
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
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(119, 141, 169, 0.2)' : 'rgba(65, 90, 119, 0.1)',
                color: 'secondary.main',
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
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(65, 90, 119, 0.2)' : 'rgba(13, 27, 42, 0.1)',
                mb: 3,
              }}>
                <CloudDownload sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Data Collection
              </Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Automatically scrapes articles from multiple Bangladeshi news sources including Prothom Alo, Daily Star, BD Pratidin, Ekattor TV, and ATN News.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                display: 'inline-flex',
                p: 3,
                borderRadius: '50%',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(76, 175, 80, 0.2)' : 'rgba(76, 175, 80, 0.1)',
                mb: 3,
              }}>
                <Psychology sx={{ fontSize: 40, color: 'success.main' }} />
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
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(33, 150, 243, 0.2)' : 'rgba(33, 150, 243, 0.1)',
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
                  <CheckCircle color="success" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Multi-Source Analysis</Typography>}
                  secondary={<Typography color="text.secondary">Analyze articles from 5+ major Bangladeshi news sources</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Bias Detection</Typography>}
                  secondary={<Typography color="text.secondary">Detect political bias, sentiment, and emotional language patterns</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Cross-Source Comparison</Typography>}
                  secondary={<Typography color="text.secondary">Compare how different sources cover the same story</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Real-time Scraping</Typography>}
                  secondary={<Typography color="text.secondary">Continuously collect and analyze new articles</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" sx={{ fontSize: 28 }} />
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
                  <Psychology color="primary" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Political Bias Score</Typography>}
                  secondary={<Typography color="text.secondary">0-40%: Left-leaning, 40-60%: Center, 60-100%: Right-leaning. Analyzes word choices, framing, and political indicators.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology color="primary" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Sentiment Analysis</Typography>}
                  secondary={<Typography color="text.secondary">Negative: Critical/pessimistic tone, Neutral: Balanced reporting, Positive: Optimistic/supportive tone.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology color="primary" sx={{ fontSize: 28 }} />
                </ListItemIcon>
                <ListItemText 
                  primary={<Typography variant="h6" sx={{ fontWeight: 500 }}>Emotional Language</Typography>}
                  secondary={<Typography color="text.secondary">Measures use of emotionally charged words, dramatic language, and subjective expressions vs neutral reporting.</Typography>}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ mt: 0.5 }}>
                  <Psychology color="primary" sx={{ fontSize: 28 }} />
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
              <Typography variant="h5" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
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
              <Typography variant="h5" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
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
              <Typography variant="h5" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
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
              <Typography variant="h5" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
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
              <Typography variant="h5" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
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
              bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(65, 90, 119, 0.1)' : 'rgba(0, 0, 0, 0.02)',
              border: '2px dashed',
              borderColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(119, 141, 169, 0.3)' : 'rgba(0, 0, 0, 0.12)',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(65, 90, 119, 0.2)' : 'rgba(13, 27, 42, 0.05)',
              }
            }}>
              <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 600, mb: 1 }}>
                More Sources
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Continuously expanding coverage
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Get Started Section */}
      <Paper sx={{ 
        p: { xs: 4, md: 6 }, 
        textAlign: 'center', 
        background: (theme) => theme.palette.mode === 'dark'
          ? 'linear-gradient(135deg, #415A77 0%, #778DA9 100%)'
          : 'linear-gradient(135deg, #0D1B2A 0%, #1B263B 100%)',
        color: 'white',
        borderRadius: 3,
      }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600 }}>
          Get Started
        </Typography>
        <Typography variant="h6" paragraph sx={{ 
          opacity: 0.9, 
          maxWidth: '600px', 
          mx: 'auto',
          fontWeight: 400,
          lineHeight: 1.6,
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
          <Button 
            variant="contained" 
            size="large" 
            component={Link} 
            to="/dashboard" 
            sx={{ 
              bgcolor: 'white', 
              color: 'primary.main', 
              '&:hover': { 
                bgcolor: 'grey.100',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
              } 
            }}
          >
            View Dashboard
          </Button>
          <Button 
            variant="outlined" 
            size="large" 
            component={Link} 
            to="/scraper" 
            sx={{ 
              borderColor: 'white', 
              color: 'white', 
              '&:hover': { 
                borderColor: 'grey.300', 
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