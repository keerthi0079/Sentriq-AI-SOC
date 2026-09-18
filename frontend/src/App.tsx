import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { Incidents } from './pages/Incidents';
import { SecurityLogs } from './pages/SecurityLogs';
import { ThreatAnalysis } from './pages/ThreatAnalysis';
import { IncidentDetails } from './pages/IncidentDetails';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="incidents" element={<Incidents />} />
          <Route path="incidents/:id" element={<IncidentDetails />} />
          <Route path="logs" element={<SecurityLogs />} />
          <Route path="analysis" element={<ThreatAnalysis />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

