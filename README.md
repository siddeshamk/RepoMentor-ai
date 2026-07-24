RepoMind AI 🧠
AI-powered GitHub repository analysis platform — 100% local, 100% free.

Paste any public GitHub URL and RepoMind AI will:

Clone and analyze every source file
Detect languages, frameworks, and tools
Generate documentation automatically
Create architecture diagrams (Mermaid)
Scan for security vulnerabilities
Score repository health
Let you chat with the codebase using Ollama AI
🚀 Quick Start
1. Start the Backend
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
Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

2. Start the Frontend
cd frontend
npm install
npm run dev
Frontend runs at: http://localhost:5173

3. Set Up Ollama (for AI Chat)
# Install Ollama from https://ollama.ai
# Then pull a model:
ollama pull qwen2.5-coder:7b   # Recommended (7B, ~4GB)
# or
ollama pull llama3.2:3b         # Lighter alternative
🗂️ Project Structure
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
⚙️ Configuration
Edit backend/.env:

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
EMBEDDING_MODEL=all-MiniLM-L6-v2
📋 Features
Feature	Status
Repository cloning	✅
File tree explorer	✅
Technology detection	✅
File analysis (AST)	✅
Security scanning	✅
Code quality analysis	✅
Health scoring	✅
Documentation generation	✅
Architecture diagrams	✅
Learning path	✅
AI chat (RAG)	✅ (requires Ollama)
Vector search (FAISS)	✅
Streaming responses	✅
🛠️ Tech Stack
Backend: Python · FastAPI · SQLAlchemy · GitPython
AI: Ollama · sentence-transformers · FAISS
Frontend: React · Vite · Tailwind CSS · Zustand
Diagrams: Mermaid.js
AI Repo Mentor / RepoMind AI 🧠
Production-Ready AI-Powered Repository Intelligence Platform
📌 Project Overview

AI Repo Mentor (RepoMind AI) is an AI-powered software engineering platform that automatically analyzes any public GitHub repository or uploaded ZIP project and generates a complete engineering report.

Unlike traditional code analysis tools that only detect syntax issues or security vulnerabilities, AI Repo Mentor understands the repository as a software architect would. It studies the project's structure, identifies the technologies used, explains the architecture, evaluates code quality, detects security risks, analyzes performance, generates documentation, creates workflow diagrams, and provides an AI assistant capable of answering repository-specific questions.

The platform performs all analysis locally without permanently storing repository source code. Users simply provide a GitHub repository URL or upload a ZIP archive, and the system clones or extracts the project into a temporary workspace, performs live analysis, generates an AI-powered report, and securely deletes the temporary files after completion.

The application is intended for developers, students, software architects, recruiters, open-source contributors, engineering managers, and technical interviewers who need to quickly understand an unfamiliar codebase.

🎯 Problem Statement

Modern software repositories often contain thousands of files spread across multiple technologies and frameworks. Understanding an unfamiliar repository requires significant manual effort.

Developers typically need to answer questions such as:

What technologies are used?
How does the application work?
What is the project architecture?
Is the code secure?
Is the project maintainable?
Which files are most important?
What improvements should be made?
How healthy is the repository overall?

Reading every source file manually can take hours or even days.

AI Repo Mentor automates this entire process.

🎯 Project Goals

The primary objectives of AI Repo Mentor are:

Analyze any GitHub repository automatically
Generate comprehensive engineering reports
Explain repository architecture
Detect technologies and frameworks
Perform static code analysis
Detect security vulnerabilities
Evaluate performance bottlenecks
Assess documentation quality
Score overall repository health
Generate interactive architecture diagrams
Provide repository-aware AI conversations
Export reports in PDF and text formats
👥 Target Users

The platform is designed for:

