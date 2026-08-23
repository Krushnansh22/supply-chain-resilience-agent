/**
 * src/components/auth/LoginPage.jsx
 *
 * Polished, responsive login form.
 * Supports show/hide password, loading state, error display, and redirect.
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const loggedUser = await login(email, password);
      // Success redirection based on role
      if (loggedUser.role === "admin") {
        navigate("/");
      } else if (loggedUser.role === "supplier") {
        navigate("/supplier-dashboard");
      } else {
        navigate("/user-dashboard");
      }
    } catch (err) {
      setError(err.message || "Failed to log in. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        <div className="auth-card-logo">
          <svg viewBox="0 0 40 40" width="44" height="44" fill="none">
            <path d="M20 6C12.268 6 6 12.268 6 20h7c0-3.866 3.134-7 7-7V6z" fill="#EF4444"/>
            <path d="M6 20c0 7.732 6.268 14 14 14v-7c-3.866 0-7-3.134-7-7H6z" fill="#F59E0B"/>
            <path d="M20 34c7.732 0 14-6.268 14-14h-7c0 3.866-3.134 7-7 7v7z" fill="#10B981"/>
            <path d="M34 20c0-7.732-6.268-14-14-14v7c3.866 0 7 3.134 7 7h7z" fill="#00C6FF"/>
          </svg>
        </div>
        <h2 className="auth-title">Sign In</h2>
        <p className="auth-subtitle">Access your Control Tower dashboard</p>

        {error && <div className="auth-error-box">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="e.g. user@scda.io"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="auth-form-group">
            <div className="auth-label-row">
              <label htmlFor="password">Password</label>
              <Link to="/forgot-password" className="auth-link-sm">Forgot password?</Link>
            </div>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
              />
              <button
                type="button"
                className="btn-show-hide"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <p className="auth-footer-text">
          Don't have an account? <Link to="/register" className="auth-link">Register here</Link>
        </p>
        
        <p className="auth-footer-text-sm" style={{ marginTop: "12px", fontSize: "11px", color: "var(--text-muted)" }}>
          Demo: admin@scda.io (Admin) | supplier@alpha-components.in (Supplier) | user@scda.io (User)
          <br/>Password: Admin@1234 / Supplier@1234 / User@1234
        </p>
      </div>
    </div>
  );
}
