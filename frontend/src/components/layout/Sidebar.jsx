/**
 * src/components/layout/Sidebar.jsx
 * Owner: Developer 4 (Frontend)
 * Fixed-width dark navy sidebar with icon-over-label nav items, matching the
 * Control Tower screenshot spec. All navigation routes UNCHANGED.
 * Backend API integration preserved (this component owns no data fetching).
 */

import { NavLink } from "react-router-dom";

function Icon({ name }) {
  const paths = {
    overview: <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>,
    incidents: <><path d="M12 3 2 20h20L12 3Z" strokeLinejoin="round" /><path d="M12 10v4" strokeLinecap="round" /><circle cx="12" cy="17" r="0.5" fill="currentColor" /></>,
    approvals: <><circle cx="12" cy="12" r="9" /><path d="m8 12 3 3 5-6" strokeLinecap="round" strokeLinejoin="round" /></>,
    inventory: <><path d="M21 8 12 3 3 8v8l9 5 9-5V8Z" strokeLinejoin="round" /><path d="M3 8l9 5 9-5M12 13v8" /></>,
    production: <><path d="M3 21V10l5 3V10l5 3V10l5 3v8H3Z" strokeLinejoin="round" /></>,
    suppliers: <><rect x="4" y="3" width="16" height="18" rx="1" /><path d="M9 8h1M14 8h1M9 12h1M14 12h1M9 16h1M14 16h1" strokeLinecap="round" /></>,
    audit: <><path d="M6 3h9l4 4v14H6z" strokeLinejoin="round" /><path d="M9 12h6M9 16h6M9 8h3" strokeLinecap="round" /></>,
    simulator: <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" strokeLinejoin="round" strokeLinecap="round" />,
  };
  return (
    <svg viewBox="0 0 24 24">
      {paths[name]}
    </svg>
  );
}

const NAV_ITEMS = [
  { to: "/", label: "Overview", end: true, icon: "overview" },
  { to: "/incidents", label: "Incidents", icon: "incidents" },
  { to: "/approvals", label: "Approvals", icon: "approvals" },
  { to: "/inventory", label: "Inventory", icon: "inventory" },
  { to: "/production", label: "Production", icon: "production" },
  { to: "/suppliers", label: "Suppliers", icon: "suppliers" },
  { to: "/audit", label: "Audit", icon: "audit" },
  { to: "/simulator", label: "Simulator", icon: "simulator" },
];

export default function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation" role="navigation">
      <div className="sidebar-brand">
        <div className="brand-mark">CT</div>
        <span className="sidebar-title">Control Tower</span>
      </div>

      <div className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <span className="nav-icon">
              <Icon name={item.icon} />
            </span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
