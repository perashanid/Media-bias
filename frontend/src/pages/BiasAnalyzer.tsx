import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  MenuItem,
  Divider,
  Container,
  Chip,
} from '@mui/material';
import { Analytics, Clear, AutoAwesome, Psychology, TrendingUp, Bolt } from '@mui/icons-material';
import { biasApi } from '../services/api';
import { useDashboard } from '../contexts/DashboardContext';
import { BiasAnalysisResult } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';

const BiasAnalyzer: React.FC = () => {
  const { triggerRefresh } = useDashboard();
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('');
  const [result, setResult] = useState<BiasAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const analysisResult = await biasApi.analyzeText(text, language || undefined);
      setResult(analysisResult);
      triggerRefresh(); // Refresh dashboard after analysis

    } catch (err) {
      setError('Failed to analyze text. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setLanguage('');
    setResult(null);
    setError(null);
  };

  const getBiasScoreFromResult = (result: BiasAnalysisResult) => {
    return {
      sentiment_score: result.sentiment_score,
      political_bias_score: result.political_bias_score,
      emotional_language_score: result.emotional_language_score,
      factual_vs_opinion_score: result.factual_vs_opinion_score,
      overall_bias_score: result.overall_bias_score,
      analyzed_at: new Date().toISOString(),
    };
  };

  const getBiasClassificationColor = (classification: string) => {
    switch (classification) {
      case 'low_bias':
        return 'var(--color-success)';
      case 'moderate_bias':
        return 'var(--color-warning)';
      case 'high_bias':
      case 'very_high_bias':
        return 'var(--color-error)';
      default:
        return 'var(--color-text-muted)';
    }
  };

  const getBiasClassificationLabel = (classification: string) => {
    switch (classification) {
      case 'low_bias':
        return 'Low Bias';
      case 'moderate_bias':
        return 'Moderate Bias';
      case 'high_bias':
        return 'High Bias';
      case 'very_high_bias':
        return 'Very High Bias';
      default:
        return 'Unknown';
    }
  };

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
        {/* Background decoration */}
        <Box
          sx={{
            position: 'absolute',
            top: '10%',
            right: '5%',
            width: 300,
            height: 300,
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
            left: '10%',
            width: 250,
            height: 250,
            borderRadius: '50%',
            background: '#4f46e5',
            filter: 'blur(100px)',
            opacity: 0.1,
          }}
        />
        
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
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
              <Psychology sx={{ color: '#67e8f9', fontSize: 28 }} />
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
              Bias Analyzer
            </Typography>
          </Box>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: 400,
              maxWidth: 600,
              lineHeight: 1.7,
            }}
          >
            Analyze any text for bias using our advanced AI. Detect sentiment, political leanings, 
            emotional language, and factual content in both Bengali and English.
          </Typography>

          {/* Feature badges */}
          <Box sx={{ display: 'flex', gap: 2, mt: 4, flexWrap: 'wrap' }}>
            {[
              { icon: <Bolt />, label: 'Real-time Analysis' },
              { icon: <TrendingUp />, label: 'Multi-metric Scoring' },
              { icon: <AutoAwesome />, label: 'AI Powered' },
            ].map((badge, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 1,
                  borderRadius: 'var(--radius-full)',
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                }}
              >
                <Box sx={{ color: '#fbbf24' }}>{badge.icon}</Box>
                <Typography variant="body2" sx={{ color: '#ffffff', fontWeight: 500 }}>
                  {badge.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Input Section */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                borderRadius: 'var(--radius-2xl)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-lg)',
                overflow: 'hidden',
              }}
            >
              {/* Card header bar */}
              <Box
                sx={{
                  height: 4,
                  background: '#0891b2',
                }}
              />
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-accent-100)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Analytics sx={{ color: 'var(--color-accent-600)' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    Text Input
                  </Typography>
                </Box>

                <TextField
                  fullWidth
                  multiline
                  rows={12}
                  placeholder="Enter the text you want to analyze for bias..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  sx={{ 
                    mb: 3,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 'var(--radius-xl)',
                      backgroundColor: 'var(--color-background)',
                      '&.Mui-focused': {
                        boxShadow: '0 0 0 3px rgba(6, 182, 212, 0.15)',
                      },
                    }
                  }}
                />

                <TextField
                  select
                  fullWidth
                  label="Language (Optional)"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  sx={{ 
                    mb: 3,
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 'var(--radius-xl)',
                    }
                  }}
                >
                  <MenuItem value="">Auto-detect</MenuItem>
                  <MenuItem value="bengali">Bengali</MenuItem>
                  <MenuItem value="english">English</MenuItem>
                </TextField>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleAnalyze}
                    disabled={loading || !text.trim()}
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Analytics />}
                    sx={{ 
                      flex: 1,
                      py: 1.75,
                      borderRadius: 'var(--radius-xl)',
                      background: '#0891b2',
                      fontWeight: 600,
                      textTransform: 'none',
                      fontSize: '1rem',
                      boxShadow: '0 2px 8px rgba(8, 145, 178, 0.25)',
                      '&:hover': {
                        background: '#0e7490',
                        boxShadow: '0 4px 12px rgba(8, 145, 178, 0.35)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    {loading ? 'Analyzing...' : 'Analyze Bias'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    onClick={handleClear}
                    startIcon={<Clear />}
                    sx={{ 
                      py: 1.75,
                      px: 3,
                      borderRadius: 'var(--radius-xl)',
                      borderColor: 'var(--color-border)',
                      color: 'var(--color-text-secondary)',
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': {
                        borderColor: 'var(--color-error)',
                        color: 'var(--color-error)',
                        backgroundColor: 'rgba(239, 68, 68, 0.05)',
                      },
                    }}
                  >
                    Clear
                  </Button>
                </Box>

                {error && (
                  <Alert 
                    severity="error" 
                    sx={{ 
                      mt: 3,
                      borderRadius: 'var(--radius-xl)',
                    }}
                  >
                    {error}
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Results Section */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                borderRadius: 'var(--radius-2xl)',
                border: '1px solid var(--color-border)',
                boxShadow: 'var(--shadow-lg)',
                overflow: 'hidden',
                height: '100%',
              }}
            >
              {/* Card header bar */}
              <Box
                sx={{
                  height: 4,
                  background: result 
                    ? getBiasClassificationColor(result.bias_classification)
                    : '#4f46e5',
                }}
              />
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-primary-100)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <TrendingUp sx={{ color: 'var(--color-primary-600)' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    Analysis Results
                  </Typography>
                </Box>

                {result ? (
                  <>
                    {/* Overall Classification */}
                    <Box 
                      sx={{ 
                        mb: 4,
                        p: 3,
                        borderRadius: 'var(--radius-xl)',
                        background: 'var(--color-surface-elevated)',
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      <Typography variant="body2" sx={{ color: 'var(--color-text-muted)', mb: 2 }}>
                        Overall Classification
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                        <Typography 
                          variant="h4" 
                          sx={{ 
                            fontWeight: 800,
                            color: getBiasClassificationColor(result.bias_classification),
                          }}
                        >
                          {getBiasClassificationLabel(result.bias_classification)}
                        </Typography>
                        <Chip
                          label={`${(result.overall_bias_score * 100).toFixed(1)}% bias`}
                          sx={{
                            fontWeight: 700,
                            borderRadius: 'var(--radius-lg)',
                            background: `${getBiasClassificationColor(result.bias_classification)}20`,
                            color: getBiasClassificationColor(result.bias_classification),
                          }}
                        />
                      </Box>
                    </Box>

                    <Divider sx={{ mb: 3 }} />

                    {/* Detailed Scores */}
                    <BiasScoreCard 
                      biasScore={getBiasScoreFromResult(result)} 
                      showDetails={true} 
                    />

                    <Divider sx={{ my: 3 }} />

                    {/* Additional Information */}
                    <Box 
                      sx={{ 
                        display: 'flex', 
                        gap: 2, 
                        flexWrap: 'wrap',
                      }}
                    >
                      <Chip
                        label={`Language: ${result.language}`}
                        variant="outlined"
                        sx={{ borderRadius: 'var(--radius-lg)' }}
                      />
                      <Chip
                        label={`${text.length} characters`}
                        variant="outlined"
                        sx={{ borderRadius: 'var(--radius-lg)' }}
                      />
                      <Chip
                        label={`${text.split(/\s+/).filter(word => word.length > 0).length} words`}
                        variant="outlined"
                        sx={{ borderRadius: 'var(--radius-lg)' }}
                      />
                    </Box>
                  </>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <Box
                      sx={{
                        width: 80,
                        height: 80,
                        borderRadius: '50%',
                        background: 'var(--color-surface-elevated)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 3,
                      }}
                    >
                      <Psychology sx={{ fontSize: 40, color: 'var(--color-text-muted)' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Ready to Analyze
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'var(--color-text-secondary)', mb: 4 }}>
                      Enter text and click "Analyze Bias" to see detailed results here.
                    </Typography>
                    
                    <Box sx={{ textAlign: 'left', maxWidth: 300, mx: 'auto' }}>
                      <Typography variant="body2" sx={{ color: 'var(--color-text-muted)', mb: 2 }}>
                        The analysis will detect:
                      </Typography>
                      {[
                        'Sentiment (positive/negative/neutral)',
                        'Political bias (left/right leaning)',
                        'Emotional language intensity',
                        'Factual vs opinion content',
                        'Overall bias classification',
                      ].map((item, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Box
                            sx={{
                              width: 6,
                              height: 6,
                              borderRadius: '50%',
                              background: '#0891b2',
                            }}
                          />
                          <Typography variant="body2" sx={{ color: 'var(--color-text-secondary)' }}>
                            {item}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Sample Texts */}
        <Card 
          sx={{ 
            mt: 4,
            borderRadius: 'var(--radius-2xl)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-md)',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 4 }}>
              Sample Texts for Testing
            </Typography>
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Box
                  sx={{
                    p: 3,
                    borderRadius: 'var(--radius-xl)',
                    background: 'var(--color-surface-elevated)',
                    border: '1px solid var(--color-border)',
                    height: '100%',
                  }}
                >
                  <Chip 
                    label="Bengali - Political" 
                    size="small" 
                    sx={{ 
                      mb: 2,
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-warning)',
                      color: '#ffffff',
                      fontWeight: 600,
                    }}
                  />
                  <Typography variant="body2" sx={{ color: 'var(--color-text-secondary)', mb: 3, lineHeight: 1.8 }}>
                    সরকারের এই যুগান্তকারী সিদ্ধান্ত দেশের উন্নয়নে অসাধারণ অবদান রাখবে। প্রধানমন্ত্রীর দূরদর্শী নেতৃত্বে বাংলাদেশ এগিয়ে চলেছে।
                  </Typography>
                  <Button 
                    variant="outlined"
                    size="small"
                    onClick={() => setText('সরকারের এই যুগান্তকারী সিদ্ধান্ত দেশের উন্নয়নে অসাধারণ অবদান রাখবে। প্রধানমন্ত্রীর দূরদর্শী নেতৃত্বে বাংলাদেশ এগিয়ে চলেছে।')}
                    sx={{
                      borderRadius: 'var(--radius-lg)',
                      fontWeight: 600,
                      textTransform: 'none',
                    }}
                  >
                    Use This Text
                  </Button>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box
                  sx={{
                    p: 3,
                    borderRadius: 'var(--radius-xl)',
                    background: 'var(--color-surface-elevated)',
                    border: '1px solid var(--color-border)',
                    height: '100%',
                  }}
                >
                  <Chip 
                    label="English - Neutral" 
                    size="small" 
                    sx={{ 
                      mb: 2,
                      borderRadius: 'var(--radius-lg)',
                      background: 'var(--color-success)',
                      color: '#ffffff',
                      fontWeight: 600,
                    }}
                  />
                  <Typography variant="body2" sx={{ color: 'var(--color-text-secondary)', mb: 3, lineHeight: 1.8 }}>
                    The government announced new economic policies yesterday. According to official sources, the measures are designed to address inflation concerns. The implementation will begin next month.
                  </Typography>
                  <Button 
                    variant="outlined"
                    size="small"
                    onClick={() => setText('The government announced new economic policies yesterday. According to official sources, the measures are designed to address inflation concerns. The implementation will begin next month.')}
                    sx={{
                      borderRadius: 'var(--radius-lg)',
                      fontWeight: 600,
                      textTransform: 'none',
                    }}
                  >
                    Use This Text
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default BiasAnalyzer;