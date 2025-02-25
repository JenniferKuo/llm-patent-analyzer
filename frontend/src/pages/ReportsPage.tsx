import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress
} from '@mui/material';

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

const getRiskColor = (risk: string): 'success' | 'warning' | 'error' => {
  if (risk.includes('Low')) return 'success';
  if (risk.includes('High')) return 'error';
  return 'warning';
};

const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('/api/reports');
        if (!response.ok) throw new Error('Failed to fetch reports');
        const data = await response.json();
        setReports(data.sort((a: Report, b: Report) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 3, mt: 4, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography>{error}</Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Saved Reports
        </Typography>

        {reports.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography>No saved reports found.</Typography>
          </Paper>
        ) : (
          reports.map((report) => (
            <Accordion key={report.id} sx={{ mb: 2 }}>
              <AccordionSummary 
                expandIcon={<span>▼</span>}
              >
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  width: '100%',
                  pr: 2
                }}>
                  <Box>
                    <Typography variant="subtitle1">
                      {report.patent_title || report.patent_id}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(report.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                  <Chip
                    label={`Overall Risk: ${report.overall_risk_assessment}`}
                    color={getRiskColor(report.overall_risk_assessment)}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Patent ID: {report.patent_id}
                    <br />
                    Company: {report.company_name}
                  </Typography>

                  {report.top_infringing_products.map((product, index) => (
                    <Paper key={index} sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6">{product.product_name}</Typography>
                        <Chip
                          label={`${product.infringement_score}% - ${product.infringement_likelihood}`}
                          color={getRiskColor(product.infringement_likelihood)}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2">{product.explanation}</Typography>
                      
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
                    </Paper>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))
        )}
      </Box>
    </Container>
  );
};

export default ReportsPage; 