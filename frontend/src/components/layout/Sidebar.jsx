import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard, FolderTree, Network, MessageSquare,
  FileText, Shield, Activity, ChevronLeft, GitBranch,
  Zap, Circle
} from "lucide-react";
import useRepoStore from "../../store/repoStore";

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: "Dashboard", path: "dashboard" },
  { icon: FolderTree, label: "File Explorer", path: "tree" },
  { icon: Network, label: "Architecture", path: "architecture" },
  { icon: MessageSquare, label: "AI Chat", path: "chat" },
  { icon: FileText, label: "Documentation", path: "docs" },
  { icon: Shield, label: "Security", path: "security" },
  { icon: Activity, label: "Health Score", path: "health" },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { activeRepo, activeRepoId, ollamaAvailable } = useRepoStore();

  // Extract repoId from URL path since Sidebar is rendered outside Route components
  const pathMatch = location.pathname.match(/\/repo\/([^/]+)/);
  const repoId = pathMatch?.[1] || activeRepoId;

  const repoName = activeRepo?.name || "Repository";
  const owner = activeRepo?.owner || "";

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div style={{ padding: "20px 16px 16px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg, #6366f1, #22d3ee)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18,
          }}>🧠</div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>RepoMind AI</div>
            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Intelligence Platform</div>
          </div>
        </div>

        {/* Back button */}
        <button
          className="btn-ghost"
          style={{ width: "100%", justifyContent: "center", fontSize: 13 }}
          onClick={() => navigate("/")}
        >
          <ChevronLeft size={14} /> Back to Home
        </button>
      </div>

      {/* Current Repo */}
      {activeRepo && (
        <div style={{
          padding: "12px 16px",
          borderBottom: "1px solid var(--border)",
          background: "rgba(99, 102, 241, 0.04)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <GitBranch size={13} style={{ color: "var(--accent-primary)" }} />
            <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Active Repository
            </span>
          </div>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {owner}/{repoName}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
            {activeRepo.total_files} files · {activeRepo.total_folders} dirs
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "10px 0", overflowY: "auto" }}>
        {NAV_ITEMS.map(({ icon: Icon, label, path }) => (
          <NavLink
            key={path}
            to={`/repo/${repoId}/${path}`}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <Icon size={16} className="nav-icon" />
            <span>{label}</span>
            {path === "chat" && (
              <span style={{
                marginLeft: "auto",
                fontSize: 10,
                padding: "2px 6px",
                borderRadius: 10,
                background: ollamaAvailable ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                color: ollamaAvailable ? "#10b981" : "#ef4444",
                border: `1px solid ${ollamaAvailable ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
              }}>
                {ollamaAvailable ? "ON" : "OFF"}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div style={{
        padding: "12px 16px",
        borderTop: "1px solid var(--border)",
        fontSize: 11,
        color: "var(--text-muted)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
          <Circle
            size={7}
            fill={ollamaAvailable ? "#10b981" : "#ef4444"}
            style={{ color: ollamaAvailable ? "#10b981" : "#ef4444" }}
          />
          <span>Ollama: {ollamaAvailable === null ? "Checking..." : ollamaAvailable ? "Connected" : "Offline"}</span>
        </div>
        <div>AI-Powered · 100% Local · Free</div>
      </div>
    </aside>
  );
}
