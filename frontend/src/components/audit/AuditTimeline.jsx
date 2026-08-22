/**
 * src/components/audit/AuditTimeline.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 17: full chronological audit trail across all incidents.
 * RECEIVES: GET /audit (src/api/audit.js) -> schemas/common.AuditLogOut[]
 */
import { useEffect, useState } from "react";
import { listAuditLogs } from "../../api/audit.js";
import ActivityFeed from "./ActivityFeed.jsx";

export default function AuditTimeline() {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    const load = () => listAuditLogs().then(setLogs).catch(console.error);
    load();
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Audit Timeline</h1>
          <div className="page-subtitle">Every disruption, investigation, decision, and approval — in order.</div>
        </div>
      </div>
      <ActivityFeed logs={logs} showFilters title="Audit history" />
    </div>
  );
}
