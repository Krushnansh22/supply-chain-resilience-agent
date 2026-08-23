/**
 * src/components/dashboards/UserDashboard.jsx
 *
 * User dashboard showing personal summary, metrics, production status, and active incidents.
 * Enforces User role perspective.
 */

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { listIncidents } from "../../api/incidents.js";
import { listProductionOrders } from "../../api/production.js";
import { listInventory } from "../../api/inventory.js";

export default function UserDashboard() {
  const { user } = useAuth();
  const [incidents, setIncidents] = useState([]);
  const [productionOrders, setProductionOrders] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const load = useCallback(() => {
    Promise.all([
      listIncidents("all").catch(() => []),
      listProductionOrders().catch(() => []),
      listInventory().catch(() => [])
    ])
      .then(([inc, prod, inv]) => {
        setIncidents(Array.isArray(inc) ? inc : []);
        setProductionOrders(Array.isArray(prod) ? prod : []);
        setInventory(Array.isArray(inv) ? inv : []);
        setError(null);
      })
      .catch((err) => {
        console.error("UserDashboard load failed:", err);
        setError("Failed to load dashboard data.");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading) {
    return <div className="empty-state">Loading user dashboard...</div>;
  }

  if (error && incidents.length === 0 && productionOrders.length === 0) {
    return <div className="empty-state" style={{ color: "var(--red-accent)" }}>{error}</div>;
  }

  // Calculate metrics safely with Array.isArray guards
  const activeIncidents = (Array.isArray(incidents) ? incidents : []).filter(i => ["DETECTED", "INVESTIGATING", "SUPPLIER_CONTACT", "EVALUATING", "PLAN_READY", "WAITING_APPROVAL", "EXECUTING", "REPLANNING"].includes(i.status));
  const blockedProduction = (Array.isArray(productionOrders) ? productionOrders : []).filter(p => p.status === "BLOCKED" || p.status === "WAITING_PARTS");
  const lowStock = (Array.isArray(inventory) ? inventory : []).filter(i => i.usable_stock <= i.safety_stock);

  return (
    <div className="page-container">
      {/* Welcome banner */}
      <div style={{
        background: "linear-gradient(135deg, #1E2337 0%, #2D3554 100%)",
        borderRadius: "var(--radius-lg)",
        padding: "24px",
        color: "#FFFFFF",
        marginBottom: "24px",
        boxShadow: "var(--shadow-card)"
      }}>
        <h2 style={{ color: "#FFFFFF", fontSize: "22px", marginBottom: "8px" }}>Welcome Back, {user.name}</h2>
        <p style={{ color: "#8E9BAE", fontSize: "14px", margin: 0 }}>
          Role: <span className="status-pill info" style={{ padding: "2px 8px" }}>Procurement User</span> · Email: {user.email}
        </p>
      </div>

      {/* Metrics Row */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle red">⚠️</div>
            <span className="kpi-title-text">Active Incidents</span>
          </div>
          <div className="kpi-amount-val">{activeIncidents.length}</div>
          <div className="kpi-footer-row">
            <span>Requiring resolution</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle yellow">⚙️</div>
            <span className="kpi-title-text">Production Alerts</span>
          </div>
          <div className="kpi-amount-val">{blockedProduction.length}</div>
          <div className="kpi-footer-row">
            <span>Blocked or waiting parts</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">📦</div>
            <span className="kpi-title-text">Low Stock Components</span>
          </div>
          <div className="kpi-amount-val">{lowStock.length}</div>
          <div className="kpi-footer-row">
            <span>Below safety threshold</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle green">📈</div>
            <span className="kpi-title-text">Total Projects</span>
          </div>
          <div className="kpi-amount-val">{productionOrders.length}</div>
          <div className="kpi-footer-row">
            <span>Active production orders</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        
        {/* Production Status */}
        <div className="dashboard-card">
          <div className="card-header-row">
            <h3 className="card-header-title">My Production Deadlines</h3>
          </div>
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {productionOrders.slice(0, 5).map((p) => (
                  <tr key={p.production_id}>
                    <td style={{ fontWeight: "600" }}>{p.product}</td>
                    <td>{p.quantity} units</td>
                    <td>
                      <span className={`status-pill ${p.priority === "CRITICAL" ? "danger" : p.priority === "HIGH" ? "warning" : "info"}`}>
                        {p.priority}
                      </span>
                    </td>
                    <td>
                      <span className={`status-pill ${p.status === "ON_TRACK" || p.status === "COMPLETED" ? "success" : "danger"}`}>
                        {p.status.replace("_", " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="dashboard-card">
          <div className="card-header-row">
            <h3 className="card-header-title">Recent Operational Disruptions</h3>
          </div>
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {activeIncidents.slice(0, 5).map((inc) => (
                  <tr key={inc.incident_id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontWeight: "600" }}>{inc.incident_id}</td>
                    <td>{inc.type.replace("_", " ")}</td>
                    <td>
                      <span className={`badge ${inc.severity === "CRITICAL" ? "badge-critical" : inc.severity === "HIGH" ? "badge-warning" : "badge-primary"}`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td>
                      <span className="status-pill warning">{inc.status.replace("_", " ")}</span>
                    </td>
                  </tr>
                ))}
                {activeIncidents.length === 0 && (
                  <tr>
                    <td colSpan="4" className="empty-state">No active disruptions detected.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
