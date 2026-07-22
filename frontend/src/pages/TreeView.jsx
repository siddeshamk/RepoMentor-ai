import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import {
  Folder, FolderOpen, File, FileCode, ChevronRight, ChevronDown,
  X, Loader2, Search, Hash, Box, ArrowDownUp
} from "lucide-react";
import useRepoStore from "../store/repoStore";

const FILE_ICONS = {
  ".py": { icon: "🐍", color: "#3b82f6" },
  ".js": { icon: "🟨", color: "#f59e0b" },
  ".jsx": { icon: "⚛️", color: "#22d3ee" },
  ".ts": { icon: "🔷", color: "#3b82f6" },
  ".tsx": { icon: "⚛️", color: "#22d3ee" },
  ".java": { icon: "☕", color: "#f97316" },
  ".css": { icon: "🎨", color: "#ec4899" },
  ".html": { icon: "🌐", color: "#f97316" },
  ".json": { icon: "📦", color: "#10b981" },
  ".md": { icon: "📄", color: "#8b5cf6" },
  ".yaml": { icon: "⚙️", color: "#f59e0b" },
  ".yml": { icon: "⚙️", color: "#f59e0b" },
  ".sh": { icon: "💻", color: "#6366f1" },
  ".go": { icon: "🐹", color: "#22d3ee" },
  ".rs": { icon: "🦀", color: "#f97316" },
  ".cpp": { icon: "🔧", color: "#6366f1" },
  ".c": { icon: "🔧", color: "#6366f1" },
};

function getFileIcon(name) {
  const ext = name.substring(name.lastIndexOf("."));
  return FILE_ICONS[ext] || { icon: "📄", color: "var(--text-muted)" };
}

function TreeNode({ node, depth = 0, onSelect, selectedPath }) {
  const [expanded, setExpanded] = useState(depth < 2);
  const isDir = node.type === "directory";
  const isSelected = selectedPath === node.path;
  const { icon: fileIcon, color } = getFileIcon(node.name);

  return (
    <div>
      <div
        className={`tree-item ${isSelected ? "selected" : ""}`}
        style={{ paddingLeft: 8 + depth * 16 }}
        onClick={() => {
          if (isDir) setExpanded(!expanded);
          else onSelect(node);
        }}
      >
        <span style={{ flexShrink: 0, display: "flex", alignItems: "center", gap: 4 }}>
          {isDir ? (
            <>
              {expanded ? <ChevronDown size={12} style={{ color: "var(--text-muted)" }} /> : <ChevronRight size={12} style={{ color: "var(--text-muted)" }} />}
              {expanded ? <FolderOpen size={14} style={{ color: "#f59e0b" }} /> : <Folder size={14} style={{ color: "#f59e0b" }} />}
            </>
          ) : (
            <>
              <span style={{ width: 12 }} />
              <span style={{ fontSize: 13 }}>{fileIcon}</span>
            </>
          )}
        </span>
        <span style={{
          fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
          color: isSelected ? "var(--accent-secondary)" : isDir ? "var(--text-primary)" : "var(--text-secondary)",
          fontWeight: isDir ? 500 : 400,
        }}>{node.name}</span>
        {!isDir && node.size_bytes > 0 && (
          <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--text-muted)", flexShrink: 0 }}>
            {(node.size_bytes / 1024).toFixed(0)}K
          </span>
        )}
      </div>

      {isDir && expanded && node.children?.map((child, i) => (
        <TreeNode key={i} node={child} depth={depth + 1} onSelect={onSelect} selectedPath={selectedPath} />
      ))}
    </div>
  );
}

