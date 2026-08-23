/**
 * src/components/auth/ForgotPasswordPage.jsx
 *
 * Screen for entering email to receive a password reset token.
 * Includes visual demo interceptor to proceed with reset without SMTP setup.
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../../api/auth.js";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [demoToken, setDemoToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError("Please enter your email address.");
      return;
    }

    setLoading(true);
    setError(null);
    setDemoToken(null);

    try {
      const data = await authApi.forgotPassword(email);
      setSuccess(true);
      
      // In the backend, we return reset token in response for demo purposes
      if (data.message && data.message.includes("Reset token:")) {
        const token = data.message.split("Reset token:")[1].trim();
        setDemoToken(token);
      }
    } catch (err) {
      setError(err.message || "Failed to process request. Please try again.");
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
        <h2 className="auth-title">Reset Password</h2>
        <p className="auth-subtitle">We will generate a secure reset token</p>

        {error && <div className="auth-error-box">{error}</div>}

        {!success ? (
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

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Processing..." : "Request Reset Token"}
            </button>
          </form>
        ) : (
          <div className="auth-success-state">
            <div className="success-icon-badge">✓</div>
            <p className="success-msg-heading">Reset Requested</p>
            <p className="success-msg-desc">
              If the email <strong>{email}</strong> is registered, a password reset link has been dispatched.
            </p>

            {demoToken && (
              <div className="demo-token-interceptor">
                <span className="interceptor-title">⚠️ Demo Mode Interceptor</span>
                <p>We intercepted the generated single-use reset token from the server response:</p>
                <code className="demo-token-box">{demoToken}</code>
                <Link
                  to={`/reset-password?token=${demoToken}`}
                  className="btn btn-amber btn-block"
                  style={{ marginTop: "12px", textDecoration: "none" }}
                >
                  Proceed to Reset Password
                </Link>
              </div>
            )}
          </div>
        )}

        <p className="auth-footer-text" style={{ marginTop: "20px" }}>
          Remember your password? <Link to="/login" className="auth-link">Sign in here</Link>
        </p>
      </div>
    </div>
  );
}
