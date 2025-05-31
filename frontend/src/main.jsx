import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter } from 'react-router-dom';

// Updated theme for a dark, high-tech feel
const theme = createTheme({
  palette: {
    // Set the theme to dark mode
    mode: 'dark',
    primary: {
      // Set the primary color to an electric blue
      main: '#00BFFF',
    },
    background: {
      // Set the default background to a dark charcoal gray
      default: '#121212',
      // Set a slightly lighter color for elevated surfaces like Cards and Paper
      paper: '#1E1E1E',
    },
    text: {
      primary: '#E0E0E0',
      secondary: '#BDBDBD',
    }
  },
  typography: {
    // Set the default font family to "Inter" with fallbacks
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);