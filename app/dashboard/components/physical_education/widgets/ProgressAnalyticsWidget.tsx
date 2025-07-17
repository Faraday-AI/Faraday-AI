import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Assessment as AssessmentIcon,
  Add as AddIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface Student {
  id: string;
  name: string;
  grade: string;
  performance: {
    date: string;
    skillScore: number;
    fitnessScore: number;
    participationScore: number;
  }[];
}

interface Milestone {
  id: string;
  name: string;
  description: string;
  targetScore: number;
  achievedBy: string[];
}

const DEFAULT_STUDENTS: Student[] = [
  {
    id: '1',
    name: 'John Doe',
    grade: '9th',
    performance: [
      {
        date: '2024-01-01',
        skillScore: 75,
        fitnessScore: 80,
        participationScore: 90,
      },
      {
        date: '2024-02-01',
        skillScore: 82,
        fitnessScore: 85,
        participationScore: 95,
      },
    ],
  },
  {
    id: '2',
    name: 'Jane Smith',
    grade: '10th',
    performance: [
      {
        date: '2024-01-01',
        skillScore: 85,
        fitnessScore: 90,
        participationScore: 95,
      },
      {
        date: '2024-02-01',
        skillScore: 88,
        fitnessScore: 92,
        participationScore: 98,
      },
    ],
  },
];

const DEFAULT_MILESTONES: Milestone[] = [
  {
    id: '1',
    name: 'Fitness Excellence',
    description: 'Achieve 90% in all fitness assessments',
    targetScore: 90,
    achievedBy: ['2'],
  },
  {
    id: '2',
    name: 'Skill Mastery',
    description: 'Master 5 core skills',
    targetScore: 85,
    achievedBy: ['1', '2'],
  },
];

export const ProgressAnalyticsWidget: React.FC = () => {
  const [students, setStudents] = useState<Student[]>(DEFAULT_STUDENTS);
  const [milestones, setMilestones] = useState<Milestone[]>(DEFAULT_MILESTONES);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showMilestoneDialog, setShowMilestoneDialog] = useState(false);
  const [newMilestone, setNewMilestone] = useState<Partial<Milestone>>({
    targetScore: 80,
  });
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'semester'>('month');

  const getStudentProgress = (studentId: string) => {
    const student = students.find(s => s.id === studentId);
    if (!student) return [];

    return student.performance.map(p => ({
      date: p.date,
      score: (p.skillScore + p.fitnessScore + p.participationScore) / 3,
    }));
  };

  const getClassAverage = () => {
    const averages = students.map(student => {
      const latest = student.performance[student.performance.length - 1];
      return (latest.skillScore + latest.fitnessScore + latest.participationScore) / 3;
    });
    return averages.reduce((a, b) => a + b, 0) / averages.length;
  };

  const getPerformanceDistribution = () => {
    const latestScores = students.map(student => {
      const latest = student.performance[student.performance.length - 1];
      return (latest.skillScore + latest.fitnessScore + latest.participationScore) / 3;
    });

    return [
      { name: 'Excellent (90-100)', value: latestScores.filter(s => s >= 90).length },
      { name: 'Good (80-89)', value: latestScores.filter(s => s >= 80 && s < 90).length },
      { name: 'Average (70-79)', value: latestScores.filter(s => s >= 70 && s < 80).length },
      { name: 'Needs Improvement (<70)', value: latestScores.filter(s => s < 70).length },
    ];
  };

  const COLORS = ['#4CAF50', '#2196F3', '#FFC107', '#F44336'];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Progress Analytics</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={() => setShowMilestoneDialog(true)}
              >
                Add Milestone
              </Button>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => {/* Export functionality */}}
              >
                Export Report
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Time Range Selector */}
          <FormControl fullWidth>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value as 'week' | 'month' | 'semester')}
            >
              <MenuItem value="week">Last Week</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
              <MenuItem value="semester">This Semester</MenuItem>
            </Select>
          </FormControl>

          {/* Class Overview */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Class Average
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <Typography variant="h4">
                    {getClassAverage().toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={getClassAverage()}
                    sx={{ flexGrow: 1 }}
                  />
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Performance Distribution
                </Typography>
                <Box height={200}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getPerformanceDistribution()}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                      >
                        {getPerformanceDistribution().map((entry, index) => (
                          <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <ChartTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Student Progress */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Student Progress
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Latest Score</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.map(student => {
                    const latest = student.performance[student.performance.length - 1];
                    const averageScore = (latest.skillScore + latest.fitnessScore + latest.participationScore) / 3;
                    const previous = student.performance[student.performance.length - 2];
                    const previousAverage = previous ? (previous.skillScore + previous.fitnessScore + previous.participationScore) / 3 : 0;
                    const progress = averageScore - previousAverage;

                    return (
                      <TableRow key={student.id}>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>{student.grade}</TableCell>
                        <TableCell>{averageScore.toFixed(1)}%</TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography
                              variant="body2"
                              color={progress >= 0 ? 'success.main' : 'error.main'}
                            >
                              {progress >= 0 ? '+' : ''}{progress.toFixed(1)}%
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => setSelectedStudent(student)}
                            >
                              <AssessmentIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => {/* View details */}}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Milestones */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Milestones
            </Typography>
            <Grid container spacing={2}>
              {milestones.map(milestone => (
                <Grid item xs={12} md={6} key={milestone.id}>
                  <Paper sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle2">{milestone.name}</Typography>
                      <Chip
                        label={`${milestone.achievedBy.length} achieved`}
                        color="primary"
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {milestone.description}
                    </Typography>
                    <Box mt={1}>
                      <LinearProgress
                        variant="determinate"
                        value={(milestone.achievedBy.length / students.length) * 100}
                      />
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Box>
      </CardContent>

      {/* Add Milestone Dialog */}
      <Dialog open={showMilestoneDialog} onClose={() => setShowMilestoneDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Milestone</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Name"
              fullWidth
              onChange={(e) => setNewMilestone({ ...newMilestone, name: e.target.value })}
            />
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewMilestone({ ...newMilestone, description: e.target.value })}
            />
            <TextField
              label="Target Score"
              type="number"
              fullWidth
              defaultValue={80}
              onChange={(e) => setNewMilestone({ ...newMilestone, targetScore: parseInt(e.target.value) })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMilestoneDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newMilestone.name && newMilestone.description && newMilestone.targetScore) {
                setMilestones([
                  ...milestones,
                  {
                    ...newMilestone as Milestone,
                    id: Date.now().toString(),
                    achievedBy: [],
                  },
                ]);
                setShowMilestoneDialog(false);
                setNewMilestone({ targetScore: 80 });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 