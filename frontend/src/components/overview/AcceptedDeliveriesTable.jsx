import { useState } from "react";
import { Link } from "react-router-dom";

export default function AcceptedDeliveriesTable({ incidents = [], productionOrders = [] }) {
  const [sortField, setSortField] = useState(null);
  const [sortAsc, setSortAsc] = useState(true);
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [filterText, setFilterText] = useState("");

  const baseRows = [
    { id: "DEL-84920", status: "In Transit", statusType: "info", weight: "1,240 kg", date: "26.08.2026", time: "14:30", link: "/production", supplier: "Alpha Components" },
    { id: "DEL-84919", status: "Delivered", statusType: "success", weight: "850 kg", date: "26.08.2026", time: "12:15", link: "/inventory", supplier: "GalaxTech" },
    { id: "DEL-84918", status: "Delayed", statusType: "danger", weight: "3,100 kg", date: "25.08.2026", time: "10:45", link: "/incidents", supplier: "Apex Logistics" },
    { id: "DEL-84917", status: "Accepted", statusType: "success", weight: "420 kg", date: "25.08.2026", time: "18:20", link: "/approvals", supplier: "Alpha Components" },
    { id: "DEL-84916", status: "Pending", statusType: "warning", weight: "2,680 kg", date: "24.08.2026", time: "16:00", link: "/production", supplier: "GalaxTech" }
  ];

  const dynamicRows = incidents.slice(0, 3).map((inc, i) => ({
    id: inc.affected_po || inc.incident_id || `INC-00${i+1}`,
    status: inc.status === "RESOLVED" ? "Resolved" : inc.status === "WAITING_APPROVAL" ? "Pending" : "Active Alert",
    statusType: inc.status === "RESOLVED" ? "success" : inc.status === "WAITING_APPROVAL" ? "warning" : "danger",
    weight: inc.affected_component || "Component Batch",
    date: "26.08.2026",
    time: "Live",
    link: `/incidents`,
    supplier: inc.supplier || "Primary Vendor"
  }));

  const combined = dynamicRows.length > 0 ? [...dynamicRows, ...baseRows.slice(dynamicRows.length)] : baseRows;

  // Filter
  const filtered = combined.filter((r) =>
    r.id.toLowerCase().includes(filterText.toLowerCase()) ||
    r.status.toLowerCase().includes(filterText.toLowerCase()) ||
    r.supplier.toLowerCase().includes(filterText.toLowerCase())
  );

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    if (!sortField) return 0;
    const valA = a[sortField] || "";
    const valB = b[sortField] || "";
    return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
  });

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <div className="dashboard-card" style={{ position: "relative" }}>
      {/* Header */}
      <div className="card-header-row" style={{ flexWrap: "wrap", gap: 12 }}>
        <span className="card-header-title">Accepted Deliveries</span>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginLeft: "auto" }}>
          <input
            type="text"
            placeholder="Search delivery or vendor..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            style={{
              padding: "5px 10px",
              borderRadius: "6px",
              border: "1px solid var(--border-subtle)",
              fontSize: "12px",
              width: "180px",
              background: "#FFFFFF",
            }}
          />
        </div>
      </div>

      {/* Table */}
      <div className="deliveries-table-wrap">
        <table className="custom-data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort("id")} style={{ cursor: "pointer", userSelect: "none" }}>
                Delivery Number {sortField === "id" ? (sortAsc ? "▲" : "▼") : ""}
              </th>
              <th onClick={() => handleSort("status")} style={{ cursor: "pointer", userSelect: "none" }}>
                Status {sortField === "status" ? (sortAsc ? "▲" : "▼") : ""}
              </th>
              <th onClick={() => handleSort("weight")} style={{ cursor: "pointer", userSelect: "none" }}>
                Weight / Batch {sortField === "weight" ? (sortAsc ? "▲" : "▼") : ""}
              </th>
              <th onClick={() => handleSort("date")} style={{ cursor: "pointer", userSelect: "none" }}>
                Date {sortField === "date" ? (sortAsc ? "▲" : "▼") : ""}
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, idx) => (
              <tr key={idx} style={{ cursor: "pointer" }} onClick={() => setSelectedDelivery(row)}>
                <td style={{ fontWeight: 600 }}>
                  <span className="code-chip">{row.id}</span>
                </td>
                <td>
                  <span className={`status-pill ${row.statusType}`}>
                    {row.status}
                  </span>
                </td>
                <td style={{ color: "var(--text-secondary)" }}>{row.weight}</td>
                <td style={{ color: "var(--text-secondary)" }}>{row.date} ({row.time})</td>
                <td>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedDelivery(row);
                    }}
                    style={{
                      background: "none",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "6px",
                      padding: "4px 8px",
                      fontSize: "11px",
                      fontWeight: 600,
                      color: "var(--primary)",
                      cursor: "pointer",
                    }}
                  >
                    Inspect
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quick Inspection Modal */}
      {selectedDelivery && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(15, 23, 42, 0.4)", backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 9999,
        }}>
          <div style={{
            background: "#FFFFFF", borderRadius: 16, padding: 24,
            width: 420, maxWidth: "90%", boxShadow: "0 20px 50px rgba(0,0,0,0.2)",
            border: "1px solid var(--border-subtle)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 16 }}>Delivery Manifest: {selectedDelivery.id}</h3>
              <button
                onClick={() => setSelectedDelivery(null)}
                style={{ background: "none", border: "none", fontSize: 18, cursor: "pointer", color: "var(--text-muted)" }}
              >
                ✕
              </button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: 13 }}>
              <div><strong>Status:</strong> <span className={`status-pill ${selectedDelivery.statusType}`}>{selectedDelivery.status}</span></div>
              <div><strong>Supplier Vendor:</strong> {selectedDelivery.supplier}</div>
              <div><strong>Weight / Cargo:</strong> {selectedDelivery.weight}</div>
              <div><strong>Scheduled Arrival:</strong> {selectedDelivery.date} at {selectedDelivery.time}</div>
              <div><strong>Route Status:</strong> On track, cleared customs & warehouse gate</div>
            </div>
            <div style={{ marginTop: 20, textAlign: "right" }}>
              <Link
                to={selectedDelivery.link}
                className="btn-primary"
                onClick={() => setSelectedDelivery(null)}
                style={{ textDecoration: "none", fontSize: 12, display: "inline-block" }}
              >
                Open Full Operations Page →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
