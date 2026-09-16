import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import ToastContainer from './components/ui/Toast';
import Dashboard from './pages/Dashboard';
import LiveMonitoring from './pages/LiveMonitoring';
import Alerts from './pages/Alerts';
import NotificationHistory from './pages/NotificationHistory';
import Simulator from './pages/Simulator';
import Users from './pages/Users';
import SystemLogs from './pages/SystemLogs';

const routes = [
  { path: '/',              Component: Dashboard,           title: 'Dashboard',             subtitle: 'AI Fall Detection Overview' },
  { path: '/monitoring',    Component: LiveMonitoring,      title: 'Live Sensor Monitoring', subtitle: 'Real-time wearable sensor data' },
  { path: '/alerts',        Component: Alerts,              title: 'Emergency Alerts',       subtitle: 'Active fall events requiring attention' },
  { path: '/notifications', Component: NotificationHistory, title: 'Notification History',   subtitle: 'All past emergency notifications' },
  { path: '/simulator',     Component: Simulator,           title: 'Sensor Simulator',       subtitle: 'Demo Mode — test the AI pipeline' },
  { path: '/users',         Component: Users,               title: 'Users & Devices',        subtitle: 'Monitored users and wearable devices' },
  { path: '/logs',          Component: SystemLogs,          title: 'System Logs',            subtitle: 'Event log for API calls and pipeline steps' },
];

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Routes>
          {routes.map(({ path, Component, title, subtitle }) => (
            <Route
              key={path}
              path={path}
              element={
                <>
                  <Header
                    onMenuClick={() => setSidebarOpen(true)}
                    title={title}
                    subtitle={subtitle}
                  />
                  <main className="flex-1 overflow-y-auto p-4 lg:p-6">
                    <Component />
                  </main>
                </>
              }
            />
          ))}
        </Routes>
      </div>

      <ToastContainer />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <AppLayout />
      </AppProvider>
    </BrowserRouter>
  );
}
