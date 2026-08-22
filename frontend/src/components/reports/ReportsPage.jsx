import { useEffect, useState } from "react";
import { downloadOperatorReport, fetchReportPreview } from "../../api/reports.js";
import { listIncidents } from "../../api/incidents.js";

export default function ReportsPage() {
  const [incidentsList, setIncidentsList] = useState([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [includeDiagnostics, setIncludeDiagnostics] = useState(false);
  const [downloadState, setDownloadState] = useState("idle");
  const [previewState, setPreviewState] = useState("idle");
  const [previewData, setPreviewData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    listIncidents("all")
      .then((data) => setIncidentsList(data || []))
      .catch((err) => console.error("Failed to load incidents for report selector:", err));
  }, []);

  const handleDownload = async () => {
    setDownloadState("loading");
    setError(null);
    try {
      await downloadOperatorReport({
        incidentId: selectedIncidentId || undefined,
        startDate: selectedIncidentId ? undefined : startDate,
        endDate: selectedIncidentId ? undefined : endDate,
        includeDiagnostics,
      });
      setDownloadState("done");
      setTimeout(() => setDownloadState("idle"), 4000);
    } catch (reportError) {
      setDownloadState("idle");
      setError(reportError.message || "Unable to download report.");
    }
  };

  const handlePreview = async () => {
    setPreviewState("loading");
    setError(null);
    try {
      const data = await fetchReportPreview({
        incidentId: selectedIncidentId || undefined,
        startDate: selectedIncidentId ? undefined : startDate,
        endDate: selectedIncidentId ? undefined : endDate,
        includeDiagnostics,
      });
      setPreviewData(data);
      setPreviewState("done");
    } catch (err) {
      setPreviewState("idle");
      setError(err.message || "Unable to generate report preview.");
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div>
          <h1>Operations & Resilience Reports</h1>
          <div className="page-subtitle">
            Generate comprehensive, LLM-synthesized operations intelligence briefs and download publication-ready PDFs for individual incidents or operations scopes.
          </div>
        </div>
      </div>

      <div className="panel report-builder" style={{ marginBottom: 24, padding: "20px 24px" }}>
        {/* Incident Scope Selection */}
        <div className="report-field" style={{ minWidth: 240 }}>
          <label htmlFor="report-incident">Report Target Scope</label>
          <select
            id="report-incident"
            value={selectedIncidentId}
            onChange={(e) => setSelectedIncidentId(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "var(--radius-sm, 6px)",
              background: "var(--bg-elevated, #1a2234)",
              color: "var(--text-primary, #fff)",
              border: "1px solid var(--border-subtle, #334155)",
              fontSize: 13,
            }}
          >
            <option value="">🌐 All Operations (Multi-Incident Report)</option>
            {incidentsList.map((inc) => (
              <option key={inc.incident_id} value={inc.incident_id}>
                {inc.incident_id} — {inc.affected_po || inc.type?.replaceAll("_", " ")} ({inc.severity})
              </option>
            ))}
          </select>
        </div>

        {!selectedIncidentId && (
          <>
            <div className="report-field">
              <label htmlFor="report-start">From Date</label>
              <input
                id="report-start"
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </div>
            <div className="report-field">
              <label htmlFor="report-end">To Date</label>
              <input
                id="report-end"
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
              />
            </div>
          </>
        )}

        <label className="report-checkbox" style={{ cursor: "pointer", userSelect: "none" }}>
          <input
            type="checkbox"
            checked={includeDiagnostics}
            onChange={(event) => setIncludeDiagnostics(event.target.checked)}
          />
          Include Diagnostics Appendix
        </label>

        <div style={{ display: "flex", gap: 10, marginLeft: "auto" }}>
          <button
            className="btn-ghost"
            disabled={previewState === "loading"}
            onClick={handlePreview}
            style={{ display: "flex", alignItems: "center", gap: 6 }}
          >
            {previewState === "loading" ? "Analyzing with LLM…" : "👁 Preview AI Brief"}
          </button>
          <button
            className="btn-primary"
            disabled={downloadState === "loading"}
            onClick={handleDownload}
            style={{ display: "flex", alignItems: "center", gap: 6 }}
          >
            {downloadState === "loading" ? "Compiling PDF…" : "↓ Download PDF"}
          </button>
        </div>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: 20 }}>{error}</div>}
      {downloadState === "done" && (
        <div className="panel" style={{ marginBottom: 20, borderColor: "rgba(22, 164, 107, 0.4)", background: "rgba(22, 164, 107, 0.08)", color: "var(--success)" }}>
          ✓ Operations PDF downloaded successfully.
        </div>
      )}

      {/* LLM Report Live Preview */}
      {previewData && (
        <div className="panel elevated-panel" style={{ padding: 24, marginTop: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 16, marginBottom: 20 }}>
            <div>
              <span className="badge badge-primary" style={{ marginRight: 8 }}>LLM INTELLIGENCE BRIEF</span>
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                Generated at {previewData.summary_stats?.generation_time_utc}
              </span>
              <h2 style={{ marginTop: 8, marginBottom: 4 }}>Operations Resilience Synthesis</h2>
              <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                Scope: <strong>{previewData.summary_stats?.scope}</strong>
              </div>
            </div>
            <button
              className="btn-primary"
              disabled={downloadState === "loading"}
              onClick={handleDownload}
              style={{ fontSize: 13 }}
            >
              {downloadState === "loading" ? "Downloading…" : "↓ Download Full PDF"}
            </button>
          </div>

          {/* KPI Mini Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 24 }}>
            <div className="panel" style={{ padding: 14, background: "rgba(255, 255, 255, 0.02)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Total Incidents</div>
              <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4, color: "var(--text-primary)" }}>
                {previewData.summary_stats?.incident_count ?? 0}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                {previewData.summary_stats?.critical_count ?? 0} Critical · {previewData.summary_stats?.high_count ?? 0} High
              </div>
            </div>

            <div className="panel" style={{ padding: 14, background: "rgba(255, 255, 255, 0.02)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Min Stock Runway</div>
              <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4, color: "var(--primary)" }}>
                {previewData.summary_stats?.min_days_of_supply} Days
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                {previewData.inventory_count} Component(s) tracked
              </div>
            </div>

            <div className="panel" style={{ padding: 14, background: "rgba(255, 255, 255, 0.02)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Exposed PO Value</div>
              <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4, color: "var(--text-primary)" }}>
                ${(previewData.summary_stats?.total_po_value_exposed || 0).toLocaleString()}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                {previewData.po_count} Purchase Order(s)
              </div>
            </div>

            <div className="panel" style={{ padding: 14, background: "rgba(255, 255, 255, 0.02)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Governance Routing</div>
              <div style={{ fontSize: 16, fontWeight: 700, marginTop: 6, color: previewData.summary_stats?.requires_human_approval ? "var(--warning)" : "var(--success)" }}>
                {previewData.summary_stats?.requires_human_approval ? "HUMAN APPROVAL" : "AUTONOMOUS"}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                Limit: ${(previewData.summary_stats?.approval_threshold_usd || 50000).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Narrative Sections */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <h3 style={{ fontSize: 15, display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
                <span>📋</span> Executive Summary
              </h3>
              <p style={{ lineHeight: 1.6, color: "var(--text-secondary)", margin: "6px 0 0 0" }}>
                {previewData.narrative?.executive_summary}
              </p>
            </div>

            <div>
              <h3 style={{ fontSize: 15, display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
                <span>⚠️</span> Supply Chain Impact Assessment
              </h3>
              <p style={{ lineHeight: 1.6, color: "var(--text-secondary)", margin: "6px 0 0 0" }}>
                {previewData.narrative?.impact_assessment}
              </p>
            </div>

            <div>
              <h3 style={{ fontSize: 15, display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
                <span>🎯</span> Decision & Recovery Strategy
              </h3>
              <p style={{ lineHeight: 1.6, color: "var(--text-secondary)", margin: "6px 0 0 0" }}>
                {previewData.narrative?.recovery_strategy}
              </p>
            </div>

            <div>
              <h3 style={{ fontSize: 15, display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
                <span>⚖️</span> Governance & Policy Compliance
              </h3>
              <p style={{ lineHeight: 1.6, color: "var(--text-secondary)", margin: "6px 0 0 0" }}>
                {previewData.narrative?.governance_and_approval}
              </p>
            </div>

            {previewData.narrative?.action_items && previewData.narrative.action_items.length > 0 && (
              <div>
                <h3 style={{ fontSize: 15, display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
                  <span>🚀</span> Actionable Directives
                </h3>
                <ul style={{ margin: "8px 0 0 0", paddingLeft: 20, color: "var(--text-secondary)", lineHeight: 1.7 }}>
                  {previewData.narrative.action_items.map((item, idx) => (
                    <li key={idx} style={{ marginBottom: 4 }}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
