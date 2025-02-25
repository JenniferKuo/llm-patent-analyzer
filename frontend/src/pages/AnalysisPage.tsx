import React, { useState } from 'react';
import { Button, TextField, Container, Paper, Typography, Box, Chip, CircularProgress, List, ListItem, ListItemText, Collapse, Snackbar, Alert, AlertColor } from '@mui/material';
import { v4 as uuidv4 } from 'uuid';

// Define the structure of analysis result
interface AnalysisResult {
  analysis_id: string;
  patent_id: string;
  company_name: string;
  analysis_date: string;
  top_infringing_products: Array<{
    product_name: string;
    infringement_score: number;
    infringement_likelihood: string;
    relevant_claims: string[];
    explanation: string;
    specific_features: string[];
  }>;
  overall_risk_assessment: string;
}

// Add new interfaces for suggestions
interface PatentSuggestion {
  id: string;
  title: string;
}

interface CompanySuggestion {
  name: string;
}

// Update Report interface
interface Report {
  id: string;
  created_at: string;
  patent_id: string;
  patent_title: string;
  patent_abstract: string;
  company_name: string;
  top_infringing_products: Array<{
    product_name: string;
    infringement_score: number;
    infringement_likelihood: string;
    relevant_claims: string[];
    explanation: string;
    specific_features: string[];
  }>;
  overall_risk_assessment: string;
}

// Helper function to determine chip color
const getRiskColor = (risk: string): 'success' | 'warning' | 'error' => {
  if (risk.includes('Low')) return 'success';
  if (risk.includes('High')) return 'error';
  return 'warning';
};

