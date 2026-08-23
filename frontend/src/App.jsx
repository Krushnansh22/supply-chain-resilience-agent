/**
 * src/App.jsx
 * Top-level router with ProtectedRoute enforcement, AuthProvider, and Agent Control Ribbon.
 */

import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import Sidebar from "./components/layout/Sidebar.jsx";
import TopBar from "./components/layout/TopBar.jsx";
import AgentControlRibbon from "./components/layout/AgentControlRibbon.jsx";

import LoginPage from "./components/auth/LoginPage.jsx";
import OverviewDashboard from "./components/overview/OverviewDashboard.jsx";
import IncidentsListPage from "./components/incidents/IncidentsListPage.jsx";
import IncidentCommandCenter from "./components/incidents/IncidentCommandCenter.jsx";
import ApprovalsPage from "./components/approvals/ApprovalsPage.jsx";
import InventoryPage from "./components/inventory/InventoryPage.jsx";
import ProductionPage from "./components/production/ProductionPage.jsx";
import SuppliersPage from "./components/suppliers/SuppliersPage.jsx";
import AgentActivityPage from "./components/audit/AgentActivityPage.jsx";
import DisruptionSimulatorPanel from "./components/simulator/DisruptionSimulatorPanel.jsx";
import DiagnosticsPage from "./components/diagnostics/DiagnosticsPage.jsx";
import ReportsPage from "./components/reports/ReportsPage.jsx";

function ProtectedRoute({ children }) {
  const { currentUser, token } = useAuth();
  const location = useLocation();

  // If not authenticated, strictly redirect to /login
  if (!currentUser && !token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

function DashboardLayout() {
  return (
    <ProtectedRoute>
      <div className="app-shell">
        <Sidebar />
        <div className="app-main">
          <TopBar />
          <AgentControlRibbon />
          <div className="app-content">
            <Routes>
              <Route path="/" element={<OverviewDashboard />} />
              <Route path="/incidents" element={<IncidentsListPage />} />
              <Route path="/incidents/:incidentId" element={<IncidentCommandCenter />} />
              <Route path="/approvals" element={<ApprovalsPage />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/production" element={<ProductionPage />} />
              <Route path="/suppliers" element={<SuppliersPage />} />
              <Route path="/audit" element={<Navigate to="/agent-activity" replace />} />
              <Route path="/agent-activity" element={<AgentActivityPage />} />
              <Route path="/diagnostics" element={<DiagnosticsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/simulator" element={<DisruptionSimulatorPanel />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={<DashboardLayout />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
