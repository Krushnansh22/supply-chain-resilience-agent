/**
 * src/App.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Top-level composition root. Wraps routes in AuthProvider, enforces ProtectedRoute,
 * maps public routes (Landing, Login, Register, Forgot, Reset) and role dashboards.
 */

import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import ProtectedRoute from "./components/auth/ProtectedRoute.jsx";

// Auth Pages
import LandingPage from "./components/auth/LandingPage.jsx";
import LoginPage from "./components/auth/LoginPage.jsx";
import RegisterPage from "./components/auth/RegisterPage.jsx";
import ForgotPasswordPage from "./components/auth/ForgotPasswordPage.jsx";
import ResetPasswordPage from "./components/auth/ResetPasswordPage.jsx";

// Dashboards & Shell layout
import Sidebar from "./components/layout/Sidebar.jsx";
import TopBar from "./components/layout/TopBar.jsx";
import OverviewDashboard from "./components/overview/OverviewDashboard.jsx";
import UserDashboard from "./components/dashboards/UserDashboard.jsx";
import SupplierDashboard from "./components/dashboards/SupplierDashboard.jsx";

// Core App Pages
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

function DashboardHome() {
  const { user } = useAuth();
  if (user?.role === "admin") {
    return <OverviewDashboard />;
  } else if (user?.role === "supplier") {
    return <Navigate to="/supplier-dashboard" replace />;
  } else {
    return <Navigate to="/user-dashboard" replace />;
  }
}

function AppRoutes() {
  const { handleUnauthorized, loading, user } = useAuth();

  // Listen to 401 unauthorized events from the api client
  useEffect(() => {
    const handleUnauth = () => {
      handleUnauthorized();
    };
    window.addEventListener("scda_unauthorized", handleUnauth);
    return () => window.removeEventListener("scda_unauthorized", handleUnauth);
  }, [handleUnauthorized]);

  // Only show full-screen loader when the token is being validated server-side
  // and there's no user yet. If user is hydrated from localStorage, render
  // routes immediately so post-login navigation works without being blocked.
  if (loading && !user) {
    return (
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "var(--bg-canvas)",
        fontFamily: "var(--font-display)",
        fontWeight: "600",
        color: "var(--text-secondary)"
      }}>
        <h2>Restoring Control Tower session...</h2>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Protected Application Area */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <div className="app-shell">
              <Sidebar />
              <div className="app-main">
                <TopBar />
                <div className="app-content">
                  <Routes>
                    <Route path="/" element={<DashboardHome />} />
                    
                    {/* Admin/Internal only routes */}
                    <Route path="/incidents" element={<ProtectedRoute allowedRoles={["admin"]}><IncidentsListPage /></ProtectedRoute>} />
                    <Route path="/incidents/:incidentId" element={<ProtectedRoute allowedRoles={["admin"]}><IncidentCommandCenter /></ProtectedRoute>} />
                    <Route path="/approvals" element={<ProtectedRoute allowedRoles={["admin"]}><ApprovalsPage /></ProtectedRoute>} />
                    <Route path="/inventory" element={<ProtectedRoute allowedRoles={["admin", "supplier"]}><InventoryPage /></ProtectedRoute>} />
                    <Route path="/production" element={<ProtectedRoute allowedRoles={["admin", "user"]}><ProductionPage /></ProtectedRoute>} />
                    <Route path="/suppliers" element={<ProtectedRoute allowedRoles={["admin"]}><SuppliersPage /></ProtectedRoute>} />
                    <Route path="/reports" element={<ProtectedRoute allowedRoles={["admin"]}><ReportsPage /></ProtectedRoute>} />
                    <Route path="/simulator" element={<ProtectedRoute allowedRoles={["admin"]}><DisruptionSimulatorPanel /></ProtectedRoute>} />
                    <Route path="/diagnostics" element={<ProtectedRoute allowedRoles={["admin"]}><DiagnosticsPage /></ProtectedRoute>} />
                    <Route path="/agent-activity" element={<ProtectedRoute allowedRoles={["admin"]}><AgentActivityPage /></ProtectedRoute>} />
                    
                    {/* Role Dashboards */}
                    <Route path="/user-dashboard" element={<ProtectedRoute allowedRoles={["user"]}><UserDashboard /></ProtectedRoute>} />
                    <Route path="/supplier-dashboard" element={<ProtectedRoute allowedRoles={["supplier"]}><SupplierDashboard /></ProtectedRoute>} />

                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </div>
              </div>
            </div>
          </ProtectedRoute>
        }
      />
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
