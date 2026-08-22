import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listIncidents } from "../../api/incidents.js";
import { getDiagnostics } from "../../api/diagnostics.js";
import { injectDiagnostics } from "../../api/diagnostics.js";

const BROKEN_SCENARIOS = [
  ["inventory", "Inventory anomaly"],
  ["suppliers", "Supplier anomaly"],
  ["purchase_orders", "Purchase order anomaly"],
  ["production_orders", "Production anomaly"],
  ["audit_logs", "Audit event anomaly"],
  ["integration_errors", "Integration failure"],
];

export default function DiagnosticsPage() {
  const [incidents, setIncidents] = useState([]);
  const [diagnostics, setDiagnostics] = useState({ audit_logs: [], integration_errors: [] });
  const [loading, setLoading] = useState(true);
  const [injecting, setInjecting] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    const load = () => Promise.all([listIncidents("diagnostic"), getDiagnostics()])
      .then(([incidentRows, diagnosticRows]) => {
        setIncidents(incidentRows);
        setDiagnostics(diagnosticRows);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleInject = async (scenario) => {
    setInjecting(scenario);
    setMessage(null);
    try {
      await injectDiagnostics(scenario);
      setMessage(`${scenario.replaceAll("_", " ")} fixtures injected.`);
      const [incidentRows, diagnosticRows] = await Promise.all([listIncidents("diagnostic"), getDiagnostics()]);
      setIncidents(incidentRows);
      setDiagnostics(diagnosticRows);
    } catch (error) {
      setMessage(error.message || "Failed to inject diagnostic fixtures.");
    } finally {
      setInjecting(null);
    }
  };

  const records = [
    ...incidents.map((incident) => ({
      id: incident.incident_id,
      category: "DATA QUALITY",
      title: `${incident.type.replaceAll("_", " ")} detected`,
      detail: `Component ${incident.affected_component || "—"} · PO ${incident.affected_po || "—"}`,
      time: incident.created_at,
      link: `/incidents/${incident.incident_id}`,
    })),
    ...diagnostics.audit_logs.map((log, index) => ({
      id: `${log.event_id || "audit"}-${index}`,
      category: "INTEGRATION",
      title: log.action || log.event_type || "Integration event",
      detail: log.reason || log.result || "No diagnostic detail recorded.",
      time: log.timestamp || log.ingested_at,
    })),
    ...diagnostics.integration_errors.map((error) => ({
      id: error.error_id,
      category: "WORKFLOW ERROR",
      title: error.error_type,
      detail: `${error.workflow} · ${error.error_message}`,
      time: error.timestamp,
    })),
  ].sort((a, b) => new Date(b.time) - new Date(a.time));

  return <div>
    <div className="page-header">
      <div><h1>Diagnostics</h1><div className="page-subtitle">Data-quality and integration exceptions kept separate from operational incidents.</div></div>
      <span className="badge badge-info">LIVE · 5S</span>
    </div>
    <div className="panel">
      <div className="diagnostic-controls">
        <strong>Test a failure mode</strong>
        <span>These fixtures are injected only when you choose them.</span>
        <div className="diagnostic-actions">
          {BROKEN_SCENARIOS.map(([scenario, label]) => <button key={scenario} disabled={!!injecting} onClick={() => handleInject(scenario)}>
            {injecting === scenario ? "Injecting…" : label}
          </button>)}
          <button className="btn-primary" disabled={!!injecting} onClick={() => handleInject("all")}>Inject all</button>
        </div>
        {message && <div className="diagnostic-message">{message}</div>}
      </div>
      {loading ? <p className="empty-state">Loading diagnostics…</p> : records.length === 0 ? <p className="empty-state">No diagnostic exceptions.</p> : records.map((record) => (
        <div className="diagnostic-row" key={record.id}>
          <span className="activity-kind activity-kind-event">{record.category}</span>
          <div className="diagnostic-copy"><strong>{record.title}</strong><span>{record.detail}</span></div>
          <time>{new Date(record.time).toLocaleString()}</time>
          {record.link && <Link to={record.link}>Open</Link>}
        </div>
      ))}
    </div>
  </div>;
}