/**
 * src/components/auth/RegisterPage.jsx
 *
 * Polished, responsive registration form.
 * Supports choosing between User and Supplier, matching validation, and redirects.
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("user"); // default to regular user
  
  // Supplier fields
  const [companyName, setCompanyName] = useState("");
  const [contactPhone, setContactPhone] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Frontend validations
    if (!name || !email || !password || !confirmPassword) {
      setError("Please fill in all required fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setError("Password must contain at least one letter and one number.");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        name,
        email,
        password,
        role,
        ...(role === "supplier" ? { company_name: companyName, contact_phone: contactPhone } : {})
      };

      const newUser = await register(payload);

      // Redirect to correct dashboard
      if (newUser.role === "admin") {
        navigate("/");
      } else if (newUser.role === "supplier") {
        navigate("/supplier-dashboard");
      } else {
        navigate("/user-dashboard");
      }
    } catch (err) {
      setError(err.message || "Failed to register. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card" style={{ maxWidth: "480px" }}>
        <div className="auth-card-logo">
          <svg viewBox="0 0 40 40" width="44" height="44" fill="none">
            <path d="M20 6C12.268 6 6 12.268 6 20h7c0-3.866 3.134-7 7-7V6z" fill="#EF4444"/>
            <path d="M6 20c0 7.732 6.268 14 14 14v-7c-3.866 0-7-3.134-7-7H6z" fill="#F59E0B"/>
            <path d="M20 34c7.732 0 14-6.268 14-14h-7c0 3.866-3.134 7-7 7v7z" fill="#10B981"/>
            <path d="M34 20c0-7.732-6.268-14-14-14v7c3.866 0 7 3.134 7 7h7z" fill="#00C6FF"/>
          </svg>
        </div>
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-subtitle">Join the Supply Chain Control Tower network</p>

        {error && <div className="auth-error-box">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form-group">
            <label htmlFor="name">Full Name *</label>
            <input
              id="name"
              type="text"
              placeholder="e.g. John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="auth-form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              id="email"
              type="email"
              placeholder="e.g. john@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="auth-form-group">
            <label>I want to register as a: *</label>
            <div className="role-selector-row">
              <label className={`role-option-label ${role === "user" ? "active" : ""}`}>
                <input
                  type="radio"
                  name="role"
                  value="user"
                  checked={role === "user"}
                  onChange={() => setRole("user")}
                  disabled={loading}
                />
                Procurement User
              </label>
              <label className={`role-option-label ${role === "supplier" ? "active" : ""}`}>
                <input
                  type="radio"
                  name="role"
                  value="supplier"
                  checked={role === "supplier"}
                  onChange={() => setRole("supplier")}
                  disabled={loading}
                />
                Supplier Vendor
              </label>
            </div>
          </div>

          {role === "supplier" && (
            <div className="supplier-fields-panel">
              <div className="auth-form-group">
                <label htmlFor="companyName">Company Name *</label>
                <input
                  id="companyName"
                  type="text"
                  placeholder="e.g. Alpha Precision Inc"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  disabled={loading}
                  required={role === "supplier"}
                />
              </div>
              <div className="auth-form-group">
                <label htmlFor="contactPhone">Contact Phone</label>
                <input
                  id="contactPhone"
                  type="text"
                  placeholder="e.g. +1 (555) 019-2834"
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>
          )}

          <div className="auth-form-group">
            <label htmlFor="password">Password *</label>
            <input
              id="password"
              type="password"
              placeholder="Min. 8 chars, letters & digits"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="auth-form-group">
            <label htmlFor="confirmPassword">Confirm Password *</label>
            <input
              id="confirmPassword"
              type="password"
              placeholder="Verify password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Registering account..." : "Register Now"}
          </button>
        </form>

        <p className="auth-footer-text">
          Already have an account? <Link to="/login" className="auth-link">Sign in here</Link>
        </p>
      </div>
    </div>
  );
}
