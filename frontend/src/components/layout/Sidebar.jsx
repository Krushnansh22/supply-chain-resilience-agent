/**
 * src/components/layout/Sidebar.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Exact match to the reference dashboard screenshot:
 *  - Colorful square logo at the top with segmented colors (red, yellow, green, cyan)
 *  - Vertical icon navigation with active cyan glow pill on right edge
 *  - Added extra comfortable width (104px) as requested
 *  - Full route support for all backend capabilities (including audit & reports)
 */

import { NavLink } from "react-router-dom";

function NavIcon({ name }) {
  switch (name) {
    case "overview":
      // Home icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      );
    case "incidents":
      // Pie / Donut chart icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
          <path d="M22 12A10 10 0 0 0 12 2v10z"/>
        </svg>
      );
    case "approvals":
      // 4 Squares Grid icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>
      );
    case "inventory":
      // Connected nodes / branching icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="18" cy="5" r="3"/>
          <circle cx="6" cy="12" r="3"/>
          <circle cx="18" cy="19" r="3"/>
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
        </svg>
      );
    case "production":
      // Delivery truck icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="1" y="3" width="15" height="13" rx="1"/>
          <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
          <circle cx="5.5" cy="18.5" r="2.5"/>
          <circle cx="18.5" cy="18.5" r="2.5"/>
        </svg>
      );
    case "suppliers":
      // Inbox / Tray download icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
          <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
        </svg>
      );
    case "reports":
      // Document / Report icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      );
    case "simulator":
      // Lightning bolt icon
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
      );
    default:
      return null;
  }
}

const NAV_ITEMS = [
  { to: "/",          label: "Home",       end: true, icon: "overview"   },
  { to: "/incidents", label: "Incidents",             icon: "incidents"  },
  { to: "/approvals", label: "Approvals",             icon: "approvals"  },
  { to: "/inventory", label: "Inventory",             icon: "inventory"  },
  { to: "/production",label: "Production",            icon: "production" },
  { to: "/suppliers", label: "Suppliers",             icon: "suppliers"  },
  { to: "/reports",   label: "Reports",               icon: "reports"    },
  { to: "/simulator", label: "Simulator",             icon: "simulator"  },
];

export default function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      {/* Segmented Colorful Logo Matching Screenshot */}
      <NavLink to="/" title="Supply Chain Control Tower" style={{ textDecoration: "none" }}>
        <div className="sidebar-logo">
          <svg viewBox="0 0 40 40" width="34" height="34" fill="none">
            {/* Red top left curve */}
            <path d="M20 6C12.268 6 6 12.268 6 20h7c0-3.866 3.134-7 7-7V6z" fill="#EF4444"/>
            {/* Orange/Yellow bottom left curve */}
            <path d="M6 20c0 7.732 6.268 14 14 14v-7c-3.866 0-7-3.134-7-7H6z" fill="#F59E0B"/>
            {/* Green bottom right curve */}
            <path d="M20 34c7.732 0 14-6.268 14-14h-7c0 3.866-3.134 7-7 7v7z" fill="#10B981"/>
            {/* Cyan/Blue top right curve */}
            <path d="M34 20c0-7.732-6.268-14-14-14v7c3.866 0 7 3.134 7 7h7z" fill="#00C6FF"/>
            {/* Center dot/ring */}
            <circle cx="20" cy="20" r="3.5" fill="#1E2337"/>
          </svg>
        </div>
      </NavLink>

      {/* Navigation Icons */}
      <div className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `sidebar-nav-item${isActive ? " active" : ""}`}
            title={item.label}
          >
            <div className="sidebar-icon-wrap">
              <NavIcon name={item.icon} />
            </div>
            <span className="sidebar-nav-label">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
