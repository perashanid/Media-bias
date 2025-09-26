import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Chip,
  Grid,
} from '@mui/material';
import { BiasScore } from '../types/Article';

interface BiasScoreCardProps {
  biasScore: BiasScore;
  showDetails?: boolean;
}

const BiasScoreCard: React.FC<BiasScoreCardProps> = ({ biasScore, showDetails = true }) => {
  const getBiasLevel = (score: number): { label: string; color: 'success' | 'warning' | 'error' } => {
    if (score < 0.3) return { label: 'Low Bias', color: 'success' };
    if (score < 0.6) return { label: 'Moderate Bias', color: 'warning' };
    return { label: 'High Bias', color: 'error' };
  };

  const getSentimentLabel = (score: number): string => {
    if (score > 0.1) return 'Positive';
    if (score < -0.1) return 'Negative';
    return 'Neutral';
  };

  const getPoliticalBiasLabel = (score: number): string => {
    if (score > 0.2) return 'Right-leaning';
    if (score < -0.2) return 'Left-leaning';
    return 'Neutral';
  };

  const getFactualLabel = (score: number): string => {
    if (score > 0.7) return 'Factual';
    if (score < 0.3) return 'Opinion';
    return 'Mixed';
  };

  const biasLevel = getBiasLevel(biasScore.overall_bias_score);

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Bias Analysis</Typography>
          <Chip label={biasLevel.label} color={biasLevel.color} />
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Overall Bias Score
          </Typography>
          <LinearProgress
            variant="determinate"
            value={biasScore.overall_bias_score * 100}
            color={biasLevel.color}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="text.secondary">
            {(biasScore.overall_bias_score * 100).toFixed(1)}%
          </Typography>
        </Box>

        {showDetails && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Sentiment: {getSentimentLabel(biasScore.sentiment_score)}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={Math.abs(biasScore.sentiment_score) * 100}
                  color={biasScore.sentiment_score > 0 ? 'success' : 'error'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {biasScore.sentiment_score.toFixed(2)}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Political: {getPoliticalBiasLabel(biasScore.political_bias_score)}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={Math.abs(biasScore.political_bias_score) * 100}
                  color={Math.abs(biasScore.political_bias_score) > 0.3 ? 'warning' : 'success'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {biasScore.political_bias_score.toFixed(2)}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Emotional Language
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={biasScore.emotional_language_score * 100}
                  color={biasScore.emotional_language_score > 0.5 ? 'warning' : 'success'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {(biasScore.emotional_language_score * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Content: {getFactualLabel(biasScore.factual_vs_opinion_score)}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={biasScore.factual_vs_opinion_score * 100}
                  color={biasScore.factual_vs_opinion_score > 0.5 ? 'success' : 'warning'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {(biasScore.factual_vs_opinion_score * 100).toFixed(1)}% factual
                </Typography>
              </Box>
            </Grid>
          </Grid>
        )}

        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
          Analyzed: {new Date(biasScore.analyzed_at).toLocaleString()}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default BiasScoreCard;