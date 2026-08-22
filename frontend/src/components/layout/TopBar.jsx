/**
 * src/components/layout/TopBar.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Exact match to the reference dashboard screenshot:
 *  - Left: "Hello, Ducky" + Date picker pill [ 📅 26 / 12 / 2023 ]
 *  - Right:
 *      - Notification Bell 🔔 (with red badge)
 *      - Messages 💬
 *      - Apps Grid ⠶
 *      - User Profile [ Avatar + "Ducky Lee" + "Admin #1234" ] + live status
 */

import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client.js";

export default function TopBar() {
  const [online, setOnline] = useState(null);

  useEffect(() => {
    const check = () =>
      apiRequest("/health")
        .then(() => setOnline(true))
        .catch(() => setOnline(false));
    check();
    const interval = setInterval(check, 10_000);
    return () => clearInterval(interval);
  }, []);

  const todayStr = new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date()).replace(/\//g, " / ");

  return (
    <header className="top-header">
      {/* Left side: Greeting + Date Pill */}
      <div className="header-left">
        <h1 className="greeting-text">Hello, Ducky</h1>
        <div className="date-pill">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>{todayStr || "26 / 12 / 2023"}</span>
        </div>
      </div>

      {/* Right side: Action icons + User Profile */}
      <div className="header-right">
        {/* Notification Bell */}
        <button className="header-icon-btn" aria-label="Notifications" title="Notifications">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span className="header-badge-dot" />
        </button>

        {/* Message / Chat */}
        <button className="header-icon-btn" aria-label="Messages" title="Messages">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </button>

        {/* Apps Grid */}
        <button className="header-icon-btn" aria-label="Apps" title="Applications">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="6" cy="6" r="1.5" fill="currentColor"/>
            <circle cx="12" cy="6" r="1.5" fill="currentColor"/>
            <circle cx="18" cy="6" r="1.5" fill="currentColor"/>
            <circle cx="6" cy="12" r="1.5" fill="currentColor"/>
            <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
            <circle cx="18" cy="12" r="1.5" fill="currentColor"/>
            <circle cx="6" cy="18" r="1.5" fill="currentColor"/>
            <circle cx="12" cy="18" r="1.5" fill="currentColor"/>
            <circle cx="18" cy="18" r="1.5" fill="currentColor"/>
          </svg>
        </button>

        {/* User Profile Card */}
        <div className="user-profile-badge">
          {/* Avatar */}
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #FFB703 0%, #FB8500 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              fontWeight: "700",
              fontSize: 13,
              boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
              overflow: "hidden"
            }}
          >
            <img
              src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
              alt="Ducky Lee"
              className="user-avatar-img"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
            DL
          </div>
          <div className="user-info">
            <span className="user-name">Ducky Lee</span>
            <span className="user-role">
              Admin #1234 · {online === null ? "..." : online ? "Live" : "Offline"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}