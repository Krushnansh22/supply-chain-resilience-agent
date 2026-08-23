/**
 * src/components/dashboards/SupplierDashboard.jsx
 *
 * Supplier dashboard showing supplier's own profile details, active supply orders (POs),
 * performance metrics, RFQ quotes, and message thread history.
 */

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { getSupplier, listSuppliers, getSupplierMessages } from "../../api/suppliers.js";
import { apiRequest } from "../../api/client.js";

export default function SupplierDashboard() {
  const { user } = useAuth();
  const [supplierInfo, setSupplierInfo] = useState(null);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadSupplierData = useCallback(async () => {
    try {
      // 1. Resolve supplier profile & ID
      let targetSupplierId = user?.supplier_id;
      let info = null;

      if (targetSupplierId) {
        info = await getSupplier(targetSupplierId).catch(() => null);
      }

      if (!info) {
        const suppliersList = await listSuppliers().catch(() => []);
        if (Array.isArray(suppliersList) && suppliersList.length > 0) {
          info = suppliersList[0];
          targetSupplierId = info.supplier_id;
        }
      }

      if (!info && !targetSupplierId) {
        setError("No supplier profile linked to this user account.");
        setLoading(false);
        return;
      }

      setSupplierInfo(info);

      // 2. Fetch active POs and filter to this supplier
      const allPOs = await apiRequest("/integrations/purchase-orders/active").catch(() => []);
      const myPOs = Array.isArray(allPOs)
        ? allPOs.filter(po => !targetSupplierId || po.supplier_id === targetSupplierId)
        : [];
      setPurchaseOrders(myPOs);

      // 3. Fetch message thread history
      if (targetSupplierId) {
        const msgs = await getSupplierMessages(targetSupplierId).catch(() => []);
        setMessages(Array.isArray(msgs) ? msgs : []);
      }

      setError(null);
    } catch (err) {
      console.error("SupplierDashboard load error:", err);
      setError("Failed to fetch supplier operational data.");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadSupplierData();
    const interval = setInterval(loadSupplierData, 10000);
    return () => clearInterval(interval);
  }, [loadSupplierData]);

  if (loading) {
    return <div className="empty-state">Loading supplier console...</div>;
  }

  if (error) {
    return <div className="empty-state" style={{ color: "var(--red-accent)" }}>{error}</div>;
  }

  const activePOs = purchaseOrders.filter(po => ["OPEN", "ORDERED", "IN_TRANSIT", "DELAYED", "AT_RISK"].includes(po.status));
  const completedPOs = purchaseOrders.filter(po => po.status === "RECEIVED");

  return (
    <div className="page-container">
      {/* Supplier Profile Banner */}
      <div style={{
        background: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
        borderRadius: "var(--radius-lg)",
        padding: "24px",
        color: "#FFFFFF",
        marginBottom: "24px",
        boxShadow: "var(--shadow-card)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px"
      }}>
        <div>
          <h2 style={{ color: "#FFFFFF", fontSize: "22px", marginBottom: "8px" }}>
            {supplierInfo?.name || user.company_name}
          </h2>
          <p style={{ color: "rgba(255,255,255,0.8)", fontSize: "14px", margin: 0 }}>
            Vendor Console · Registered Email: {supplierInfo?.contact_email || user.email}
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px" }}>
          <span className="status-pill success" style={{ background: "#FFFFFF", color: "#059669" }}>
            ID: {user.supplier_id}
          </span>
          <span className="status-pill success" style={{ background: "#FFFFFF", color: "#059669" }}>
            Status: {supplierInfo?.status || "ACTIVE"}
          </span>
        </div>
      </div>

      {/* Performance Scorecard Row */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle green">⭐</div>
            <span className="kpi-title-text">Quality Score</span>
          </div>
          <div className="kpi-amount-val">
            {supplierInfo?.quality_score !== null ? `${supplierInfo?.quality_score}%` : "N/A"}
          </div>
          <div className="kpi-footer-row">
            <span>SCDA Quality standard</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">🤝</div>
            <span className="kpi-title-text">Reliability Score</span>
          </div>
          <div className="kpi-amount-val">
            {supplierInfo?.reliability_score !== null ? `${supplierInfo?.reliability_score}%` : "N/A"}
          </div>
          <div className="kpi-footer-row">
            <span>Historical trust rating</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle yellow">📦</div>
            <span className="kpi-title-text">Min Order Qty</span>
          </div>
          <div className="kpi-amount-val">
            {supplierInfo?.min_order_qty !== null ? supplierInfo?.min_order_qty : "N/A"}
          </div>
          <div className="kpi-footer-row">
            <span>Units per batch</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle red">🚚</div>
            <span className="kpi-title-text">Active Shipments</span>
          </div>
          <div className="kpi-amount-val">{activePOs.length}</div>
          <div className="kpi-footer-row">
            <span>Orders in transit / open</span>
          </div>
        </div>
      </div>

      {/* Tables Section */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px" }}>
        {/* Active Purchase Orders */}
        <div className="dashboard-card">
          <div className="card-header-row">
            <h3 className="card-header-title">My Supply commitments (Purchase Orders)</h3>
          </div>
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>PO ID</th>
                  <th>Quantity</th>
                  <th>Total Value</th>
                  <th>Promised Delivery</th>
                  <th>Notes</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {purchaseOrders.map((po) => (
                  <tr key={po.po_id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontWeight: "600" }}>{po.po_id}</td>
                    <td>{po.quantity} units</td>
                    <td style={{ fontWeight: "600" }}>₹{po.total_value?.toLocaleString()}</td>
                    <td>{po.promised_delivery ? new Date(po.promised_delivery).toLocaleDateString() : "N/A"}</td>
                    <td style={{ fontSize: "12px", color: "var(--text-secondary)" }}>{po.notes || "—"}</td>
                    <td>
                      <span className={`status-pill ${
                        po.status === "RECEIVED" ? "success" :
                        po.status === "DELAYED" || po.status === "AT_RISK" ? "danger" :
                        "info"
                      }`}>
                        {po.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {purchaseOrders.length === 0 && (
                  <tr>
                    <td colSpan="6" className="empty-state">No purchase orders assigned.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Message Thread & Inquiries */}
        <div className="dashboard-card" style={{ marginTop: "20px" }}>
          <div className="card-header-row">
            <h3 className="card-header-title">Communication & Incident Dispatch Log</h3>
          </div>
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Sender</th>
                  <th>Message / Inquiry</th>
                  <th>Incident Ref</th>
                </tr>
              </thead>
              <tbody>
                {messages.map((m, idx) => (
                  <tr key={idx}>
                    <td style={{ fontSize: "12px", whiteSpace: "nowrap" }}>
                      {m.timestamp ? new Date(m.timestamp).toLocaleString() : "Recent"}
                    </td>
                    <td style={{ fontWeight: "600" }}>{m.sender || "Control Tower Agent"}</td>
                    <td style={{ fontSize: "13px" }}>{m.message || m.body || m.content || JSON.stringify(m)}</td>
                    <td>
                      <span className="status-pill info">{m.incident_id || "SYSTEM"}</span>
                    </td>
                  </tr>
                ))}
                {messages.length === 0 && (
                  <tr>
                    <td colSpan="4" className="empty-state">No message dispatches recorded.</td>
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
