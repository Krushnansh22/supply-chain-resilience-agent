/**
 * src/components/auth/LandingPage.jsx
 *
 * Public landing page explaining the Supply Chain Control Tower platform
 * with clear calls to action (Login, Register).
 */

import React from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function LandingPage() {
  const { user } = useAuth();

  // Check stored user as fallback
  let activeUser = user;
  if (!activeUser) {
    try {
      const stored = localStorage.getItem("scda_auth_user");
      if (stored) activeUser = JSON.parse(stored);
    } catch {
      activeUser = null;
    }
  }

  // If already logged in, redirect to correct dashboard
  if (activeUser) {
    if (activeUser.role === "admin") return <Navigate to="/" replace />;
    if (activeUser.role === "supplier") return <Navigate to="/supplier-dashboard" replace />;
    return <Navigate to="/user-dashboard" replace />;
  }

  return (
    <div className="landing-container">
      {/* Header */}
      <header className="landing-header">
        <div className="landing-logo">
          <svg viewBox="0 0 40 40" width="34" height="34" fill="none">
            <path d="M20 6C12.268 6 6 12.268 6 20h7c0-3.866 3.134-7 7-7V6z" fill="#EF4444"/>
            <path d="M6 20c0 7.732 6.268 14 14 14v-7c-3.866 0-7-3.134-7-7H6z" fill="#F59E0B"/>
            <path d="M20 34c7.732 0 14-6.268 14-14h-7c0 3.866-3.134 7-7 7v7z" fill="#10B981"/>
            <path d="M34 20c0-7.732-6.268-14-14-14v7c3.866 0 7 3.134 7 7h7z" fill="#00C6FF"/>
          </svg>
          <span className="landing-logo-text">SCDA Tower</span>
        </div>
        <div className="landing-nav-btns">
          <Link to="/login" className="btn btn-ghost">Sign In</Link>
          <Link to="/register" className="btn btn-primary">Get Started</Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <h1 className="hero-title">
          Autonomous Resilience for <br />
          <span className="text-gradient">Modern Supply Chains</span>
        </h1>
        <p className="hero-subtitle">
          SCDA Control Tower detects disruptions, auto-requests quotes, runs multi-modal
          re-routing analysis, and executes recovery plans in real-time.
        </p>
        <div className="hero-ctas">
          <Link to="/register" className="btn btn-primary btn-lg">Create Free Account</Link>
          <Link to="/login" className="btn btn-ghost btn-lg">Access Dashboard</Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="landing-features">
        <h2 className="section-title">Enabling End-to-End Resilience</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon blue">🔍</div>
            <h3>Disruption Monitor</h3>
            <p>Monitors ERP purchase orders and transit schedules to instantly catch delayed components.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon green">🤖</div>
            <h3>Autonomous Triage</h3>
            <p>LLM-powered agents source alternatives, draft RFQs, and run deterministic recovery calculations.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon purple">⚡</div>
            <h3>Smart RBAC Routing</h3>
            <p>Admin control, supplier inventory updates, and procurement officer summary dashboards.</p>
          </div>
        </div>
      </section>

      {/* Info block */}
      <section className="landing-info-banner">
        <div className="info-content">
          <h2>Continuous Operational Integrity</h2>
          <p>
            By integrating deterministic business rules with state-of-the-art LLM reasoning,
            the Control Tower keeps lines running with up to ₹50,000 autonomous approval limit.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>&copy; 2026 Supply Chain Disruption Control Agent (SCDA). All rights reserved.</p>
      </footer>
    </div>
  );
}
