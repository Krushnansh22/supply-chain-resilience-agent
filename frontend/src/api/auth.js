/**
 * src/api/auth.js
 * Authentication and User Session API Client
 */
import { apiRequest } from "./client.js";

export const loginUser = ({ email, password }) =>
  apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const registerUser = ({ name, email, password, role, assigned_warehouse, title }) =>
  apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role, assigned_warehouse, title }),
  });

export const fetchCurrentUser = () => apiRequest("/auth/me");

export const fetchDemoUsers = () => apiRequest("/auth/demo-users");
