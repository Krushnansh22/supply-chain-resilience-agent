import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../../api/client.js";
import { useAuth } from "../../context/AuthContext.jsx";

const QUICK_LINKS = [
  { label: "Incidents", path: "/incidents", icon: "🚨", color: "#EF4444" },
  { label: "Inventory", path: "/inventory", icon: "📦", color: "#2563EB" },
  { label: "Suppliers", path: "/suppliers", icon: "🤝", color: "#10B981" },
  { label: "Approvals", path: "/approvals", icon: "✅", color: "#F59E0B" },
  { label: "Reports",   path: "/reports",   icon: "📊", color: "#8B5CF6" },
  { label: "Simulator", path: "/simulator", icon: "⚡", color: "#06B6D4" },
  { label: "Production",path: "/production",icon: "🏭", color: "#F97316" },
  { label: "Diagnostics",path:"/diagnostics",icon:"🛠️",color: "#64748B" },
  { label: "Activity",  path: "/agent-activity", icon: "🤖", color: "#EC4899" },
];

const DEMO_NOTIFICATIONS = [
  { id: 1, type: "critical", title: "INC-002 — Delivery Breach", body: "Industrial Controller IC-7 critical shortage detected.", time: "2m ago", read: false },
  { id: 2, type: "warning",  title: "INC-011 — Awaiting Approval", body: "Recovery plan ₹93,000 exceeds autonomous threshold.", time: "18m ago", read: false },
  { id: 3, type: "info",     title: "INC-012 — Executing Recovery", body: "Split PO dispatched to Alpha Components & GalaxTech.", time: "1h ago", read: true },
  { id: 4, type: "success",  title: "INC-004 — Resolved", body: "Signal Amplifier SA-5 fully restocked. Production resumed.", time: "3h ago", read: true },
];

