import React from 'react';
import { 
  Box, 
  Button, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Typography,
  Skeleton // Import Skeleton
} from '@mui/material';
// Import required icons
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import ErrorIcon from '@mui/icons-material/Error';

// A helper function to render the correct icon based on status
const renderStatusIcon = (status) => {
  switch (status) {
    case 'complete':
      return <CheckCircleIcon color="success" />;
    case 'pending':
      return <HourglassEmptyIcon color="action" />;
    case 'failed':
      return <ErrorIcon color="error" />;
    default:
      return null;
  }
};

function JobList({ jobs, deleteJob, isLoading }) {

  // Render Skeleton loading state
  if (isLoading) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          <Skeleton width="200px" />
        </Typography>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[...Array(3)].map((_, index) => (
                <TableRow key={index}>
                  <TableCell><Skeleton variant="circular" width={24} height={24} /></TableCell>
                  <TableCell><Skeleton /></TableCell>
                  <TableCell><Skeleton /></TableCell>
                  <TableCell><Skeleton /></TableCell>
                  <TableCell><Skeleton /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  }

  // Render placeholder if not loading and no jobs
  if (!jobs || jobs.length === 0) {
    return (
      <Paper sx={{ p: 2, mt: 4, textAlign: 'center' }}>
        <Typography variant="h6">My Analyses</Typography>
        <Typography sx={{ mt: 2 }}>Your analysis jobs will appear here.</Typography>
      </Paper>
    );
  }

  const handleDeleteClick = (jobId) => {
    if (window.confirm('Are you sure you want to permanently delete this job?')) {
      deleteJob(jobId);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>My Analyses</Typography>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="analysis jobs table">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', width: '60px' }}>Icon</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Job ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Date Created</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map((job) => (
              <TableRow
                key={job.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell>{renderStatusIcon(job.status)}</TableCell>
                <TableCell component="th" scope="row">{job.id}</TableCell>
                <TableCell>{job.status}</TableCell>
                <TableCell>{new Date(job.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={() => handleDeleteClick(job.id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default JobList;