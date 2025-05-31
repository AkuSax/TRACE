import React from 'react';
import { Box, Container, Typography } from '@mui/material';

function Footer() {
  const currentYear = new Date().getFullYear();
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto', // Pushes the footer to the bottom
        backgroundColor: (theme) =>
          theme.palette.mode === 'dark'
            ? theme.palette.grey[900]
            : theme.palette.grey[200],
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          &copy; {currentYear} TRACE Project. All Rights Reserved.
        </Typography>
      </Container>
    </Box>
  );
}

export default Footer;