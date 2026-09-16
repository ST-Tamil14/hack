import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Patients } from './pages/Patients';
import { PatientProfile } from './pages/PatientProfile';
import { NewAssessment } from './pages/NewAssessment';
import { SessionDetails } from './pages/SessionDetails';
import { Reports } from './pages/Reports';
import { Alerts } from './pages/Alerts';
import { SettingsPage } from './pages/Settings';
import { AuthUser } from './types';

export function App() {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const saved = localStorage.getItem('painsense_user');
    return saved ? JSON.parse(saved) : { id: 'u-1', email: 'dr.jenkins@hospital.org', full_name: 'Dr. Sarah Jenkins', role: 'clinician' };
  });

  const handleLoginSuccess = (loggedInUser: AuthUser) => {
    setUser(loggedInUser);
    localStorage.setItem('painsense_user', JSON.stringify(loggedInUser));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('painsense_user');
    localStorage.removeItem('painsense_auth_token');
  };

  if (!user) {
    return <BrowserRouter><Login onLoginSuccess={handleLoginSuccess} /></BrowserRouter>;
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans antialiased text-slate-900 selection:bg-cyan-100 selection:text-cyan-900">
        <Navbar user={user} onLogout={handleLogout} />
        
        <div className="flex-1 flex max-w-7xl w-full mx-auto">
          <Sidebar />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/patient/:id" element={<PatientProfile />} />
              <Route path="/assessment/new" element={<NewAssessment />} />
              <Route path="/session/:id" element={<SessionDetails />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
