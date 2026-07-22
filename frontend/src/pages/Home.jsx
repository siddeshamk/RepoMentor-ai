import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { GitBranch, Zap, Search, Clock, Trash2, ArrowRight, Star, GitFork, AlertCircle } from "lucide-react";
import useRepoStore from "../store/repoStore";

const EXAMPLE_REPOS = [
  "https://github.com/tiangolo/fastapi",
  "https://github.com/facebook/react",
  "https://github.com/django/django",
  "https://github.com/vercel/next.js",
];

const FEATURES = [
  { icon: "🔍", title: "Deep Analysis", desc: "Scans every file, detects tech, builds dependency graphs" },
  { icon: "🤖", title: "AI-Powered Q&A", desc: "Ask anything about the codebase in natural language" },
  { icon: "🏗️", title: "Architecture Diagrams", desc: "Auto-generated Mermaid diagrams and data flows" },
  { icon: "🔒", title: "Security Scanner", desc: "Finds hardcoded secrets, SQL injection, weak crypto" },
  { icon: "📊", title: "Health Scoring", desc: "Multi-dimensional code quality metrics" },
  { icon: "📖", title: "Auto Documentation", desc: "Generates README, onboarding guides, API docs" },
];

export default function Home() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { startAnalysis, loadRecentRepos, recentRepos, resetRepo } = useRepoStore();
  const inputRef = useRef(null);

  useEffect(() => {
    resetRepo();
    loadRecentRepos().catch(() => {}); // Silently ignore if backend isn't ready
    inputRef.current?.focus();
  }, []);

  const handleAnalyze = async (repoUrl = url) => {
    const trimmed = repoUrl.trim();
    if (!trimmed) { setError("Please enter a GitHub repository URL"); return; }
    if (!trimmed.includes("github.com")) { setError("Please enter a valid GitHub URL (https://github.com/owner/repo)"); return; }

    setError("");
    setIsLoading(true);
    try {
      const repoId = await startAnalysis(trimmed);
      if (!repoId || repoId === "undefined") {
        throw new Error("Failed to get repository ID from server. Please try again.");
      }
      navigate(`/repo/${repoId}/dashboard`);
    } catch (e) {
      setError(e.message || "Failed to start analysis. Is the backend running?");
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => { if (e.key === "Enter") handleAnalyze(); };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", position: "relative", overflow: "hidden" }}>

      {/* Ambient background orbs */}
      <div style={{
        position: "fixed", top: "10%", left: "15%", width: 500, height: 500,
        background: "radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)",
        pointerEvents: "none", filter: "blur(40px)",
      }} />
      <div style={{
        position: "fixed", bottom: "15%", right: "10%", width: 400, height: 400,
        background: "radial-gradient(circle, rgba(34,211,238,0.08) 0%, transparent 70%)",
        pointerEvents: "none", filter: "blur(40px)",
      }} />

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "60px 24px 80px", position: "relative" }}>

        {/* Hero */}
        <div className="animate-fade-in" style={{ textAlign: "center", marginBottom: 56 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 16px",
            borderRadius: 20, background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)",
            marginBottom: 28, fontSize: 13, color: "var(--accent-primary)",
          }}>
            <Zap size={13} fill="currentColor" />
            <span>AI-Powered · 100% Local · Free &amp; Open Source</span>
          </div>

          <h1 style={{ fontSize: "clamp(2.5rem, 6vw, 4rem)", fontWeight: 900, lineHeight: 1.1, marginBottom: 20 }}>
            <span className="gradient-text">Understand any</span>
            <br />
            <span style={{ color: "var(--text-primary)" }}>GitHub Repository</span>
            <br />
            <span className="gradient-text">in minutes</span>
          </h1>

          <p style={{ fontSize: 18, color: "var(--text-secondary)", maxWidth: 600, margin: "0 auto 40px", lineHeight: 1.7 }}>
            Paste a GitHub URL. RepoMind AI clones it, analyzes every file, detects tech stacks,
            generates documentation, and lets you chat with your codebase using AI.
          </p>

          {/* URL Input Card */}
          <div className="glass-card animate-pulse-glow" style={{
            padding: 24, maxWidth: 680, margin: "0 auto 12px",
            borderRadius: 20,
          }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <GitBranch size={20} style={{ color: "var(--accent-primary)" }} />
              </div>

              <input
                ref={inputRef}
                type="url"
                className="input-field"
                placeholder="https://github.com/owner/repository"
                value={url}
                onChange={(e) => { setUrl(e.target.value); setError(""); }}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                style={{ flex: 1 }}
              />

              <button
                className="btn-primary"
                onClick={() => handleAnalyze()}
                disabled={isLoading}
                style={{ flexShrink: 0, padding: "12px 20px" }}
              >
                {isLoading ? (
                  <>
                    <span style={{
                      width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)",
                      borderTop: "2px solid white", borderRadius: "50%",
                      animation: "spin 0.8s linear infinite", display: "inline-block",
                    }} />
                    Cloning...
                  </>
                ) : (
                  <>Analyze <ArrowRight size={16} /></>
                )}
              </button>
            </div>

            {error && (
              <div style={{
                marginTop: 12, padding: "10px 14px", borderRadius: 10,
                background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
                color: "#ef4444", fontSize: 13, display: "flex", alignItems: "center", gap: 8,
              }}>
                <AlertCircle size={14} /> {error}
              </div>
            )}
          </div>

          {/* Example Repos */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", marginTop: 12 }}>
            <span style={{ fontSize: 13, color: "var(--text-muted)", alignSelf: "center" }}>Try:</span>
            {EXAMPLE_REPOS.map((repo) => (
              <button
                key={repo}
                className="btn-ghost"
                style={{ fontSize: 12, padding: "5px 12px" }}
                onClick={() => { setUrl(repo); handleAnalyze(repo); }}
              >
                {repo.replace("https://github.com/", "")}
              </button>
            ))}
          </div>
        </div>

        {/* Features Grid */}
        <div className="animate-fade-in" style={{ marginBottom: 56, animationDelay: "0.1s" }}>
          <h2 style={{ textAlign: "center", fontSize: 22, fontWeight: 700, marginBottom: 28, color: "var(--text-secondary)" }}>
            Everything you need to understand a codebase
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
            {FEATURES.map((f, i) => (
              <div key={i} className="glass-card" style={{ padding: 20, animationDelay: `${i * 0.05}s` }}>
                <div style={{ fontSize: 28, marginBottom: 10 }}>{f.icon}</div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 6 }}>{f.title}</div>
                <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Repos */}
        {recentRepos.length > 0 && (
          <div className="animate-fade-in" style={{ animationDelay: "0.2s" }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
              <Clock size={16} style={{ color: "var(--accent-primary)" }} />
              Recent Repositories
            </h2>
            <div style={{ display: "grid", gap: 10 }}>
              {recentRepos.slice(0, 5).map((repo) => (
                <div
                  key={repo.id}
                  className="glass-card"
                  style={{ padding: "14px 18px", cursor: "pointer", display: "flex", alignItems: "center", gap: 14 }}
                  onClick={() => navigate(`/repo/${repo.id}/dashboard`)}
                >
                  <GitBranch size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                  <div style={{ flex: 1, overflow: "hidden" }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>
                      {repo.owner}/{repo.name}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {repo.description || repo.url}
                    </div>
                  </div>
                  <div style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 12 }}>
                    <span className="badge" style={{
                      background: repo.status === "complete" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
                      color: repo.status === "complete" ? "#10b981" : "#f59e0b",
                      border: `1px solid ${repo.status === "complete" ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`,
                      fontSize: 10,
                    }}>
                      {repo.status}
                    </span>
                    <ArrowRight size={14} style={{ color: "var(--text-muted)" }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
