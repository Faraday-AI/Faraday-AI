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
  TextField,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Alert,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccessibilityNew as AccessibilityIcon,
  Assignment as AssignmentIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface Student {
  id: string;
  name: string;
  grade: string;
  accommodations: string[];
  medicalNotes: string;
  emergencyContact: string;
  goals: AdaptiveGoal[];
  activities: AdaptiveActivity[];
}

interface AdaptiveGoal {
  id: string;
  description: string;
  targetDate: string;
  status: 'in-progress' | 'achieved' | 'needs-review';
  notes: string;
}

interface AdaptiveActivity {
  id: string;
  name: string;
  description: string;
  modifications: string[];
  equipment: string[];
  safetyNotes: string;
  difficulty: 'low' | 'medium' | 'high';
  lastPerformed?: string;
  progress?: number;
}

const DEFAULT_STUDENTS: Student[] = [
  {
    id: '1',
    name: 'Alex Johnson',
    grade: '9th',
    accommodations: [
      'Modified equipment',
      'Extended rest periods',
      'Visual demonstrations',
    ],
    medicalNotes: 'Mild mobility limitations in left leg',
    emergencyContact: 'Sarah Johnson (555-0123)',
    goals: [
      {
        id: '1',
        description: 'Improve balance and coordination',
        targetDate: '2024-06-01',
        status: 'in-progress',
        notes: 'Making steady progress with balance exercises',
      },
    ],
    activities: [
      {
        id: '1',
        name: 'Modified Basketball',
        description: 'Basketball drills adapted for limited mobility',
        modifications: [
          'Lower basket height',
          'Use lighter ball',
          'Allow additional steps',
        ],
        equipment: ['Lightweight basketball', 'Adjustable hoop'],
        safetyNotes: 'Ensure clear path and non-slip surface',
        difficulty: 'medium',
        lastPerformed: '2024-03-01',
        progress: 75,
      },
    ],
  },
  {
    id: '2',
    name: 'Emily Chen',
    grade: '10th',
    accommodations: [
      'Sensory accommodations',
      'Clear verbal instructions',
      'Partner assistance',
    ],
    medicalNotes: 'Sensory processing sensitivity',
    emergencyContact: 'David Chen (555-0124)',
    goals: [
      {
        id: '2',
        description: 'Develop team sport participation',
        targetDate: '2024-05-15',
        status: 'in-progress',
        notes: 'Showing increased comfort in group activities',
      },
    ],
    activities: [
      {
        id: '2',
        name: 'Adaptive Volleyball',
        description: 'Modified volleyball with sensory considerations',
        modifications: [
          'Soft touch ball',
          'Reduced noise environment',
          'Modified rules',
        ],
        equipment: ['Soft volleyball', 'Lower net'],
        safetyNotes: 'Monitor sensory overload signs',
        difficulty: 'low',
        lastPerformed: '2024-03-02',
        progress: 60,
      },
    ],
  },
];

