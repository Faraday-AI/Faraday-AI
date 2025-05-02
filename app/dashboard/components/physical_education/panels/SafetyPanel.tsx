import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Alert,
  CircularProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  EmergencyShare as EmergencyIcon,
  Assessment as AssessmentIcon,
  Report as ReportIcon,
} from '@mui/icons-material';

interface SafetyProtocol {
  id: number;
  name: string;
  description: string;
  category: string;
  steps: string[];
  lastUpdated: string;
  status: string;
}

interface EmergencyProcedure {
  id: number;
  name: string;
  description: string;
  steps: string[];
  contactInfo: string[];
  lastDrillDate: string;
  nextDrillDate: string;
}

interface RiskAssessment {
  id: number;
  activity: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  hazards: string[];
  controls: string[];
  lastAssessed: string;
  nextAssessment: string;
}

interface IncidentReport {
  id: number;
  date: string;
  time: string;
  location: string;
  type: string;
  description: string;
  severity: 'MINOR' | 'MODERATE' | 'SEVERE';
  actionsTaken: string[];
  followUpRequired: boolean;
  status: string;
}

const API_BASE_URL = '/api/safety';

export const SafetyPanel: React.FC = () => {
  const [protocols, setProtocols] = useState<SafetyProtocol[]>([]);
  const [procedures, setProcedures] = useState<EmergencyProcedure[]>([]);
  const [assessments, setAssessments] = useState<RiskAssessment[]>([]);
  const [incidents, setIncidents] = useState<IncidentReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const fetchSafetyData = async () => {
    setLoading(true);
    try {
      const [protocolsRes, proceduresRes, assessmentsRes, incidentsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/protocols`),
        fetch(`${API_BASE_URL}/procedures`),
        fetch(`${API_BASE_URL}/assessments`),
        fetch(`${API_BASE_URL}/incidents`)
      ]);

      if (!protocolsRes.ok || !proceduresRes.ok || !assessmentsRes.ok || !incidentsRes.ok) {
        throw new Error('Failed to fetch safety data');
      }

      const [protocolsData, proceduresData, assessmentsData, incidentsData] = await Promise.all([
        protocolsRes.json(),
        proceduresRes.json(),
        assessmentsRes.json(),
        incidentsRes.json()
      ]);

      setProtocols(protocolsData);
      setProcedures(proceduresData);
      setAssessments(assessmentsData);
      setIncidents(incidentsData);
    } catch (err) {
      setError('Failed to fetch safety data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProtocol = async (protocol: SafetyProtocol) => {
    try {
      const response = await fetch(`${API_BASE_URL}/protocols`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(protocol),
      });

      if (!response.ok) {
        throw new Error('Failed to add protocol');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to add protocol');
    }
  };

  const handleUpdateProtocol = async (protocol: SafetyProtocol) => {
    try {
      const response = await fetch(`${API_BASE_URL}/protocols/${protocol.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(protocol),
      });

      if (!response.ok) {
        throw new Error('Failed to update protocol');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to update protocol');
    }
  };

  const handleDeleteProtocol = async (protocolId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/protocols/${protocolId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete protocol');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to delete protocol');
    }
  };

  useEffect(() => {
    fetchSafetyData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="safety tabs">
          <Tab label="Safety Protocols" icon={<WarningIcon />} />
          <Tab label="Emergency Procedures" icon={<EmergencyIcon />} />
          <Tab label="Risk Assessment" icon={<AssessmentIcon />} />
          <Tab label="Incident Reports" icon={<ReportIcon />} />
        </Tabs>
      </Box>

      <TabPanel value={selectedTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Safety Protocols
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  sx={{ mb: 2 }}
                >
                  Add Protocol
                </Button>
                <List>
                  {protocols.map((protocol: SafetyProtocol) => (
                    <React.Fragment key={protocol.id}>
                      <ListItem>
                        <ListItemText
                          primary={protocol.name}
                          secondary={protocol.description}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="edit">
                            <EditIcon />
                          </IconButton>
                          <IconButton edge="end" aria-label="delete">
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Emergency Procedures
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  sx={{ mb: 2 }}
                >
                  Add Procedure
                </Button>
                <List>
                  {procedures.map((procedure: EmergencyProcedure) => (
                    <React.Fragment key={procedure.id}>
                      <ListItem>
                        <ListItemText
                          primary={procedure.name}
                          secondary={procedure.description}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="edit">
                            <EditIcon />
                          </IconButton>
                          <IconButton edge="end" aria-label="delete">
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Assessments
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  sx={{ mb: 2 }}
                >
                  Add Assessment
                </Button>
                <List>
                  {assessments.map((assessment: RiskAssessment) => (
                    <React.Fragment key={assessment.id}>
                      <ListItem>
                        <ListItemText
                          primary={assessment.activity}
                          secondary={`Risk Level: ${assessment.riskLevel}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="edit">
                            <EditIcon />
                          </IconButton>
                          <IconButton edge="end" aria-label="delete">
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Incident Reports
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  sx={{ mb: 2 }}
                >
                  Add Report
                </Button>
                <List>
                  {incidents.map((incident: IncidentReport) => (
                    <React.Fragment key={incident.id}>
                      <ListItem>
                        <ListItemText
                          primary={`${incident.type} - ${incident.date}`}
                          secondary={`Severity: ${incident.severity}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton edge="end" aria-label="edit">
                            <EditIcon />
                          </IconButton>
                          <IconButton edge="end" aria-label="delete">
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`safety-tabpanel-${index}`}
      aria-labelledby={`safety-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
} 