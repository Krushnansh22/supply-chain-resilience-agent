/**
 * src/components/auth/LoginPage.jsx
 * High-Aesthetic Login & Sign-Up Portal with 1-Click Demo Accounts
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, signup, quickLogin, usersList, warehousesList, loading } = useAuth();

  const [tab, setTab] = useState("login"); // "login" | "signup"
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Login Form
  const [email, setEmail] = useState("alex.whitfield@atlas-scm.io");
  const [password, setPassword] = useState("Admin@1234");

  // Signup Form
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupRole, setSignupRole] = useState("WAREHOUSE_MANAGER");
  const [signupWarehouse, setSignupWarehouse] = useState("Warehouse-A");

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Invalid login credentials.");
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await signup({
        name: signupName,
        email: signupEmail,
        password: signupPassword,
        role: signupRole,
        assigned_warehouse: signupRole === "ADMIN" ? "ALL" : signupWarehouse,
      });
      setSuccessMsg("Account created successfully! Redirecting...");
      setTimeout(() => navigate("/"), 1000);
    } catch (err) {
      setError(err.message || "Failed to create account.");
    }
  };

  const handleQuickLogin = (demoUser) => {
    quickLogin(demoUser);
    navigate("/");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "radial-gradient(ellipse at top, #0A192F 0%, #030712 100%)",
        padding: 24,
        fontFamily: "Space Grotesk, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 960,
          display: "grid",
          gridTemplateColumns: "1.1fr 1fr",
          background: "rgba(15, 23, 42, 0.8)",
          backdropFilter: "blur(16px)",
          border: "1px solid rgba(35, 184, 201, 0.25)",
          borderRadius: 16,
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 30px rgba(35, 184, 201, 0.15)",
          overflow: "hidden",
        }}
      >
        {/* Left Side: Brand & Hero */}
        <div
          style={{
            padding: 40,
            background: "linear-gradient(145deg, rgba(7, 63, 70, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%)",
            borderRight: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
              <div
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 10,
                  background: "linear-gradient(135deg, #073F46 0%, #23B8C9 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 20,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  boxShadow: "0 0 16px rgba(35, 184, 201, 0.5)",
                }}
              >
                SC
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#FFFFFF", letterSpacing: "0.5px" }}>
                  ATLAS CONTROL TOWER
                </h2>
                <span style={{ fontSize: 11, color: "#23B8C9", fontWeight: 600, letterSpacing: "1px" }}>
                  RESILIENCE & RE-ROUTING AGENT
                </span>
              </div>
            </div>

            <h1 style={{ fontSize: 26, fontWeight: 800, color: "#FFFFFF", lineHeight: 1.3, marginBottom: 14 }}>
              Autonomous Multi-Facility Operations & Supply Chain Defense
            </h1>

            <p style={{ fontSize: 13.5, color: "#94A3B8", lineHeight: 1.6, marginBottom: 28 }}>
              Role-Based Access Control (RBAC) isolating telemetry, stock levels, and incident triage across discrete warehouse nodes.
            </p>

            {/* Quick Demo Login Chips */}
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#23B8C9", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 10 }}>
                ⚡ 1-Click Fast Track Login:
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {usersList.map((u) => {
                  const isAdm = u.role === "ADMIN";
                  return (
                    <button
                      key={u.user_id}
                      type="button"
                      onClick={() => handleQuickLogin(u)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "8px 12px",
                        borderRadius: 8,
                        background: isAdm ? "rgba(35, 184, 201, 0.12)" : "rgba(245, 158, 11, 0.08)",
                        border: isAdm ? "1px solid rgba(35, 184, 201, 0.35)" : "1px solid rgba(245, 158, 11, 0.25)",
                        color: "#FFFFFF",
                        cursor: "pointer",
                        fontSize: 12,
                        textAlign: "left",
                        transition: "all 0.15s ease",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.transform = "translateX(4px)")}
                      onMouseLeave={(e) => (e.currentTarget.style.transform = "translateX(0px)")}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span>{isAdm ? "👑" : "🏭"}</span>
                        <div>
                          <strong style={{ color: isAdm ? "#23B8C9" : "#F59E0B" }}>{u.name}</strong>
                          <div style={{ fontSize: 10, color: "#94A3B8" }}>{u.email}</div>
                        </div>
                      </div>
                      <span style={{ fontSize: 10, fontWeight: 700, color: isAdm ? "#23B8C9" : "#F59E0B" }}>
                        {isAdm ? "GLOBAL" : u.assigned_warehouse} →
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div style={{ marginTop: 24, fontSize: 11, color: "#64748B" }}>
            HOP 2026 Hackathon // Team TRACE // Enterprise Resilience Engine
          </div>
        </div>

        {/* Right Side: Auth Forms */}
        <div style={{ padding: 40, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          
          {/* Tab Switcher */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              background: "rgba(0, 0, 0, 0.3)",
              borderRadius: 8,
              padding: 4,
              marginBottom: 24,
              border: "1px solid rgba(255, 255, 255, 0.08)",
            }}
          >
            <button
              type="button"
              onClick={() => { setTab("login"); setError(null); }}
              style={{
                padding: "8px 0",
                borderRadius: 6,
                border: "none",
                fontWeight: 700,
                fontSize: 13,
                cursor: "pointer",
                background: tab === "login" ? "linear-gradient(135deg, #073F46, #07535A)" : "transparent",
                color: tab === "login" ? "#23B8C9" : "#94A3B8",
                boxShadow: tab === "login" ? "0 2px 8px rgba(0,0,0,0.3)" : "none",
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setTab("signup"); setError(null); }}
              style={{
                padding: "8px 0",
                borderRadius: 6,
                border: "none",
                fontWeight: 700,
                fontSize: 13,
                cursor: "pointer",
                background: tab === "signup" ? "linear-gradient(135deg, #073F46, #07535A)" : "transparent",
                color: tab === "signup" ? "#23B8C9" : "#94A3B8",
                boxShadow: tab === "signup" ? "0 2px 8px rgba(0,0,0,0.3)" : "none",
              }}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div
              style={{
                background: "rgba(239, 68, 68, 0.12)",
                border: "1px solid rgba(239, 68, 68, 0.4)",
                color: "#EF4444",
                padding: "10px 14px",
                borderRadius: 8,
                fontSize: 12.5,
                marginBottom: 18,
              }}
            >
              ⚠️ {error}
            </div>
          )}

          {successMsg && (
            <div
              style={{
                background: "rgba(16, 185, 129, 0.12)",
                border: "1px solid rgba(16, 185, 129, 0.4)",
                color: "#10B981",
                padding: "10px 14px",
                borderRadius: 8,
                fontSize: 12.5,
                marginBottom: 18,
              }}
            >
              ✓ {successMsg}
            </div>
          )}

          {tab === "login" ? (
            /* ─── Sign In Form ─── */
            <form onSubmit={handleLoginSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                  Email or User ID
                </label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.whitfield@atlas-scm.io"
                  required
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: 8,
                    background: "#0B132B",
                    color: "#FFFFFF",
                    border: "1px solid #1E293B",
                    fontSize: 13.5,
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ marginBottom: 24 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: 8,
                    background: "#0B132B",
                    color: "#FFFFFF",
                    border: "1px solid #1E293B",
                    fontSize: 13.5,
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "12px 0",
                  borderRadius: 8,
                  background: "linear-gradient(135deg, #07535A 0%, #23B8C9 100%)",
                  color: "#FFFFFF",
                  border: "none",
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: loading ? "not-allowed" : "pointer",
                  boxShadow: "0 4px 14px rgba(35, 184, 201, 0.4)",
                  transition: "opacity 0.2s ease",
                }}
              >
                {loading ? "Authenticating…" : "Sign In to Control Tower →"}
              </button>
            </form>
          ) : (
            /* ─── Sign Up Form ─── */
            <form onSubmit={handleSignupSubmit}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                  Full Name *
                </label>
                <input
                  type="text"
                  value={signupName}
                  onChange={(e) => setSignupName(e.target.value)}
                  placeholder="e.g. Jordan Mitchell"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    borderRadius: 8,
                    background: "#0B132B",
                    color: "#FFFFFF",
                    border: "1px solid #1E293B",
                    fontSize: 13,
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                  Corporate Email *
                </label>
                <input
                  type="email"
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  placeholder="jordan.mitchell@atlas-scm.io"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    borderRadius: 8,
                    background: "#0B132B",
                    color: "#FFFFFF",
                    border: "1px solid #1E293B",
                    fontSize: 13,
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                  Password *
                </label>
                <input
                  type="password"
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  placeholder="Create strong password"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px",
                    borderRadius: 8,
                    background: "#0B132B",
                    color: "#FFFFFF",
                    border: "1px solid #1E293B",
                    fontSize: 13,
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                <div>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                    User Role *
                  </label>
                  <select
                    value={signupRole}
                    onChange={(e) => setSignupRole(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "9px 10px",
                      borderRadius: 8,
                      background: "#0B132B",
                      color: "#FFFFFF",
                      border: "1px solid #1E293B",
                      fontSize: 12.5,
                      boxSizing: "border-box",
                    }}
                  >
                    <option value="WAREHOUSE_MANAGER">🏭 Warehouse Manager</option>
                    <option value="ADMIN">👑 Global Admin</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94A3B8", marginBottom: 6 }}>
                    Assigned Facility *
                  </label>
                  <select
                    value={signupWarehouse}
                    onChange={(e) => setSignupWarehouse(e.target.value)}
                    disabled={signupRole === "ADMIN"}
                    style={{
                      width: "100%",
                      padding: "9px 10px",
                      borderRadius: 8,
                      background: signupRole === "ADMIN" ? "rgba(0,0,0,0.3)" : "#0B132B",
                      color: signupRole === "ADMIN" ? "#64748B" : "#FFFFFF",
                      border: "1px solid #1E293B",
                      fontSize: 12.5,
                      boxSizing: "border-box",
                    }}
                  >
                    {warehousesList.map((wh) => (
                      <option key={wh.warehouse_id} value={wh.warehouse_id}>
                        {wh.warehouse_id}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "12px 0",
                  borderRadius: 8,
                  background: "linear-gradient(135deg, #07535A 0%, #23B8C9 100%)",
                  color: "#FFFFFF",
                  border: "none",
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: loading ? "not-allowed" : "pointer",
                  boxShadow: "0 4px 14px rgba(35, 184, 201, 0.4)",
                }}
              >
                {loading ? "Creating Account…" : "Register & Open Portal →"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
