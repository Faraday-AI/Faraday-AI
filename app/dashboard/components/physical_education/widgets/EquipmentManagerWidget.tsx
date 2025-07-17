import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
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
  Chip,
  Alert,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Badge,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Build as MaintenanceIcon,
  SwapHoriz as CheckoutIcon,
  History as HistoryIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

interface Equipment {
  id: string;
  name: string;
  category: EquipmentCategory;
  quantity: number;
  available: number;
  condition: EquipmentCondition;
  lastMaintenance: string;
  nextMaintenance: string;
  location: string;
  notes?: string;
}

interface CheckoutRecord {
  id: string;
  equipmentId: string;
  quantity: number;
  borrower: string;
  checkoutDate: string;
  expectedReturnDate: string;
  returnDate?: string;
  status: 'active' | 'returned' | 'overdue';
  notes?: string;
}

interface MaintenanceRecord {
  id: string;
  equipmentId: string;
  date: string;
  type: MaintenanceType;
  description: string;
  cost?: number;
  technician?: string;
  nextMaintenanceDate: string;
}

type EquipmentCategory = 'sports' | 'fitness' | 'safety' | 'measurement';
type EquipmentCondition = 'excellent' | 'good' | 'fair' | 'poor' | 'maintenance-required';
type MaintenanceType = 'routine' | 'repair' | 'replacement' | 'inspection';

const DEFAULT_EQUIPMENT: Equipment[] = [
  {
    id: '1',
    name: 'Basketball',
    category: 'sports',
    quantity: 20,
    available: 15,
    condition: 'good',
    lastMaintenance: '2024-01-15',
    nextMaintenance: '2024-04-15',
    location: 'Storage Room A',
  },
  {
    id: '2',
    name: 'Yoga Mat',
    category: 'fitness',
    quantity: 30,
    available: 25,
    condition: 'excellent',
    lastMaintenance: '2024-02-01',
    nextMaintenance: '2024-05-01',
    location: 'Storage Room B',
  },
];

const EQUIPMENT_CATEGORIES: EquipmentCategory[] = ['sports', 'fitness', 'safety', 'measurement'];
const EQUIPMENT_CONDITIONS: EquipmentCondition[] = ['excellent', 'good', 'fair', 'poor', 'maintenance-required'];
const MAINTENANCE_TYPES: MaintenanceType[] = ['routine', 'repair', 'replacement', 'inspection'];

