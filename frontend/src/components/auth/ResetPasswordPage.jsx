/**
 * src/components/auth/ResetPasswordPage.jsx
 *
 * Screen for entering the reset token and choosing a new password.
 * Automatically extracts the token from URL query parameters.
 */

import React, { useState, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth.js";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Extract token from query params on mount
  useEffect(() => {
    const urlToken = searchParams.get("token");
    if (urlToken) {
      setToken(urlToken);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("Reset token is required.");
      return;
    }

    if (!newPassword || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (!/[A-Za-z]/.test(newPassword) || !/\d/.test(newPassword)) {
      setError("Password must contain at least one letter and one number.");
      return;
    }

    setLoading(true);

    try {
      await authApi.resetPassword(token, newPassword, confirmPassword);
      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 3000);
    } catch (err) {
      setError(err.message || "Failed to reset password. The token may be expired or already used.");
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
        <h2 className="auth-title">Set New Password</h2>
        <p className="auth-subtitle">Choose a strong, unique password</p>

        {error && <div className="auth-error-box">{error}</div>}

        {!success ? (
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-form-group">
              <label htmlFor="token">Reset Token *</label>
              <input
                id="token"
                type="text"
                placeholder="Enter single-use token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="newPassword">New Password *</label>
              <input
                id="newPassword"
                type="password"
                placeholder="Min. 8 chars, letters & digits"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <input
                id="confirmPassword"
                type="password"
                placeholder="Verify new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Updating password..." : "Reset Password"}
            </button>
          </form>
        ) : (
          <div className="auth-success-state">
            <div className="success-icon-badge">✓</div>
            <p className="success-msg-heading">Password Reset!</p>
            <p className="success-msg-desc">
              Your password has been updated successfully.
            </p>
            <p className="success-redirect-tip">
              Redirecting to sign-in page in a few seconds...
            </p>
            <Link to="/login" className="btn btn-primary btn-block" style={{ marginTop: "16px", textDecoration: "none" }}>
              Sign In Now
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
