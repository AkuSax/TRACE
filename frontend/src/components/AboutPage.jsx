import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const AboutPage = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          About Me
        </Typography>
        <Typography variant="body1" paragraph>
          This is the about page. Here you can introduce yourself, your background,
          and the motivation behind creating the TRACE application. Discuss your
          skills in bioinformatics, web development, and data analysis.
        </Typography>
        <Typography variant="body1" paragraph>
          This project serves as a portfolio piece to demonstrate full-stack
          development capabilities, from a secure FastAPI backend to a responsive
          and functional React frontend with Material-UI.
        </Typography>
      </Paper>
    </Container>
  );
};

export default AboutPage;