Software Developers
Full Stack Engineers
Students
Professors
Recruiters
Technical Interviewers
Open Source Contributors
Engineering Managers
Startup Teams
Software Architects
Complete Workflow
                     USER

                       │

                       ▼

       Enter GitHub URL / Upload ZIP

                       │

                       ▼

          Repository Acquisition Layer

       ┌─────────────────────────────┐
       │ Clone GitHub Repository     │
       │ OR                          │
       │ Extract ZIP                 │
       └─────────────────────────────┘

                       │

                       ▼

          Temporary Workspace Created

                       │

                       ▼

             Repository Parsing Engine

        Detect every file and directory

                       │

                       ▼

           Language Detection Engine

        Python
        Java
        JavaScript
        TypeScript
        Go
        Rust
        C#
        C++
        PHP
        Kotlin
        Swift

                       │

                       ▼

        Framework Detection Engine

        React
        Angular
        Vue
        FastAPI
        Flask
        Django
        Express
        Spring Boot
        Laravel
        ASP.NET

                       │

                       ▼

      Dependency Detection Engine

       package.json
       requirements.txt
       pom.xml
       Cargo.toml
       composer.json
       build.gradle

                       │

                       ▼

      Project Architecture Detection

       Frontend

       Backend

       APIs

       Database

       Authentication

       Storage

       Cloud

                       │

                       ▼

         Static Code Analysis Engine

       Semgrep

       Bandit

       Radon

       Tree-sitter

                       │

                       ▼

      Security Vulnerability Scanner

       SQL Injection

       XSS

       Secrets

       Hardcoded Keys

       Command Injection

       Dependency Vulnerabilities

                       │

                       ▼

      Performance Analysis Engine

       Complexity

       Memory

       Bundle Size

       Duplicate Code

       Large Files

                       │

                       ▼

     Documentation Quality Analysis

       README

       Comments

       Installation

       Usage

       Examples

                       │

                       ▼

     AI Repository Understanding Layer

                Ollama

                       │

                       ▼

      Executive Summary Generation

                       │

                       ▼

      Workflow Diagram Generation

                       │

                       ▼

   System Architecture Diagram Generation

                       │

                       ▼

       Repository Health Calculation

                       │

                       ▼

        Improvement Recommendation

                       │

                       ▼

         Repository-aware AI Chat

                       │

                       ▼

          Export PDF / Text Report

                       │

                       ▼

       Temporary Files Deleted
System Architecture
                FRONTEND (Next.js)

─────────────────────────────────────────────

Landing Page

Dashboard

Workflow Viewer

Architecture Viewer

Repository Explorer

AI Chat

Charts

PDF Export

─────────────────────────────────────────────

             REST API

─────────────────────────────────────────────

            FastAPI Backend

─────────────────────────────────────────────

Repository Manager

GitHub Service

ZIP Service

Parser

Analyzer

Architecture Generator

Workflow Generator

Security Scanner

Performance Analyzer

Documentation Analyzer

Rating Engine

Chat Engine

Report Generator

─────────────────────────────────────────────

          Ollama AI Engine

─────────────────────────────────────────────

DeepSeek

Qwen

Llama

Gemma

Mistral

CodeLlama

─────────────────────────────────────────────

Static Analysis Tools

Tree-sitter

Semgrep

Bandit

Radon

Graphviz

NetworkX

─────────────────────────────────────────────

Temporary Workspace

Clone Repository

↓

Analyze

↓

Delete
Repository Analysis Flow

When a user submits a GitHub URL:

GitHub URL

↓

Validate URL

↓

Clone Repository

↓

Temporary Directory

↓

Read every file

↓

Generate File Tree

↓

Detect Technologies

↓

Parse Source Code

↓

Run Static Analysis

↓

Generate Architecture

↓

Generate Workflow

↓

Run Security Scan

↓

Run Performance Scan

↓

Run Documentation Analysis

↓

Generate AI Summary

↓

Calculate Ratings

↓

Generate Report

↓

Delete Repository
ZIP Analysis Flow
Upload ZIP

