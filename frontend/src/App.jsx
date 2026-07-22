import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Sidebar from "./components/layout/Sidebar";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import TreeView from "./pages/TreeView";
import Architecture from "./pages/Architecture";
import ChatPage from "./pages/Chat";
import DocsPage from "./pages/Docs";
import SecurityPage from "./pages/Security";
import HealthPage from "./pages/Health";
import useRepoStore from "./store/repoStore";

export default function App() {
  const location = useLocation();
  const { activeRepoId, checkOllama } = useRepoStore();
  const isHome = location.pathname === "/";

  useEffect(() => {
    checkOllama();
  }, []);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {!isHome && <Sidebar />}
      <main style={{ flex: 1, marginLeft: isHome ? 0 : "var(--sidebar-width)" }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/repo/:repoId/dashboard" element={<Dashboard />} />
          <Route path="/repo/:repoId/tree" element={<TreeView />} />
          <Route path="/repo/:repoId/architecture" element={<Architecture />} />
          <Route path="/repo/:repoId/chat" element={<ChatPage />} />
          <Route path="/repo/:repoId/docs" element={<DocsPage />} />
          <Route path="/repo/:repoId/security" element={<SecurityPage />} />
          <Route path="/repo/:repoId/health" element={<HealthPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
