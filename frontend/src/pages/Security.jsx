import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Shield, AlertTriangle, AlertOctagon, Info, Lock, Key, Database,
  Eye, FileWarning, ChevronDown, ChevronUp, Loader2, CheckCircle
} from "lucide-react";
import useRepoStore from "../store/repoStore";

const SEVERITY_CONFIG = {
  critical: { color: "#ef4444", bg: "rgba(239,68,68,0.1)", border: "rgba(239,68,68,0.3)", icon: AlertOctagon, label: "Critical" },
  high:     { color: "#f97316", bg: "rgba(249,115,22,0.1)", border: "rgba(249,115,22,0.3)", icon: AlertTriangle, label: "High" },
  medium:   { color: "#f59e0b", bg: "rgba(245,158,11,0.1)", border: "rgba(245,158,11,0.3)", icon: AlertTriangle, label: "Medium" },
  low:      { color: "#22c55e", bg: "rgba(34,197,94,0.1)",  border: "rgba(34,197,94,0.3)",  icon: Info, label: "Low" },
  info:     { color: "#818cf8", bg: "rgba(99,102,241,0.1)", border: "rgba(99,102,241,0.3)", icon: Info, label: "Info" },
};

const CATEGORY_ICONS = {
  secrets: Key,
  authentication: Lock,
  sql_injection: Database,
  sensitive_data: Eye,
  todo: FileWarning,
  default: Shield,
};

function FindingCard({ finding }) {
  const [expanded, setExpanded] = useState(false);
  const sev = finding.severity?.toLowerCase() || "info";
  const cfg = SEVERITY_CONFIG[sev] || SEVERITY_CONFIG.info;
  const Icon = cfg.icon;

  return (
    <div
      className="glass-card"
      style={{ marginBottom: 10, borderColor: cfg.border, overflow: "hidden", cursor: "pointer" }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: cfg.bg, border: `1px solid ${cfg.border}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Icon size={15} style={{ color: cfg.color }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 2 }}>
            {finding.description || finding.type || "Security Finding"}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", display: "flex", gap: 12, flexWrap: "wrap" }}>
            {finding.file && <span>📁 {finding.file.split("/").slice(-2).join("/")}</span>}
            {finding.line && <span>Line {finding.line}</span>}
            {finding.category && <span>🏷️ {finding.category}</span>}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
          <span className={`badge severity-${sev}`} style={{ fontSize: 10 }}>{cfg.label}</span>
          {expanded ? <ChevronUp size={14} style={{ color: "var(--text-muted)" }} /> : <ChevronDown size={14} style={{ color: "var(--text-muted)" }} />}
        </div>
      </div>

      {expanded && (finding.code_snippet || finding.recommendation || finding.match) && (
        <div style={{ padding: "0 16px 16px", borderTop: "1px solid var(--border)" }}>
          {(finding.code_snippet || finding.match) && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>Code</div>
              <pre style={{ background: "rgba(0,0,0,0.4)", border: "1px solid var(--border)", borderRadius: 6, padding: "10px 14px", fontSize: 12, overflowX: "auto", margin: 0, color: cfg.color }}>
                {finding.code_snippet || finding.match}
              </pre>
            </div>
          )}
          {finding.recommendation && (
            <div style={{ marginTop: 12, padding: "10px 14px", borderRadius: 8, background: "rgba(16,185,129,0.06)", border: "1px solid rgba(16,185,129,0.2)" }}>
              <div style={{ fontSize: 11, color: "#10b981", marginBottom: 4, fontWeight: 600 }}>💡 Recommendation</div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>{finding.recommendation}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SeverityBadge({ count, severity }) {
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.info;
  if (!count) return null;
  return (
    <div className="glass-card" style={{ padding: "16px 20px", textAlign: "center", borderColor: cfg.border }}>
      <div style={{ fontSize: 32, fontWeight: 800, color: cfg.color, marginBottom: 4 }}>{count}</div>
      <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{cfg.label}</div>
    </div>
  );
}

export default function SecurityPage() {
  const { repoId } = useParams();
  const { loadSecurity, loadRepo, activeRepo, security, loading } = useRepoStore();
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    if (!activeRepo && repoId) loadRepo(repoId);
    if (!security) loadSecurity(repoId);
  }, [repoId]);

  if (loading.security) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <div style={{ textAlign: "center" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent-primary)", marginBottom: 16 }} />
          <div style={{ color: "var(--text-secondary)" }}>Running security scan...</div>
        </div>
      </div>
    );
  }

  const findings = security?.findings || [];
  const counts = security?.counts || {};
  const total = security?.total || findings.length;

  const filtered = filter === "all" ? findings : findings.filter((f) => f.severity?.toLowerCase() === filter);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "32px 32px 60px" }} className="animate-fade-in">
      <div style={{ maxWidth: 900, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>
            <span className="gradient-text">Security</span> Analysis
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, margin: 0 }}>
            Automated detection of secrets, vulnerabilities, and security issues.
          </p>
        </div>

        {/* Severity Summary */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginBottom: 28 }}>
          <SeverityBadge count={counts.critical || 0} severity="critical" />
          <SeverityBadge count={counts.high || 0} severity="high" />
          <SeverityBadge count={counts.medium || 0} severity="medium" />
          <SeverityBadge count={counts.low || 0} severity="low" />
          <SeverityBadge count={counts.info || 0} severity="info" />
        </div>

        {total === 0 ? (
          <div className="glass-card" style={{ padding: 48, textAlign: "center" }}>
            <CheckCircle size={48} style={{ color: "#10b981", marginBottom: 16 }} />
            <h2 style={{ fontSize: 20, fontWeight: 700, color: "#10b981", marginBottom: 8 }}>No Issues Found</h2>
            <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>No security vulnerabilities were detected in this repository.</p>
          </div>
        ) : (
          <>
            {/* Filter Tabs */}
            <div className="tab-bar" style={{ marginBottom: 20 }}>
              {["all", "critical", "high", "medium", "low", "info"].map((sev) => {
                const c = sev === "all" ? total : (counts[sev] || 0);
                return (
                  <button
                    key={sev}
                    className={`tab-item ${filter === sev ? "active" : ""}`}
                    onClick={() => setFilter(sev)}
                  >
                    {sev.charAt(0).toUpperCase() + sev.slice(1)}
                    {c > 0 && <span style={{ marginLeft: 6, fontSize: 10, padding: "1px 6px", borderRadius: 10, background: "rgba(255,255,255,0.06)" }}>{c}</span>}
                  </button>
                );
              })}
            </div>

            {/* Findings */}
            <div>
              {filtered.length === 0 ? (
                <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: 14 }}>
                  No {filter} severity findings.
                </div>
              ) : (
                filtered.map((f, i) => <FindingCard key={i} finding={f} />)
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
