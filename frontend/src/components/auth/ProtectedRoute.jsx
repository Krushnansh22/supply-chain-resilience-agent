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
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
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

  if (!isAuthenticated) {
    return <Navigate to="/landing" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to their default dashboard based on their role
    if (user.role === "admin") {
      return <Navigate to="/admin-dashboard" replace />;
    } else if (user.role === "supplier") {
      return <Navigate to="/supplier-dashboard" replace />;
    } else {
      return <Navigate to="/user-dashboard" replace />;
    }
  }

  return children;
}
