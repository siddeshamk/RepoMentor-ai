import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import {
  MessageSquare, Send, Zap, User, Bot, AlertTriangle, Sparkles,
  RefreshCw, Copy, Check
} from "lucide-react";
import { streamChat } from "../services/api";
import useRepoStore from "../store/repoStore";

const SUGGESTED_QUESTIONS = [
  "Explain the overall architecture of this project",
  "What is the entry point of this application?",
  "How does authentication work?",
  "Where are the API routes defined?",
  "How is the database connected?",
  "Explain the folder structure",
  "What are the main features of this project?",
  "How do I set up and run this project?",
  "Find potential security vulnerabilities",
  "Suggest improvements to the codebase",
  "What design patterns are used?",
  "Explain like I'm a beginner",
];

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: "2px 6px" }}
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
    >
      {copied ? <Check size={12} style={{ color: "#10b981" }} /> : <Copy size={12} />}
    </button>
  );
}

function MessageBubble({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`chat-message ${isUser ? "user" : "assistant"}`} style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10, maxWidth: "85%", ...(isUser ? { flexDirection: "row-reverse" } : {}) }}>
        <div style={{
          width: 32, height: 32, borderRadius: "50%", flexShrink: 0,
          background: isUser
            ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
            : "linear-gradient(135deg, #22d3ee22, #6366f122)",
          border: isUser ? "none" : "1px solid rgba(99,102,241,0.3)",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          {isUser ? <User size={15} style={{ color: "white" }} /> : <Bot size={15} style={{ color: "var(--accent-primary)" }} />}
        </div>

        <div>
          <div className={`chat-bubble ${isUser ? "user" : "assistant"}`} style={{ position: "relative" }}>
            {/* Render with basic markdown-ish formatting */}
            <div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
              {msg.content || <span style={{ opacity: 0.5 }}>▌</span>}
            </div>
            {!isUser && msg.content && (
              <div style={{ position: "absolute", top: 8, right: 8 }}>
                <CopyButton text={msg.content} />
              </div>
            )}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, paddingLeft: isUser ? 0 : 4, textAlign: isUser ? "right" : "left" }}>
            {msg.time}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { repoId } = useParams();
  const { ollamaAvailable, activeRepo, loadRepo } = useRepoStore();
  const [messages, setMessages] = useState([{
    role: "assistant",
    content: `👋 Hi! I'm RepoMind AI. I'm ready to answer your questions about this repository.\n\nAsk me anything about the codebase — architecture, specific files, functions, how to run it, security issues, and more!`,
    time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Load repo data if missing (direct URL visit / page refresh)
  useEffect(() => {
    if (!activeRepo && repoId) {
      loadRepo(repoId);
    }
  }, [repoId]);

  // Update greeting once we know the repo name
  useEffect(() => {
    if (activeRepo?.owner && activeRepo?.name) {
      setMessages([{
        role: "assistant",
        content: `👋 Hi! I'm RepoMind AI. I've analyzed **${activeRepo.owner}/${activeRepo.name}** and I'm ready to answer your questions.\n\nAsk me anything about the codebase — architecture, specific files, functions, how to run it, security issues, and more!`,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }]);
    }
  }, [activeRepo?.owner, activeRepo?.name]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async (question = input) => {
    const q = question.trim();
    if (!q || isStreaming) return;

    setInput("");
    setError("");

    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const userMsg = { role: "user", content: q, time: timestamp };
    const assistantMsg = { role: "assistant", content: "", time: timestamp };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    let assistantIdx;
    setMessages((prev) => {
      assistantIdx = prev.length - 1;
      return prev;
    });

    streamChat(
      repoId,
      q,
      (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last.role === "assistant") {
            updated[updated.length - 1] = { ...last, content: last.content + token };
          }
          return updated;
        });
      },
      () => setIsStreaming(false),
      (err) => {
        setError(err || "Failed to get response.");
        setIsStreaming(false);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: `⚠️ Error: ${err}`,
          };
          return updated;
        });
      }
    );
  }, [input, isStreaming, repoId]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "var(--bg-primary)" }}>
      {/* Header */}
      <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)", flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: 10, background: "linear-gradient(135deg, #6366f1, #22d3ee)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <MessageSquare size={18} style={{ color: "white" }} />
          </div>
          <div>
            <h1 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>AI Repository Chat</h1>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Powered by Ollama · {activeRepo?.owner}/{activeRepo?.name}
            </div>
          </div>
          <div style={{ marginLeft: "auto" }}>
            <span className="badge" style={{
              background: ollamaAvailable ? "rgba(16,185,129,0.1)" : "rgba(239,68,68,0.1)",
              color: ollamaAvailable ? "#10b981" : "#ef4444",
              border: `1px solid ${ollamaAvailable ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
              fontSize: 11,
            }}>
              {ollamaAvailable ? "🟢 Ollama Online" : "🔴 Ollama Offline"}
            </span>
          </div>
        </div>
      </div>

      {!ollamaAvailable && (
        <div style={{ padding: "10px 24px", background: "rgba(239,68,68,0.08)", borderBottom: "1px solid rgba(239,68,68,0.2)", flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#f87171" }}>
            <AlertTriangle size={14} />
            Ollama is not running. Start it with: <code style={{ background: "rgba(0,0,0,0.3)", padding: "1px 8px", borderRadius: 4 }}>ollama serve</code>
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px" }}>
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}
        {isStreaming && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)", fontSize: 13, marginBottom: 16 }}>
            <Bot size={14} style={{ color: "var(--accent-primary)" }} />
            <span>Thinking...</span>
            <span style={{ animation: "pulse 1s infinite" }}>▌</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      <div style={{ padding: "8px 24px 0", flexShrink: 0, overflowX: "auto" }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "nowrap", paddingBottom: 8 }}>
          {SUGGESTED_QUESTIONS.slice(0, 6).map((q, i) => (
            <button
              key={i}
              className="btn-ghost"
              style={{ fontSize: 12, padding: "5px 12px", whiteSpace: "nowrap", flexShrink: 0 }}
              onClick={() => sendMessage(q)}
              disabled={isStreaming}
            >
              <Sparkles size={11} style={{ color: "var(--accent-primary)" }} />
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div style={{ padding: "12px 24px 24px", flexShrink: 0, borderTop: "1px solid var(--border)" }}>
        {error && (
          <div style={{ marginBottom: 8, padding: "8px 12px", borderRadius: 8, background: "rgba(239,68,68,0.1)", color: "#ef4444", fontSize: 13 }}>
            {error}
          </div>
        )}
        <div style={{ display: "flex", gap: 12, alignItems: "flex-end" }}>
          <textarea
            ref={inputRef}
            className="input-field"
            style={{ flex: 1, resize: "none", minHeight: 48, maxHeight: 120, lineHeight: 1.5 }}
            placeholder="Ask anything about this repository... (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button
            className="btn-primary"
            style={{ padding: "12px 20px", flexShrink: 0, opacity: isStreaming ? 0.6 : 1 }}
            onClick={() => sendMessage()}
            disabled={isStreaming || !input.trim()}
          >
            {isStreaming
              ? <RefreshCw size={16} className="animate-spin" />
              : <Send size={16} />}
          </button>
        </div>
      </div>
    </div>
  );
}
