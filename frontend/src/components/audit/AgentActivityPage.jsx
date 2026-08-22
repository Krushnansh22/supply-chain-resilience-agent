/**
 * Safe, operator-facing view of agent decisions and tool activity.
 * Raw model chain-of-thought is intentionally not persisted or displayed.
 */
import { useEffect, useState } from "react";
import { listAuditLogs } from "../../api/audit.js";
import ActivityFeed from "./ActivityFeed.jsx";

export default function AgentActivityPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = () => listAuditLogs().then((items) => {
      if (mounted) setLogs(items);
    }).catch(console.error).finally(() => {
      if (mounted) setLoading(false);
    });
    load();
    const interval = setInterval(load, 2000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Agent Activity</h1>
          <div className="page-subtitle">One live stream for decisions, tool calls, reasons, and technical details.</div>
        </div>
        <span className="badge badge-info">LIVE · 2S</span>
      </div>
      {loading ? <p className="empty-state">Loading activity…</p> : <ActivityFeed logs={logs} showFilters title="Live agent activity" />}
    </div>
  );
}