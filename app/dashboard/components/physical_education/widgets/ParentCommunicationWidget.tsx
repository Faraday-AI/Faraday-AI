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
  Badge,
} from '@mui/material';
import {
  Send as SendIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  History as HistoryIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Message as MessageIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';

interface Parent {
  id: string;
  studentName: string;
  parentName: string;
  email: string;
  phone: string;
  preferredContact: 'email' | 'phone' | 'both';
  lastContacted?: string;
}

interface Communication {
  id: string;
  parentId: string;
  type: 'update' | 'conference' | 'progress' | 'emergency';
  subject: string;
  message: string;
  date: string;
  status: 'sent' | 'scheduled' | 'draft';
  scheduledDate?: string;
  readStatus?: boolean;
}

const DEFAULT_PARENTS: Parent[] = [
  {
    id: '1',
    studentName: 'John Doe',
    parentName: 'Jane Doe',
    email: 'jane.doe@email.com',
    phone: '555-0101',
    preferredContact: 'email',
    lastContacted: '2024-03-01',
  },
  {
    id: '2',
    studentName: 'Sarah Smith',
    parentName: 'Mike Smith',
    email: 'mike.smith@email.com',
    phone: '555-0102',
    preferredContact: 'both',
    lastContacted: '2024-02-28',
  },
];

const DEFAULT_COMMUNICATIONS: Communication[] = [
  {
    id: '1',
    parentId: '1',
    type: 'update',
    subject: 'Weekly Progress Update',
    message: 'John has shown great improvement in basketball skills this week.',
    date: '2024-03-01',
    status: 'sent',
    readStatus: true,
  },
  {
    id: '2',
    parentId: '2',
    type: 'conference',
    subject: 'Parent-Teacher Conference',
    message: 'Request for conference to discuss Sarah\'s fitness goals.',
    date: '2024-02-28',
    status: 'scheduled',
    scheduledDate: '2024-03-15T14:00',
  },
];

export const ParentCommunicationWidget: React.FC = () => {
  const [parents, setParents] = useState<Parent[]>(DEFAULT_PARENTS);
  const [communications, setCommunications] = useState<Communication[]>(DEFAULT_COMMUNICATIONS);
  const [selectedParent, setSelectedParent] = useState<Parent | null>(null);
  const [showMessageDialog, setShowMessageDialog] = useState(false);
  const [showConferenceDialog, setShowConferenceDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [newMessage, setNewMessage] = useState<Partial<Communication>>({
    type: 'update',
    status: 'draft',
  });
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'sent' | 'scheduled' | 'draft'>('all');

  const handleSendMessage = () => {
    if (!newMessage.subject || !newMessage.message || !selectedParent) {
      setError('Please fill in all required fields');
      return;
    }

    const message: Communication = {
      id: Date.now().toString(),
      parentId: selectedParent.id,
      type: newMessage.type || 'update',
      subject: newMessage.subject,
      message: newMessage.message,
      date: new Date().toISOString().split('T')[0],
      status: 'sent',
      scheduledDate: newMessage.scheduledDate,
      readStatus: false,
    };

    setCommunications([...communications, message]);
    setShowMessageDialog(false);
    setNewMessage({ type: 'update', status: 'draft' });
    setSelectedParent(null);
  };

  const getFilteredCommunications = () => {
    return communications.filter(comm => {
      if (filter === 'all') return true;
      return comm.status === filter;
    });
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Parent Communication</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<ScheduleIcon />}
                onClick={() => setShowConferenceDialog(true)}
              >
                Schedule Conference
              </Button>
              <Button
                variant="contained"
                startIcon={<SendIcon />}
                onClick={() => setShowMessageDialog(true)}
              >
                New Message
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
            <Tab label="Messages" />
            <Tab label="Parents" />
            <Tab label="History" />
          </Tabs>

          {/* Messages Tab */}
          {activeTab === 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <FormControl size="small" sx={{ width: 200 }}>
                  <InputLabel>Filter</InputLabel>
                  <Select
                    value={filter}
                    label="Filter"
                    onChange={(e) => setFilter(e.target.value as typeof filter)}
                  >
                    <MenuItem value="all">All Messages</MenuItem>
                    <MenuItem value="sent">Sent</MenuItem>
                    <MenuItem value="scheduled">Scheduled</MenuItem>
                    <MenuItem value="draft">Drafts</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Parent</TableCell>
                      <TableCell>Subject</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {getFilteredCommunications().map(comm => {
                      const parent = parents.find(p => p.id === comm.parentId);
                      return (
                        <TableRow key={comm.id}>
                          <TableCell>
                            {comm.scheduledDate
                              ? new Date(comm.scheduledDate).toLocaleDateString()
                              : new Date(comm.date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={comm.type}
                              color={
                                comm.type === 'emergency'
                                  ? 'error'
                                  : comm.type === 'conference'
                                  ? 'warning'
                                  : 'default'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{parent?.parentName}</TableCell>
                          <TableCell>{comm.subject}</TableCell>
                          <TableCell>
                            <Chip
                              label={comm.status}
                              color={
                                comm.status === 'sent'
                                  ? 'success'
                                  : comm.status === 'scheduled'
                                  ? 'info'
                                  : 'default'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedParent(parent || null);
                                setNewMessage(comm);
                                setShowMessageDialog(true);
                              }}
                            >
                              <EditIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setCommunications(communications.filter(c => c.id !== comm.id));
                              }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Parents Tab */}
          {activeTab === 1 && (
            <Grid container spacing={2}>
              {parents.map(parent => (
                <Grid item xs={12} md={6} key={parent.id}>
                  <Paper sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle1">
                        {parent.studentName}'s Parent
                      </Typography>
                      <Box>
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedParent(parent);
                            setShowMessageDialog(true);
                          }}
                        >
                          <SendIcon />
                        </IconButton>
                      </Box>
                    </Box>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="Parent Name"
                          secondary={parent.parentName}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Email"
                          secondary={parent.email}
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            size="small"
                            onClick={() => {/* Email functionality */}}
                          >
                            <EmailIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Phone"
                          secondary={parent.phone}
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            size="small"
                            onClick={() => {/* Phone functionality */}}
                          >
                            <PhoneIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Last Contacted"
                          secondary={new Date(parent.lastContacted || '').toLocaleDateString()}
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}

          {/* History Tab */}
          {activeTab === 2 && (
            <Paper sx={{ p: 2 }}>
              <List>
                {communications
                  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                  .map(comm => {
                    const parent = parents.find(p => p.id === comm.parentId);
                    return (
                      <ListItem key={comm.id}>
                        <ListItemText
                          primary={`${comm.subject} - ${parent?.parentName}`}
                          secondary={`${new Date(comm.date).toLocaleDateString()} - ${comm.type}`}
                        />
                        <ListItemSecondaryAction>
                          <Chip
                            label={comm.status}
                            size="small"
                            color={
                              comm.status === 'sent'
                                ? 'success'
                                : comm.status === 'scheduled'
                                ? 'info'
                                : 'default'
                            }
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    );
                  })}
              </List>
            </Paper>
          )}
        </Box>
      </CardContent>

      {/* New Message Dialog */}
      <Dialog open={showMessageDialog} onClose={() => setShowMessageDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {newMessage.id ? 'Edit Message' : 'New Message'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Parent</InputLabel>
              <Select
                value={selectedParent?.id || ''}
                label="Parent"
                onChange={(e) => {
                  const parent = parents.find(p => p.id === e.target.value);
                  setSelectedParent(parent || null);
                }}
              >
                {parents.map(parent => (
                  <MenuItem key={parent.id} value={parent.id}>
                    {parent.parentName} ({parent.studentName}'s Parent)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={newMessage.type || 'update'}
                label="Type"
                onChange={(e) => setNewMessage({ ...newMessage, type: e.target.value as Communication['type'] })}
              >
                <MenuItem value="update">Update</MenuItem>
                <MenuItem value="conference">Conference</MenuItem>
                <MenuItem value="progress">Progress Report</MenuItem>
                <MenuItem value="emergency">Emergency</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Subject"
              fullWidth
              defaultValue={newMessage.subject}
              onChange={(e) => setNewMessage({ ...newMessage, subject: e.target.value })}
            />
            <TextField
              label="Message"
              multiline
              rows={4}
              fullWidth
              defaultValue={newMessage.message}
              onChange={(e) => setNewMessage({ ...newMessage, message: e.target.value })}
            />
            {newMessage.type === 'conference' && (
              <TextField
                label="Schedule Date"
                type="datetime-local"
                fullWidth
                defaultValue={newMessage.scheduledDate}
                onChange={(e) => setNewMessage({ ...newMessage, scheduledDate: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowMessageDialog(false);
            setNewMessage({ type: 'update', status: 'draft' });
            setSelectedParent(null);
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color={newMessage.type === 'emergency' ? 'error' : 'primary'}
            onClick={handleSendMessage}
          >
            {newMessage.id ? 'Update' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Schedule Conference Dialog */}
      <Dialog open={showConferenceDialog} onClose={() => setShowConferenceDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Schedule Parent-Teacher Conference</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Parent</InputLabel>
              <Select
                value={selectedParent?.id || ''}
                label="Parent"
                onChange={(e) => {
                  const parent = parents.find(p => p.id === e.target.value);
                  setSelectedParent(parent || null);
                }}
              >
                {parents.map(parent => (
                  <MenuItem key={parent.id} value={parent.id}>
                    {parent.parentName} ({parent.studentName}'s Parent)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Date & Time"
              type="datetime-local"
              fullWidth
              InputLabelProps={{ shrink: true }}
              onChange={(e) => setNewMessage({ ...newMessage, scheduledDate: e.target.value })}
            />
            <TextField
              label="Notes"
              multiline
              rows={3}
              fullWidth
              onChange={(e) => setNewMessage({ ...newMessage, message: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowConferenceDialog(false);
            setNewMessage({ type: 'update', status: 'draft' });
            setSelectedParent(null);
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (selectedParent && newMessage.scheduledDate) {
                const conference: Communication = {
                  id: Date.now().toString(),
                  parentId: selectedParent.id,
                  type: 'conference',
                  subject: 'Parent-Teacher Conference',
                  message: newMessage.message || 'Parent-teacher conference scheduled.',
                  date: new Date().toISOString().split('T')[0],
                  status: 'scheduled',
                  scheduledDate: newMessage.scheduledDate,
                };
                setCommunications([...communications, conference]);
                setShowConferenceDialog(false);
                setNewMessage({ type: 'update', status: 'draft' });
                setSelectedParent(null);
              } else {
                setError('Please select a parent and schedule date');
              }
            }}
          >
            Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 