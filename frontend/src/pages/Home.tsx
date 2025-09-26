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
      <Box sx={{ textAlign: 'center', py: 8, mb: 6 }}>
        <Typography variant="h2" component="h1" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 2 }}>
          Media Bias Detector
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph sx={{ maxWidth: '800px', mx: 'auto', mb: 4 }}>
          Advanced AI-powered analysis to detect bias, sentiment, and political leanings in news articles from multiple Bangladeshi sources
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
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
      <Paper sx={{ p: 4, mb: 6, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4, color: 'primary.main' }}>
          About Media Bias Detector
        </Typography>
        <Typography variant="h6" paragraph sx={{ textAlign: 'center', mb: 4, color: 'text.secondary' }}>
          An AI-powered platform for analyzing media bias in Bangladeshi news sources
        </Typography>
        
        <Grid container spacing={4} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              🎯 What We Do
            </Typography>
            <Typography paragraph>
              We automatically collect and analyze news articles from major Bangladeshi media outlets to detect bias patterns, 
              sentiment variations, and coverage differences across sources. Our platform helps readers understand how different 
              news sources present the same stories.
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              🤖 How We Do It
            </Typography>
            <Typography paragraph>
              Using advanced Natural Language Processing (NLP) and machine learning algorithms, we analyze article content for 
              political bias, emotional language, sentiment, and factual vs opinion content. Our AI models are specifically 
              trained to understand both Bengali and English text patterns.
            </Typography>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
          How It Works
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <CloudDownload sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                1. Data Collection
              </Typography>
              <Typography color="text.secondary">
                Automatically scrapes articles from multiple Bangladeshi news sources including Prothom Alo, Daily Star, BD Pratidin, Ekattor TV, and ATN News.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Psychology sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                2. AI Analysis
              </Typography>
              <Typography color="text.secondary">
                Advanced NLP algorithms analyze sentiment, political bias, emotional language, and factual vs opinion content using machine learning models trained on news data.
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Compare sx={{ fontSize: 60, color: 'info.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                3. Comparison & Insights
              </Typography>
              <Typography color="text.secondary">
                Compare how different sources cover the same story, identify bias patterns, and get detailed reports on media coverage differences and similarities.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Features Section */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Key Features
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Multi-Source Analysis" 
                  secondary="Analyze articles from 5+ major Bangladeshi news sources"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Bias Detection" 
                  secondary="Detect political bias, sentiment, and emotional language patterns"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Cross-Source Comparison" 
                  secondary="Compare how different sources cover the same story"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Real-time Scraping" 
                  secondary="Continuously collect and analyze new articles"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText 
                  primary="Multi-language Support" 
                  secondary="Analyze both Bengali and English articles"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Analysis Metrics Explained
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <Psychology color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Political Bias Score (0-100%)" 
                  secondary="0-40%: Left-leaning, 40-60%: Center, 60-100%: Right-leaning. Analyzes word choices, framing, and political indicators."
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Psychology color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Sentiment Analysis (-100% to +100%)" 
                  secondary="Negative: Critical/pessimistic tone, Neutral: Balanced reporting, Positive: Optimistic/supportive tone."
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Psychology color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Emotional Language (0-100%)" 
                  secondary="Measures use of emotionally charged words, dramatic language, and subjective expressions vs neutral reporting."
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Psychology color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Factual vs Opinion (0-100%)" 
                  secondary="0%: Pure opinion/editorial, 50%: Mixed content, 100%: Pure factual reporting with verifiable information."
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* News Sources Section */}
      <Paper sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4 }}>
          News Sources We Monitor
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary">Prothom Alo</Typography>
              <Typography variant="body2" color="text.secondary">Leading Bengali daily newspaper</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary">The Daily Star</Typography>
              <Typography variant="body2" color="text.secondary">Premier English daily newspaper</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary">BD Pratidin</Typography>
              <Typography variant="body2" color="text.secondary">Popular Bengali news portal</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary">Ekattor TV</Typography>
              <Typography variant="body2" color="text.secondary">24/7 news television channel</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary">ATN News</Typography>
              <Typography variant="body2" color="text.secondary">Satellite news channel</Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Card sx={{ textAlign: 'center', p: 2, bgcolor: 'action.hover' }}>
              <Typography variant="h6" color="text.secondary">+ More Sources</Typography>
              <Typography variant="body2" color="text.secondary">Continuously expanding coverage</Typography>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Get Started Section */}
      <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h4" gutterBottom>
          Get Started
        </Typography>
        <Typography variant="h6" paragraph sx={{ opacity: 0.9 }}>
          Explore media bias patterns and make informed decisions about news consumption
        </Typography>
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button variant="contained" size="large" component={Link} to="/dashboard" sx={{ bgcolor: 'white', color: 'primary.main', '&:hover': { bgcolor: 'grey.100' } }}>
            View Dashboard
          </Button>
          <Button variant="outlined" size="large" component={Link} to="/scraper" sx={{ borderColor: 'white', color: 'white', '&:hover': { borderColor: 'grey.300', bgcolor: 'rgba(255,255,255,0.1)' } }}>
            Manual Scraper
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Home;