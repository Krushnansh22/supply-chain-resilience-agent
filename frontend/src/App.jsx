/**
 * src/App.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Top-level router + layout shell for the Control Tower (team doc Section 11).
 * Sidebar sections map 1:1 to backend routers:
 *   Overview -> /incidents + /audit (activity feed)
 *   Incidents -> /incidents/{id}, /agent/state/{id}, /agent/plan/{id}
 *   Inventory -> /inventory
 *   Production -> /production
 *   Suppliers -> /suppliers
 *   Audit -> /audit
 *
 * RECEIVES: nothing (composition root)
 * DELIVERS: rendered app shell; individual pages own their own data fetching via src/api/*
 */

import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar.jsx";
import TopBar from "./components/layout/TopBar.jsx";

import OverviewDashboard from "./components/overview/OverviewDashboard.jsx";
import IncidentCommandCenter from "./components/incidents/IncidentCommandCenter.jsx";
import InventoryPage from "./components/inventory/InventoryPage.jsx";
import ProductionPage from "./components/production/ProductionPage.jsx";
import SuppliersPage from "./components/suppliers/SuppliersPage.jsx";
import AuditTimeline from "./components/audit/AuditTimeline.jsx";
import DisruptionSimulatorPanel from "./components/simulator/DisruptionSimulatorPanel.jsx";

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
              <Route path="/incidents/:incidentId" element={<IncidentCommandCenter />} />
              <Route path="/inventory" element={<InventoryPage />} />
              <Route path="/production" element={<ProductionPage />} />
              <Route path="/suppliers" element={<SuppliersPage />} />
              <Route path="/audit" element={<AuditTimeline />} />
              <Route path="/simulator" element={<DisruptionSimulatorPanel />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
