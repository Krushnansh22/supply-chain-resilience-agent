/**
 * src/components/layout/TopBar.jsx
 * Header with RBAC User Role Switcher, Multi-Warehouse Selector, and Health Indicator.
 */
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

export default function TopBar() {
  const navigate = useNavigate();
  const {
    currentUser,
    isAdmin,
    isWarehouseManager,
    activeWarehouse,
    usersList,
    warehousesList,
    switchUser,
    setWarehouse,
    logout,
  } = useAuth();

  const [online, setOnline] = useState(null);

  useEffect(() => {
    const check = () =>
      apiRequest("/health")
        .then(() => setOnline(true))
        .catch(() => setOnline(false));
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const statusColor = online === null ? "#667085" : online ? "#16A46B" : "#D94B5B";
  const statusLabel = online === null ? "CHECKING" : online ? "LIVE" : "OFFLINE";

  return (
    <header className="header-top" style={{ borderBottom: "1px solid var(--border-subtle, #1E293B)", padding: "10px 24px" }}>
      <div className="header-top-inner" style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div className="header-logo" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            className="mark"
            style={{
              width: 30,
              height: 30,
              borderRadius: 6,
              background: "linear-gradient(135deg, #073F46 0%, #07535A 35%, #23B8C9 65%, #E5A11A 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#ffffff",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            SC
          </div>
          <span
            className="name"
            style={{ fontFamily: "Space Grotesk, sans-serif", fontSize: 13, fontWeight: 700, color: "#ffffff" }}
          >
            Supply Chain Resilience Agent
          </span>
        </div>
      </div>

      {/* ─── RBAC & WAREHOUSE CONTEXT CONTROLS ─── */}
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginLeft: "auto" }}>
        
        {/* 1. Warehouse Selector / Lock Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted, #94A3B8)", textTransform: "uppercase" }}>
            Warehouse Scope:
          </span>
          {isAdmin ? (
            <select
              value={activeWarehouse}
              onChange={(e) => setWarehouse(e.target.value)}
              style={{
                background: "rgba(35, 184, 201, 0.1)",
                color: "#23B8C9",
                border: "1px solid rgba(35, 184, 201, 0.4)",
                padding: "5px 10px",
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              <option value="ALL" style={{ background: "#0F172A", color: "#fff" }}>🌐 All Warehouses (Global View)</option>
              {warehousesList.map((wh) => (
                <option key={wh.warehouse_id} value={wh.warehouse_id} style={{ background: "#0F172A", color: "#fff" }}>
                  📍 {wh.name}
                </option>
              ))}
            </select>
          ) : (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                background: "rgba(245, 158, 11, 0.12)",
                color: "#F59E0B",
                border: "1px solid rgba(245, 158, 11, 0.35)",
                padding: "4px 10px",
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 600,
              }}
              title="Your user account is restricted to your assigned warehouse facility."
            >
              <span>🔒</span>
              <span>{activeWarehouse} (Assigned)</span>
            </div>
          )}
        </div>

        {/* 2. User & Role Switcher */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, borderLeft: "1px solid rgba(255,255,255,0.1)", paddingLeft: 14 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted, #94A3B8)", textTransform: "uppercase" }}>
            User Role:
          </span>
          <select
            value={currentUser?.user_id || ""}
            onChange={(e) => switchUser(e.target.value)}
            style={{
              background: "rgba(255, 255, 255, 0.05)",
              color: "#FFFFFF",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              padding: "5px 10px",
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {usersList.map((u) => (
              <option key={u.user_id} value={u.user_id} style={{ background: "#0F172A", color: "#fff" }}>
                {u.role === "ADMIN" ? "👑" : "🏭"} {u.name} ({u.role.replace("_", " ")})
              </option>
            ))}
          </select>
        </div>

        {/* 3. Auth Logout / Portal Link */}
        <button
          type="button"
          onClick={handleLogout}
          style={{
            background: "rgba(239, 68, 68, 0.1)",
            color: "#EF4444",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            padding: "5px 10px",
            borderRadius: 6,
            fontSize: 11,
            fontWeight: 600,
            cursor: "pointer",
          }}
          title="Sign out or switch portal accounts"
        >
          Sign Out
        </button>

        {/* 4. System Health Beacon */}
        <div className="header-status" style={{ display: "flex", alignItems: "center", gap: 6, borderLeft: "1px solid rgba(255,255,255,0.1)", paddingLeft: 14 }}>
          <span className="status-dot-sm" style={{ background: statusColor, width: 6, height: 6, borderRadius: "50%" }} />
          <span
            className="status-text"
            style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10, color: statusColor, letterSpacing: "0.05em" }}
          >
            {statusLabel}
          </span>
        </div>
      </div>
    </header>
  );
}