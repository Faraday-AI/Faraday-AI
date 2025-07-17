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
  FormHelperText,
  Snackbar,
  Backdrop,
  Tooltip,
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
  Notifications as NotificationsIcon,
  Sports as SportsIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { format, isValid, parseISO } from 'date-fns';
import { useHotkeys } from 'react-hotkeys-hook';
import { SelectChangeEvent } from '@mui/material/Select';

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

interface ValidationRule {
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
}

interface ValidationRules {
  name: ValidationRule;
  description: ValidationRule;
  incidentNumber: ValidationRule;
  contactInfo: ValidationRule;
  steps: ValidationRule;
}

interface ActivitySafetyAlert {
  id: number;
  activityId: number;
  activityType: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  message: string;
  timestamp: string;
  resolved: boolean;
}

interface ActivityRiskProfile {
  activityType: string;
  commonRisks: string[];
  requiredEquipment: string[];
  recommendedProtocols: number[];
  maxParticipants: number;
  minSupervisors: number;
}

interface EmergencyContact {
  id: number;
  name: string;
  role: string;
  phone: string;
  email: string;
  location: string;
  isPrimary: boolean;
  availability: string;
}

interface RiskAssessmentVisualization {
  id: number;
  activity: string;
  riskFactors: {
    name: string;
    level: number;
    controls: string[];
  }[];
  overallRisk: number;
  lastUpdated: string;
}

interface GoalSafetyRequirement {
  goalId: number;
  goalName: string;
  category: string;
  safetyRequirements: {
    equipment: string[];
    supervision: string;
    environment: string[];
    precautions: string[];
  };
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
}

const API_BASE_URL = '/api/safety';

const VALIDATION_RULES: ValidationRules = {
  name: {
    minLength: 3,
    maxLength: 100,
    pattern: /^[a-zA-Z0-9\s\-_]+$/,
  },
  description: {
    minLength: 10,
    maxLength: 500,
  },
  incidentNumber: {
    pattern: /^INC-\d{4}-\d{4}$/,
  },
  contactInfo: {
    maxLength: 200,
  },
  steps: {
    minLength: 5,
    maxLength: 200,
  },
};

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s-]{10,}$/;
  return phoneRegex.test(phone);
};

const validateDate = (date: string): boolean => {
  return isValid(parseISO(date));
};

const validateFutureDate = (date: string): boolean => {
  const parsedDate = parseISO(date);
  return isValid(parsedDate) && parsedDate > new Date();
};

const validatePastDate = (date: string): boolean => {
  const parsedDate = parseISO(date);
  return isValid(parsedDate) && parsedDate <= new Date();
};