export default function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [online, setOnline] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showApps, setShowApps] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState(DEMO_NOTIFICATIONS);
  const notifRef = useRef(null);
  const appsRef  = useRef(null);
  const userRef  = useRef(null);

  // Health-check polling
  useEffect(() => {
    const check = () =>
      apiRequest("/health")
        .then(() => setOnline(true))
        .catch(() => setOnline(false));
    check();
    const interval = setInterval(check, 10_000);
    return () => clearInterval(interval);
  }, []);

  // Click-outside to close dropdowns
  useEffect(() => {
    const handler = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) setShowNotifications(false);
      if (appsRef.current  && !appsRef.current.contains(e.target))  setShowApps(false);
      if (userRef.current  && !userRef.current.contains(e.target))   setShowUserMenu(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const todayStr = new Intl.DateTimeFormat("en-IN", {
    day: "2-digit", month: "2-digit", year: "numeric",
  }).format(new Date()).replace(/\//g, " / ");

  const firstName     = user?.name ? user.name.split(" ")[0] : "User";
  const userInitials  = user?.name ? user.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2) : "US";
  const displayRole   = user?.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User";
  const unreadCount   = notifications.filter(n => !n.read).length;
  const avatarGradient = user?.role === "admin"
    ? "linear-gradient(135deg, #FFB703 0%, #FB8500 100%)"
    : user?.role === "supplier"
      ? "linear-gradient(135deg, #10B981 0%, #059669 100%)"
      : "linear-gradient(135deg, #2563EB 0%, #00C6FF 100%)";

  const markAllRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));

  const notifTypeStyle = {
    critical: { border: "#EF4444", icon: "🔴" },
    warning:  { border: "#F59E0B", icon: "🟡" },
    info:     { border: "#2563EB", icon: "🔵" },
    success:  { border: "#10B981", icon: "🟢" },
  };

  return (
    <header style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      marginBottom: "24px", flexWrap: "wrap", gap: "16px", position: "relative",
    }}>
      {/* ── Left: Greeting + Date ── */}
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "26px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em", margin: 0, lineHeight: 1.2 }}>
            Hello, {firstName} 👋
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "13px", marginTop: "3px" }}>
            {online === true ? (
              <span>
                <span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", background: "#10B981", marginRight: 6, verticalAlign: "middle" }} />
                All systems operational
              </span>
            ) : online === false ? (
              <span style={{ color: "#EF4444" }}>⚠️ Backend offline — retrying...</span>
            ) : "Connecting to backend..."}
          </p>
        </div>

        {/* Date Pill */}
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "8px",
          background: "#FFFFFF", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)", padding: "8px 16px",
          fontFamily: "var(--font-mono)", fontSize: "13px", fontWeight: 600,
          color: "var(--text-secondary)", boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>{todayStr}</span>
        </div>
      </div>

      {/* ── Right: Action Buttons + User ── */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>

        {/* ── Notification Bell ── */}
        <div ref={notifRef} style={{ position: "relative" }}>
          <button
            onClick={() => { setShowNotifications(v => !v); setShowApps(false); setShowUserMenu(false); }}
            style={{
              width: 40, height: 40, borderRadius: 12,
              background: showNotifications ? "rgba(37,99,235,0.08)" : "#FFFFFF",
              border: `1px solid ${showNotifications ? "var(--primary)" : "var(--border-subtle)"}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: showNotifications ? "var(--primary)" : "var(--text-secondary)",
              cursor: "pointer", transition: "all 0.15s",
              boxShadow: "0 1px 3px rgba(0,0,0,0.04)", position: "relative",
            }}
            title={`Notifications (${unreadCount} unread)`}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            {unreadCount > 0 && (
              <span style={{
                position: "absolute", top: 6, right: 6, width: 8, height: 8,
                background: "#EF4444", borderRadius: "50%", border: "1.5px solid #FFFFFF",
              }} />
            )}
          </button>

          {showNotifications && (
            <div style={{
              position: "absolute", top: "calc(100% + 10px)", right: 0,
              width: 360, background: "#FFFFFF", borderRadius: 16,
              border: "1px solid var(--border-subtle)", boxShadow: "0 20px 60px rgba(15,23,42,0.15)",
              zIndex: 1000, overflow: "hidden",
            }}>
              <div style={{ padding: "16px 20px 12px", borderBottom: "1px solid var(--border-subtle)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: 15, fontWeight: 700 }}>Notifications</h4>
                  <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--text-muted)" }}>{unreadCount} unread alerts</p>
                </div>
                {unreadCount > 0 && (
                  <button onClick={markAllRead} style={{ background: "none", border: "none", color: "var(--primary)", fontSize: 12, fontWeight: 600, cursor: "pointer", padding: "4px 8px" }}>
                    Mark all read
                  </button>
                )}
              </div>
              <div style={{ maxHeight: 320, overflowY: "auto" }}>
                {notifications.map(notif => (
                  <div key={notif.id} style={{
                    padding: "14px 20px", borderBottom: "1px solid var(--border-subtle)",
                    background: notif.read ? "transparent" : "rgba(37,99,235,0.03)",
                    cursor: "pointer", transition: "background 0.15s",
                    borderLeft: `3px solid ${notifTypeStyle[notif.type]?.border || "#E2E8F0"}`,
                  }}
                    onClick={() => setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, read: true } : n))}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 }}>
                      <span style={{ fontWeight: notif.read ? 500 : 700, fontSize: 13, color: "var(--text-primary)" }}>
                        {notifTypeStyle[notif.type]?.icon} {notif.title}
                      </span>
                      <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 8, whiteSpace: "nowrap" }}>{notif.time}</span>
                    </div>
                    <p style={{ fontSize: 12, color: "var(--text-secondary)", margin: 0, lineHeight: 1.4 }}>{notif.body}</p>
                  </div>
                ))}
              </div>
              <div style={{ padding: "12px 20px", textAlign: "center" }}>
                <button
                  onClick={() => { navigate("/incidents"); setShowNotifications(false); }}
                  style={{ background: "none", border: "none", color: "var(--primary)", fontSize: 13, fontWeight: 600, cursor: "pointer" }}
                >
                  View all incidents →
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ── App Switcher ── */}
        <div ref={appsRef} style={{ position: "relative" }}>
          <button
            onClick={() => { setShowApps(v => !v); setShowNotifications(false); setShowUserMenu(false); }}
            style={{
              width: 40, height: 40, borderRadius: 12,
              background: showApps ? "rgba(37,99,235,0.08)" : "#FFFFFF",
              border: `1px solid ${showApps ? "var(--primary)" : "var(--border-subtle)"}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: showApps ? "var(--primary)" : "var(--text-secondary)",
              cursor: "pointer", transition: "all 0.15s",
              boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
            }}
            title="Quick Navigation"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="4.5" cy="4.5" r="2"/><circle cx="12" cy="4.5" r="2"/><circle cx="19.5" cy="4.5" r="2"/>
              <circle cx="4.5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19.5" cy="12" r="2"/>
              <circle cx="4.5" cy="19.5" r="2"/><circle cx="12" cy="19.5" r="2"/><circle cx="19.5" cy="19.5" r="2"/>
            </svg>
          </button>

          {showApps && (
            <div style={{
              position: "absolute", top: "calc(100% + 10px)", right: 0,
              width: 280, background: "#FFFFFF", borderRadius: 16,
              border: "1px solid var(--border-subtle)", boxShadow: "0 20px 60px rgba(15,23,42,0.15)",
              zIndex: 1000, padding: "16px",
            }}>
              <p style={{ margin: "0 0 12px", fontSize: 12, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Quick Access
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px" }}>
                {QUICK_LINKS.map(link => (
                  <button
                    key={link.path}
                    onClick={() => { navigate(link.path); setShowApps(false); }}
                    style={{
                      display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
                      padding: "12px 8px", borderRadius: 10, border: "1px solid var(--border-subtle)",
                      background: "#F8FAFC", cursor: "pointer", transition: "all 0.15s",
                      fontSize: 11, fontWeight: 600, color: "var(--text-secondary)",
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = link.color + "12"; e.currentTarget.style.borderColor = link.color + "40"; e.currentTarget.style.color = link.color; }}
                    onMouseLeave={e => { e.currentTarget.style.background = "#F8FAFC"; e.currentTarget.style.borderColor = "var(--border-subtle)"; e.currentTarget.style.color = "var(--text-secondary)"; }}
                  >
                    <span style={{ fontSize: 20 }}>{link.icon}</span>
                    {link.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── User Profile ── */}
        <div ref={userRef} style={{ position: "relative" }}>
          <button
            onClick={() => { setShowUserMenu(v => !v); setShowNotifications(false); setShowApps(false); }}
            style={{
              display: "flex", alignItems: "center", gap: "10px",
              padding: "6px 14px 6px 6px",
              background: showUserMenu ? "rgba(37,99,235,0.06)" : "#FFFFFF",
              border: `1px solid ${showUserMenu ? "var(--primary)" : "var(--border-subtle)"}`,
              borderRadius: 12, cursor: "pointer", transition: "all 0.15s",
              boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
            }}
          >
            <div style={{
              width: 32, height: 32, borderRadius: "50%", background: avatarGradient,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#FFFFFF", fontWeight: 700, fontSize: 12, flexShrink: 0,
            }}>
              {userInitials}
            </div>
            <div style={{ textAlign: "left", minWidth: 90 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)", lineHeight: 1.2 }}>{user?.name || "Loading..."}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{
                  background: user?.role === "admin" ? "#FEF3C7" : user?.role === "supplier" ? "#D1FAE5" : "#DBEAFE",
                  color: user?.role === "admin" ? "#D97706" : user?.role === "supplier" ? "#059669" : "#2563EB",
                  padding: "1px 6px", borderRadius: 4, fontSize: 10, fontWeight: 700,
                }}>
                  {displayRole}
                </span>
              </div>
            </div>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>

          {showUserMenu && (
            <div style={{
              position: "absolute", top: "calc(100% + 10px)", right: 0,
              width: 220, background: "#FFFFFF", borderRadius: 14,
              border: "1px solid var(--border-subtle)", boxShadow: "0 20px 60px rgba(15,23,42,0.15)",
              zIndex: 1000, overflow: "hidden",
            }}>
              <div style={{ padding: "16px", borderBottom: "1px solid var(--border-subtle)", background: "linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)" }}>
                <div style={{ width: 44, height: 44, borderRadius: "50%", background: avatarGradient, display: "flex", alignItems: "center", justifyContent: "center", color: "#FFF", fontWeight: 700, fontSize: 16, marginBottom: 8 }}>
                  {userInitials}
                </div>
                <div style={{ fontWeight: 700, fontSize: 14, color: "var(--text-primary)" }}>{user?.name}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{user?.email}</div>
              </div>
              <div style={{ padding: "8px" }}>
                {[
                  { label: "My Dashboard", icon: "🏠", action: () => { navigate("/"); setShowUserMenu(false); } },
                  { label: "System Status", icon: online ? "🟢" : "🔴", action: () => { navigate("/diagnostics"); setShowUserMenu(false); } },
                ].map(item => (
                  <button
                    key={item.label}
                    onClick={item.action}
                    style={{
                      width: "100%", display: "flex", alignItems: "center", gap: 10,
                      padding: "9px 12px", borderRadius: 8, border: "none",
                      background: "none", cursor: "pointer", fontSize: 13,
                      color: "var(--text-primary)", fontWeight: 500, textAlign: "left",
                      transition: "background 0.12s",
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = "#F1F5F9"}
                    onMouseLeave={e => e.currentTarget.style.background = "none"}
                  >
                    <span>{item.icon}</span>{item.label}
                  </button>
                ))}
                <div style={{ height: 1, background: "var(--border-subtle)", margin: "6px 4px" }} />
                <button
                  onClick={() => { logout(); setShowUserMenu(false); }}
                  style={{
                    width: "100%", display: "flex", alignItems: "center", gap: 10,
                    padding: "9px 12px", borderRadius: 8, border: "none",
                    background: "none", cursor: "pointer", fontSize: 13,
                    color: "#EF4444", fontWeight: 600, textAlign: "left",
                    transition: "background 0.12s",
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = "#FEF2F2"}
                  onMouseLeave={e => e.currentTarget.style.background = "none"}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                  </svg>
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}