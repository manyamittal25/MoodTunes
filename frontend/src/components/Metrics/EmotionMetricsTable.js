import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
} from '@mui/material';

const EmotionMetricsTable = () => {
  // Sample data - replace with actual metrics from your project
  const metricsData = {
    text: {
      accuracy: {
        happy: 0.92,
        sad: 0.88,
        angry: 0.85,
        neutral: 0.90,
        surprise: 0.87,
      },
      latency: {
        happy: 0.8,
        sad: 0.9,
        angry: 0.85,
        neutral: 0.75,
        surprise: 0.95,
      },
      detectionRate: {
        happy: 0.95,
        sad: 0.93,
        angry: 0.91,
        neutral: 0.97,
        surprise: 0.89,
      },
    },
    facial: {
      accuracy: {
        happy: 0.89,
        sad: 0.86,
        angry: 0.84,
        neutral: 0.88,
        surprise: 0.85,
      },
      latency: {
        happy: 1.2,
        sad: 1.3,
        angry: 1.1,
        neutral: 1.0,
        surprise: 1.4,
      },
      detectionRate: {
        happy: 0.92,
        sad: 0.90,
        angry: 0.88,
        neutral: 0.94,
        surprise: 0.87,
      },
    },
    speech: {
      accuracy: {
        happy: 0.87,
        sad: 0.85,
        angry: 0.83,
        neutral: 0.86,
        surprise: 0.82,
      },
      latency: {
        happy: 1.5,
        sad: 1.6,
        angry: 1.4,
        neutral: 1.3,
        surprise: 1.7,
      },
      detectionRate: {
        happy: 0.90,
        sad: 0.88,
        angry: 0.86,
        neutral: 0.92,
        surprise: 0.85,
      },
    },
  };

  const emotions = ['happy', 'sad', 'angry', 'neutral', 'surprise'];
  const recognitionTypes = ['text', 'facial', 'speech'];
  const metrics = ['accuracy', 'latency', 'detectionRate'];

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
        Emotion Recognition Performance Metrics
      </Typography>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="emotion metrics table">
          <TableHead>
            <TableRow>
              <TableCell>Emotion</TableCell>
              {recognitionTypes.map((type) => (
                <TableCell key={type} colSpan={3} align="center">
                  {type.charAt(0).toUpperCase() + type.slice(1)} Recognition
                </TableCell>
              ))}
            </TableRow>
            <TableRow>
              <TableCell></TableCell>
              {recognitionTypes.map((type) =>
                metrics.map((metric) => (
                  <TableCell key={`${type}-${metric}`} align="center">
                    {metric.charAt(0).toUpperCase() + metric.slice(1)}
                  </TableCell>
                ))
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {emotions.map((emotion) => (
              <TableRow key={emotion}>
                <TableCell component="th" scope="row">
                  {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                </TableCell>
                {recognitionTypes.map((type) =>
                  metrics.map((metric) => (
                    <TableCell key={`${type}-${emotion}-${metric}`} align="center">
                      {metric === 'latency'
                        ? `${metricsData[type][metric][emotion]}s`
                        : `${(metricsData[type][metric][emotion] * 100).toFixed(1)}%`}
                    </TableCell>
                  ))
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary">
          * Accuracy: Percentage of correct emotion detections
        </Typography>
        <Typography variant="body2" color="text.secondary">
          * Latency: Time taken for emotion detection in seconds
        </Typography>
        <Typography variant="body2" color="text.secondary">
          * Detection Rate: Percentage of successful emotion detections
        </Typography>
      </Box>
    </Box>
  );
};

export default EmotionMetricsTable; 