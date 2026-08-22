/**
 * src/api/client.js
 * Owner: Developer 4 (Frontend)
 *
 * Single fetch wrapper every other file in src/api/ uses. Keeps base URL,
 * error handling, and JSON parsing in one place.
 *
 * RECEIVES: VITE_API_BASE_URL from frontend/.env
 * DELIVERS: parsed JSON (or throws) to the individual api/*.js modules
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${options.method || "GET"} ${path} failed: ${res.status} ${body}`);
  }

  if (res.status === 204) return null;
  return res.json();
}
