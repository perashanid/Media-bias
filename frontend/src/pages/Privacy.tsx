import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
} from '@mui/material';
import {
  Security,
  DataUsage,
  Cookie,
  ContactMail,
} from '@mui/icons-material';

const Privacy: React.FC = () => {
  const lastUpdated = 'December 15, 2024';

  const sections = [
    {
      id: 'information-collection',
      title: 'Information We Collect',
      icon: <DataUsage />,
      content: [
        {
          subtitle: 'Personal Information',
          items: [
            'Account information (username, email address)',
            'Profile information you choose to provide',
            'Communication preferences',
          ],
        },
        {
          subtitle: 'Usage Information',
          items: [
            'Articles you analyze and compare',
            'Search queries and filters applied',
            'Time spent on different features',
            'Device and browser information',
          ],
        },
        {
          subtitle: 'Technical Information',
          items: [
            'IP address and location data',
            'Browser type and version',
            'Operating system information',
            'Referral URLs',
          ],
        },
      ],
    },
    {
      id: 'information-use',
      title: 'How We Use Your Information',
      icon: <Security />,
      content: [
        {
          subtitle: 'Service Provision',
          items: [
            'Provide and maintain our media bias detection services',
            'Process and analyze news articles for bias detection',
            'Generate personalized recommendations and insights',
            'Improve our machine learning algorithms',
          ],
        },
        {
          subtitle: 'Communication',
          items: [
            'Send service-related notifications',
            'Respond to your inquiries and support requests',
            'Send updates about new features (with your consent)',
          ],
        },
        {
          subtitle: 'Analytics and Improvement',
          items: [
            'Analyze usage patterns to improve our services',
            'Conduct research and development',
            'Monitor and prevent fraud or abuse',
          ],
        },
      ],
    },
    {
      id: 'information-sharing',
      title: 'Information Sharing',
      icon: <ContactMail />,
      content: [
        {
          subtitle: 'We Do Not Sell Your Data',
          items: [
            'We never sell, rent, or trade your personal information',
            'We do not share your data with advertisers',
            'Your privacy is our top priority',
          ],
        },
        {
          subtitle: 'Limited Sharing Scenarios',
          items: [
            'With your explicit consent',
            'To comply with legal obligations',
            'To protect our rights and prevent fraud',
            'With trusted service providers under strict agreements',
          ],
        },
      ],
    },
    {
      id: 'data-security',
      title: 'Data Security',
      icon: <Security />,
      content: [
        {
          subtitle: 'Security Measures',
          items: [
            'Industry-standard encryption for data transmission',
            'Secure data storage with access controls',
            'Regular security audits and updates',
            'Employee training on data protection',
          ],
        },
        {
          subtitle: 'Data Retention',
          items: [
            'Account data: Retained while your account is active',
            'Usage data: Retained for up to 2 years for analytics',
            'Communication records: Retained for up to 3 years',
            'You can request data deletion at any time',
          ],
        },
      ],
    },
    {
      id: 'cookies',
      title: 'Cookies and Tracking',
      icon: <Cookie />,
      content: [
        {
          subtitle: 'Essential Cookies',
          items: [
            'Authentication and session management',
            'Security and fraud prevention',
            'Basic functionality and preferences',
          ],
        },
        {
          subtitle: 'Analytics Cookies',
          items: [
            'Usage statistics and performance monitoring',
            'Feature usage and user behavior analysis',
            'Error tracking and debugging',
          ],
        },
        {
          subtitle: 'Cookie Control',
          items: [
            'You can control cookies through your browser settings',
            'Disabling cookies may affect site functionality',
            'We respect Do Not Track signals',
          ],
        },
      ],
    },
  ];

  const userRights = [
    'Access your personal data',
    'Correct inaccurate information',
    'Delete your account and data',
    'Export your data',
    'Opt-out of communications',
    'Restrict data processing',
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
          Privacy Policy
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
          We are committed to protecting your privacy and being transparent about how we collect,
          use, and protect your information.
        </Typography>
        <Chip
          label={`Last updated: ${lastUpdated}`}
          color="primary"
          variant="outlined"
          sx={{ mt: 2 }}
        />
      </Box>

      <Box sx={{ mb: 4 }}>
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
          <Typography variant="h6" gutterBottom color="primary">
            🎓 Educational Purpose Only
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            <strong>Important Notice:</strong> This platform is developed solely for educational and research purposes. 
            The developer does not claim any rights to the scraped news content and has no intention to use, 
            redistribute, or monetize the content in any way. All news articles remain the intellectual property 
            of their respective publishers.
          </Typography>
          <Typography variant="h6" gutterBottom>
            Quick Summary
          </Typography>
          <Typography variant="body1" color="text.secondary">
            We collect minimal personal information to provide our media bias detection services.
            We never sell your data, use industry-standard security measures, and give you full
            control over your information. You can delete your account and data at any time.
          </Typography>
        </Paper>
      </Box>

      {sections.map((section, index) => (
        <Card key={section.id} sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box sx={{ color: 'primary.main', mr: 2 }}>
                {section.icon}
              </Box>
              <Typography variant="h4" component="h2">
                {section.title}
              </Typography>
            </Box>
            
            {section.content.map((subsection, subIndex) => (
              <Box key={subIndex} sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                  {subsection.subtitle}
                </Typography>
                <List sx={{ pl: 2 }}>
                  {subsection.items.map((item, itemIndex) => (
                    <ListItem key={itemIndex} sx={{ py: 0.5, px: 0 }}>
                      <ListItemText
                        primary={item}
                        primaryTypographyProps={{
                          variant: 'body1',
                          color: 'text.secondary',
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
                {subIndex < section.content.length - 1 && <Divider sx={{ my: 2 }} />}
              </Box>
            ))}
          </CardContent>
        </Card>
      ))}

      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            Your Rights
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            You have the following rights regarding your personal data:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {userRights.map((right, index) => (
              <Chip
                key={index}
                label={right}
                variant="outlined"
                color="primary"
                sx={{ mb: 1 }}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            Contact Us About Privacy
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            If you have any questions about this Privacy Policy or want to exercise your rights,
            please contact us:
          </Typography>
          <Box sx={{ pl: 2 }}>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>Email:</strong> shanidsajjatz@gmail.com
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>Purpose:</strong> Educational research and development only
            </Typography>
            <Typography variant="body1">
              <strong>Response Time:</strong> We will respond to privacy requests within 30 days
            </Typography>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ 
        mt: 4, 
        p: 3, 
        bgcolor: (theme) => theme.palette.mode === 'dark' 
          ? 'rgba(65, 90, 119, 0.1)' 
          : 'rgba(0, 0, 0, 0.02)', 
        borderRadius: 2,
        border: '1px solid',
        borderColor: (theme) => theme.palette.mode === 'dark' 
          ? 'rgba(119, 141, 169, 0.2)' 
          : 'rgba(0, 0, 0, 0.08)',
      }}>
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          This Privacy Policy may be updated from time to time. We will notify you of any
          significant changes by email or through our service. Your continued use of our
          service after changes become effective constitutes acceptance of the updated policy.
        </Typography>
      </Box>
    </Container>
  );
};

export default Privacy;