/**
 * API service layer — all calls to the FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ── Repository API ─────────────────────────────────────────────────────────

export const api = {
  /**
   * Start analyzing a GitHub repository.
   * Returns { repo_id, status }
   */
  analyzeRepo: (url) =>
    request("/api/repos/analyze", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  /** Poll analysis status. */
  getStatus: (repoId) => request(`/api/repos/${repoId}/status`),

  /** Get full repo data (after analysis). */
  getRepo: (repoId) => request(`/api/repos/${repoId}`),

  /** Get repository list. */
  listRepos: () => request("/api/repos/"),

  /** Get file tree. */
  getTree: (repoId) => request(`/api/repos/${repoId}/tree`),

  /** Get analysis for a specific file. */
  getFileAnalysis: (repoId, filePath) =>
    request(`/api/repos/${repoId}/file?path=${encodeURIComponent(filePath)}`),

  /** Get tech stack. */
  getTech: (repoId) => request(`/api/repos/${repoId}/tech`),

  /** Get security findings. */
  getSecurity: (repoId) => request(`/api/repos/${repoId}/security`),

  /** Get quality report. */
  getQuality: (repoId) => request(`/api/repos/${repoId}/quality`),

  /** Get health scores. */
  getHealth: (repoId) => request(`/api/repos/${repoId}/health`),

  /** Get architecture and diagrams. */
  getArchitecture: (repoId) => request(`/api/repos/${repoId}/architecture`),

  /** Get documentation. */
  getDocs: (repoId, section = "all") =>
    request(`/api/docs/${repoId}?section=${section}`),

  /** Delete a repository. */
  deleteRepo: (repoId) =>
    request(`/api/repos/${repoId}`, { method: "DELETE" }),

  /** Health check. */
  healthCheck: () => request("/api/health"),
};

// ── Streaming Chat ─────────────────────────────────────────────────────────

/**
 * Stream a chat response using Server-Sent Events.
 * @param {string} repoId
 * @param {string} question
 * @param {(token: string) => void} onToken - called for each token
 * @param {() => void} onDone - called when streaming ends
 * @param {(err: string) => void} onError - called on error
 */
export function streamChat(repoId, question, onToken, onDone, onError) {
  let buffer = "";

  fetch(`${BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_id: repoId, question }),
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        onError(err.detail || `HTTP ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          onDone();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              onDone();
              return;
            }
            // Restore newlines that were escaped in SSE
            const token = data.replace(/\\n/g, "\n");
            onToken(token);
          }
        }
      }
    })
    .catch((err) => onError(err.message));
}
