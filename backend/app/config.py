"""
Application configuration using pydantic-settings.
All values can be overridden via environment variables or a .env file.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b"
    ollama_timeout: int = 120

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Database
    database_url: str = "sqlite+aiosqlite:///./repomind.db"

    # File system paths
    repos_dir: Path = Path("./cloned_repos")
    indices_dir: Path = Path("./faiss_indices")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Analysis limits
    max_file_size_mb: int = 2
    max_repo_size_mb: int = 500
    max_files_to_analyze: int = 2000


settings = Settings()
