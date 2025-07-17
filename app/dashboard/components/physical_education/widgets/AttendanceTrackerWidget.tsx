import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Alert,
  Tooltip,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  TrendingUp as StatsIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';

interface Student {
  id: string;
  name: string;
  grade: string;
  attendance: AttendanceRecord[];
  participation: ParticipationRecord[];
}

interface AttendanceRecord {
  id: string;
  date: string;
  status: 'present' | 'absent' | 'late' | 'excused';
  notes?: string;
}

interface ParticipationRecord {
  id: string;
  date: string;
  level: 'excellent' | 'good' | 'fair' | 'poor';
  activity: string;
  notes?: string;
}

const DEFAULT_STUDENTS: Student[] = [
  {
    id: '1',
    name: 'John Doe',
    grade: '9th',
    attendance: [],
    participation: [],
  },
  {
    id: '2',
    name: 'Jane Smith',
    grade: '10th',
    attendance: [],
    participation: [],
  },
];

const ATTENDANCE_STATUS = ['present', 'absent', 'late', 'excused'];
const PARTICIPATION_LEVELS = ['excellent', 'good', 'fair', 'poor'];

export const AttendanceTrackerWidget: React.FC = () => {
  const [students, setStudents] = useState<Student[]>(DEFAULT_STUDENTS);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showStudentDialog, setShowStudentDialog] = useState(false);
  const [showAttendanceDialog, setShowAttendanceDialog] = useState(false);
  const [showParticipationDialog, setShowParticipationDialog] = useState(false);
  const [newStudent, setNewStudent] = useState<Partial<Student>>({
    grade: '9th',
  });
  const [newAttendance, setNewAttendance] = useState<Partial<AttendanceRecord>>({
    status: 'present',
    date: new Date().toISOString().split('T')[0],
  });
  const [newParticipation, setNewParticipation] = useState<Partial<ParticipationRecord>>({
    level: 'good',
    date: new Date().toISOString().split('T')[0],
  });
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);

  const addStudent = (student: Student) => {
    setStudents([...students, student]);
    setShowStudentDialog(false);
    setNewStudent({ grade: '9th' });
  };

  const addAttendance = (studentId: string, attendance: AttendanceRecord) => {
    setStudents(students.map(student => {
      if (student.id === studentId) {
        return {
          ...student,
          attendance: [...student.attendance, attendance],
        };
      }
      return student;
    }));
    setShowAttendanceDialog(false);
    setNewAttendance({
      status: 'present',
      date: new Date().toISOString().split('T')[0],
    });
  };

  const addParticipation = (studentId: string, participation: ParticipationRecord) => {
    setStudents(students.map(student => {
      if (student.id === studentId) {
        return {
          ...student,
          participation: [...student.participation, participation],
        };
      }
      return student;
    }));
    setShowParticipationDialog(false);
    setNewParticipation({
      level: 'good',
      date: new Date().toISOString().split('T')[0],
    });
  };

  const removeStudent = (studentId: string) => {
    setStudents(students.filter(s => s.id !== studentId));
  };

  const getAttendanceStats = () => {
    const stats = {
      present: 0,
      absent: 0,
      late: 0,
      excused: 0,
    };

    students.forEach(student => {
      student.attendance.forEach(record => {
        if (record.date === selectedDate) {
          stats[record.status]++;
        }
      });
    });

    return stats;
  };

  const getParticipationStats = () => {
    const stats = {
      excellent: 0,
      good: 0,
      fair: 0,
      poor: 0,
    };

    students.forEach(student => {
      student.participation.forEach(record => {
        if (record.date === selectedDate) {
          stats[record.level]++;
        }
      });
    });

    return stats;
  };

  const exportData = () => {
    const data = {
      students,
      date: selectedDate,
      attendanceStats: getAttendanceStats(),
      participationStats: getParticipationStats(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_data_${selectedDate}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Attendance Tracker</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowStudentDialog(true)}
              >
                Add Student
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={exportData}
              >
                Export
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Date Selection */}
          <TextField
            type="date"
            label="Select Date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            fullWidth
            InputLabelProps={{ shrink: true }}
          />

          {/* Tabs */}
          <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)}>
            <Tab label="Attendance" />
            <Tab label="Participation" />
            <Tab label="Statistics" />
          </Tabs>

          {/* Attendance Tab */}
          {activeTab === 0 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Notes</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.map(student => {
                    const attendance = student.attendance.find(a => a.date === selectedDate);
                    return (
                      <TableRow key={student.id}>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>{student.grade}</TableCell>
                        <TableCell>
                          <Chip
                            label={attendance?.status || 'Not Recorded'}
                            color={
                              attendance?.status === 'present'
                                ? 'success'
                                : attendance?.status === 'absent'
                                ? 'error'
                                : attendance?.status === 'late'
                                ? 'warning'
                                : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>{attendance?.notes}</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => {
                              setSelectedStudent(student);
                              setShowAttendanceDialog(true);
                            }}
                          >
                            Record
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Participation Tab */}
          {activeTab === 1 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Student</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Level</TableCell>
                    <TableCell>Activity</TableCell>
                    <TableCell>Notes</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {students.map(student => {
                    const participation = student.participation.find(p => p.date === selectedDate);
                    return (
                      <TableRow key={student.id}>
                        <TableCell>{student.name}</TableCell>
                        <TableCell>{student.grade}</TableCell>
                        <TableCell>
                          <Chip
                            label={participation?.level || 'Not Recorded'}
                            color={
                              participation?.level === 'excellent'
                                ? 'success'
                                : participation?.level === 'good'
                                ? 'primary'
                                : participation?.level === 'fair'
                                ? 'warning'
                                : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell>{participation?.activity}</TableCell>
                        <TableCell>{participation?.notes}</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => {
                              setSelectedStudent(student);
                              setShowParticipationDialog(true);
                            }}
                          >
                            Record
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Statistics Tab */}
          {activeTab === 2 && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box p={2} border="1px solid" borderColor="divider" borderRadius={1}>
                  <Typography variant="subtitle1" gutterBottom>
                    Attendance Statistics
                  </Typography>
                  <Box height={300}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={[getAttendanceStats()]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <ChartTooltip />
                        <Bar dataKey="present" fill="#4CAF50" name="Present" />
                        <Bar dataKey="absent" fill="#F44336" name="Absent" />
                        <Bar dataKey="late" fill="#FFC107" name="Late" />
                        <Bar dataKey="excused" fill="#9E9E9E" name="Excused" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box p={2} border="1px solid" borderColor="divider" borderRadius={1}>
                  <Typography variant="subtitle1" gutterBottom>
                    Participation Statistics
                  </Typography>
                  <Box height={300}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={[getParticipationStats()]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <ChartTooltip />
                        <Bar dataKey="excellent" fill="#4CAF50" name="Excellent" />
                        <Bar dataKey="good" fill="#2196F3" name="Good" />
                        <Bar dataKey="fair" fill="#FFC107" name="Fair" />
                        <Bar dataKey="poor" fill="#F44336" name="Poor" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      </CardContent>

      {/* Add Student Dialog */}
      <Dialog open={showStudentDialog} onClose={() => setShowStudentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Student</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Student Name"
              fullWidth
              onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Grade</InputLabel>
              <Select
                label="Grade"
                value={newStudent.grade}
                onChange={(e) => setNewStudent({ ...newStudent, grade: e.target.value })}
              >
                {['9th', '10th', '11th', '12th'].map(grade => (
                  <MenuItem key={grade} value={grade}>{grade}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowStudentDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (newStudent.name && newStudent.grade) {
                addStudent({
                  ...newStudent as Student,
                  id: Date.now().toString(),
                  attendance: [],
                  participation: [],
                });
              } else {
                setError('Please fill in all fields');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Attendance Dialog */}
      <Dialog open={showAttendanceDialog} onClose={() => setShowAttendanceDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Attendance</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                label="Status"
                value={newAttendance.status}
                onChange={(e) => setNewAttendance({ ...newAttendance, status: e.target.value as AttendanceRecord['status'] })}
              >
                {ATTENDANCE_STATUS.map(status => (
                  <MenuItem key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewAttendance({ ...newAttendance, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAttendanceDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedStudent && newAttendance.status) {
                addAttendance(selectedStudent.id, {
                  ...newAttendance as AttendanceRecord,
                  id: Date.now().toString(),
                  date: selectedDate,
                });
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Participation Dialog */}
      <Dialog open={showParticipationDialog} onClose={() => setShowParticipationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Participation</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Level</InputLabel>
              <Select
                label="Level"
                value={newParticipation.level}
                onChange={(e) => setNewParticipation({ ...newParticipation, level: e.target.value as ParticipationRecord['level'] })}
              >
                {PARTICIPATION_LEVELS.map(level => (
                  <MenuItem key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Activity"
              fullWidth
              onChange={(e) => setNewParticipation({ ...newParticipation, activity: e.target.value })}
            />
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewParticipation({ ...newParticipation, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowParticipationDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedStudent && newParticipation.level && newParticipation.activity) {
                addParticipation(selectedStudent.id, {
                  ...newParticipation as ParticipationRecord,
                  id: Date.now().toString(),
                  date: selectedDate,
                });
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 