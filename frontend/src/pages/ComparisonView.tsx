import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Alert,
  CircularProgress,

  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,

  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
} from '@mui/material';
import { 
  Compare, 
  TrendingUp, 
  TrendingDown, 
  Add, 
  Delete, 
  Link, 
  TextFields, 
  Article as ArticleIcon 
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { comparisonApi, articlesApi } from '../services/api';
import { Article, ComparisonReport } from '../types/Article';
import BiasScoreCard from '../components/BiasScoreCard';

interface ComparisonInput {
  id: string;
  type: 'url' | 'text' | 'article_id';
  value: string;
  title?: string;
  source?: string;
  language?: string;
}

const ComparisonView: React.FC = () => {
  const [searchParams] = useSearchParams();
  const articleId = searchParams.get('article');

  const [targetArticle, setTargetArticle] = useState<Article | null>(null);
  const [comparisonReport, setComparisonReport] = useState<ComparisonReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Custom comparison state
  const [customMode, setCustomMode] = useState(false);
  const [comparisonInputs, setComparisonInputs] = useState<ComparisonInput[]>([]);
  const [addInputDialog, setAddInputDialog] = useState(false);
  const [newInputType, setNewInputType] = useState<'url' | 'text' | 'article_id'>('url');
  const [newInputValue, setNewInputValue] = useState('');
  const [newInputTitle, setNewInputTitle] = useState('');
  const [newInputSource, setNewInputSource] = useState('');
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (articleId && !customMode) {
      fetchComparison(articleId);
    }
  }, [articleId, customMode]);

  const fetchComparison = async (id: string) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch target article
      const article = await articlesApi.getArticle(id);
      setTargetArticle(article);

      // Fetch comparison report
      const report = await comparisonApi.getComparisonReport(id);
      setComparisonReport(report);

    } catch (err: any) {
      if (err.response?.status === 404 || err.response?.data?.message?.includes('No related articles')) {
        setError('No related articles found for comparison. This article may be unique or too recent.');
      } else {
        setError('Failed to generate comparison report');
      }
      console.error('Comparison error:', err);
    } finally {
      setLoading(false);
    }
  };

  const performCustomComparison = async () => {
    if (comparisonInputs.length < 2) {
      setError('At least 2 inputs are required for comparison');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setTargetArticle(null);

      const report = await comparisonApi.customComparison(comparisonInputs);
      setComparisonReport(report);

    } catch (err: any) {
      setError('Failed to perform custom comparison');
      console.error('Custom comparison error:', err);
    } finally {
      setLoading(false);
    }
  };

  const addComparisonInput = () => {
    if (!newInputValue.trim()) return;

    const newInput: ComparisonInput = {
      id: Date.now().toString(),
      type: newInputType,
      value: newInputValue.trim(),
      title: newInputTitle.trim() || undefined,
      source: newInputSource.trim() || undefined,
      language: 'en',
    };

    setComparisonInputs([...comparisonInputs, newInput]);
    setNewInputValue('');
    setNewInputTitle('');
    setNewInputSource('');
    setAddInputDialog(false);
  };

  const removeComparisonInput = (id: string) => {
    setComparisonInputs(comparisonInputs.filter(input => input.id !== id));
  };

  const getInputTypeIcon = (type: string) => {
    switch (type) {
      case 'url': return <Link />;
      case 'text': return <TextFields />;
      case 'article_id': return <ArticleIcon />;
      default: return <Compare />;
    }
  };

  const getBiasComparisonData = () => {
    if (!comparisonReport) return [];

    return comparisonReport.articles.map(article => ({
      source: article.source,
      sentiment: article.bias_scores?.sentiment_score || 0,
      political_bias: article.bias_scores?.political_bias_score || 0,
      emotional_language: article.bias_scores?.emotional_language_score || 0,
      factual_content: article.bias_scores?.factual_vs_opinion_score || 0,
      overall_bias: article.bias_scores?.overall_bias_score || 0,
    }));
  };

  const getBiasDifferenceIcon = (difference: number) => {
    if (difference > 10) return <TrendingUp color="error" />;
    if (difference < -10) return <TrendingDown color="success" />;
    return null;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !customMode) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Article Comparison
        </Typography>
        <Alert severity="warning">{error}</Alert>
        <Button 
          variant="contained" 
          onClick={() => setCustomMode(true)}
          sx={{ mt: 2 }}
        >
          Try Custom Comparison
        </Button>
      </Box>
    );
  }

  if (!customMode && (!targetArticle || !comparisonReport)) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Article Comparison
        </Typography>
        <Alert severity="info">
          Select an article to compare with similar articles from other sources.
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => setCustomMode(true)}
          sx={{ mt: 2 }}
        >
          Create Custom Comparison
        </Button>
      </Box>
    );
  }

  const biasData = getBiasComparisonData();

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Article Comparison
        </Typography>
        <Box>
          <Button
            variant={customMode ? 'outlined' : 'contained'}
            onClick={() => setCustomMode(false)}
            sx={{ mr: 1 }}
            disabled={!articleId}
          >
            Auto Comparison
          </Button>
          <Button
            variant={customMode ? 'contained' : 'outlined'}
            onClick={() => setCustomMode(true)}
          >
            Custom Comparison
          </Button>
        </Box>
      </Box>

      {customMode && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Custom Comparison Setup
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add multiple URLs, text snippets, or article IDs to compare their bias patterns.
            </Typography>

            {/* Comparison Inputs */}
            <Box sx={{ mb: 2 }}>
              {comparisonInputs.map((input) => (
                <Card key={input.id} variant="outlined" sx={{ mb: 1 }}>
                  <CardContent sx={{ py: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                        {getInputTypeIcon(input.type)}
                        <Box sx={{ ml: 2, flex: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {input.type.toUpperCase()}: {input.title || `Input ${input.id}`}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            maxWidth: '400px'
                          }}>
                            {input.value}
                          </Typography>
                          {input.source && (
                            <Chip label={input.source} size="small" sx={{ mt: 0.5 }} />
                          )}
                        </Box>
                      </Box>
                      <IconButton 
                        onClick={() => removeComparisonInput(input.id)}
                        color="error"
                        size="small"
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => setAddInputDialog(true)}
              >
                Add Input
              </Button>
              <Button
                variant="contained"
                onClick={performCustomComparison}
                disabled={comparisonInputs.length < 2 || loading}
              >
                Compare ({comparisonInputs.length} inputs)
              </Button>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Add Input Dialog */}
      <Dialog open={addInputDialog} onClose={() => setAddInputDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Comparison Input</DialogTitle>
        <DialogContent>
          <Tabs value={tabValue} onChange={(_, newValue) => {
            setTabValue(newValue);
            setNewInputType(['url', 'text', 'article_id'][newValue] as any);
          }}>
            <Tab label="URL" />
            <Tab label="Text" />
            <Tab label="Article ID" />
          </Tabs>

          <Box sx={{ mt: 2 }}>
            {newInputType === 'url' && (
              <>
                <TextField
                  fullWidth
                  label="Article URL"
                  value={newInputValue}
                  onChange={(e) => setNewInputValue(e.target.value)}
                  placeholder="https://example.com/article"
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Title (optional)"
                  value={newInputTitle}
                  onChange={(e) => setNewInputTitle(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Source (optional)"
                  value={newInputSource}
                  onChange={(e) => setNewInputSource(e.target.value)}
                />
              </>
            )}

            {newInputType === 'text' && (
              <>
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  label="Article Text"
                  value={newInputValue}
                  onChange={(e) => setNewInputValue(e.target.value)}
                  placeholder="Paste the article text here..."
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Title"
                  value={newInputTitle}
                  onChange={(e) => setNewInputTitle(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Source"
                  value={newInputSource}
                  onChange={(e) => setNewInputSource(e.target.value)}
                />
              </>
            )}

            {newInputType === 'article_id' && (
              <TextField
                fullWidth
                label="Article ID"
                value={newInputValue}
                onChange={(e) => setNewInputValue(e.target.value)}
                placeholder="Enter existing article ID"
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddInputDialog(false)}>Cancel</Button>
          <Button onClick={addComparisonInput} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>

      {/* Target Article Info - only show for auto comparison */}
      {!customMode && targetArticle && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Target Article
            </Typography>
            <Typography variant="h5" gutterBottom>
              {targetArticle.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip label={targetArticle.source} color="primary" />
              <Chip label={targetArticle.language} variant="outlined" />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Published: {new Date(targetArticle.publication_date).toLocaleDateString()}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Comparison Report - show when we have data */}
      {comparisonReport && (
        <>
          {/* Comparison Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Articles Compared
              </Typography>
              <Typography variant="h3" color="primary">
                {comparisonReport.articles.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                From {new Set(comparisonReport.articles.map(a => a.source)).size} sources
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Story ID
              </Typography>
              <Typography variant="h6" color="primary">
                {comparisonReport.story_id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Generated: {new Date(comparisonReport.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Differences
              </Typography>
              <Typography variant="h3" color="secondary">
                {comparisonReport.key_differences.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Identified differences
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bias Comparison Chart */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Bias Comparison Across Sources
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={biasData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="source" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="overall_bias" fill="#1976d2" name="Overall Bias" />
              <Bar dataKey="sentiment" fill="#00C49F" name="Sentiment" />
              <Bar dataKey="political_bias" fill="#FF8042" name="Political Bias" />
              <Bar dataKey="emotional_language" fill="#FFBB28" name="Emotional Language" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Bias Differences Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Bias Percentage Differences
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Source Comparison</TableCell>
                  <TableCell align="right">Percentage Difference</TableCell>
                  <TableCell align="center">Trend</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(comparisonReport.bias_differences).map(([comparison, difference]) => (
                  <TableRow key={comparison}>
                    <TableCell>{comparison}</TableCell>
                    <TableCell align="right">
                      {difference.toFixed(1)}%
                    </TableCell>
                    <TableCell align="center">
                      {getBiasDifferenceIcon(difference)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Comparison Methodology */}
      <Card sx={{ mb: 3, bgcolor: 'info.light', color: 'info.contrastText' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            🔍 How Articles Were Compared
          </Typography>
          <Typography variant="body2" paragraph>
            Our AI system analyzed the full text content of each article to identify:
          </Typography>
          <Box component="ul" sx={{ pl: 2, mb: 2 }}>
            <li>Similar topics and keywords</li>
            <li>Sentiment and emotional tone differences</li>
            <li>Political bias indicators</li>
            <li>Factual vs opinion content ratios</li>
            <li>Language patterns and word choices</li>
          </Box>
          <Typography variant="body2">
            The comparison text shown above for each article represents the actual content that was processed and analyzed.
          </Typography>
        </CardContent>
      </Card>

      {/* Key Differences */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Key Coverage Differences
          </Typography>
          {comparisonReport.key_differences.length > 0 ? (
            comparisonReport.key_differences.map((difference, index) => (
              <Alert key={index} severity="info" sx={{ mb: 1 }}>
                {difference}
              </Alert>
            ))
          ) : (
            <Typography variant="body2" color="text.secondary">
              No significant differences identified in coverage approach.
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Individual Article Analysis */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Individual Article Analysis
      </Typography>
      
      <Grid container spacing={3}>
        {comparisonReport.articles.map((article) => (
          <Grid item xs={12} md={6} key={article.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {article.title}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip label={article.source} color="primary" size="small" />
                  <Chip 
                    label={article.id === targetArticle?.id ? 'Target' : 'Related'} 
                    color={article.id === targetArticle?.id ? 'secondary' : 'default'}
                    size="small" 
                  />
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Published: {new Date(article.publication_date).toLocaleDateString()}
                </Typography>

                {/* Article Content Preview */}
                <Card variant="outlined" sx={{ mb: 2, bgcolor: 'grey.50', border: '2px solid', borderColor: 'primary.light' }}>
                  <CardContent sx={{ py: 2 }}>
                    <Typography variant="subtitle2" color="primary" gutterBottom sx={{ fontWeight: 'bold' }}>
                      📄 Article Content (Used for Comparison Analysis)
                    </Typography>
                    <Typography variant="body2" sx={{
                      display: '-webkit-box',
                      WebkitLineClamp: 6,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      fontSize: '0.875rem',
                      lineHeight: 1.5,
                      fontStyle: 'italic',
                      color: 'text.primary'
                    }}>
                      {article.content || 'Content not available'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      This text was analyzed for bias patterns, sentiment, and compared with other sources covering the same story.
                    </Typography>
                  </CardContent>
                </Card>

                {article.bias_scores && (
                  <BiasScoreCard biasScore={article.bias_scores} showDetails={false} />
                )}

                <Button
                  variant="outlined"
                  size="small"
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ mt: 2 }}
                >
                  Read Original
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
        </>
      )}
    </Box>
  );
};

export default ComparisonView;