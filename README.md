# RepoMind AI 🧠

> AI-powered GitHub repository analysis platform — **100% local, 100% free**.

Paste any public GitHub URL and RepoMind AI will:
- Clone and analyze every source file
- Detect languages, frameworks, and tools
- Generate documentation automatically
- Create architecture diagrams (Mermaid)
- Scan for security vulnerabilities
- Score repository health
- Let you chat with the codebase using Ollama AI

---

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

### 3. Set Up Ollama (for AI Chat)

```bash
# Install Ollama from https://ollama.ai
# Then pull a model:
ollama pull qwen2.5-coder:7b   # Recommended (7B, ~4GB)
# or
ollama pull llama3.2:3b         # Lighter alternative
```

---

## 🗂️ Project Structure

```
repomind-ai/
├── backend/                   # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Settings
│   │   ├── database.py        # SQLite setup
│   │   ├── api/               # API routes
│   │   ├── analyzers/         # Code analyzers
│   │   ├── ai/                # Ollama + FAISS + RAG
│   │   ├── generators/        # Doc + Mermaid generators
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Helpers
│   └── requirements.txt
│
└── frontend/                  # React + Vite + Tailwind
    └── src/
        ├── pages/             # All page components
        ├── components/        # Reusable UI components
        ├── store/             # Zustand state
        └── services/          # API client
```

---

## ⚙️ Configuration

Edit `backend/.env`:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 📋 Features

| Feature | Status |
|---------|--------|
| Repository cloning | ✅ |
| File tree explorer | ✅ |
| Technology detection | ✅ |
| File analysis (AST) | ✅ |
| Security scanning | ✅ |
| Code quality analysis | ✅ |
| Health scoring | ✅ |
| Documentation generation | ✅ |
| Architecture diagrams | ✅ |
| Learning path | ✅ |
| AI chat (RAG) | ✅ (requires Ollama) |
| Vector search (FAISS) | ✅ |
| Streaming responses | ✅ |

---

## 🛠️ Tech Stack

**Backend**: Python · FastAPI · SQLAlchemy · GitPython  
**AI**: Ollama · sentence-transformers · FAISS  
**Frontend**: React · Vite · Tailwind CSS · Zustand  
**Diagrams**: Mermaid.js  

---

*Built with ❤️ using 100% open-source tools.*
