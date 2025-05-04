import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import EmotionMetricsTable from '../components/Metrics/EmotionMetricsTable';

const MetricsPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Emotion Recognition System Performance
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center" sx={{ mb: 4 }}>
          Comparative analysis of text, facial, and speech-based emotion recognition
        </Typography>
        
        <EmotionMetricsTable />
        
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Key Observations:
          </Typography>
          <Typography variant="body1" paragraph>
            1. Text-based recognition shows the highest accuracy across all emotions, particularly for neutral and happy emotions.
          </Typography>
          <Typography variant="body1" paragraph>
            2. Facial recognition provides the fastest response times, making it ideal for real-time applications.
          </Typography>
          <Typography variant="body1" paragraph>
            3. Speech recognition, while slightly slower, offers good detection rates for emotional speech patterns.
          </Typography>
          <Typography variant="body1" paragraph>
            4. Neutral emotion is consistently well-detected across all three methods, indicating robust baseline performance.
          </Typography>
          <Typography variant="body1" paragraph>
            5. Surprise shows the most variation in detection rates, suggesting it's the most challenging emotion to recognize consistently.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default MetricsPage; 