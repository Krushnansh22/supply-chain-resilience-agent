/**
 * src/api/client.js
 * Single fetch wrapper that automatically attaches Authorization Bearer tokens,
 * X-User-Id, and X-Warehouse-Id headers, and manages 401 session expiry.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("scda_auth_token");
  const userId = localStorage.getItem("scda_user_id");
  const warehouseId = localStorage.getItem("scda_warehouse_id");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...(userId ? { "X-User-Id": userId } : {}),
    ...(warehouseId ? { "X-Warehouse-Id": warehouseId } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401 && !path.startsWith("/auth/login") && !path.startsWith("/auth/demo-users")) {
    localStorage.removeItem("scda_auth_token");
    localStorage.removeItem("scda_active_user");
    window.dispatchEvent(new CustomEvent("scda_auth_expired"));
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    let errorDetail = body;
    try {
      const parsed = JSON.parse(body);
      if (parsed.detail) errorDetail = parsed.detail;
    } catch {
      // keep raw body
    }
    throw new Error(errorDetail || `API ${options.method || "GET"} ${path} failed: ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}