export const AdaptivePEWidget: React.FC = () => {
  const [students, setStudents] = useState<Student[]>(DEFAULT_STUDENTS);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showStudentDialog, setShowStudentDialog] = useState(false);
  const [showActivityDialog, setShowActivityDialog] = useState(false);
  const [showGoalDialog, setShowGoalDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [newActivity, setNewActivity] = useState<Partial<AdaptiveActivity>>({
    difficulty: 'medium',
  });
  const [newGoal, setNewGoal] = useState<Partial<AdaptiveGoal>>({
    status: 'in-progress',
  });

  const handleAddActivity = () => {
    if (!selectedStudent || !newActivity.name || !newActivity.description) {
      setError('Please fill in all required fields');
      return;
    }

    const activity: AdaptiveActivity = {
      id: Date.now().toString(),
      name: newActivity.name,
      description: newActivity.description,
      modifications: newActivity.modifications || [],
      equipment: newActivity.equipment || [],
      safetyNotes: newActivity.safetyNotes || '',
      difficulty: newActivity.difficulty || 'medium',
      lastPerformed: new Date().toISOString().split('T')[0],
      progress: 0,
    };

    setStudents(students.map(student =>
      student.id === selectedStudent.id
        ? { ...student, activities: [...student.activities, activity] }
        : student
    ));
    setShowActivityDialog(false);
    setNewActivity({ difficulty: 'medium' });
  };

  const handleAddGoal = () => {
    if (!selectedStudent || !newGoal.description || !newGoal.targetDate) {
      setError('Please fill in all required fields');
      return;
    }

    const goal: AdaptiveGoal = {
      id: Date.now().toString(),
      description: newGoal.description,
      targetDate: newGoal.targetDate,
      status: newGoal.status || 'in-progress',
      notes: newGoal.notes || '',
    };

    setStudents(students.map(student =>
      student.id === selectedStudent.id
        ? { ...student, goals: [...student.goals, goal] }
        : student
    ));
    setShowGoalDialog(false);
    setNewGoal({ status: 'in-progress' });
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Adaptive Physical Education</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setShowStudentDialog(true)}
              >
                Add Student
              </Button>
              <Button
                variant="contained"
                startIcon={<AssignmentIcon />}
                onClick={() => {
                  if (selectedStudent) {
                    setShowActivityDialog(true);
                  } else {
                    setError('Please select a student first');
                  }
                }}
              >
                Add Activity
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Tabs */}
          <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
            <Tab label="Students" />
            <Tab label="Activities" />
            <Tab label="Goals" />
          </Tabs>

          {/* Students Tab */}
          {activeTab === 0 && (
            <Grid container spacing={2}>
              {students.map(student => (
                <Grid item xs={12} key={student.id}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <AccessibilityIcon color="primary" />
                        <Typography variant="subtitle1">{student.name}</Typography>
                        <Chip label={student.grade} size="small" />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Accommodations
                            </Typography>
                            <List dense>
                              {student.accommodations.map((acc, index) => (
                                <ListItem key={index}>
                                  <ListItemText primary={acc} />
                                </ListItem>
                              ))}
                            </List>
                          </Paper>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Medical Information
                            </Typography>
                            <Typography variant="body2" color="error">
                              {student.medicalNotes}
                            </Typography>
                            <Typography variant="body2" mt={1}>
                              Emergency Contact: {student.emergencyContact}
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={12}>
                          <Box display="flex" gap={1}>
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => {
                                setSelectedStudent(student);
                                setShowGoalDialog(true);
                              }}
                            >
                              Add Goal
                            </Button>
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => {
                                setSelectedStudent(student);
                                setShowActivityDialog(true);
                              }}
                            >
                              Add Activity
                            </Button>
                          </Box>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              ))}
            </Grid>
          )}

          {/* Activities Tab */}
          {activeTab === 1 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Activity</TableCell>
                    <TableCell>Difficulty</TableCell>
                    <TableCell>Last Performed</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.flatMap(student =>
                    student.activities.map(activity => (
                      <TableRow key={`${student.id}-${activity.id}`}>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>
                          <Tooltip title={activity.description}>
                            <Typography variant="body2">{activity.name}</Typography>
                          </Tooltip>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={activity.difficulty}
                            color={
                              activity.difficulty === 'high'
                                ? 'error'
                                : activity.difficulty === 'medium'
                                ? 'warning'
                                : 'success'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {activity.lastPerformed
                            ? new Date(activity.lastPerformed).toLocaleDateString()
                            : 'Not started'}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body2">
                              {activity.progress || 0}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedStudent(student);
                              setNewActivity(activity);
                              setShowActivityDialog(true);
                            }}
                          >
                            <EditIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Goals Tab */}
          {activeTab === 2 && (
            <Grid container spacing={2}>
              {students.map(student => (
                <Grid item xs={12} md={6} key={student.id}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {student.name}'s Goals
                    </Typography>
                    <List>
                      {student.goals.map(goal => (
                        <ListItem key={goal.id}>
                          <ListItemText
                            primary={goal.description}
                            secondary={`Target: ${new Date(goal.targetDate).toLocaleDateString()}`}
                          />
                          <ListItemSecondaryAction>
                            <Chip
                              label={goal.status}
                              color={
                                goal.status === 'achieved'
                                  ? 'success'
                                  : goal.status === 'needs-review'
                                  ? 'warning'
                                  : 'default'
                              }
                              size="small"
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<AddIcon />}
                      onClick={() => {
                        setSelectedStudent(student);
                        setShowGoalDialog(true);
                      }}
                    >
                      Add Goal
                    </Button>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </CardContent>

      {/* Add/Edit Activity Dialog */}
      <Dialog open={showActivityDialog} onClose={() => setShowActivityDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {newActivity.id ? 'Edit Activity' : 'Add Activity'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Activity Name"
              fullWidth
              defaultValue={newActivity.name}
              onChange={(e) => setNewActivity({ ...newActivity, name: e.target.value })}
            />
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              defaultValue={newActivity.description}
              onChange={(e) => setNewActivity({ ...newActivity, description: e.target.value })}
            />
            <TextField
              label="Modifications (one per line)"
              multiline
              rows={3}
              fullWidth
              defaultValue={newActivity.modifications?.join('\n')}
              onChange={(e) => setNewActivity({ ...newActivity, modifications: e.target.value.split('\n') })}
            />
            <TextField
              label="Equipment (one per line)"
              multiline
              rows={2}
              fullWidth
              defaultValue={newActivity.equipment?.join('\n')}
              onChange={(e) => setNewActivity({ ...newActivity, equipment: e.target.value.split('\n') })}
            />
            <TextField
              label="Safety Notes"
              multiline
              rows={2}
              fullWidth
              defaultValue={newActivity.safetyNotes}
              onChange={(e) => setNewActivity({ ...newActivity, safetyNotes: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Difficulty</InputLabel>
              <Select
                value={newActivity.difficulty || 'medium'}
                label="Difficulty"
                onChange={(e) => setNewActivity({ ...newActivity, difficulty: e.target.value as AdaptiveActivity['difficulty'] })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowActivityDialog(false);
            setNewActivity({ difficulty: 'medium' });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAddActivity}
          >
            {newActivity.id ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Goal Dialog */}
      <Dialog open={showGoalDialog} onClose={() => setShowGoalDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {newGoal.id ? 'Edit Goal' : 'Add Goal'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Goal Description"
              multiline
              rows={2}
              fullWidth
              defaultValue={newGoal.description}
              onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
            />
            <TextField
              label="Target Date"
              type="date"
              fullWidth
              defaultValue={newGoal.targetDate}
              onChange={(e) => setNewGoal({ ...newGoal, targetDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={newGoal.status || 'in-progress'}
                label="Status"
                onChange={(e) => setNewGoal({ ...newGoal, status: e.target.value as AdaptiveGoal['status'] })}
              >
                <MenuItem value="in-progress">In Progress</MenuItem>
                <MenuItem value="achieved">Achieved</MenuItem>
                <MenuItem value="needs-review">Needs Review</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              defaultValue={newGoal.notes}
              onChange={(e) => setNewGoal({ ...newGoal, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowGoalDialog(false);
            setNewGoal({ status: 'in-progress' });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAddGoal}
          >
            {newGoal.id ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 