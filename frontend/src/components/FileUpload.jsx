import React, { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import toast from 'react-hot-toast'; // Import toast

function FileUpload({ token, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      toast.error('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/analyses/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) throw new Error('File upload failed.');
      
      toast.success('File uploaded! Analysis has started.'); // Success notification
      
      setSelectedFile(null);
      event.target.reset();
      onUploadSuccess();
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('An error occurred during file upload.'); // Error notification
    }
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit}
      sx={{ p: 2, border: '1px solid #ddd', borderRadius: '8px', mt: 4 }}
    >
      <Typography variant="h6" gutterBottom>Upload and Analyze</Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
        <Button
          variant="contained"
          component="label"
        >
          Choose File
          <input
            type="file"
            hidden
            onChange={handleFileChange}
          />
        </Button>
        {selectedFile && <Typography variant="body1">{selectedFile.name}</Typography>}
        <Button type="submit" variant="contained" disabled={!selectedFile}>
          Analyze
        </Button>
      </Box>
    </Box>
  );
}

export default FileUpload;