↓

Validate ZIP

↓

Extract

↓

Temporary Directory

↓

Read Files

↓

Analyze

↓

Generate Report

↓

Delete Files
AI Processing Flow
Repository

↓

Chunks

↓

Embeddings

↓

Vector Index

↓

User Question

↓

Relevant Files Retrieved

↓

Ollama

↓

Repository-aware Response

This is a Retrieval-Augmented Generation (RAG) pipeline. Instead of answering from general knowledge, the AI retrieves the most relevant parts of the analyzed repository, ensuring responses are grounded in the actual codebase.

Repository Scoring Formula

The repository health score is calculated using weighted metrics:

Metric	Weight
Creativity	20%
Code Quality	20%
Architecture	15%
Maintainability	15%
Security	10%
Performance	10%
Documentation	10%

The final score is presented on a scale of 0–10, along with a breakdown for each category.

Key Modules
1. Repository Manager
Clones GitHub repositories
Extracts ZIP files
Manages temporary workspaces
Cleans up after analysis
2. Parser Engine
Reads all project files
Builds the file tree
Detects programming languages
Identifies project structure
3. Technology Detector
Detects frameworks
Identifies databases
Finds package managers
Recognizes cloud services
Detects Docker and CI/CD configurations
4. Static Analysis Engine
AST parsing with Tree-sitter
Code smell detection
Complexity analysis
Duplicate code detection
5. Security Analyzer
SQL Injection
XSS
Hardcoded secrets
Dependency vulnerabilities
Authentication issues
6. Performance Analyzer
Cyclomatic complexity
Large files
Nested loops
Expensive operations
Memory inefficiencies
7. Documentation Analyzer
README quality
API documentation
Installation guide
Usage examples
Code comments
8. AI Engine
Uses Ollama with any installed model
Generates summaries
Answers repository questions
Produces improvement suggestions
Assists with documentation
9. Report Generator
Plain text reports
PDF reports
Architecture diagrams
Workflow diagrams
Repository ratings
Recommendations
Example User Journey
The user opens AI Repo Mentor.
They paste a GitHub repository URL or upload a ZIP archive.
They select an installed Ollama model (e.g., Qwen, DeepSeek, Llama).
The backend clones or extracts the repository into a temporary workspace.
The parser scans the repository and identifies files, languages, frameworks, dependencies, and architecture.
Static analysis tools evaluate code quality, security, performance, and documentation.
Ollama generates an executive summary and improvement recommendations.
The frontend displays interactive dashboards, workflow graphs, architecture diagrams, and repository metrics.
The user can chat with the AI assistant about the repository.
Finally, the user exports a professional PDF or text report, and the temporary repository files are deleted.
Advantages
✅ Fully local analysis (repository code is never permanently stored)
✅ Supports GitHub repositories and ZIP uploads
✅ Live, on-demand analysis (no cached results)
✅ AI-powered repository explanations
✅ Interactive workflow and architecture visualization
✅ Security and performance auditing
✅ Repository-aware AI chat using RAG
✅ Professional PDF report generation
✅ Extensible modular architecture
✅ Open-source friendly
Future Enhancements
Multi-repository comparison
Team collaboration and shared workspaces
Pull Request review automation
Commit history analytics
Test coverage analysis
License compliance checks
Cloud deployment recommendations
CI/CD optimization suggestions
GitHub App integration
Multi-agent AI analysis
Fine-tuned repository embedding models
Incremental re-analysis for updated repositories
Conclusion

AI Repo Mentor is more than a code analysis tool—it is an AI software engineering mentor. By combining repository parsing, static analysis, architecture inference, documentation evaluation, security auditing, performance profiling, and repository-aware conversational AI, it transforms complex codebases into understandable, actionable insights. The platform empowers developers to onboard faster, improve code quality, strengthen security, and make informed architectural decisions through a polished, interactive experience.
