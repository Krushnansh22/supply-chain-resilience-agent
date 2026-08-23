/**
 * src/components/layout/Sidebar.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Dynamic Sidebar rendering based on authenticated User role.
 * Includes a Logout button at the bottom.
 */

import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

function NavIcon({ name }) {
  switch (name) {
    case "overview":
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      );
    case "incidents":
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
          <path d="M22 12A10 10 0 0 0 12 2v10z"/>
        </svg>
      );
    case "approvals":
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>
      );
    case "inventory":
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
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="1" y="3" width="15" height="13" rx="1"/>
          <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
          <circle cx="5.5" cy="18.5" r="2.5"/>
          <circle cx="18.5" cy="18.5" r="2.5"/>
        </svg>
      );
    case "suppliers":
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
          <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
        </svg>
      );
    case "reports":
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
      return (
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
      );
    default:
      return null;
  }
}

export default function Sidebar() {
  const { user, logout } = useAuth();

  // Define navigation items dynamically based on the role
  const getNavItems = () => {
    if (!user) return [];

    if (user.role === "admin") {
      return [
        { to: "/",          label: "Home",       end: true, icon: "overview"   },
        { to: "/incidents", label: "Incidents",             icon: "incidents"  },
        { to: "/approvals", label: "Approvals",             icon: "approvals"  },
        { to: "/inventory", label: "Inventory",             icon: "inventory"  },
        { to: "/production",label: "Production",            icon: "production" },
        { to: "/suppliers", label: "Suppliers",             icon: "suppliers"  },
        { to: "/reports",   label: "Reports",               icon: "reports"    },
        { to: "/simulator", label: "Simulator",             icon: "simulator"  },
      ];
    }

    if (user.role === "supplier") {
      return [
        { to: "/",          label: "Home",       end: true, icon: "overview"   },
        { to: "/inventory", label: "Inventory",             icon: "inventory"  },
      ];
    }

    if (user.role === "user") {
      return [
        { to: "/",          label: "Home",       end: true, icon: "overview"   },
        { to: "/production",label: "Production",            icon: "production" },
      ];
    }

    return [];
  };

  const navItems = getNavItems();

  return (
    <nav className="sidebar" aria-label="Main navigation">
      {/* Segmented Colorful Logo */}
      <NavLink to="/" title="Supply Chain Control Tower" style={{ textDecoration: "none" }}>
        <div className="sidebar-logo">
          <svg viewBox="0 0 40 40" width="34" height="34" fill="none">
            <path d="M20 6C12.268 6 6 12.268 6 20h7c0-3.866 3.134-7 7-7V6z" fill="#EF4444"/>
            <path d="M6 20c0 7.732 6.268 14 14 14v-7c-3.866 0-7-3.134-7-7H6z" fill="#F59E0B"/>
            <path d="M20 34c7.732 0 14-6.268 14-14h-7c0 3.866-3.134 7-7 7v7z" fill="#10B981"/>
            <path d="M34 20c0-7.732-6.268-14-14-14v7c3.866 0 7 3.134 7 7h7z" fill="#00C6FF"/>
            <circle cx="20" cy="20" r="3.5" fill="#1E2337"/>
          </svg>
        </div>
      </NavLink>

      {/* Navigation Icons */}
      <div className="sidebar-nav" style={{ flexGrow: 1 }}>
        {navItems.map((item) => (
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

      {/* Logout button at the bottom */}
      <div className="sidebar-nav" style={{ marginTop: "auto" }}>
        <button
          onClick={logout}
          className="sidebar-nav-item"
          title="Logout"
          style={{
            background: "none",
            border: "none",
            width: "100%",
            color: "#8E9BAE"
          }}
        >
          <div className="sidebar-icon-wrap">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </div>
          <span className="sidebar-nav-label">Logout</span>
        </button>
      </div>
    </nav>
  );
}