function FilePanel({ analysis, filePath, onClose }) {
  if (!analysis) return null;
  return (
    <div style={{
      width: 380, flexShrink: 0, borderLeft: "1px solid var(--border)",
      background: "var(--bg-secondary)", overflowY: "auto", height: "100%",
    }} className="animate-fade-in">
      <div style={{
        padding: "16px 20px", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, background: "var(--bg-secondary)", zIndex: 10,
      }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
            {filePath?.split("/").pop()}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2, wordBreak: "break-all" }}>
            {filePath}
          </div>
        </div>
        <button className="btn-ghost" style={{ padding: "6px", borderRadius: 8 }} onClick={onClose}>
          <X size={14} />
        </button>
      </div>

      <div style={{ padding: 20 }}>

        {/* Purpose */}
        {analysis.purpose && (
          <Section title="Purpose">
            <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>{analysis.purpose}</p>
          </Section>
        )}

        {/* Responsibilities */}
        {analysis.responsibilities?.length > 0 && (
          <Section title="Responsibilities">
            <ul style={{ margin: 0, paddingLeft: 16 }}>
              {analysis.responsibilities.map((r, i) => (
                <li key={i} style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.7 }}>{r}</li>
              ))}
            </ul>
          </Section>
        )}

        {/* Classes */}
        {analysis.classes?.length > 0 && (
          <Section title={`Classes (${analysis.classes.length})`} icon={<Box size={13} style={{ color: "var(--accent-primary)" }} />}>
            {analysis.classes.map((cls, i) => (
              <div key={i} style={{ marginBottom: 8, padding: "8px 12px", borderRadius: 8, background: "rgba(99,102,241,0.06)", border: "1px solid rgba(99,102,241,0.15)" }}>
                <code style={{ fontSize: 13, color: "var(--accent-primary)", fontWeight: 600 }}>{cls.name}</code>
                {cls.docstring && <p style={{ fontSize: 11, color: "var(--text-muted)", margin: "4px 0 0", lineHeight: 1.4 }}>{cls.docstring.slice(0, 120)}</p>}
              </div>
            ))}
          </Section>
        )}

        {/* Functions */}
        {analysis.functions?.length > 0 && (
          <Section title={`Functions (${analysis.functions.length})`} icon={<Hash size={13} style={{ color: "var(--accent-secondary)" }} />}>
            {analysis.functions.slice(0, 15).map((fn, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "monospace" }}>fn</span>
                <code style={{ fontSize: 12, color: "var(--accent-secondary)" }}>{fn.name || fn}</code>
                {fn.line && <span style={{ fontSize: 10, color: "var(--text-muted)", marginLeft: "auto" }}>L{fn.line}</span>}
              </div>
            ))}
            {analysis.functions.length > 15 && (
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>+{analysis.functions.length - 15} more</div>
            )}
          </Section>
        )}

        {/* Imports */}
        {analysis.imports?.length > 0 && (
          <Section title={`Imports (${analysis.imports.length})`} icon={<ArrowDownUp size={13} style={{ color: "#10b981" }} />}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {analysis.imports.slice(0, 20).map((imp, i) => (
                <code key={i} style={{
                  fontSize: 11, padding: "2px 8px", borderRadius: 4,
                  background: "rgba(16,185,129,0.08)", color: "#10b981",
                  border: "1px solid rgba(16,185,129,0.2)",
                }}>{typeof imp === "string" ? imp : imp.name || imp.module}</code>
              ))}
            </div>
          </Section>
        )}

        {/* Stats */}
        {(analysis.lines_of_code || analysis.complexity) && (
          <Section title="Stats">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {analysis.lines_of_code && (
                <div style={{ textAlign: "center", padding: "10px", borderRadius: 8, background: "var(--bg-glass)", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: 20, fontWeight: 700, color: "var(--text-primary)" }}>{analysis.lines_of_code}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Lines</div>
                </div>
              )}
              {analysis.complexity !== undefined && (
                <div style={{ textAlign: "center", padding: "10px", borderRadius: 8, background: "var(--bg-glass)", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: 20, fontWeight: 700, color: analysis.complexity > 10 ? "#f59e0b" : "var(--accent-green)" }}>{analysis.complexity}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Complexity</div>
                </div>
              )}
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}

function Section({ title, icon, children }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
        {icon}
        <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{title}</span>
      </div>
      {children}
    </div>
  );
}

export default function TreeView() {
  const { repoId } = useParams();
  const { loadTree, loadRepo, activeRepo, tree, loadFileAnalysis, fileAnalysis, loading } = useRepoStore();
  const [selectedPath, setSelectedPath] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loadingFile, setLoadingFile] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!activeRepo && repoId) loadRepo(repoId);
    if (!tree) loadTree(repoId);
  }, [repoId]);

  const handleSelect = useCallback(async (node) => {
    setSelectedPath(node.path);
    setLoadingFile(true);
    try {
      const analysis = await loadFileAnalysis(repoId, node.path);
      setSelectedAnalysis(analysis);
    } catch (e) {
      setSelectedAnalysis({ purpose: "Analysis not available for this file." });
    } finally {
      setLoadingFile(false);
    }
  }, [repoId]);

  const treeData = tree?.root || tree;

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--bg-primary)" }}>
      {/* Header */}
      <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)", flexShrink: 0 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, margin: "0 0 4px" }}>File Explorer</h1>
        <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>
          Click any file to see its AI analysis. Click folders to expand/collapse.
        </p>
      </div>

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Tree Panel */}
        <div style={{ width: 300, flexShrink: 0, borderRight: "1px solid var(--border)", overflowY: "auto", padding: "12px 0" }}>
          <div style={{ padding: "8px 12px 12px" }}>
            <div style={{ position: "relative" }}>
              <Search size={14} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
              <input
                className="input-field"
                style={{ paddingLeft: 32, fontSize: 13, padding: "8px 12px 8px 32px" }}
                placeholder="Filter files..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          {loading.tree ? (
            <div style={{ padding: 24, textAlign: "center" }}>
              <Loader2 size={20} className="animate-spin" style={{ color: "var(--accent-primary)" }} />
              <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 8 }}>Loading tree...</div>
            </div>
          ) : treeData ? (
            Array.isArray(treeData)
              ? treeData.map((node, i) => <TreeNode key={i} node={node} onSelect={handleSelect} selectedPath={selectedPath} />)
              : treeData.children?.map((node, i) => <TreeNode key={i} node={node} onSelect={handleSelect} selectedPath={selectedPath} />)
          ) : (
            <div style={{ padding: 24, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>No tree data</div>
          )}
        </div>

        {/* Main content area */}
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
          {!selectedPath ? (
            <div style={{ textAlign: "center", color: "var(--text-muted)" }}>
              <FileCode size={48} style={{ marginBottom: 16, opacity: 0.4 }} />
              <p style={{ fontSize: 14 }}>Select a file to view its AI analysis</p>
            </div>
          ) : loadingFile ? (
            <div style={{ textAlign: "center" }}>
              <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent-primary)", marginBottom: 16 }} />
              <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>Analyzing file...</p>
            </div>
          ) : null}
        </div>

        {/* File analysis panel */}
        {selectedPath && !loadingFile && selectedAnalysis && (
          <FilePanel
            analysis={selectedAnalysis}
            filePath={selectedPath}
            onClose={() => { setSelectedPath(null); setSelectedAnalysis(null); }}
          />
        )}
      </div>
    </div>
  );
}
