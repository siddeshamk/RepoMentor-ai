<<<<<<< HEAD
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
=======
# RepoMentor-ai
An AI-powered system that analyses a Git repository, reconstructs its architecture, teaches the source code in execution order, explains each component step by step, predicts code-change impact, and recommends project improvements.
🚀 RepoMentor AI

AI-Powered Git Repository Analysis, Code Learning, and Project Improvement System

RepoMentor AI is an intelligent AI and Machine Learning-based developer tool designed to analyze a Git repository, understand its architecture, explain the source code step by step, and provide practical recommendations to improve the overall project.

The main goal of RepoMentor AI is to make complex and unfamiliar repositories easier to understand for students, developers, and contributors.

Instead of manually exploring hundreds of files, users can provide a Git repository and allow RepoMentor AI to automatically reconstruct the project structure, identify important components, and generate a guided learning path.

---

💡 Problem Statement

Understanding an unfamiliar software repository can be difficult and time-consuming.

Developers and students often face problems such as:

- Not knowing where to start reading the code.
- Difficulty understanding the relationship between files.
- Complex project architectures.
- Limited or outdated documentation.
- Difficulty understanding the execution flow.
- Identifying code quality and architecture issues.
- Predicting the impact of modifying or removing code.

RepoMentor AI aims to solve these problems using AI-powered code intelligence and repository analysis.

---

🎯 Project Objectives

RepoMentor AI is designed to:

- Analyze complete Git repositories.
- Understand the purpose of a software project.
- Detect programming languages, frameworks, and technologies.
- Reconstruct the project architecture.
- Identify important files, classes, and functions.
- Explain source code step by step.
- Generate the correct learning order for understanding a project.
- Identify code quality and architecture issues.
- Recommend practical project improvements.
- Analyze the possible impact of code changes.
- Generate a personalized project learning roadmap.

---

🔍 Repository Analysis

After receiving a repository, RepoMentor AI analyzes:

- Folder structure
- Source code files
- Functions
- Classes
- Imports
- Dependencies
- API routes
- Database connections
- Machine Learning models
- Configuration files
- Application entry points

The system then generates a high-level explanation of the project.

Example

Project Type: AI Image Detection Web Application

Purpose:
Allows users to upload images and detect objects using a Machine Learning model.

Technology Stack:
React, Python, FastAPI, YOLO, and PostgreSQL

---

🏗️ Project Architecture Reconstruction

RepoMentor AI automatically reconstructs the application's execution flow.

Example:

User Uploads Image
        ↓
React Frontend
        ↓
API Request
        ↓
FastAPI Backend
        ↓
Image Preprocessing
        ↓
Machine Learning Model
        ↓
Prediction
        ↓
Result Displayed to User

This allows users to quickly understand how data moves through the application.

---

👨‍🏫 Step-by-Step Code Teaching Mode

One of the core features of RepoMentor AI is its intelligent code teaching system.

Instead of explaining all files randomly, the AI determines the recommended order for learning the repository.

Example:

main.py
   ↓
routes.py
   ↓
auth.py
   ↓
database.py
   ↓
model.py
   ↓
utils.py

The AI explains each file and important code component step by step.

Example

app = FastAPI()

Explanation:

"FastAPI()" creates the main backend application instance used to define APIs and manage the backend application.

Next:

app.include_router(auth_router)

Explanation:

This line connects the authentication routes to the main FastAPI application.

After completing the explanation of "main.py", RepoMentor AI recommends the next file to study.

This creates an AI-generated repository learning path.

---

🚀 AI Project Improvement Engine

RepoMentor AI analyzes the repository and identifies possible improvements.

Example:

Project Improvement Score: 64/100

Possible issues detected:

- Duplicate code.
- Missing error handling.
- Inefficient Machine Learning model loading.
- Poor database query structure.
- Missing automated tests.
- Architecture scalability issues.
- Code maintainability problems.

The system explains:

1. What the problem is.
2. Why the problem matters.
3. Which files are affected.
4. How the project can be improved.

Example

Problem:

The Machine Learning model is loaded for every API request.

Why it matters:

Repeated model loading increases memory usage and application response time.

Current architecture:

Request → Load Model → Predict
Request → Load Model → Predict

Recommended architecture:

Application Start → Load Model

Request → Predict
Request → Predict
Request → Predict

---

🔄 Code Change Impact Analysis

RepoMentor AI analyzes how modifying or removing a code component may affect the project.

Example:

def verify_token():

If a user asks:

«What happens if I remove this function?»

The system analyzes the dependency graph.

verify_token()
       ↓
Authentication Middleware
       ↓
/profile
/dashboard
/admin

RepoMentor AI may report:

Impact Level: HIGH

The verify_token() function is connected to multiple protected routes.
Removing or modifying this function may affect authentication behavior.

This feature helps developers understand code dependencies before making changes.

---

🧠 Personalized Project Learning Roadmap

RepoMentor AI identifies the technologies and concepts required to understand a repository.

Example:

Recommended Learning Path

1. Python Functions
2. Python Modules
3. REST API Fundamentals
4. FastAPI
5. JSON
6. Authentication
7. JWT
8. Database Connectivity
9. Machine Learning Inference

The system also estimates the project difficulty.

Project Difficulty: Intermediate

---

🤖 AI and Machine Learning Architecture

Git Repository
       ↓
Repository Parser
       ↓
AST Code Analysis
       ↓
Dependency Graph
       ↓
Code Embeddings
       ↓
Project Knowledge Graph
       ↓
Retrieval-Augmented Generation
       ↓
AI Reasoning Layer
     ↙      ↓       ↘
 Explain   Teach   Improve

---

🛠️ Proposed Technology Stack

Frontend

- React
- HTML
- CSS
- JavaScript

Backend

- Python
- FastAPI

Code Analysis

- Tree-sitter
- Python AST

Graph Processing

- NetworkX
- Neo4j

Artificial Intelligence

- Large Language Models
- Code-focused AI Models
- Retrieval-Augmented Generation

Machine Learning

- Code Embeddings
- Repository Component Classification
- Improvement Recommendation Ranking

Vector Database

- FAISS or ChromaDB

---

🌟 Key Features

- Complete Git repository analysis
- Automatic project purpose identification
- Technology stack detection
- Software architecture reconstruction
- AI-generated code learning order
- Step-by-step source code explanation
- Dependency graph generation
- Code change impact analysis
- Project improvement recommendations
- Project quality scoring
- Personalized learning roadmap
- AI-powered repository question answering

---

🔮 Future Scope

Future versions of RepoMentor AI may include:

- Automatic code refactoring.
- AI-generated documentation.
- Visual architecture diagrams.
- Pull request analysis.
- Automatic test generation.
- Repository comparison.
- Team onboarding assistance.
- Voice-based code teaching.
- IDE extensions.
- Real-time repository monitoring.

---

📌 Project Title

RepoMentor AI: An Intelligent Repository Comprehension, Adaptive Code Teaching, and Software Improvement Recommendation Framework

📖 Project Description

RepoMentor AI is an AI-powered repository intelligence system that analyzes software repositories, reconstructs project architecture and execution flow, explains source code step by step in an intelligent learning order, analyzes code-change impact, and provides practical recommendations to improve software quality and maintainability.
>>>>>>> 065e72b2e3c1e837d7cdfdad127b1ea7d33cc6d0
