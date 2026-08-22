/**
 * src/api/simulator.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_simulator.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const injectScenario = (scenario) =>
  apiRequest("/simulator/inject", { method: "POST", body: JSON.stringify({ scenario }) });