const AnalysisPage: React.FC = () => {
  const [patentId, setPatentId] = useState('');
  const [patentTitle, setPatentTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [companySuggestions, setCompanySuggestions] = useState<CompanySuggestion[]>([]);
  const [patentSuggestions, setPatentSuggestions] = useState<PatentSuggestion[]>([]);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: AlertColor;
  }>({
    open: false,
    message: '',
    severity: 'success'
  });
  const [savedReports, setSavedReports] = useState<Set<string>>(new Set());

  // Handle patent title suggestions
  const handlePatentSuggest = async (title: string) => {
    if (title.length < 2) {
      setPatentSuggestions([]);
      return;
    }
    
    try {
      const response = await fetch(`/api/search/patent/suggest/${encodeURIComponent(title)}?limit=5&threshold=60`);
      const data = await response.json();
      setPatentSuggestions(data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching patent suggestions:', error);
    }
  };

  // Handle company name suggestions
  const handleCompanySuggest = async (name: string) => {
    if (name.length < 2) {
      setCompanySuggestions([]);
      return;
    }

    try {
      const response = await fetch(`/api/search/company/suggest/${encodeURIComponent(name)}?limit=5&threshold=60`);
      const data = await response.json();
      setCompanySuggestions(data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching company suggestions:', error);
    }
  };

  // Handle the patent infringement analysis
  const handleAnalysis = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analysis/company`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patent_id: patentId,
          company_name: companyName,
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error during analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Update save report function
  const handleSaveReport = async () => {
    if (!result) return;

    // Check if this analysis has already been saved
    const reportKey = `${result.patent_id}-${result.company_name}`;
    if (savedReports.has(reportKey)) {
      setSnackbar({
        open: true,
        message: 'This analysis has already been saved',
        severity: 'warning'
      });
      return;
    }

    try {
      setSaving(true);
      const reportData: Omit<Report, 'id' | 'created_at'> = {
        patent_id: result.patent_id,
        patent_title: patentTitle,
        patent_abstract: "",
        company_name: result.company_name,
        top_infringing_products: result.top_infringing_products,
        overall_risk_assessment: result.overall_risk_assessment
      };

      const response = await fetch(`/api/reports`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: uuidv4(),
          created_at: new Date().toISOString(),
          ...reportData
        }),
      });

      if (response.ok) {
        // Add to saved reports
        setSavedReports(prev => new Set(prev).add(reportKey));
        setSnackbar({
          open: true,
          message: 'Report saved successfully!',
          severity: 'success'
        });
      } else {
        throw new Error('Failed to save report');
      }
    } catch (error) {
      console.error('Error saving report:', error);
      setSnackbar({
        open: true,
        message: 'Failed to save report',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Patent Infringement AI Analyzer
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Patent Search Section */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Box sx={{ flex: 1, position: 'relative', zIndex: 2 }}>
                <TextField
                  fullWidth
                  label="Search Patent by Title"
                  placeholder="e.g., shopping"
                  value={patentTitle}
                  onChange={(e) => {
                    setPatentTitle(e.target.value);
                    handlePatentSuggest(e.target.value);
                  }}
                  variant="outlined"
                />
                <Collapse in={patentSuggestions.length > 0}>
                  <Paper 
                    elevation={3} 
                    sx={{ 
                      position: 'absolute', 
                      top: 'calc(100% + 8px)',
                      left: 0, 
                      right: 0, 
                      zIndex: 2,
                      maxHeight: '300px',
                      overflow: 'auto',
                      bgcolor: 'background.paper',
                      border: 1,
                      borderColor: 'divider'
                    }}
                  >
                    <List>
                      {patentSuggestions.map((patent) => (
                        <ListItem 
                          component="button"
                          key={patent.id}
                          onClick={() => {
                            setPatentId(patent.id);
                            setPatentTitle(patent.title);
                            setPatentSuggestions([]);
                          }}
                          sx={{ 
                            textAlign: 'left', 
                            width: '100%',
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                        >
                          <ListItemText 
                            primary={patent.title}
                            secondary={patent.id}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Collapse>
              </Box>
              <Typography 
                variant="body1" 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  px: 2,
                  color: 'text.secondary'
                }}
              >
                or
              </Typography>
              <TextField
                sx={{ flex: 1 }}
                label="Patent ID"
                placeholder="e.g., US-RE49889-E1"
                value={patentId}
                onChange={(e) => setPatentId(e.target.value)}
                variant="outlined"
              />
            </Box>

            {/* Company Search Section */}
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <TextField
                fullWidth
                label="Company Name"
                placeholder="e.g., Walmart Inc."
                value={companyName}
                onChange={(e) => {
                  setCompanyName(e.target.value);
                  handleCompanySuggest(e.target.value);
                }}
                variant="outlined"
              />
              <Collapse in={companySuggestions.length > 0}>
                <Paper 
                  elevation={3} 
                  sx={{ 
                    position: 'absolute', 
                    top: 'calc(100% + 8px)',
                    left: 0, 
                    right: 0, 
                    zIndex: 1,
                    maxHeight: '300px',
                    overflow: 'auto',
                    bgcolor: 'background.paper',
                    border: 1,
                    borderColor: 'divider'
                  }}
                >
                  <List>
                    {companySuggestions.map((company) => (
                      <ListItem 
                        component="button"
                        key={company.name}
                        onClick={() => {
                          setCompanyName(company.name);
                          setCompanySuggestions([]);
                        }}
                        sx={{ 
                          textAlign: 'left', 
                          width: '100%',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      >
                        <ListItemText primary={company.name} />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Collapse>
            </Box>

            <Button 
              variant="contained" 
              onClick={handleAnalysis}
              disabled={loading || !patentId || !companyName}
              fullWidth
              sx={{ mt: 2 }}
            >
              {loading ? 'Analyzing...' : 'Start Analysis'}
            </Button>
          </Box>
        </Paper>

        {/* Loading State */}
        {loading && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box className="loading-container">
              <CircularProgress size={60} />
              <Typography variant="h6" className="loading-text">
                AI is analyzing patent infringement...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                This may take a few moments. We're thoroughly examining the patent claims.
              </Typography>
            </Box>
          </Paper>
        )}

        {/* Analysis Results Section */}
        {result && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h5">Analysis Results</Typography>
                <Button
                  variant="outlined"
                  onClick={handleSaveReport}
                  disabled={saving}
                  startIcon={saving ? <CircularProgress size={20} /> : null}
                >
                  {saving ? 'Saving...' : '💾 Save Report'}
                </Button>
              </Box>
              <Chip 
                label={`Overall Risk: ${result.overall_risk_assessment}`}
                color={getRiskColor(result.overall_risk_assessment)}
                sx={{ fontWeight: 'bold' }}
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Analysis ID: {result.analysis_id}
              <br />
              Date: {new Date(result.analysis_date).toLocaleString()}
            </Typography>

            {result.top_infringing_products.map((product, index) => (
              <Box key={index} sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6" color="primary">
                    {product.product_name}
                  </Typography>
                  <Chip 
                    label={`${product.infringement_score}% - ${product.infringement_likelihood}`}
                    color={getRiskColor(product.infringement_likelihood)}
                  />
                </Box>

                <Typography variant="body1" sx={{ mt: 2 }}>
                  {product.explanation}
                </Typography>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Relevant Claims:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {product.relevant_claims.map((claim, i) => (
                      <Chip key={i} label={claim} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Specific Features:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {product.specific_features.map((feature, i) => (
                      <Chip key={i} label={feature} size="small" />
                    ))}
                  </Box>
                </Box>
              </Box>
            ))}
          </Paper>
        )}
      </Box>

      {/* Add Snackbar at the end of the component */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AnalysisPage; 