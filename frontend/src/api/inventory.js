/**
 * src/api/inventory.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_inventory.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listInventory = () => apiRequest("/inventory/");
export const getComponent = (componentId) => apiRequest(`/inventory/${componentId}`);
