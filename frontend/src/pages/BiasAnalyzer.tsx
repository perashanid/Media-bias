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
} from '@mui/material';
import { Analytics, Clear } from '@mui/icons-material';
import { biasApi } from '../services/api';
import { BiasAnalysisResult } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';

const BiasAnalyzer: React.FC = () => {
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
        return 'success';
      case 'moderate_bias':
        return 'warning';
      case 'high_bias':
      case 'very_high_bias':
        return 'error';
      default:
        return 'default';
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
    <Box>
      <Typography variant="h4" gutterBottom>
        Bias Analyzer
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Enter any text to analyze its bias characteristics. This tool can detect sentiment, 
        political bias, emotional language, and factual vs opinion content in both Bengali and English.
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Text Input
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={12}
                placeholder="Enter the text you want to analyze for bias..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                sx={{ mb: 2 }}
              />

              <TextField
                select
                label="Language (Optional)"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                sx={{ mb: 2, minWidth: 200 }}
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
                  startIcon={loading ? <CircularProgress size={20} /> : <Analytics />}
                  sx={{ flexGrow: 1 }}
                >
                  {loading ? 'Analyzing...' : 'Analyze Bias'}
                </Button>
                
                <Button
                  variant="outlined"
                  onClick={handleClear}
                  startIcon={<Clear />}
                >
                  Clear
                </Button>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          {result ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>

                {/* Overall Classification */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Overall Classification
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h5">
                      {getBiasClassificationLabel(result.bias_classification)}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        px: 2, 
                        py: 0.5, 
                        borderRadius: 1, 
                        bgcolor: `${getBiasClassificationColor(result.bias_classification)}.light`,
                        color: `${getBiasClassificationColor(result.bias_classification)}.dark`
                      }}
                    >
                      {(result.overall_bias_score * 100).toFixed(1)}% bias
                    </Typography>
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
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Detected Language: <strong>{result.language}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Text Length: <strong>{text.length} characters</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Word Count: <strong>{text.split(/\s+/).filter(word => word.length > 0).length} words</strong>
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Enter text and click "Analyze Bias" to see detailed bias analysis results here.
                </Typography>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    The analysis will provide:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>
                      <Typography variant="body2" color="text.secondary">
                        Sentiment analysis (positive/negative/neutral)
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" color="text.secondary">
                        Political bias detection (left/right leaning)
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" color="text.secondary">
                        Emotional language intensity
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" color="text.secondary">
                        Factual vs opinion content classification
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2" color="text.secondary">
                        Overall bias score and classification
                      </Typography>
                    </li>
                  </ul>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Sample Texts */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Sample Texts for Testing
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Bengali Sample (Political)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                সরকারের এই যুগান্তকারী সিদ্ধান্ত দেশের উন্নয়নে অসাধারণ অবদান রাখবে। প্রধানমন্ত্রীর দূরদর্শী নেতৃত্বে বাংলাদেশ এগিয়ে চলেছে।
              </Typography>
              <Button 
                size="small" 
                onClick={() => setText('সরকারের এই যুগান্তকারী সিদ্ধান্ত দেশের উন্নয়নে অসাধারণ অবদান রাখবে। প্রধানমন্ত্রীর দূরদর্শী নেতৃত্বে বাংলাদেশ এগিয়ে চলেছে।')}
              >
                Use This Text
              </Button>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                English Sample (Neutral)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                The government announced new economic policies yesterday. According to official sources, the measures are designed to address inflation concerns. The implementation will begin next month.
              </Typography>
              <Button 
                size="small" 
                onClick={() => setText('The government announced new economic policies yesterday. According to official sources, the measures are designed to address inflation concerns. The implementation will begin next month.')}
              >
                Use This Text
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BiasAnalyzer;