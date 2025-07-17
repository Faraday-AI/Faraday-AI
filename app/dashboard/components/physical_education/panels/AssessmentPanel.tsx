import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Rating,
  Chip,
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

interface Assessment {
  id: string;
  skill: string;
  level: number;
  lastAssessed: string;
  nextAssessment: string;
  status: 'excellent' | 'good' | 'needs-improvement' | 'poor';
  notes: string;
  category: string;
  history: {
    date: string;
    level: number;
    notes: string;
  }[];
}

interface AssessmentReport {
  id: string;
  date: string;
  overallScore: number;
  skills: Assessment[];
  feedback: string;
  recommendations: string[];
}

const AssessmentPanel: React.FC = () => {
  const theme = useTheme();
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [reports, setReports] = useState<AssessmentReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);

  const categories = useMemo(() => ['all', 'fitness', 'nutrition', 'health'], []);

  useEffect(() => {
    const fetchAssessmentData = async () => {
      try {
        // Simulated data with more comprehensive metrics
        const mockAssessments: Assessment[] = [
          {
            id: '1',
            skill: 'Endurance',
            level: 4,
            lastAssessed: '2024-04-01',
            nextAssessment: '2024-07-01',
            status: 'good',
            notes: 'Showing steady improvement in stamina',
            category: 'fitness',
            history: [
              { date: '2024-01-01', level: 3, notes: 'Initial assessment' },
              { date: '2024-02-01', level: 3.5, notes: 'Improved stamina' },
              { date: '2024-03-01', level: 4, notes: 'Consistent performance' },
            ],
          },
          {
            id: '2',
            skill: 'Flexibility',
            level: 3,
            lastAssessed: '2024-04-01',
            nextAssessment: '2024-07-01',
            status: 'needs-improvement',
            notes: 'Focus on stretching exercises',
            category: 'fitness',
            history: [
              { date: '2024-01-01', level: 2, notes: 'Limited range of motion' },
              { date: '2024-02-01', level: 2.5, notes: 'Slight improvement' },
              { date: '2024-03-01', level: 3, notes: 'Regular stretching helping' },
            ],
          },
        ];

        const mockReports: AssessmentReport[] = [
          {
            id: '1',
            date: '2024-04-01',
            overallScore: 3.5,
            skills: mockAssessments,
            feedback: 'Good progress overall, but need to focus on flexibility training',
            recommendations: [
              'Increase stretching routine to 3 times per week',
              'Add yoga sessions to improve flexibility',
              'Monitor progress with weekly measurements',
            ],
          },
        ];

        setAssessments(mockAssessments);
        setReports(mockReports);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching assessment data:', error);
        setLoading(false);
      }
    };

    fetchAssessmentData();
  }, []);

  const filteredAssessments = useMemo(() => {
    return assessments.filter(
      (assessment) => selectedCategory === 'all' || assessment.category === selectedCategory
    );
  }, [assessments, selectedCategory]);

  const getStatusColor = (status: Assessment['status']) => {
    switch (status) {
      case 'excellent':
        return 'success';
      case 'good':
        return 'info';
      case 'needs-improvement':
        return 'warning';
      case 'poor':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleOpenDialog = (assessment: Assessment | null) => {
    setSelectedAssessment(assessment);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedAssessment(null);
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      label="Category"
                    >
                      {categories.map((category) => (
                        <MenuItem key={category} value={category}>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog(null)}
                  >
                    New Assessment
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                  <Tab label="Skills Assessment" />
                  <Tab label="Historical Data" />
                  <Tab label="Reports" />
                </Tabs>
              </Box>

              {activeTab === 0 && (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Skill</TableCell>
                        <TableCell>Level</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Last Assessed</TableCell>
                        <TableCell>Next Assessment</TableCell>
                        <TableCell>Notes</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredAssessments.map((assessment) => (
                        <TableRow key={assessment.id}>
                          <TableCell>{assessment.skill}</TableCell>
                          <TableCell>
                            <Rating value={assessment.level} readOnly />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={assessment.status}
                              color={getStatusColor(assessment.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(assessment.lastAssessed).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            {new Date(assessment.nextAssessment).toLocaleDateString()}
                          </TableCell>
                          <TableCell>{assessment.notes}</TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handleOpenDialog(assessment)}
                            >
                              <EditIcon />
                            </IconButton>
                            <IconButton size="small" color="error">
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {activeTab === 1 && (
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={filteredAssessments}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="skill" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="level" fill={theme.palette.primary.main} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              )}

              {activeTab === 2 && (
                <Grid container spacing={3}>
                  {reports.map((report) => (
                    <Grid item xs={12} key={report.id}>
                      <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Assessment Report - {new Date(report.date).toLocaleDateString()}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Typography variant="body1" sx={{ mr: 1 }}>
                            Overall Score:
                          </Typography>
                          <Rating value={report.overallScore} precision={0.5} readOnly />
                        </Box>
                        <Typography variant="body1" paragraph>
                          {report.feedback}
                        </Typography>
                        <Typography variant="h6" gutterBottom>
                          Recommendations:
                        </Typography>
                        <ul>
                          {report.recommendations.map((rec, index) => (
                            <li key={index}>
                              <Typography variant="body2">{rec}</Typography>
                            </li>
                          ))}
                        </ul>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assessment Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedAssessment ? 'Edit Assessment' : 'New Assessment'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Skill"
                defaultValue={selectedAssessment?.skill}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  label="Category"
                  defaultValue={selectedAssessment?.category || 'fitness'}
                >
                  {categories.filter(cat => cat !== 'all').map((category) => (
                    <MenuItem key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={4}
                defaultValue={selectedAssessment?.notes}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleCloseDialog}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssessmentPanel; 