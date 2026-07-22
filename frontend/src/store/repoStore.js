/**
 * Zustand global store for repository state.
 */
import { create } from "zustand";
import { api } from "../services/api";

const useRepoStore = create((set, get) => ({
  // Currently active repository
  activeRepo: null,
  activeRepoId: null,

  // Analysis status polling
  analysisStatus: null,
  analysisProgress: 0,
  analysisMessage: "",

  // Cached data (loaded on demand)
  tree: null,
  tech: null,
  security: null,
  quality: null,
  health: null,
  architecture: null,
  docs: null,
  fileAnalysis: null,

  // Recent repos list
  recentRepos: [],

  // Ollama status
  ollamaAvailable: null,

  // UI
  loading: {},
  errors: {},

  // ── Actions ──────────────────────────────────────────────────────────────

  setLoading: (key, value) =>
    set((s) => ({ loading: { ...s.loading, [key]: value } })),

  setError: (key, value) =>
    set((s) => ({ errors: { ...s.errors, [key]: value } })),

  clearError: (key) =>
    set((s) => {
      const e = { ...s.errors };
      delete e[key];
      return { errors: e };
    }),

  startAnalysis: async (url) => {
    set({ analysisStatus: "pending", analysisProgress: 0, analysisMessage: "Connecting..." });
    const result = await api.analyzeRepo(url);
    set({ activeRepoId: result.repo_id, analysisStatus: result.status });
    return result.repo_id;
  },

  pollStatus: async (repoId) => {
    const { analysisStatus } = get();
    if (analysisStatus === "complete" || analysisStatus === "error") return;

    try {
      const status = await api.getStatus(repoId);
      set({
        analysisStatus: status.status,
        analysisProgress: status.progress,
        analysisMessage: status.message || "",
      });

      if (status.status === "complete") {
        await get().loadRepo(repoId);
      }
    } catch (e) {
      set({ analysisStatus: "error", analysisMessage: e.message });
    }
  },

  loadRepo: async (repoId) => {
    set({ loading: { ...get().loading, repo: true } });
    try {
      const repo = await api.getRepo(repoId);
      // Clear stale cache if switching repos
      const prevId = get().activeRepoId;
      const cacheReset = prevId && prevId !== repoId
        ? { tree: null, tech: null, security: null, quality: null, health: null, architecture: null, docs: null, fileAnalysis: null }
        : {};
      set({
        activeRepo: repo,
        activeRepoId: repoId,
        analysisStatus: repo.status,
        analysisProgress: repo.progress || (repo.status === "complete" ? 100 : 0),
        analysisMessage: repo.progress_message || "",
        ...cacheReset,
      });
    } catch (e) {
      set((s) => ({ errors: { ...s.errors, repo: e.message } }));
    } finally {
      set((s) => ({ loading: { ...s.loading, repo: false } }));
    }
  },

  loadTree: async (repoId) => {
    if (get().tree) return get().tree;
    set((s) => ({ loading: { ...s.loading, tree: true } }));
    try {
      const tree = await api.getTree(repoId);
      set({ tree });
      return tree;
    } finally {
      set((s) => ({ loading: { ...s.loading, tree: false } }));
    }
  },

  loadTech: async (repoId) => {
    if (get().tech) return get().tech;
    const tech = await api.getTech(repoId);
    set({ tech });
    return tech;
  },

  loadSecurity: async (repoId) => {
    if (get().security) return get().security;
    set((s) => ({ loading: { ...s.loading, security: true } }));
    try {
      const security = await api.getSecurity(repoId);
      set({ security });
      return security;
    } finally {
      set((s) => ({ loading: { ...s.loading, security: false } }));
    }
  },

  loadQuality: async (repoId) => {
    if (get().quality) return get().quality;
    set((s) => ({ loading: { ...s.loading, quality: true } }));
    try {
      const quality = await api.getQuality(repoId);
      set({ quality });
      return quality;
    } finally {
      set((s) => ({ loading: { ...s.loading, quality: false } }));
    }
  },

  loadHealth: async (repoId) => {
    if (get().health) return get().health;
    set((s) => ({ loading: { ...s.loading, health: true } }));
    try {
      const health = await api.getHealth(repoId);
      set({ health });
      return health;
    } finally {
      set((s) => ({ loading: { ...s.loading, health: false } }));
    }
  },

  loadArchitecture: async (repoId) => {
    if (get().architecture) return get().architecture;
    set((s) => ({ loading: { ...s.loading, architecture: true } }));
    try {
      const arch = await api.getArchitecture(repoId);
      set({ architecture: arch });
      return arch;
    } finally {
      set((s) => ({ loading: { ...s.loading, architecture: false } }));
    }
  },

  loadDocs: async (repoId) => {
    if (get().docs) return get().docs;
    set((s) => ({ loading: { ...s.loading, docs: true } }));
    try {
      const docs = await api.getDocs(repoId);
      set({ docs });
      return docs;
    } finally {
      set((s) => ({ loading: { ...s.loading, docs: false } }));
    }
  },

  loadFileAnalysis: async (repoId, filePath) => {
    const analysis = await api.getFileAnalysis(repoId, filePath);
    set({ fileAnalysis: { path: filePath, data: analysis } });
    return analysis;
  },

  loadRecentRepos: async () => {
    try {
      const repos = await api.listRepos();
      set({ recentRepos: repos });
      return repos;
    } catch {
      return [];
    }
  },

  checkOllama: async () => {
    try {
      const health = await api.healthCheck();
      set({ ollamaAvailable: health.ollama });
    } catch {
      set({ ollamaAvailable: false });
    }
  },

  resetRepo: () =>
    set({
      activeRepo: null,
      activeRepoId: null,
      tree: null,
      tech: null,
      security: null,
      quality: null,
      health: null,
      architecture: null,
      docs: null,
      fileAnalysis: null,
      analysisStatus: null,
      analysisProgress: 0,
    }),
}));

export default useRepoStore;
