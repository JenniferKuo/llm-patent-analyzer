import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AnalysisPage from './pages/AnalysisPage.tsx';
import ReportsPage from './pages/ReportsPage.tsx';
import { Box, AppBar, Toolbar, Button, Typography, createTheme, ThemeProvider } from '@mui/material';
import { Link } from 'react-router-dom';
import './App.css';

// Create custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3', // Bright blue
    },
    background: {
      default: '#f8f9fa', // Light gray background
      paper: '#ffffff',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <div className="App">
        <Router>
          <Box sx={{ flexGrow: 1 }}>
            <AppBar 
              position="static" 
              elevation={1}
              sx={{ 
                bgcolor: '#1976d2', // Medium blue
                background: 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)', // Lighter blue gradient
              }}
            >
              <Toolbar>
                <Typography 
                  variant="h6" 
                  component="div" 
                  sx={{ 
                    flexGrow: 1,
                    color: '#fff',
                    fontWeight: 'bold',
                    letterSpacing: 1,
                  }}
                >
                  PatentAI
                </Typography>
                <Button 
                  color="inherit"
                  component={Link} 
                  to="/analysis"
                  sx={{ 
                    mx: 1,
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.08)'
                    }
                  }}
                >
                  Analysis
                </Button>
                <Button 
                  color="inherit"
                  component={Link} 
                  to="/saved-reports"
                  sx={{ 
                    mx: 1,
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.08)'
                    }
                  }}
                >
                  Saved Reports
                </Button>
              </Toolbar>
            </AppBar>
            <Routes>
              <Route path="/" element={<Navigate to="/analysis" replace />} />
              <Route path="/saved-reports" element={<ReportsPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="*" element={<Navigate to="/analysis" replace />} />
            </Routes>
          </Box>
        </Router>
      </div>
    </ThemeProvider>
  );
}

export default App;