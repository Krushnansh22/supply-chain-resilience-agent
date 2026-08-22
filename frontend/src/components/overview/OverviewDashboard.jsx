/**
 * src/components/overview/OverviewDashboard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Exact visual match to the reference dashboard screenshot:
 *  - 4 KPI Stat Cards (Current balance, Income, Expence, Nearest delivery)
 *  - Middle Section: Warehouse workload (Pie Chart with callouts) + Warehouse workload (Line Chart)
 *  - Bottom Section: Accepted deliveries data table
 *
 * All backend API interactions & polling are preserved.
 */

import { useCallback, useEffect, useState } from "react";
import { listIncidents } from "../../api/incidents.js";
import { listAuditLogs } from "../../api/audit.js";
import { listProductionOrders } from "../../api/production.js";
import { listSuppliers } from "../../api/suppliers.js";

import KpiCards from "./KpiCards.jsx";
import WarehousePieChart from "./WarehousePieChart.jsx";
import WarehouseLineChart from "./WarehouseLineChart.jsx";
import AcceptedDeliveriesTable from "./AcceptedDeliveriesTable.jsx";

export default function OverviewDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [productionOrders, setProductionOrders] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    Promise.all([
      listIncidents(),
      listAuditLogs(),
      listProductionOrders(),
      listSuppliers(),
    ])
      .then(([incidentsRes, auditRes, productionRes, suppliersRes]) => {
        setIncidents(incidentsRes);
        setAuditLogs(auditRes);
        setProductionOrders(productionRes);
        setSuppliers(suppliersRes);
      })
      .catch((err) => console.error("Overview load failed:", err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading) {
    return (
      <div style={{ padding: "40px 0", color: "var(--text-muted)", fontSize: 14, fontFamily: "var(--font-display)" }}>
        Loading dashboard...
      </div>
    );
  }

  return (
    <div>
      {/* ── Row 1: 4 KPI Cards ── */}
      <KpiCards
        incidents={incidents}
        productionOrders={productionOrders}
        suppliers={suppliers}
      />

      {/* ── Row 2: Two Middle Charts ── */}
      <div className="middle-charts-grid">
        {/* Left: Warehouse Workload Pie Chart */}
        <WarehousePieChart />

        {/* Right: Warehouse Workload Multi-Line Chart */}
        <WarehouseLineChart />
      </div>

      {/* ── Row 3: Accepted Deliveries Table ── */}
      <AcceptedDeliveriesTable
        incidents={incidents}
        productionOrders={productionOrders}
      />
    </div>
  );
}