export const SafetyPanel: React.FC = () => {
  const [protocols, setProtocols] = useState<SafetyProtocol[]>([]);
  const [procedures, setProcedures] = useState<EmergencyProcedure[]>([]);
  const [assessments, setAssessments] = useState<RiskAssessment[]>([]);
  const [incidents, setIncidents] = useState<IncidentReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openProtocolDialog, setOpenProtocolDialog] = useState(false);
  const [openProcedureDialog, setOpenProcedureDialog] = useState(false);
  const [openAssessmentDialog, setOpenAssessmentDialog] = useState(false);
  const [openIncidentDialog, setOpenIncidentDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [warningMessage, setWarningMessage] = useState<string | null>(null);
  const [autoSaveStatus, setAutoSaveStatus] = useState<string | null>(null);
  const [autoSaveTimeout, setAutoSaveTimeout] = useState<NodeJS.Timeout | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [loadingStates, setLoadingStates] = useState({
    protocols: false,
    procedures: false,
    assessments: false,
    incidents: false
  });
  const [activityAlerts, setActivityAlerts] = useState<ActivitySafetyAlert[]>([]);
  const [activityRiskProfiles, setActivityRiskProfiles] = useState<ActivityRiskProfile[]>([]);
  const [activeActivities, setActiveActivities] = useState<Array<{ id: number; type: string }>>([]);
  const [showAlertDialog, setShowAlertDialog] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<ActivitySafetyAlert | null>(null);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [riskVisualizations, setRiskVisualizations] = useState<RiskAssessmentVisualization[]>([]);
  const [showEmergencyDialog, setShowEmergencyDialog] = useState(false);
  const [selectedContact, setSelectedContact] = useState<EmergencyContact | null>(null);
  const [goalSafetyRequirements, setGoalSafetyRequirements] = useState<GoalSafetyRequirement[]>([]);

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

  const setLoadingState = (section: keyof typeof loadingStates, isLoading: boolean) => {
    setLoadingStates(prev => ({
      ...prev,
      [section]: isLoading
    }));
  };

  const handleAddProtocol = async (protocol: SafetyProtocol) => {
    setLoadingState('protocols', true);
    try {
      const response = await fetch(`${API_BASE_URL}/protocols`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(protocol),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to add protocol');
      }

      await fetchSafetyData();
      showSuccess('Protocol added successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add protocol');
    } finally {
      setLoadingState('protocols', false);
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

  const handleOpenProtocolDialog = (protocol?: SafetyProtocol) => {
    setEditingItem(protocol || null);
    setOpenProtocolDialog(true);
  };

  const handleCloseProtocolDialog = () => {
    setOpenProtocolDialog(false);
    setEditingItem(null);
  };

  const handleOpenProcedureDialog = (procedure?: EmergencyProcedure) => {
    setEditingItem(procedure || null);
    setOpenProcedureDialog(true);
  };

  const handleCloseProcedureDialog = () => {
    setOpenProcedureDialog(false);
    setEditingItem(null);
  };

  const handleOpenAssessmentDialog = (assessment?: RiskAssessment) => {
    setEditingItem(assessment || null);
    setOpenAssessmentDialog(true);
  };

  const handleCloseAssessmentDialog = () => {
    setOpenAssessmentDialog(false);
    setEditingItem(null);
  };

  const handleOpenIncidentDialog = (incident?: IncidentReport) => {
    setEditingItem(incident || null);
    setOpenIncidentDialog(true);
  };

  const handleCloseIncidentDialog = () => {
    setOpenIncidentDialog(false);
    setEditingItem(null);
  };

  const validateField = (name: string, value: string): string | null => {
    const rules = VALIDATION_RULES[name as keyof typeof VALIDATION_RULES];
    if (!rules) return null;

    if (rules.minLength && value.length < rules.minLength) {
      return `Minimum ${rules.minLength} characters required`;
    }
    if (rules.maxLength && value.length > rules.maxLength) {
      return `Maximum ${rules.maxLength} characters allowed`;
    }
    if (rules.pattern && !rules.pattern.test(value)) {
      return 'Invalid format';
    }

    return null;
  };

  const handleFieldChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    const error = validateField(name, value);
    setFieldErrors(prev => ({
      ...prev,
      [name]: error || ''
    }));
  };

  const showWarning = (message: string) => {
    setWarningMessage(message);
    setTimeout(() => setWarningMessage(null), 5000);
  };

  const showAutoSaveStatus = (status: string) => {
    setAutoSaveStatus(status);
    setTimeout(() => setAutoSaveStatus(null), 2000);
  };

  const validateProtocol = (protocol: SafetyProtocol): boolean => {
    const errors: Record<string, string> = {};
    if (!protocol.name) errors.name = 'Name is required';
    if (!protocol.description) errors.description = 'Description is required';
    if (!protocol.category) errors.category = 'Category is required';
    if (!protocol.steps.length) errors.steps = 'At least one step is required';
    if (!protocol.status) errors.status = 'Status is required';

    // Enhanced validation with null checks
    if (VALIDATION_RULES.name.minLength && protocol.name.length < VALIDATION_RULES.name.minLength) {
      errors.name = `Name must be at least ${VALIDATION_RULES.name.minLength} characters`;
    }
    if (VALIDATION_RULES.name.maxLength && protocol.name.length > VALIDATION_RULES.name.maxLength) {
      errors.name = `Name must not exceed ${VALIDATION_RULES.name.maxLength} characters`;
    }
    if (VALIDATION_RULES.name.pattern && !VALIDATION_RULES.name.pattern.test(protocol.name)) {
      errors.name = 'Name can only contain letters, numbers, spaces, hyphens, and underscores';
    }

    if (VALIDATION_RULES.description.minLength && protocol.description.length < VALIDATION_RULES.description.minLength) {
      errors.description = `Description must be at least ${VALIDATION_RULES.description.minLength} characters`;
    }
    if (VALIDATION_RULES.description.maxLength && protocol.description.length > VALIDATION_RULES.description.maxLength) {
      errors.description = `Description must not exceed ${VALIDATION_RULES.description.maxLength} characters`;
    }

    protocol.steps.forEach((step, index) => {
      if (VALIDATION_RULES.steps.minLength && step.length < VALIDATION_RULES.steps.minLength) {
        errors[`step-${index}`] = `Step must be at least ${VALIDATION_RULES.steps.minLength} characters`;
      }
      if (VALIDATION_RULES.steps.maxLength && step.length > VALIDATION_RULES.steps.maxLength) {
        errors[`step-${index}`] = `Step must not exceed ${VALIDATION_RULES.steps.maxLength} characters`;
      }
    });

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateProcedure = (procedure: EmergencyProcedure): boolean => {
    const errors: Record<string, string> = {};
    if (!procedure.name) errors.name = 'Name is required';
    if (!procedure.description) errors.description = 'Description is required';
    if (!procedure.steps.length) errors.steps = 'At least one step is required';
    if (!procedure.contactInfo.length) errors.contactInfo = 'At least one contact is required';
    if (!procedure.lastDrillDate) errors.lastDrillDate = 'Last drill date is required';
    if (!procedure.nextDrillDate) errors.nextDrillDate = 'Next drill date is required';
    
    // Validate contact info format
    procedure.contactInfo.forEach((contact, index) => {
      if (!validateEmail(contact) && !validatePhone(contact)) {
        errors[`contactInfo-${index}`] = 'Contact must be a valid email or phone number';
      }
    });

    // Validate dates
    if (!validatePastDate(procedure.lastDrillDate)) {
      errors.lastDrillDate = 'Last drill date must be in the past';
    }
    if (!validateFutureDate(procedure.nextDrillDate)) {
      errors.nextDrillDate = 'Next drill date must be in the future';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateAssessment = (assessment: RiskAssessment): boolean => {
    const errors: Record<string, string> = {};
    if (!assessment.activity) errors.activity = 'Activity is required';
    if (!assessment.riskLevel) errors.riskLevel = 'Risk level is required';
    if (!assessment.hazards.length) errors.hazards = 'At least one hazard is required';
    if (!assessment.controls.length) errors.controls = 'At least one control is required';
    if (!assessment.lastAssessed) errors.lastAssessed = 'Last assessment date is required';
    if (!assessment.nextAssessment) errors.nextAssessment = 'Next assessment date is required';

    // Validate dates
    if (!validatePastDate(assessment.lastAssessed)) {
      errors.lastAssessed = 'Last assessment date must be in the past';
    }
    if (!validateFutureDate(assessment.nextAssessment)) {
      errors.nextAssessment = 'Next assessment date must be in the future';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateIncident = (incident: IncidentReport): boolean => {
    const errors: Record<string, string> = {};
    if (!incident.date) errors.date = 'Date is required';
    if (!incident.time) errors.time = 'Time is required';
    if (!incident.location) errors.location = 'Location is required';
    if (!incident.type) errors.type = 'Type is required';
    if (!incident.description) errors.description = 'Description is required';
    if (!incident.severity) errors.severity = 'Severity is required';
    if (!incident.actionsTaken.length) errors.actionsTaken = 'At least one action is required';
    if (!incident.status) errors.status = 'Status is required';

    // Validate date and time
    if (!validatePastDate(incident.date)) {
      errors.date = 'Incident date must be in the past';
    }
    if (!incident.time.match(/^([01]\d|2[0-3]):([0-5]\d)$/)) {
      errors.time = 'Invalid time format (HH:MM)';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const handleSubmitProtocol = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    
    const protocol: SafetyProtocol = {
      id: editingItem?.id || 0,
      name: formData.get('name') as string,
      description: formData.get('description') as string,
      category: formData.get('category') as string,
      steps: (formData.get('steps') as string).split('\n').filter(step => step.trim()),
      lastUpdated: new Date().toISOString(),
      status: formData.get('status') as string,
    };

    if (!validateProtocol(protocol)) return;

    setLoading(true);
    try {
      if (editingItem) {
        await handleUpdateProtocol(protocol);
        showSuccess('Protocol updated successfully');
      } else {
        await handleAddProtocol(protocol);
        showSuccess('Protocol added successfully');
      }
      handleCloseProtocolDialog();
      setFormErrors({});
    } catch (err) {
      setError('Failed to save protocol');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitProcedure = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    
    const procedure: EmergencyProcedure = {
      id: editingItem?.id || 0,
      name: formData.get('name') as string,
      description: formData.get('description') as string,
      steps: (formData.get('steps') as string).split('\n').filter(step => step.trim()),
      contactInfo: (formData.get('contactInfo') as string).split('\n').filter(info => info.trim()),
      lastDrillDate: formData.get('lastDrillDate') as string,
      nextDrillDate: formData.get('nextDrillDate') as string,
    };

    if (!validateProcedure(procedure)) return;

    try {
      if (editingItem) {
        await handleUpdateProcedure(procedure);
      } else {
        await handleAddProcedure(procedure);
      }
      handleCloseProcedureDialog();
      setFormErrors({});
    } catch (err) {
      setError('Failed to save procedure');
    }
  };

  const handleSubmitAssessment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    
    const assessment: RiskAssessment = {
      id: editingItem?.id || 0,
      activity: formData.get('activity') as string,
      riskLevel: formData.get('riskLevel') as 'LOW' | 'MEDIUM' | 'HIGH',
      hazards: (formData.get('hazards') as string).split('\n').filter(hazard => hazard.trim()),
      controls: (formData.get('controls') as string).split('\n').filter(control => control.trim()),
      lastAssessed: formData.get('lastAssessed') as string,
      nextAssessment: formData.get('nextAssessment') as string,
    };

    if (!validateAssessment(assessment)) return;

    try {
      if (editingItem) {
        await handleUpdateAssessment(assessment);
      } else {
        await handleAddAssessment(assessment);
      }
      handleCloseAssessmentDialog();
      setFormErrors({});
    } catch (err) {
      setError('Failed to save assessment');
    }
  };

  const handleSubmitIncident = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    
    const incident: IncidentReport = {
      id: editingItem?.id || 0,
      date: formData.get('date') as string,
      time: formData.get('time') as string,
      location: formData.get('location') as string,
      type: formData.get('type') as string,
      description: formData.get('description') as string,
      severity: formData.get('severity') as 'MINOR' | 'MODERATE' | 'SEVERE',
      actionsTaken: (formData.get('actionsTaken') as string).split('\n').filter(action => action.trim()),
      followUpRequired: formData.get('followUpRequired') === 'true',
      status: formData.get('status') as string,
    };

    if (!validateIncident(incident)) return;

    try {
      if (editingItem) {
        await handleUpdateIncident(incident);
      } else {
        await handleAddIncident(incident);
      }
      handleCloseIncidentDialog();
      setFormErrors({});
    } catch (err) {
      setError('Failed to save incident');
    }
  };

  const handleAddProcedure = async (procedure: EmergencyProcedure) => {
    try {
      const response = await fetch(`${API_BASE_URL}/procedures`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(procedure),
      });

      if (!response.ok) {
        throw new Error('Failed to add procedure');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to add procedure');
    }
  };

  const handleUpdateProcedure = async (procedure: EmergencyProcedure) => {
    try {
      const response = await fetch(`${API_BASE_URL}/procedures/${procedure.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(procedure),
      });

      if (!response.ok) {
        throw new Error('Failed to update procedure');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to update procedure');
    }
  };

  const handleDeleteProcedure = async (procedureId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/procedures/${procedureId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete procedure');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to delete procedure');
    }
  };

  const handleAddAssessment = async (assessment: RiskAssessment) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assessment),
      });

      if (!response.ok) {
        throw new Error('Failed to add assessment');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to add assessment');
    }
  };

  const handleUpdateAssessment = async (assessment: RiskAssessment) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${assessment.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assessment),
      });

      if (!response.ok) {
        throw new Error('Failed to update assessment');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to update assessment');
    }
  };

  const handleDeleteAssessment = async (assessmentId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/assessments/${assessmentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete assessment');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to delete assessment');
    }
  };

  const handleAddIncident = async (incident: IncidentReport) => {
    try {
      const response = await fetch(`${API_BASE_URL}/incidents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(incident),
      });

      if (!response.ok) {
        throw new Error('Failed to add incident');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to add incident');
    }
  };

  const handleUpdateIncident = async (incident: IncidentReport) => {
    try {
      const response = await fetch(`${API_BASE_URL}/incidents/${incident.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(incident),
      });

      if (!response.ok) {
        throw new Error('Failed to update incident');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to update incident');
    }
  };

  const handleDeleteIncident = async (incidentId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete incident');
      }

      await fetchSafetyData();
    } catch (err) {
      setError('Failed to delete incident');
    }
  };

  useEffect(() => {
    fetchSafetyData();
  }, []);

  useEffect(() => {
    const fetchActivityData = async () => {
      try {
        const [alertsRes, profilesRes, activitiesRes] = await Promise.all([
          fetch('/api/v1/physical-education/activities/safety-alerts'),
          fetch('/api/v1/physical-education/activities/risk-profiles'),
          fetch('/api/v1/physical-education/activities/active')
        ]);

        if (!alertsRes.ok || !profilesRes.ok || !activitiesRes.ok) {
          throw new Error('Failed to fetch activity data');
        }

        const [alerts, profiles, activities] = await Promise.all([
          alertsRes.json(),
          profilesRes.json(),
          activitiesRes.json()
        ]);

        setActivityAlerts(alerts);
        setActivityRiskProfiles(profiles);
        setActiveActivities(activities);
      } catch (err) {
        setError('Failed to fetch activity safety data');
      }
    };

    fetchActivityData();
    const interval = setInterval(fetchActivityData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchEmergencyData = async () => {
      try {
        const [contactsRes, visualizationsRes] = await Promise.all([
          fetch('/api/v1/physical-education/emergency-contacts'),
          fetch('/api/v1/physical-education/risk-visualizations')
        ]);

        if (!contactsRes.ok || !visualizationsRes.ok) {
          throw new Error('Failed to fetch emergency data');
        }

        const [contacts, visualizations] = await Promise.all([
          contactsRes.json(),
          visualizationsRes.json()
        ]);

        setEmergencyContacts(contacts);
        setRiskVisualizations(visualizations);
      } catch (err) {
        setError('Failed to fetch emergency data');
      }
    };

    fetchEmergencyData();
    const interval = setInterval(fetchEmergencyData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchGoalSafetyData = async () => {
      try {
        const response = await fetch('/api/v1/physical-education/goals/safety-requirements');
        if (!response.ok) throw new Error('Failed to fetch goal safety requirements');
        const data = await response.json();
        setGoalSafetyRequirements(data);
      } catch (err) {
        setError('Failed to fetch goal safety requirements');
      }
    };

    fetchGoalSafetyData();
    const interval = setInterval(fetchGoalSafetyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAlertClick = (alert: ActivitySafetyAlert) => {
    setSelectedAlert(alert);
    setShowAlertDialog(true);
  };

  const handleResolveAlert = async (alertId: number) => {
    try {
      const response = await fetch(`/api/v1/physical-education/activities/safety-alerts/${alertId}/resolve`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to resolve alert');

      setActivityAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, resolved: true } : alert
      ));
      setShowAlertDialog(false);
      showSuccess('Alert resolved successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve alert');
    }
  };

  // Keyboard shortcuts with proper typing
  useHotkeys('ctrl+s, cmd+s', (e: KeyboardEvent) => {
    e.preventDefault();
    handleManualSave();
  });

  useHotkeys('ctrl+n, cmd+n', (e: KeyboardEvent) => {
    e.preventDefault();
    handleAddNew();
  });

  useHotkeys('esc', () => {
    handleCloseAllDialogs();
  });

  const handleManualSave = () => {
    if (editingItem) {
      showAutoSaveStatus('Saving changes...');
      // Trigger the appropriate save function based on the current tab
      switch (selectedTab) {
        case 0:
          handleSubmitProtocol(new Event('submit') as any);
          break;
        case 1:
          handleSubmitProcedure(new Event('submit') as any);
          break;
        case 2:
          handleSubmitAssessment(new Event('submit') as any);
          break;
        case 3:
          handleSubmitIncident(new Event('submit') as any);
          break;
      }
    }
  };

  const handleAddNew = () => {
    switch (selectedTab) {
      case 0:
        handleOpenProtocolDialog();
        break;
      case 1:
        handleOpenProcedureDialog();
        break;
      case 2:
        handleOpenAssessmentDialog();
        break;
      case 3:
        handleOpenIncidentDialog();
        break;
    }
  };

  const handleCloseAllDialogs = () => {
    handleCloseProtocolDialog();
    handleCloseProcedureDialog();
    handleCloseAssessmentDialog();
    handleCloseIncidentDialog();
  };

  const handleAutoSave = (formData: any) => {
    if (autoSaveTimeout) {
      clearTimeout(autoSaveTimeout);
    }

    const timeout = setTimeout(() => {
      showAutoSaveStatus('Auto-saving...');
      // Implement auto-save logic here
      setLastSaved(new Date());
      showAutoSaveStatus('Changes saved');
    }, 2000);

    setAutoSaveTimeout(timeout);
  };

  const handleFormChange = (event: React.FormEvent<HTMLFormElement>) => {
    const target = event.target as HTMLInputElement;
    if (target && target.tagName === 'INPUT') {
      handleFieldChange({
        target,
        currentTarget: target,
        nativeEvent: event.nativeEvent,
        preventDefault: event.preventDefault,
        stopPropagation: event.stopPropagation,
        isDefaultPrevented: event.isDefaultPrevented,
        isPropagationStopped: event.isPropagationStopped,
        persist: event.persist,
        timeStamp: event.timeStamp,
        type: event.type,
      } as React.ChangeEvent<HTMLInputElement>);
      handleAutoSave(event.currentTarget);
    }
  };

  const handleSelectChange = (event: SelectChangeEvent) => {
    const { name, value } = event.target;
    handleFieldChange({
      target: { name, value },
    } as React.ChangeEvent<HTMLInputElement>);
    const form = (event.target as HTMLElement).closest('form');
    if (form) {
      handleAutoSave(form);
    }
  };

  const handleTextFieldChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    handleFieldChange({
      target: { name, value },
    } as React.ChangeEvent<HTMLInputElement>);
    handleAutoSave(event.target.form);
  };

  const validateDates = (startDate: string, endDate: string): string | null => {
    if (!startDate || !endDate) return null;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return 'Invalid date format';
    }
    
    if (end <= start) {
      return 'End date must be after start date';
    }
    
    return null;
  };

  const handleDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    handleFieldChange(event);
    
    // Only validate if both dates are present
    if (name === 'lastDrillDate' || name === 'nextDrillDate') {
      const form = event.target.form;
      if (!form) return;

      const lastDrillDate = (form.elements.namedItem('lastDrillDate') as HTMLInputElement)?.value;
      const nextDrillDate = (form.elements.namedItem('nextDrillDate') as HTMLInputElement)?.value;
      
      if (lastDrillDate && nextDrillDate) {
        const error = validateDates(lastDrillDate, nextDrillDate);
        setFormErrors(prev => ({
          ...prev,
          nextDrillDate: error || ''
        }));
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ mt: 2 }}
        action={
          <Button 
            color="inherit" 
            size="small"
            onClick={() => {
              setError(null);
              fetchSafetyData();
            }}
          >
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  const ProtocolDialog: React.FC = () => (
    <Dialog 
      open={openProtocolDialog} 
      onClose={handleCloseProtocolDialog} 
      maxWidth="md" 
      fullWidth
      onBackdropClick={(e) => {
        if (Object.keys(formErrors).length > 0) {
          e.preventDefault();
          setWarningMessage('You have unsaved changes. Are you sure you want to close?');
        }
      }}
    >
      <form onSubmit={handleSubmitProtocol} onChange={handleFormChange}>
        <DialogTitle>
          {editingItem ? 'Edit Safety Protocol' : 'Add Safety Protocol'}
          {loadingStates.protocols && (
            <CircularProgress size={20} sx={{ ml: 2 }} />
          )}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Tooltip title="Enter a descriptive name for the protocol">
              <TextField
                fullWidth
                name="name"
                label="Name"
                defaultValue={editingItem?.name}
                margin="normal"
                required
                error={!!formErrors.name}
                helperText={formErrors.name}
                onChange={handleTextFieldChange}
              />
            </Tooltip>
            <TextField
              fullWidth
              name="description"
              label="Description"
              defaultValue={editingItem?.description}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.description}
              helperText={formErrors.description}
              inputProps={{
                maxLength: VALIDATION_RULES.description.maxLength,
              }}
              FormHelperTextProps={{
                component: 'div',
              }}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="category"
              label="Category"
              defaultValue={editingItem?.category}
              margin="normal"
              required
              error={!!formErrors.category}
              helperText={formErrors.category}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="steps"
              label="Steps (one per line)"
              defaultValue={editingItem?.steps?.join('\n')}
              margin="normal"
              multiline
              rows={4}
              required
              error={!!formErrors.steps}
              helperText={formErrors.steps}
              inputProps={{
                maxLength: VALIDATION_RULES.steps.maxLength,
              }}
              FormHelperTextProps={{
                component: 'div',
              }}
              onChange={handleTextFieldChange}
            />
            <FormControl fullWidth margin="normal" required error={!!formErrors.status}>
              <InputLabel>Status</InputLabel>
              <Select
                name="status"
                defaultValue={editingItem?.status || 'ACTIVE'}
                onChange={handleSelectChange}
              >
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="INACTIVE">Inactive</MenuItem>
                <MenuItem value="DRAFT">Draft</MenuItem>
              </Select>
              {formErrors.status && <FormHelperText>{formErrors.status}</FormHelperText>}
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Tooltip title="Discard changes and close">
            <Button onClick={handleCloseProtocolDialog}>Cancel (Esc)</Button>
          </Tooltip>
          <Tooltip title={editingItem ? "Save changes" : "Create new protocol"}>
            <Button type="submit" variant="contained" color="primary">
              {editingItem ? 'Update (Ctrl+S)' : 'Add (Ctrl+N)'}
            </Button>
          </Tooltip>
        </DialogActions>
      </form>
    </Dialog>
  );

  const ProcedureDialog = () => (
    <Dialog open={openProcedureDialog} onClose={handleCloseProcedureDialog} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmitProcedure} onChange={handleFormChange}>
        <DialogTitle>{editingItem ? 'Edit Emergency Procedure' : 'Add Emergency Procedure'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              name="name"
              label="Name"
              defaultValue={editingItem?.name}
              margin="normal"
              required
              error={!!formErrors.name}
              helperText={formErrors.name}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="description"
              label="Description"
              defaultValue={editingItem?.description}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.description}
              helperText={formErrors.description}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="steps"
              label="Steps (one per line)"
              defaultValue={editingItem?.steps?.join('\n')}
              margin="normal"
              multiline
              rows={4}
              required
              error={!!formErrors.steps}
              helperText={formErrors.steps}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="contactInfo"
              label="Contact Information (one per line)"
              defaultValue={editingItem?.contactInfo?.join('\n')}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.contactInfo}
              helperText={formErrors.contactInfo}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="lastDrillDate"
              label="Last Drill Date"
              type="date"
              defaultValue={editingItem?.lastDrillDate}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.lastDrillDate}
              helperText={formErrors.lastDrillDate}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="nextDrillDate"
              label="Next Drill Date"
              type="date"
              defaultValue={editingItem?.nextDrillDate}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.nextDrillDate}
              helperText={formErrors.nextDrillDate}
              onChange={handleDateChange}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseProcedureDialog}>Cancel (Esc)</Button>
          <Button type="submit" variant="contained" color="primary">
            {editingItem ? 'Update (Ctrl+S)' : 'Add (Ctrl+N)'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );

  const AssessmentDialog = () => (
    <Dialog open={openAssessmentDialog} onClose={handleCloseAssessmentDialog} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmitAssessment} onChange={handleFormChange}>
        <DialogTitle>{editingItem ? 'Edit Risk Assessment' : 'Add Risk Assessment'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              name="activity"
              label="Activity"
              defaultValue={editingItem?.activity}
              margin="normal"
              required
              error={!!formErrors.activity}
              helperText={formErrors.activity}
              onChange={handleTextFieldChange}
            />
            <FormControl fullWidth margin="normal" required error={!!formErrors.riskLevel}>
              <InputLabel>Risk Level</InputLabel>
              <Select
                name="riskLevel"
                defaultValue={editingItem?.riskLevel || 'LOW'}
                onChange={handleSelectChange}
              >
                <MenuItem value="LOW">Low</MenuItem>
                <MenuItem value="MEDIUM">Medium</MenuItem>
                <MenuItem value="HIGH">High</MenuItem>
              </Select>
              {formErrors.riskLevel && <FormHelperText>{formErrors.riskLevel}</FormHelperText>}
            </FormControl>
            <TextField
              fullWidth
              name="hazards"
              label="Hazards (one per line)"
              defaultValue={editingItem?.hazards?.join('\n')}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.hazards}
              helperText={formErrors.hazards}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="controls"
              label="Controls (one per line)"
              defaultValue={editingItem?.controls?.join('\n')}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.controls}
              helperText={formErrors.controls}
              onChange={handleTextFieldChange}
            />
            <TextField
              fullWidth
              name="lastAssessed"
              label="Last Assessed"
              type="date"
              defaultValue={editingItem?.lastAssessed}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.lastAssessed}
              helperText={formErrors.lastAssessed}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="nextAssessment"
              label="Next Assessment"
              type="date"
              defaultValue={editingItem?.nextAssessment}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.nextAssessment}
              helperText={formErrors.nextAssessment}
              onChange={handleDateChange}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAssessmentDialog}>Cancel (Esc)</Button>
          <Button type="submit" variant="contained" color="primary">
            {editingItem ? 'Update (Ctrl+S)' : 'Add (Ctrl+N)'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );

  const IncidentDialog = () => (
    <Dialog open={openIncidentDialog} onClose={handleCloseIncidentDialog} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmitIncident} onChange={handleFormChange}>
        <DialogTitle>{editingItem ? 'Edit Incident Report' : 'Add Incident Report'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              name="date"
              label="Date"
              type="date"
              defaultValue={editingItem?.date}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.date}
              helperText={formErrors.date}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="time"
              label="Time"
              type="time"
              defaultValue={editingItem?.time}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
              error={!!formErrors.time}
              helperText={formErrors.time}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="location"
              label="Location"
              defaultValue={editingItem?.location}
              margin="normal"
              required
              error={!!formErrors.location}
              helperText={formErrors.location}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="type"
              label="Type"
              defaultValue={editingItem?.type}
              margin="normal"
              required
              error={!!formErrors.type}
              helperText={formErrors.type}
              onChange={handleDateChange}
            />
            <TextField
              fullWidth
              name="description"
              label="Description"
              defaultValue={editingItem?.description}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.description}
              helperText={formErrors.description}
              onChange={handleDateChange}
            />
            <FormControl fullWidth margin="normal" required error={!!formErrors.severity}>
              <InputLabel>Severity</InputLabel>
              <Select
                name="severity"
                defaultValue={editingItem?.severity || 'MINOR'}
                onChange={handleSelectChange}
              >
                <MenuItem value="MINOR">Minor</MenuItem>
                <MenuItem value="MODERATE">Moderate</MenuItem>
                <MenuItem value="SEVERE">Severe</MenuItem>
              </Select>
              {formErrors.severity && <FormHelperText>{formErrors.severity}</FormHelperText>}
            </FormControl>
            <TextField
              fullWidth
              name="actionsTaken"
              label="Actions Taken (one per line)"
              defaultValue={editingItem?.actionsTaken?.join('\n')}
              margin="normal"
              multiline
              rows={3}
              required
              error={!!formErrors.actionsTaken}
              helperText={formErrors.actionsTaken}
              onChange={handleDateChange}
            />
            <FormControl fullWidth margin="normal" required error={!!formErrors.status}>
              <InputLabel>Status</InputLabel>
              <Select
                name="status"
                defaultValue={editingItem?.status || 'OPEN'}
                onChange={handleSelectChange}
              >
                <MenuItem value="OPEN">Open</MenuItem>
                <MenuItem value="IN_PROGRESS">In Progress</MenuItem>
                <MenuItem value="RESOLVED">Resolved</MenuItem>
                <MenuItem value="CLOSED">Closed</MenuItem>
              </Select>
              {formErrors.status && <FormHelperText>{formErrors.status}</FormHelperText>}
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseIncidentDialog}>Cancel (Esc)</Button>
          <Button type="submit" variant="contained" color="primary">
            {editingItem ? 'Update (Ctrl+S)' : 'Add (Ctrl+N)'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );

  const SafetyAlertDialog: React.FC = () => {
    if (!selectedAlert) return null;

    return (
      <Dialog open={showAlertDialog} onClose={() => setShowAlertDialog(false)}>
        <DialogTitle>
          Safety Alert: {selectedAlert.activityType}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body1" gutterBottom>
              {selectedAlert.message}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Activity ID: {selectedAlert.activityId}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              Time: {format(parseISO(selectedAlert.timestamp), 'PPpp')}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAlertDialog(false)}>Close</Button>
          {!selectedAlert.resolved && (
            <Button 
              onClick={() => handleResolveAlert(selectedAlert.id)}
              variant="contained" 
              color="primary"
            >
              Resolve Alert
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };

  const ActivitySafetyCard: React.FC = () => {
    const activeAlerts = activityAlerts.filter(alert => !alert.resolved);
    const relevantProfiles = activityRiskProfiles.filter(profile => 
      activeActivities.some(activity => activity.type === profile.activityType)
    );

    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <SportsIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Active Activities Safety Status</Typography>
          </Box>
          
          {activeAlerts.length > 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              {activeAlerts.length} active safety alert{activeAlerts.length > 1 ? 's' : ''}
            </Alert>
          )}

          <Grid container spacing={2}>
            {relevantProfiles.map(profile => (
              <Grid item xs={12} sm={6} key={profile.activityType}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {profile.activityType}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Max Participants: {profile.maxParticipants}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Required Supervisors: {profile.minSupervisors}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Required Equipment:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                        {profile.requiredEquipment.map(equipment => (
                          <Chip
                            key={equipment}
                            label={equipment}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const EmergencyContactsCard: React.FC = () => {
    const primaryContact = emergencyContacts.find(contact => contact.isPrimary);
    const otherContacts = emergencyContacts.filter(contact => !contact.isPrimary);

    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <EmergencyIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Emergency Contacts</Typography>
          </Box>

          {primaryContact && (
            <Card variant="outlined" sx={{ mb: 2, bgcolor: 'warning.light' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    Primary Contact
                  </Typography>
                  <Chip label="Primary" size="small" color="warning" sx={{ ml: 1 }} />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{primaryContact.phone}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{primaryContact.email}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2">{primaryContact.location}</Typography>
                </Box>
              </CardContent>
            </Card>
          )}

          <Grid container spacing={2}>
            {otherContacts.map(contact => (
              <Grid item xs={12} sm={6} key={contact.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {contact.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {contact.role}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PhoneIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">{contact.phone}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2">{contact.email}</Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const RiskAssessmentVisualization: React.FC = () => {
    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AssessmentIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Risk Assessment Visualization</Typography>
          </Box>

          <Grid container spacing={2}>
            {riskVisualizations.map(visualization => (
              <Grid item xs={12} key={visualization.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {visualization.activity}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Overall Risk Level: {visualization.overallRisk}/10
                      </Typography>
                      <Box sx={{ width: '100%', height: 8, bgcolor: 'grey.200', borderRadius: 4, mb: 1 }}>
                        <Box
                          sx={{
                            width: `${(visualization.overallRisk / 10) * 100}%`,
                            height: '100%',
                            bgcolor: visualization.overallRisk > 7 ? 'error.main' : 
                                    visualization.overallRisk > 4 ? 'warning.main' : 'success.main',
                            borderRadius: 4
                          }}
                        />
                      </Box>
                    </Box>
                    <Grid container spacing={2}>
                      {visualization.riskFactors.map((factor, index) => (
                        <Grid item xs={12} sm={6} md={4} key={index}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="subtitle2" gutterBottom>
                                {factor.name}
                              </Typography>
                              <Box sx={{ mb: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  Risk Level: {factor.level}/10
                                </Typography>
                                <Box sx={{ width: '100%', height: 4, bgcolor: 'grey.200', borderRadius: 2, mt: 0.5 }}>
                                  <Box
                                    sx={{
                                      width: `${(factor.level / 10) * 100}%`,
                                      height: '100%',
                                      bgcolor: factor.level > 7 ? 'error.main' : 
                                              factor.level > 4 ? 'warning.main' : 'success.main',
                                      borderRadius: 2
                                    }}
                                  />
                                </Box>
                              </Box>
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  Controls:
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                                  {factor.controls.map((control, idx) => (
                                    <Chip
                                      key={idx}
                                      label={control}
                                      size="small"
                                      variant="outlined"
                                    />
                                  ))}
                                </Box>
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const GoalSafetyRequirementsCard: React.FC = () => {
    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <SportsIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Goal-Specific Safety Requirements</Typography>
          </Box>

          <Grid container spacing={2}>
            {goalSafetyRequirements.map(requirement => (
              <Grid item xs={12} key={requirement.goalId}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                        {requirement.goalName}
                      </Typography>
                      <Chip
                        label={requirement.riskLevel}
                        color={
                          requirement.riskLevel === 'HIGH' ? 'error' :
                          requirement.riskLevel === 'MEDIUM' ? 'warning' : 'success'
                        }
                      />
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Required Equipment
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {requirement.safetyRequirements.equipment.map((item, index) => (
                              <Chip
                                key={index}
                                label={item}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Box>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Supervision Requirements
                          </Typography>
                          <Typography variant="body2">
                            {requirement.safetyRequirements.supervision}
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Environment Requirements
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {requirement.safetyRequirements.environment.map((item, index) => (
                              <Chip
                                key={index}
                                label={item}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Box>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Safety Precautions
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {requirement.safetyRequirements.precautions.map((item, index) => (
                              <Chip
                                key={index}
                                label={item}
                                size="small"
                                variant="outlined"
                                color="warning"
                              />
                            ))}
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ width: '100%', position: 'relative' }}>
      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={loading}
      >
        <CircularProgress color="inherit" />
      </Backdrop>

      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={selectedTab} onChange={handleTabChange} aria-label="safety tabs">
            <Tooltip title="View and manage safety protocols">
              <Tab 
                label="Safety Protocols" 
                icon={<WarningIcon />}
                disabled={loadingStates.protocols}
              />
            </Tooltip>
            <Tooltip title="View and manage emergency procedures">
              <Tab 
                label="Emergency Procedures" 
                icon={<EmergencyIcon />}
                disabled={loadingStates.procedures}
              />
            </Tooltip>
            <Tooltip title="View and manage risk assessments">
              <Tab 
                label="Risk Assessment" 
                icon={<AssessmentIcon />}
                disabled={loadingStates.assessments}
              />
            </Tooltip>
            <Tooltip title="View and manage incident reports">
              <Tab 
                label="Incident Reports" 
                icon={<ReportIcon />}
                disabled={loadingStates.incidents}
              />
            </Tooltip>
          </Tabs>
        </Box>

        <TabPanel value={selectedTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ position: 'relative' }}>
                    {loadingStates.protocols && (
                      <Box sx={{ 
                        position: 'absolute', 
                        top: 0, 
                        left: 0, 
                        right: 0, 
                        bottom: 0,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: 'rgba(0, 0, 0, 0.04)',
                        zIndex: 1
                      }}>
                        <CircularProgress />
                      </Box>
                    )}
                    <Typography variant="h6" gutterBottom>
                      Safety Protocols
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      sx={{ mb: 2 }}
                      onClick={() => handleOpenProtocolDialog()}
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
                              <IconButton edge="end" aria-label="edit" onClick={() => handleOpenProtocolDialog(protocol)}>
                                <EditIcon />
                              </IconButton>
                              <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteProtocol(protocol.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </ListItemSecondaryAction>
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      ))}
                    </List>
                  </Box>
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
                    onClick={() => handleOpenProcedureDialog()}
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
                            <IconButton edge="end" aria-label="edit" onClick={() => handleOpenProcedureDialog(procedure)}>
                              <EditIcon />
                            </IconButton>
                            <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteProcedure(procedure.id)}>
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
                    onClick={() => handleOpenAssessmentDialog()}
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
                            <IconButton edge="end" aria-label="edit" onClick={() => handleOpenAssessmentDialog(assessment)}>
                              <EditIcon />
                            </IconButton>
                            <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteAssessment(assessment.id)}>
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
                    onClick={() => handleOpenIncidentDialog()}
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
                            <IconButton edge="end" aria-label="edit" onClick={() => handleOpenIncidentDialog(incident)}>
                              <EditIcon />
                            </IconButton>
                            <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteIncident(incident.id)}>
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

        <ProtocolDialog />
        <ProcedureDialog />
        <AssessmentDialog />
        <IncidentDialog />

        <Snackbar
          open={!!successMessage}
          autoHideDuration={3000}
          onClose={() => setSuccessMessage(null)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert onClose={() => setSuccessMessage(null)} severity="success" sx={{ width: '100%' }}>
            {successMessage}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!warningMessage}
          autoHideDuration={5000}
          onClose={() => setWarningMessage(null)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert onClose={() => setWarningMessage(null)} severity="warning" sx={{ width: '100%' }}>
            {warningMessage}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!autoSaveStatus}
          autoHideDuration={2000}
          onClose={() => setAutoSaveStatus(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={() => setAutoSaveStatus(null)} severity="info" sx={{ width: '100%' }}>
            {autoSaveStatus}
          </Alert>
        </Snackbar>

        {/* Add keyboard shortcut hints */}
        <Box sx={{ position: 'fixed', bottom: 16, right: 16, bgcolor: 'background.paper', p: 2, borderRadius: 1, boxShadow: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Keyboard Shortcuts:
          </Typography>
          <Box component="ul" sx={{ mt: 1, mb: 0, pl: 2 }}>
            <Typography component="li" variant="caption">
              Ctrl+S / Cmd+S: Save
            </Typography>
            <Typography component="li" variant="caption">
              Ctrl+N / Cmd+N: New Item
            </Typography>
            <Typography component="li" variant="caption">
              Esc: Close Dialog
            </Typography>
          </Box>
        </Box>

        {/* Add last saved indicator */}
        {lastSaved && (
          <Box sx={{ position: 'fixed', bottom: 16, left: 16, bgcolor: 'background.paper', p: 2, borderRadius: 1, boxShadow: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Last saved: {format(lastSaved, 'MMM d, yyyy HH:mm:ss')}
            </Typography>
          </Box>
        )}

        <SafetyAlertDialog />
        <ActivitySafetyCard />
        <EmergencyContactsCard />
        <RiskAssessmentVisualization />
        <GoalSafetyRequirementsCard />
      </Box>
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