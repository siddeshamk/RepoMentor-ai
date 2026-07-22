import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  GitBranch, FileCode, FolderOpen, Star, GitFork, Globe, Shield, Activity,
  BookOpen, Zap, Code2, AlertTriangle, CheckCircle, ArrowRight, RefreshCw,
  BarChart3, Hash, Layers, Target
} from "lucide-react";
import useRepoStore from "../store/repoStore";

function StatCard({ icon: Icon, label, value, color = "var(--accent-primary)", sub }) {
  return (
    <div className="glass-card" style={{ padding: "20px 24px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: `${color}18`, border: `1px solid ${color}30`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <Icon size={18} style={{ color }} />
        </div>
        <span style={{ fontSize: 13, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color: "var(--text-primary)" }}>{value ?? "—"}</div>
      {sub && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function ScoreBar({ label, score, color }) {
  const pct = Math.min(100, Math.max(0, score));
  const getColor = (s) => {
    if (s >= 80) return "#10b981";
    if (s >= 60) return "#22d3ee";
    if (s >= 40) return "#f59e0b";
    return "#ef4444";
  };
  const c = color || getColor(pct);
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color: c }}>{pct}/100</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${c}99, ${c})` }} />
      </div>
    </div>
  );
}

function LearningStep({ step, index }) {
  return (
    <div style={{ display: "flex", gap: 14, padding: "12px 0", borderBottom: "1px solid var(--border)" }}>
      <div style={{
        width: 32, height: 32, borderRadius: "50%", flexShrink: 0,
        background: "linear-gradient(135deg, var(--accent-primary), var(--gradient-mid))",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 700, color: "white",
      }}>{index + 1}</div>
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)", marginBottom: 2 }}>{step.title}</div>
        {step.description && (
          <div style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.5 }}>{step.description}</div>
        )}
        {step.files && step.files.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
            {step.files.slice(0, 3).map((f, i) => (
              <code key={i} style={{
                fontSize: 11, padding: "2px 8px", borderRadius: 4,
                background: "rgba(99,102,241,0.1)", color: "var(--accent-secondary)",
                border: "1px solid rgba(99,102,241,0.2)",
              }}>{f}</code>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { repoId } = useParams();
  const navigate = useNavigate();
  const { activeRepo, analysisStatus, analysisProgress, analysisMessage, pollStatus, loadRepo, health, loadHealth } = useRepoStore();
  const [polling, setPolling] = useState(false);

  // Always load repo if we don't have it or it's a different repo
  useEffect(() => {
    if (!repoId) return;
    if (!activeRepo || activeRepo.id !== repoId) {
      loadRepo(repoId);
    }
  }, [repoId]);

  // Poll until complete when analyzing
  useEffect(() => {
    if (!repoId) return;
    // If status is null (direct navigation), don't poll — wait for loadRepo
    if (analysisStatus === null) return;
    if (analysisStatus === "complete") {
      if (!health) loadHealth(repoId);
      return;
    }
    if (analysisStatus === "error") return;

    setPolling(true);
    const interval = setInterval(async () => {
      await pollStatus(repoId);
      const s = useRepoStore.getState().analysisStatus;
      if (s === "complete") {
        clearInterval(interval);
        setPolling(false);
        loadRepo(repoId);
        loadHealth(repoId);
      } else if (s === "error") {
        clearInterval(interval);
        setPolling(false);
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [repoId, analysisStatus]);

  useEffect(() => {
    if (activeRepo?.status === "complete" && !health) loadHealth(repoId);
  }, [activeRepo, repoId]);

  const repo = activeRepo;
  const isLoading = !repo && analysisStatus === null;
  const isAnalyzing = repo?.status === "analyzing" || repo?.status === "pending" || (analysisStatus === "analyzing" && !repo);

  // Loading spinner (direct URL visit, fetching repo data)
  if (isLoading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-primary)" }}>
        <div className="glass-card animate-fade-in" style={{ padding: 48, maxWidth: 400, width: "100%", textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 20 }}>🧠</div>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Loading Repository</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>Fetching analysis data...</p>
        </div>
      </div>
    );
  }

  // Analysis in progress state
  if (isAnalyzing) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-primary)" }}>
        <div className="glass-card animate-fade-in" style={{ padding: 48, maxWidth: 500, width: "100%", textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 20 }}>🧠</div>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>Analyzing Repository</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 32, fontSize: 14 }}>
            {analysisMessage || "Starting analysis..."}
          </p>
          <div className="progress-bar" style={{ marginBottom: 12 }}>
            <div className="progress-fill" style={{ width: `${analysisProgress}%` }} />
          </div>
          <div style={{ fontSize: 13, color: "var(--text-muted)" }}>{analysisProgress}% complete</div>
        </div>
      </div>
    );
  }


  if (repo.status === "error") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="glass-card" style={{ padding: 40, maxWidth: 400, textAlign: "center" }}>
          <AlertTriangle size={48} style={{ color: "#ef4444", marginBottom: 16 }} />
          <h2>Analysis Failed</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: 24 }}>{repo.error_message || "An unknown error occurred."}</p>
          <button className="btn-primary" onClick={() => navigate("/")}>← Try Another Repo</button>
        </div>
      </div>
    );
  }

  const summary = repo.summary || {};
  const techStack = repo.tech_stack || {};
  const learningPath = repo.learning_path || [];
  const healthScore = health || repo.health_score || {};
  const overall = healthScore.overall || 0;

  const frameworks = techStack.frameworks || [];
  const languages = techStack.languages || [];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "32px 32px 60px" }} className="animate-fade-in">

      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12,
            background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(34,211,238,0.1))",
            border: "1px solid rgba(99,102,241,0.3)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <GitBranch size={22} style={{ color: "var(--accent-primary)" }} />
          </div>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 800, margin: 0 }}>
              <span className="gradient-text">{repo.owner}</span>
              <span style={{ color: "var(--text-muted)" }}>/</span>
              <span>{repo.name}</span>
            </h1>
            <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 2 }}>
              {repo.description || "No description available"}
            </div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <span className="badge severity-info">{techStack.primary_language || summary.primary_language || "Unknown"}</span>
            <span className="badge" style={{
              background: "rgba(16,185,129,0.1)", color: "#10b981",
              border: "1px solid rgba(16,185,129,0.3)", fontSize: 11,
            }}>✓ Analysis Complete</span>
          </div>
        </div>
        <a href={repo.url} target="_blank" rel="noreferrer"
          style={{ fontSize: 13, color: "var(--text-muted)", textDecoration: "none" }}>
          {repo.url} ↗
        </a>
      </div>

      {/* Stats Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 16, marginBottom: 32 }}>
        <StatCard icon={FileCode} label="Total Files" value={repo.total_files?.toLocaleString()} color="#6366f1" />
        <StatCard icon={FolderOpen} label="Directories" value={repo.total_folders?.toLocaleString()} color="#8b5cf6" />
        <StatCard icon={Hash} label="Lines of Code" value={repo.total_lines?.toLocaleString() || "—"} color="#22d3ee" />
        <StatCard icon={BarChart3} label="Repo Size" value={`${(repo.repo_size_mb || 0).toFixed(1)} MB`} color="#f59e0b" />
        <StatCard icon={Layers} label="Classes" value={summary.total_classes?.toLocaleString() || "—"} color="#10b981" />
        <StatCard icon={Code2} label="Functions" value={summary.total_functions?.toLocaleString() || "—"} color="#ec4899" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>

        {/* Technology Stack */}
        <div className="glass-card" style={{ padding: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
            <Zap size={16} style={{ color: "var(--accent-primary)" }} /> Technology Stack
          </h2>

          {languages.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 10 }}>Languages</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {languages.map((lang, i) => (
                  <span key={i} className="tech-badge">
                    {lang.icon || "🔷"} {lang.name}
                    {lang.percentage && <span style={{ color: "var(--text-muted)", fontSize: 11 }}>{lang.percentage.toFixed(0)}%</span>}
                  </span>
                ))}
              </div>
            </div>
          )}

          {frameworks.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 10 }}>Frameworks & Tools</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {frameworks.slice(0, 12).map((fw, i) => (
                  <span key={i} className="tech-badge" style={{ background: "rgba(34,211,238,0.08)", borderColor: "rgba(34,211,238,0.2)", color: "var(--accent-secondary)" }}>
                    {fw.icon || "⚙️"} {fw.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {summary.has_tests && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", borderRadius: 8, background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)" }}>
              <CheckCircle size={14} style={{ color: "#10b981" }} />
              <span style={{ fontSize: 13, color: "#10b981" }}>Test suite detected</span>
            </div>
          )}
        </div>

        {/* Health Score */}
        <div className="glass-card" style={{ padding: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <Activity size={16} style={{ color: "var(--accent-secondary)" }} /> Repository Health
          </h2>

          {/* Overall score */}
          <div style={{ textAlign: "center", padding: "16px 0 24px" }}>
            <div style={{
              fontSize: 56, fontWeight: 900,
              color: overall >= 80 ? "#10b981" : overall >= 60 ? "#22d3ee" : overall >= 40 ? "#f59e0b" : "#ef4444",
            }}>{overall}</div>
            <div style={{ fontSize: 14, color: "var(--text-secondary)" }}>Overall Health Score</div>
          </div>

          {healthScore.dimensions && Object.entries(healthScore.dimensions).map(([key, val]) => (
            <ScoreBar key={key} label={key.charAt(0).toUpperCase() + key.slice(1)} score={val.score || val} />
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 24 }}>
        {[
          { label: "Explore Files", icon: FolderOpen, path: "tree", color: "#6366f1" },
          { label: "AI Chat", icon: Zap, path: "chat", color: "#22d3ee" },
          { label: "Architecture", icon: Globe, path: "architecture", color: "#8b5cf6" },
          { label: "Documentation", icon: BookOpen, path: "docs", color: "#10b981" },
          { label: "Security", icon: Shield, path: "security", color: "#ef4444" },
          { label: "Code Quality", icon: Target, path: "health", color: "#f59e0b" },
        ].map((action) => (
          <button
            key={action.path}
            className="glass-card btn-ghost"
            style={{ padding: "16px 20px", display: "flex", alignItems: "center", gap: 12, borderRadius: 12, width: "100%", border: "1px solid var(--border)" }}
            onClick={() => navigate(`/repo/${repoId}/${action.path}`)}
          >
            <action.icon size={18} style={{ color: action.color }} />
            <span style={{ fontWeight: 600, fontSize: 14 }}>{action.label}</span>
            <ArrowRight size={14} style={{ marginLeft: "auto", color: "var(--text-muted)" }} />
          </button>
        ))}
      </div>

      {/* Learning Path */}
      {learningPath.length > 0 && (
        <div className="glass-card" style={{ padding: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4, display: "flex", alignItems: "center", gap: 8 }}>
            <BookOpen size={16} style={{ color: "#10b981" }} /> Beginner Learning Path
          </h2>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 20 }}>
            Follow these steps to understand this codebase from the ground up.
          </p>
          {learningPath.map((step, i) => (
            <LearningStep key={i} step={step} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
