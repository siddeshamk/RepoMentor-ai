import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { Activity, AlertTriangle, CheckCircle, Info, Loader2, TrendingUp, Code, BookOpen, Shield, Zap, TestTube, Wrench } from "lucide-react";
import useRepoStore from "../store/repoStore";

const DIMENSION_ICONS = {
  architecture: Wrench,
  documentation: BookOpen,
  maintainability: TrendingUp,
  readability: Code,
  security: Shield,
  performance: Zap,
  testing: TestTube,
};

function ScoreRing({ score, size = 100 }) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score));
  const offset = circ * (1 - pct / 100);
  const color = pct >= 80 ? "#10b981" : pct >= 60 ? "#22d3ee" : pct >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div style={{ position: "relative", width: size, height: size, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
      <svg width={size} height={size} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={8}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: size === 100 ? 24 : 16, fontWeight: 800, color }}>{pct}</div>
        {size === 100 && <div style={{ fontSize: 11, color: "var(--text-muted)" }}>/ 100</div>}
      </div>
    </div>
  );
}

function DimensionCard({ name, data }) {
  const Icon = DIMENSION_ICONS[name.toLowerCase()] || Activity;
  const score = typeof data === "number" ? data : data?.score ?? 0;
  const explanation = typeof data === "object" ? data?.explanation || data?.details : null;
  const issues = typeof data === "object" ? data?.issues : null;

  const color = score >= 80 ? "#10b981" : score >= 60 ? "#22d3ee" : score >= 40 ? "#f59e0b" : "#ef4444";
  const bgColor = score >= 80 ? "rgba(16,185,129,0.08)" : score >= 60 ? "rgba(34,211,238,0.08)" : score >= 40 ? "rgba(245,158,11,0.08)" : "rgba(239,68,68,0.08)";
  const borderColor = score >= 80 ? "rgba(16,185,129,0.2)" : score >= 60 ? "rgba(34,211,238,0.2)" : score >= 40 ? "rgba(245,158,11,0.2)" : "rgba(239,68,68,0.2)";

  return (
    <div className="glass-card" style={{ padding: 24, borderColor }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: bgColor, border: `1px solid ${borderColor}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Icon size={16} style={{ color }} />
          </div>
          <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", textTransform: "capitalize" }}>{name}</span>
        </div>
        <ScoreRing score={score} size={60} />
      </div>

      {/* Progress bar */}
      <div className="progress-bar" style={{ marginBottom: 12 }}>
        <div className="progress-fill" style={{ width: `${score}%`, background: `linear-gradient(90deg, ${color}80, ${color})` }} />
      </div>

      {explanation && (
        <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6, margin: "8px 0 0" }}>{explanation}</p>
      )}

      {issues && issues.length > 0 && (
        <div style={{ marginTop: 12 }}>
          {issues.slice(0, 3).map((issue, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 6, padding: "4px 0", borderTop: "1px solid rgba(255,255,255,0.04)" }}>
              <AlertTriangle size={12} style={{ color: "#f59e0b", flexShrink: 0, marginTop: 2 }} />
              <span style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.4 }}>{issue}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function QualityIssue({ issue, type }) {
  const configs = {
    large_files: { color: "#f59e0b", label: "Large File", icon: "📂" },
    long_functions: { color: "#f97316", label: "Long Function", icon: "📏" },
    complex_files: { color: "#ef4444", label: "High Complexity", icon: "🔀" },
    todo_comments: { color: "#818cf8", label: "TODO", icon: "📝" },
    fixme_comments: { color: "#f59e0b", label: "FIXME", icon: "🔧" },
    hardcoded_values: { color: "#ef4444", label: "Hardcoded Value", icon: "🔒" },
  };
  const cfg = configs[type] || { color: "var(--text-muted)", label: type, icon: "⚠️" };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
      <span style={{ fontSize: 16, flexShrink: 0 }}>{cfg.icon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {issue.file?.split("/").slice(-2).join("/") || issue.name || "—"}
        </div>
        {(issue.lines || issue.count || issue.value) && (
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
            {issue.lines ? `${issue.lines} lines` : ""}
            {issue.count ? ` · ${issue.count} occurrences` : ""}
            {issue.complexity ? ` · complexity: ${issue.complexity}` : ""}
          </div>
        )}
      </div>
      <span className="badge" style={{ background: `${cfg.color}18`, color: cfg.color, border: `1px solid ${cfg.color}30`, fontSize: 10, flexShrink: 0 }}>
        {cfg.label}
      </span>
    </div>
  );
}

export default function HealthPage() {
  const { repoId } = useParams();
  const { loadHealth, loadQuality, loadRepo, activeRepo, health, quality, loading } = useRepoStore();

  useEffect(() => {
    if (!activeRepo && repoId) loadRepo(repoId);
    if (!health) loadHealth(repoId);
    if (!quality) loadQuality(repoId);
  }, [repoId]);

  if (loading.health || loading.quality) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <div style={{ textAlign: "center" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent-primary)", marginBottom: 16 }} />
          <div style={{ color: "var(--text-secondary)" }}>Computing health scores...</div>
        </div>
      </div>
    );
  }

  const overall = health?.overall ?? 0;
  const dimensions = health?.dimensions || {};
  const summary = quality?.summary || {};
  const issues = quality?.issues || {};

  const overallColor = overall >= 80 ? "#10b981" : overall >= 60 ? "#22d3ee" : overall >= 40 ? "#f59e0b" : "#ef4444";
  const overallLabel = overall >= 80 ? "Excellent" : overall >= 60 ? "Good" : overall >= 40 ? "Fair" : "Needs Work";

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "32px 32px 60px" }} className="animate-fade-in">
      <div style={{ maxWidth: 900, margin: "0 auto" }}>

        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>
            <span className="gradient-text">Repository</span> Health
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, margin: 0 }}>
            Multi-dimensional code quality and maintainability assessment.
          </p>
        </div>

        {/* Overall Score Hero */}
        <div className="glass-card animate-pulse-glow" style={{ padding: 40, textAlign: "center", marginBottom: 28, borderColor: `${overallColor}30` }}>
          <ScoreRing score={overall} size={140} />
          <div style={{ marginTop: 16, fontSize: 22, fontWeight: 700, color: overallColor }}>{overallLabel}</div>
          <div style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 4 }}>Overall Repository Health</div>

          {health?.summary && (
            <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 16, maxWidth: 500, margin: "16px auto 0", lineHeight: 1.6 }}>
              {health.summary}
            </p>
          )}
        </div>

        {/* Dimension Cards */}
        {Object.keys(dimensions).length > 0 && (
          <>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Health Dimensions</h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16, marginBottom: 32 }}>
              {Object.entries(dimensions).map(([name, data]) => (
                <DimensionCard key={name} name={name} data={data} />
              ))}
            </div>
          </>
        )}

        {/* Quality Summary Stats */}
        {Object.keys(summary).length > 0 && (
          <div style={{ marginBottom: 28 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Code Metrics</h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
              {[
                { key: "total_lines", label: "Total Lines" },
                { key: "total_files", label: "Files Analyzed" },
                { key: "avg_file_size", label: "Avg File (lines)" },
                { key: "max_file_size", label: "Largest File" },
                { key: "todo_count", label: "TODO Items" },
                { key: "fixme_count", label: "FIXME Items" },
              ].map(({ key, label }) => summary[key] !== undefined && (
                <div key={key} className="glass-card" style={{ padding: "14px 16px", textAlign: "center" }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)" }}>{summary[key]?.toLocaleString?.() ?? summary[key]}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>{label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quality Issues */}
        {Object.keys(issues).length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Code Quality Issues</h2>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              {Object.entries(issues).map(([type, items]) =>
                Array.isArray(items) && items.length > 0 ? (
                  <div key={type} className="glass-card" style={{ padding: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 12, textTransform: "capitalize" }}>
                      {type.replace(/_/g, " ")} ({items.length})
                    </div>
                    {items.slice(0, 6).map((item, i) => (
                      <QualityIssue key={i} issue={item} type={type} />
                    ))}
                    {items.length > 6 && (
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8 }}>+{items.length - 6} more</div>
                    )}
                  </div>
                ) : null
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
