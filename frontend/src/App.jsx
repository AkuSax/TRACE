import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom'; // Import useNavigate
import { Toaster, toast } from 'react-hot-toast';

// MUI Core
import { Box, Grid, Container } from '@mui/material'; // Import Grid and Container

// App Components
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import JobList from './components/JobList';
import Footer from './components/Footer';
import Login from './components/Login';
import AboutPage from './components/AboutPage';
import ModelPage from './components/ModelPage';
import './App.css';

// The Dashboard now uses a Grid layout
const Dashboard = ({ token, jobs, fetchJobs, deleteJob, isLoading }) => (
  <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
    <Grid container spacing={3}>
      {/* File Upload Component */}
      <Grid item xs={12} md={5} lg={4}>
        <FileUpload token={token} onUploadSuccess={fetchJobs} />
      </Grid>
      {/* Job List Component */}
      <Grid item xs={12} md={7} lg={8}>
        <JobList jobs={jobs} deleteJob={deleteJob} isLoading={isLoading} />
      </Grid>
    </Grid>
  </Container>
);

function App() {
  const [token, setToken] = useState('');
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate(); // Hook for navigation

  // ... fetchJobs and deleteJob functions remain the same ...
  const fetchJobs = async () => { /* ... */ };
  const deleteJob = async (jobId) => { /* ... */ };

  useEffect(() => {
    if (token) {
      fetchJobs();
    } else {
      setJobs([]);
    }
  }, [token]);

  // New function to handle user logout
  const handleLogout = () => {
    setToken(''); // Clear the token
    navigate('/'); // Navigate back to the login page
    toast.success('You have been logged out.');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Pass logout handler and login status to Header */}
      <Header isLoggedIn={!!token} handleLogout={handleLogout} />
      <Box component="main" sx={{ flexGrow: 1, py: 3, backgroundColor: (theme) => theme.palette.background.default }}>
        <Toaster position="top-center" reverseOrder={false} />
        <Routes>
          <Route 
            path="/" 
            element={
              !token ? (
                <Login setToken={setToken} />
              ) : (
                <Dashboard 
                  token={token} 
                  jobs={jobs} 
                  fetchJobs={fetchJobs} 
                  deleteJob={deleteJob} 
                  isLoading={isLoading}
                />
              )
            } 
          />
          <Route path="/model" element={<ModelPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Box>
      <Footer />
    </Box>
  );
}

export default App;