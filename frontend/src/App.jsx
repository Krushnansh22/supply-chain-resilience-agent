/**
 * src/App.jsx
 * Owner: Developer 4 (Frontend)
 *
 * FIX: Flattened route structure using React Router v6 Outlet pattern.
 * The previous nested <Routes> inside the app-shell JSX caused inner paths
 * (/supplier-dashboard, /user-dashboard) to never match absolute URLs because
 * the inner <Routes> component strips the parent route prefix from the path.
 *
 * All routes are now declared in a single top-level <Routes>.
 * The app-shell (Sidebar + TopBar) is rendered via AppShellLayout using <Outlet />.
 */

import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import ProtectedRoute from "./components/auth/ProtectedRoute.jsx";

// Auth Pages
import LandingPage       from "./components/auth/LandingPage.jsx";
import LoginPage         from "./components/auth/LoginPage.jsx";
import RegisterPage      from "./components/auth/RegisterPage.jsx";
import ForgotPasswordPage from "./components/auth/ForgotPasswordPage.jsx";
import ResetPasswordPage  from "./components/auth/ResetPasswordPage.jsx";

// Layout
import Sidebar from "./components/layout/Sidebar.jsx";
import TopBar  from "./components/layout/TopBar.jsx";

// Dashboards
import OverviewDashboard  from "./components/overview/OverviewDashboard.jsx";
import UserDashboard      from "./components/dashboards/UserDashboard.jsx";
import SupplierDashboard  from "./components/dashboards/SupplierDashboard.jsx";

// Core App Pages
import IncidentsListPage      from "./components/incidents/IncidentsListPage.jsx";
import IncidentCommandCenter  from "./components/incidents/IncidentCommandCenter.jsx";
import ApprovalsPage          from "./components/approvals/ApprovalsPage.jsx";
import InventoryPage          from "./components/inventory/InventoryPage.jsx";
import ProductionPage         from "./components/production/ProductionPage.jsx";
import SuppliersPage          from "./components/suppliers/SuppliersPage.jsx";
import AgentActivityPage      from "./components/audit/AgentActivityPage.jsx";
import DisruptionSimulatorPanel from "./components/simulator/DisruptionSimulatorPanel.jsx";
import DiagnosticsPage        from "./components/diagnostics/DiagnosticsPage.jsx";
import ReportsPage            from "./components/reports/ReportsPage.jsx";

/** Sidebar + TopBar layout wrapper — rendered via <Outlet /> for all protected pages */
function AppShellLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar />
        <div className="app-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

/** Redirects to the role-appropriate home page */
function DashboardHome() {
  const { user } = useAuth();
  if (user?.role === "admin")    return <OverviewDashboard />;
  if (user?.role === "supplier") return <Navigate to="/supplier-dashboard" replace />;
  return <Navigate to="/user-dashboard" replace />;
}

function AppRoutes() {
  const { handleUnauthorized, loading, user } = useAuth();

  useEffect(() => {
    const handle = () => handleUnauthorized();
    window.addEventListener("scda_unauthorized", handle);
    return () => window.removeEventListener("scda_unauthorized", handle);
  }, [handleUnauthorized]);

  // Only block on the full-screen spinner when token is being validated and
  // no user is hydrated from localStorage yet.
  if (loading && !user) {
    return (
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", background: "var(--bg-canvas)",
        fontFamily: "var(--font-display)", fontWeight: "600",
        color: "var(--text-secondary)"
      }}>
        <h2>Restoring Control Tower session...</h2>
      </div>
    );
  }

  return (
    <Routes>
      {/* ── Public Routes (no auth required) ── */}
      <Route path="/landing"         element={<LandingPage />} />
      <Route path="/login"           element={<LoginPage />} />
      <Route path="/register"        element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password"  element={<ResetPasswordPage />} />

      {/* ── Protected App Shell ── */}
      {/* AppShellLayout renders Sidebar + TopBar + <Outlet /> for all children */}
      <Route element={<ProtectedRoute><AppShellLayout /></ProtectedRoute>}>

        {/* Home: role-based landing */}
        <Route path="/"  element={<DashboardHome />} />

        {/* Role-specific dashboards */}
        <Route path="/supplier-dashboard"
          element={<ProtectedRoute allowedRoles={["supplier"]}><SupplierDashboard /></ProtectedRoute>}
        />
        <Route path="/user-dashboard"
          element={<ProtectedRoute allowedRoles={["user"]}><UserDashboard /></ProtectedRoute>}
        />

        {/* Admin-only pages */}
        <Route path="/incidents"
          element={<ProtectedRoute allowedRoles={["admin"]}><IncidentsListPage /></ProtectedRoute>}
        />
        <Route path="/incidents/:incidentId"
          element={<ProtectedRoute allowedRoles={["admin"]}><IncidentCommandCenter /></ProtectedRoute>}
        />
        <Route path="/approvals"
          element={<ProtectedRoute allowedRoles={["admin"]}><ApprovalsPage /></ProtectedRoute>}
        />
        <Route path="/suppliers"
          element={<ProtectedRoute allowedRoles={["admin"]}><SuppliersPage /></ProtectedRoute>}
        />
        <Route path="/reports"
          element={<ProtectedRoute allowedRoles={["admin"]}><ReportsPage /></ProtectedRoute>}
        />
        <Route path="/simulator"
          element={<ProtectedRoute allowedRoles={["admin"]}><DisruptionSimulatorPanel /></ProtectedRoute>}
        />
        <Route path="/diagnostics"
          element={<ProtectedRoute allowedRoles={["admin"]}><DiagnosticsPage /></ProtectedRoute>}
        />
        <Route path="/agent-activity"
          element={<ProtectedRoute allowedRoles={["admin"]}><AgentActivityPage /></ProtectedRoute>}
        />

        {/* Shared pages */}
        <Route path="/inventory"
          element={<ProtectedRoute allowedRoles={["admin", "supplier"]}><InventoryPage /></ProtectedRoute>}
        />
        <Route path="/production"
          element={<ProtectedRoute allowedRoles={["admin", "user"]}><ProductionPage /></ProtectedRoute>}
        />

        {/* Unknown path → home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
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
