/**
 * src/components/layout/Sidebar.jsx
 * Owner: Developer 4 (Frontend)
 * Navigation per team doc Section 11: Overview / Incidents / Approvals /
 * Inventory / Production / Suppliers / Audit / Simulator
 */
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "🏠 Overview", end: true },
  { to: "/incidents", label: "🚨 Incidents" },
  { to: "/approvals", label: "✅ Approvals" },
  { to: "/inventory", label: "📦 Inventory" },
  { to: "/production", label: "🏭 Production" },
  { to: "/suppliers", label: "🏢 Suppliers" },
  { to: "/audit", label: "📝 Audit" },
  { to: "/agent-activity", label: "🧠 Agent Activity" },
  { to: "/simulator", label: "⚡ Simulator" },
];

export default function Sidebar() {
  return (
    <nav className="panel" style={{ width: 220, borderRadius: 0, minHeight: "100vh" }}>
      <h2 style={{ fontSize: 16, marginBottom: 24 }}>Control Tower</h2>
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          style={({ isActive }) => ({
            display: "block",
            padding: "8px 0",
            color: isActive ? "var(--accent)" : "var(--text-secondary)",
            textDecoration: "none",
          })}
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
