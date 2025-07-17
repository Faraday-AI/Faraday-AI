import React, { createContext, useContext, useState, useCallback } from 'react';
import { DashboardContextType } from '../types';

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
};

interface DashboardProviderProps {
  children: React.ReactNode;
  userId: string;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children, userId }) => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  const handleError = useCallback((errorMessage: string | null) => {
    setError(errorMessage);
    if (errorMessage) {
      // Auto-clear error after 5 seconds
      setTimeout(() => setError(null), 5000);
    }
  }, []);

  const value: DashboardContextType = {
    userId,
    refreshKey,
    setRefreshKey: handleRefresh,
    loading,
    setLoading,
    error,
    setError: handleError,
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
}; 