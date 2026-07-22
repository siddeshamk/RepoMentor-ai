@echo off
echo Starting RepoMind AI Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt -q
if not exist .env (
    copy .env.example .env
    echo Created .env from .env.example
)
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
