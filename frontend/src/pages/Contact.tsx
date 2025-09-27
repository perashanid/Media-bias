import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  Snackbar,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Email,
  Phone,
  LocationOn,
  Send,
  GitHub,
  LinkedIn,
  Twitter,
} from '@mui/icons-material';

const Contact: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [showSuccess, setShowSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      setShowSuccess(true);
      setIsSubmitting(false);
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: '',
      });
    }, 1000);
  };

  const contactInfo = [
    {
      icon: <Email />,
      title: 'Email',
      content: 'shanidsajjatz@gmail.com',
      link: 'mailto:shanidsajjatz@gmail.com',
    },
    {
      icon: <LocationOn />,
      title: 'Purpose',
      content: 'Educational Research & Development',
      link: null,
    },
  ];

  const socialLinks = [
    {
      icon: <GitHub />,
      name: 'GitHub',
      url: 'https://github.com/mediabias',
    },
    {
      icon: <LinkedIn />,
      name: 'LinkedIn',
      url: 'https://linkedin.com/company/mediabias',
    },
    {
      icon: <Twitter />,
      name: 'Twitter',
      url: 'https://twitter.com/mediabias',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography 
          variant="h2" 
          component="h1" 
          gutterBottom 
          sx={{
            background: (theme) => theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)'
              : 'linear-gradient(135deg, #1e40af 0%, #7c3aed 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Contact Us
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
          Have questions about our educational media bias detection system? This platform is developed 
          for research and learning purposes only. Send us a message and we'll respond as soon as possible.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={8}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h4" gutterBottom>
                Send us a Message
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Fill out the form below and we'll get back to you within 24 hours.
              </Typography>
              
              <Box component="form" onSubmit={handleSubmit}>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email Address"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Message"
                      name="message"
                      multiline
                      rows={6}
                      value={formData.message}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                      placeholder="Tell us about your inquiry, feedback, or how we can help you..."
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      startIcon={<Send />}
                      disabled={isSubmitting}
                      sx={{
                        px: 4,
                        py: 1.5,
                        borderRadius: 2,
                      }}
                    >
                      {isSubmitting ? 'Sending...' : 'Send Message'}
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  Get in Touch
                </Typography>
                <List sx={{ p: 0 }}>
                  {contactInfo.map((info, index) => (
                    <ListItem
                      key={index}
                      sx={{
                        px: 0,
                        py: 1.5,
                        cursor: info.link ? 'pointer' : 'default',
                        '&:hover': info.link ? {
                          backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(65, 90, 119, 0.1)' : 'rgba(0, 0, 0, 0.04)',
                          borderRadius: 1,
                        } : {},
                      }}
                      onClick={() => info.link && window.open(info.link, '_self')}
                    >
                      <ListItemIcon sx={{ color: 'primary.main', minWidth: 40 }}>
                        {info.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={info.title}
                        secondary={info.content}
                        primaryTypographyProps={{ fontWeight: 600 }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>

            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  Follow Us
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                  {socialLinks.map((social, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      startIcon={social.icon}
                      onClick={() => window.open(social.url, '_blank')}
                      sx={{
                        borderRadius: 2,
                        flex: 1,
                        py: 1,
                      }}
                    >
                      {social.name}
                    </Button>
                  ))}
                </Box>
              </CardContent>
            </Card>

            <Paper sx={{ 
              p: 3, 
              bgcolor: (theme) => theme.palette.mode === 'dark' 
                ? 'rgba(65, 90, 119, 0.2)' 
                : 'rgba(13, 27, 42, 0.05)',
              border: '1px solid',
              borderColor: (theme) => theme.palette.mode === 'dark' 
                ? 'rgba(119, 141, 169, 0.3)' 
                : 'rgba(13, 27, 42, 0.1)',
            }}>
              <Typography variant="h6" gutterBottom>
                Office Hours
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monday - Friday: 9:00 AM - 6:00 PM EST<br />
                Saturday: 10:00 AM - 4:00 PM EST<br />
                Sunday: Closed
              </Typography>
            </Paper>
          </Box>
        </Grid>
      </Grid>

      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setShowSuccess(false)}
          severity="success"
          sx={{ width: '100%' }}
        >
          Thank you for your message! We'll get back to you soon.
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Contact;