export const EquipmentManagerWidget: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>(DEFAULT_EQUIPMENT);
  const [checkouts, setCheckouts] = useState<CheckoutRecord[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [showEquipmentDialog, setShowEquipmentDialog] = useState(false);
  const [showCheckoutDialog, setShowCheckoutDialog] = useState(false);
  const [showMaintenanceDialog, setShowMaintenanceDialog] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [newEquipment, setNewEquipment] = useState<Partial<Equipment>>({
    category: 'sports',
    condition: 'good',
  });
  const [newCheckout, setNewCheckout] = useState<Partial<CheckoutRecord>>({
    checkoutDate: new Date().toISOString().split('T')[0],
    status: 'active',
  });
  const [newMaintenance, setNewMaintenance] = useState<Partial<MaintenanceRecord>>({
    date: new Date().toISOString().split('T')[0],
    type: 'routine',
  });
  const [error, setError] = useState<string | null>(null);
  const [showOverdue, setShowOverdue] = useState(false);

  const addEquipment = (equipment: Equipment) => {
    setEquipment(prev => [...prev, equipment]);
    setShowEquipmentDialog(false);
    setNewEquipment({
      category: 'sports',
      condition: 'good',
    });
  };

  const addCheckout = (checkout: CheckoutRecord) => {
    setCheckouts(prev => [...prev, checkout]);
    setShowCheckoutDialog(false);
    setNewCheckout({
      checkoutDate: new Date().toISOString().split('T')[0],
      status: 'active',
    });

    // Update equipment availability
    if (selectedEquipment) {
      setEquipment(prev =>
        prev.map(e =>
          e.id === selectedEquipment.id
            ? { ...e, available: e.available - checkout.quantity }
            : e
        )
      );
    }
  };

  const addMaintenance = (maintenance: MaintenanceRecord) => {
    setMaintenance(prev => [...prev, maintenance]);
    setShowMaintenanceDialog(false);
    setNewMaintenance({
      date: new Date().toISOString().split('T')[0],
      type: 'routine',
    });

    // Update equipment maintenance dates
    if (selectedEquipment) {
      setEquipment(prev =>
        prev.map(e =>
          e.id === selectedEquipment.id
            ? {
                ...e,
                lastMaintenance: maintenance.date,
                nextMaintenance: maintenance.nextMaintenanceDate,
                condition: 'good',
              }
            : e
        )
      );
    }
  };

  const getEquipmentStats = () => {
    const stats = {
      total: equipment.reduce((sum, e) => sum + e.quantity, 0),
      available: equipment.reduce((sum, e) => sum + e.available, 0),
      maintenance: equipment.filter(e => e.condition === 'maintenance-required').length,
      overdue: checkouts.filter(c => c.status === 'overdue').length,
    };

    return [
      { name: 'Available', value: stats.available },
      { name: 'Checked Out', value: stats.total - stats.available },
      { name: 'Maintenance', value: stats.maintenance },
    ];
  };

  const exportData = () => {
    const data = {
      equipment,
      checkouts,
      maintenance,
      date: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `equipment_data_${new Date().toISOString().split('T')[0]}.json`;
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
            <Typography variant="h6">Equipment Manager</Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowEquipmentDialog(true)}
              >
                Add Equipment
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

          {/* Statistics */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Equipment</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Available</TableCell>
                      <TableCell>Condition</TableCell>
                      <TableCell>Next Maintenance</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {equipment.map(item => (
                      <TableRow key={item.id}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={item.category}
                            color={
                              item.category === 'sports'
                                ? 'primary'
                                : item.category === 'fitness'
                                ? 'secondary'
                                : item.category === 'safety'
                                ? 'error'
                                : 'info'
                            }
                          />
                        </TableCell>
                        <TableCell>
                          {item.available} / {item.quantity}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={item.condition}
                            color={
                              item.condition === 'excellent'
                                ? 'success'
                                : item.condition === 'good'
                                ? 'primary'
                                : item.condition === 'fair'
                                ? 'warning'
                                : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell>{item.nextMaintenance}</TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Check Out">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedEquipment(item);
                                  setShowCheckoutDialog(true);
                                }}
                                disabled={item.available === 0}
                              >
                                <CheckoutIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Maintenance">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedEquipment(item);
                                  setShowMaintenanceDialog(true);
                                }}
                              >
                                <MaintenanceIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="History">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedEquipment(item);
                                  setShowHistoryDialog(true);
                                }}
                              >
                                <HistoryIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  Equipment Status
                </Typography>
                <Box height={200}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getEquipmentStats()}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                      >
                        <Cell fill="#4CAF50" />
                        <Cell fill="#2196F3" />
                        <Cell fill="#FFC107" />
                      </Pie>
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </CardContent>

      {/* Add Equipment Dialog */}
      <Dialog open={showEquipmentDialog} onClose={() => setShowEquipmentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Equipment</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Equipment Name"
              fullWidth
              onChange={(e) => setNewEquipment({ ...newEquipment, name: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={newEquipment.category}
                onChange={(e) => setNewEquipment({ ...newEquipment, category: e.target.value as EquipmentCategory })}
              >
                {EQUIPMENT_CATEGORIES.map(category => (
                  <MenuItem key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Quantity"
              type="number"
              fullWidth
              onChange={(e) => {
                const quantity = parseInt(e.target.value);
                setNewEquipment({
                  ...newEquipment,
                  quantity,
                  available: quantity,
                });
              }}
            />
            <TextField
              label="Location"
              fullWidth
              onChange={(e) => setNewEquipment({ ...newEquipment, location: e.target.value })}
            />
            <FormControl fullWidth>
              <InputLabel>Condition</InputLabel>
              <Select
                label="Condition"
                value={newEquipment.condition}
                onChange={(e) => setNewEquipment({ ...newEquipment, condition: e.target.value as EquipmentCondition })}
              >
                {EQUIPMENT_CONDITIONS.map(condition => (
                  <MenuItem key={condition} value={condition}>
                    {condition.charAt(0).toUpperCase() + condition.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewEquipment({ ...newEquipment, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEquipmentDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                newEquipment.name &&
                newEquipment.category &&
                newEquipment.quantity &&
                newEquipment.location &&
                newEquipment.condition
              ) {
                const today = new Date().toISOString().split('T')[0];
                addEquipment({
                  ...newEquipment as Equipment,
                  id: Date.now().toString(),
                  lastMaintenance: today,
                  nextMaintenance: today,
                  available: newEquipment.quantity || 0,
                });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Checkout Dialog */}
      <Dialog open={showCheckoutDialog} onClose={() => setShowCheckoutDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Check Out Equipment: {selectedEquipment?.name}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <TextField
              label="Borrower Name"
              fullWidth
              onChange={(e) => setNewCheckout({ ...newCheckout, borrower: e.target.value })}
            />
            <TextField
              label="Quantity"
              type="number"
              fullWidth
              InputProps={{
                inputProps: {
                  min: 1,
                  max: selectedEquipment?.available || 1,
                },
              }}
              onChange={(e) =>
                setNewCheckout({ ...newCheckout, quantity: parseInt(e.target.value) })
              }
            />
            <TextField
              label="Expected Return Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              onChange={(e) =>
                setNewCheckout({ ...newCheckout, expectedReturnDate: e.target.value })
              }
            />
            <TextField
              label="Notes"
              multiline
              rows={2}
              fullWidth
              onChange={(e) => setNewCheckout({ ...newCheckout, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCheckoutDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                selectedEquipment &&
                newCheckout.borrower &&
                newCheckout.quantity &&
                newCheckout.expectedReturnDate
              ) {
                if (newCheckout.quantity <= (selectedEquipment.available || 0)) {
                  addCheckout({
                    ...newCheckout as CheckoutRecord,
                    id: Date.now().toString(),
                    equipmentId: selectedEquipment.id,
                  });
                } else {
                  setError('Requested quantity exceeds available quantity');
                }
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Check Out
          </Button>
        </DialogActions>
      </Dialog>

      {/* Maintenance Dialog */}
      <Dialog open={showMaintenanceDialog} onClose={() => setShowMaintenanceDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Maintenance: {selectedEquipment?.name}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Maintenance Type</InputLabel>
              <Select
                label="Maintenance Type"
                value={newMaintenance.type}
                onChange={(e) =>
                  setNewMaintenance({ ...newMaintenance, type: e.target.value as MaintenanceType })
                }
              >
                {MAINTENANCE_TYPES.map(type => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              onChange={(e) =>
                setNewMaintenance({ ...newMaintenance, description: e.target.value })
              }
            />
            <TextField
              label="Cost"
              type="number"
              fullWidth
              onChange={(e) =>
                setNewMaintenance({ ...newMaintenance, cost: parseFloat(e.target.value) })
              }
            />
            <TextField
              label="Technician"
              fullWidth
              onChange={(e) =>
                setNewMaintenance({ ...newMaintenance, technician: e.target.value })
              }
            />
            <TextField
              label="Next Maintenance Date"
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
              onChange={(e) =>
                setNewMaintenance({ ...newMaintenance, nextMaintenanceDate: e.target.value })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMaintenanceDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              if (
                selectedEquipment &&
                newMaintenance.type &&
                newMaintenance.description &&
                newMaintenance.nextMaintenanceDate
              ) {
                addMaintenance({
                  ...newMaintenance as MaintenanceRecord,
                  id: Date.now().toString(),
                  equipmentId: selectedEquipment.id,
                });
              } else {
                setError('Please fill in all required fields');
              }
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={showHistoryDialog} onClose={() => setShowHistoryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Equipment History: {selectedEquipment?.name}</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <Typography variant="subtitle1">Checkout History</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Borrower</TableCell>
                    <TableCell>Quantity</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Return Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {checkouts
                    .filter(c => c.equipmentId === selectedEquipment?.id)
                    .map(checkout => (
                      <TableRow key={checkout.id}>
                        <TableCell>{checkout.checkoutDate}</TableCell>
                        <TableCell>{checkout.borrower}</TableCell>
                        <TableCell>{checkout.quantity}</TableCell>
                        <TableCell>
                          <Chip
                            label={checkout.status}
                            color={
                              checkout.status === 'active'
                                ? 'primary'
                                : checkout.status === 'returned'
                                ? 'success'
                                : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell>{checkout.returnDate || '-'}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Typography variant="subtitle1" sx={{ mt: 2 }}>Maintenance History</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Cost</TableCell>
                    <TableCell>Technician</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {maintenance
                    .filter(m => m.equipmentId === selectedEquipment?.id)
                    .map(record => (
                      <TableRow key={record.id}>
                        <TableCell>{record.date}</TableCell>
                        <TableCell>{record.type}</TableCell>
                        <TableCell>{record.description}</TableCell>
                        <TableCell>${record.cost?.toFixed(2) || '-'}</TableCell>
                        <TableCell>{record.technician || '-'}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistoryDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}; 