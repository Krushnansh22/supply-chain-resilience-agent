/**
 * src/components/auth/ProtectedRoute.jsx
 *
 * Protects frontend routes by checking authentication state and user roles.
 * Redirects to landing if unauthenticated, or to appropriate dashboard if unauthorized.
 */

import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();

  // Get active user from state or synchronous localStorage fallback
  let activeUser = user;
  if (!activeUser) {
    try {
      const stored = localStorage.getItem("scda_auth_user");
      if (stored) activeUser = JSON.parse(stored);
    } catch {
      activeUser = null;
    }
  }

  // Only block on loading spinner if there's no user in state OR localStorage while loading
  if (loading && !activeUser) {
    return (
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "80vh",
        color: "var(--text-secondary)",
        fontFamily: "var(--font-display)",
        fontWeight: "600"
      }}>
        Loading session...
      </div>
    );
  }

  if (!activeUser) {
    return <Navigate to="/landing" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(activeUser.role)) {
    // Redirect to their default dashboard based on their role
    if (activeUser.role === "admin") {
      return <Navigate to="/" replace />;
    } else if (activeUser.role === "supplier") {
      return <Navigate to="/supplier-dashboard" replace />;
    } else {
      return <Navigate to="/user-dashboard" replace />;
    }
  }

  return children;
}
