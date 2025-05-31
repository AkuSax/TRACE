import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import BiotechIcon from '@mui/icons-material/Biotech'; // A great icon for a science app

// Receive handleLogout and an isLoggedIn flag as props
function Header({ isLoggedIn, handleLogout }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <BiotechIcon sx={{ mr: 1 }} />
        <Typography 
          variant="h6" 
          component={Link} 
          to="/" 
          sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}
        >
          TRACE
        </Typography>
        
        <Box>
          <Button color="inherit" component={Link} to="/model">
            Model
          </Button>
          <Button color="inherit" component={Link} to="/about">
            About
          </Button>
          {/* Conditionally render Logout button */}
          {isLoggedIn && (
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;