/**
 * src/App.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Top-level router + layout shell for the Control Tower (team doc Section 11).
 * Sidebar sections map 1:1 to backend routers:
 *   Overview -> /incidents + /audit (activity feed)
 *   Incidents (list) -> /incidents, /production (display join)
 *   Incidents (detail) -> /incidents/{id}, /agent/state/{id}, /agent/plan/{id}
 *   Approvals -> /incidents (filtered WAITING_APPROVAL) + /agent/plan/{id}
 *   Inventory -> /inventory
 *   Production -> /production
 *   Suppliers -> /suppliers
 *   Audit -> /audit
 *
 * RECEIVES: nothing (composition root)
 * DELIVERS: rendered app shell; individual pages own their own data fetching via src/api/*
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar.jsx";
import TopBar from "./components/layout/TopBar.jsx";

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

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="app-main">
          <TopBar />
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
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
