/**
 * src/components/overview/AgentActivityFeed.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `auditLogs` prop (from GET /audit, shape: schemas/common.AuditLogOut)
 * Renders the safe, human-readable narration only (team doc Section 14) —
 * NEVER shows raw LLM output, only the `action` field written by audit_logger.log_event().
 */
import ActivityFeed from "../audit/ActivityFeed.jsx";

export default function AgentActivityFeed({ auditLogs }) {
  return <ActivityFeed logs={auditLogs} compact title="Recent agent activity" />;
}
