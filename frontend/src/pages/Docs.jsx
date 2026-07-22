import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FileText, BookOpen, Download, Code, Globe, Settings, Loader2, ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import useRepoStore from "../store/repoStore";

const SECTIONS = [
  { key: "readme", label: "README", icon: BookOpen, color: "#6366f1" },
  { key: "architecture", label: "Architecture", icon: Globe, color: "#22d3ee" },
  { key: "api_documentation", label: "API Docs", icon: Code, color: "#10b981" },
  { key: "installation_guide", label: "Installation", icon: Settings, color: "#f59e0b" },
  { key: "developer_onboarding", label: "Onboarding", icon: FileText, color: "#8b5cf6" },
  { key: "deployment_guide", label: "Deployment", icon: Download, color: "#ec4899" },
];

function DocSection({ title, icon: Icon, color, content }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!content || content === "N/A" || content.trim().length < 10) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-card" style={{ marginBottom: 16, overflow: "hidden" }}>
      <div
        style={{ padding: "16px 20px", display: "flex", alignItems: "center", gap: 12, cursor: "pointer", borderBottom: expanded ? "1px solid var(--border)" : "none" }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ width: 36, height: 36, borderRadius: 8, background: `${color}18`, border: `1px solid ${color}30`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Icon size={15} style={{ color }} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>{title}</div>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{content.length} characters · Markdown</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button
            className="btn-ghost"
            style={{ padding: "5px 10px", fontSize: 12 }}
            onClick={(e) => { e.stopPropagation(); handleCopy(); }}
          >
            {copied ? <Check size={12} style={{ color: "#10b981" }} /> : <Copy size={12} />}
          </button>
          <button
            className="btn-ghost"
            style={{ padding: "5px 10px", fontSize: 12 }}
            onClick={(e) => { e.stopPropagation(); handleDownload(); }}
          >
            <Download size={12} />
          </button>
          {expanded ? <ChevronUp size={16} style={{ color: "var(--text-muted)" }} /> : <ChevronDown size={16} style={{ color: "var(--text-muted)" }} />}
        </div>
      </div>

      {expanded && (
        <div style={{ padding: "24px 28px", maxHeight: 600, overflowY: "auto" }}>
          <MarkdownContent content={content} />
        </div>
      )}
    </div>
  );
}

function MarkdownContent({ content }) {
  // Simple markdown renderer
  const lines = content.split("\n");
  const elements = [];
  let codeBlock = false;
  let codeLines = [];
  let codeLang = "";

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (codeBlock) {
        elements.push(
          <pre key={i} style={{ background: "rgba(0,0,0,0.4)", border: "1px solid var(--border)", borderRadius: 8, padding: 16, overflow: "auto", margin: "12px 0" }}>
            <code style={{ color: "var(--text-primary)", fontSize: 13, fontFamily: "JetBrains Mono, monospace" }}>{codeLines.join("\n")}</code>
          </pre>
        );
        codeBlock = false;
        codeLines = [];
        codeLang = "";
      } else {
        codeBlock = true;
        codeLang = line.slice(3);
      }
      continue;
    }

    if (codeBlock) { codeLines.push(line); continue; }

    if (line.startsWith("### ")) {
      elements.push(<h3 key={i} style={{ fontSize: 15, fontWeight: 600, color: "var(--accent-secondary)", marginTop: 20, marginBottom: 8 }}>{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i} style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginTop: 24, marginBottom: 10, borderBottom: "1px solid var(--border)", paddingBottom: 8 }}>{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i} style={{ fontSize: 22, fontWeight: 800, marginTop: 0, marginBottom: 12 }}>{line.slice(2)}</h1>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(<li key={i} style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.7, marginLeft: 16, marginBottom: 2 }}>{renderInline(line.slice(2))}</li>);
    } else if (/^\d+\.\s/.test(line)) {
      elements.push(<li key={i} style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.7, marginLeft: 16, marginBottom: 2 }}>{renderInline(line.replace(/^\d+\.\s/, ""))}</li>);
    } else if (line.trim() === "") {
      elements.push(<br key={i} />);
    } else if (line.startsWith(">")) {
      elements.push(<blockquote key={i} style={{ borderLeft: "3px solid var(--accent-primary)", paddingLeft: 16, color: "var(--text-secondary)", margin: "8px 0", fontStyle: "italic", fontSize: 14 }}>{line.slice(1)}</blockquote>);
    } else {
      elements.push(<p key={i} style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.7, margin: "4px 0" }}>{renderInline(line)}</p>);
    }
  }

  return <div className="markdown-content">{elements}</div>;
}

function renderInline(text) {
  // Handle **bold** and `code` inline
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={i} style={{ background: "rgba(99,102,241,0.1)", color: "var(--accent-secondary)", padding: "1px 6px", borderRadius: 4, fontSize: "0.9em" }}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} style={{ color: "var(--text-primary)", fontWeight: 600 }}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

export default function DocsPage() {
  const { repoId } = useParams();
  const { loadDocs, loadRepo, activeRepo, docs, loading } = useRepoStore();

  useEffect(() => {
    if (!activeRepo && repoId) loadRepo(repoId);
    if (!docs) loadDocs(repoId);
  }, [repoId]);

  const handleDownloadAll = () => {
    if (!docs) return;
    const allContent = SECTIONS
      .map((s) => docs[s.key] ? `# ${s.label}\n\n${docs[s.key]}` : "")
      .filter(Boolean)
      .join("\n\n---\n\n");
    const blob = new Blob([allContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "repomind_documentation.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading.docs) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <div style={{ textAlign: "center" }}>
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent-primary)", marginBottom: 16 }} />
          <div style={{ color: "var(--text-secondary)" }}>Loading documentation...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "32px 32px 60px" }} className="animate-fade-in">
      <div style={{ maxWidth: 800, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>
              <span className="gradient-text">Auto-Generated</span> Documentation
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: 14, margin: 0 }}>
              Click any section to expand. Download individual docs or all at once.
            </p>
          </div>
          <button className="btn-primary" style={{ flexShrink: 0 }} onClick={handleDownloadAll}>
            <Download size={15} /> Download All
          </button>
        </div>

        {!docs ? (
          <div className="glass-card" style={{ padding: 40, textAlign: "center" }}>
            <FileText size={48} style={{ color: "var(--text-muted)", marginBottom: 16, opacity: 0.4 }} />
            <p style={{ color: "var(--text-secondary)" }}>Documentation not available yet.</p>
          </div>
        ) : (
          SECTIONS.map((section) => (
            <DocSection
              key={section.key}
              title={section.label}
              icon={section.icon}
              color={section.color}
              content={docs[section.key]}
            />
          ))
        )}
      </div>
    </div>
  );
}
