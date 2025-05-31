import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const ModelPage = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          The TRACE Model
        </Typography>
        <Typography variant="body1" paragraph>
          This page is dedicated to explaining the bioinformatics model that powers
          the TRACE application. Detail the scientific principles, the algorithms
          used, and the type of data it is designed to analyze (e.g., circulating
          tumor DNA, cfDNA).
        </Typography>
        <Typography variant="body1" paragraph>
          You can include information about the model's accuracy, the validation
          process, and citations to relevant scientific literature. This demonstrates
          a deep understanding of the domain science behind the tool.
        </Typography>
      </Paper>
    </Container>
  );
};

export default ModelPage;