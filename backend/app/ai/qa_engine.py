"""
QA Engine: Retrieval-Augmented Generation (RAG) for repository Q&A.
Combines FAISS semantic search with Ollama LLM for grounded answers.
"""
from typing import AsyncGenerator

from app.ai.ollama_client import ollama
from app.ai.vector_store import VectorStore
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are RepoMind AI — an expert software engineer assistant that analyzes GitHub repositories.
You have been given context from a specific repository. Use ONLY this context to answer questions.
If you don't know the answer based on the provided context, say so honestly.
Be specific, mention file names and line numbers when relevant.
Format your responses clearly with markdown when appropriate."""


def build_prompt(question: str, context_chunks: list[dict], repo_meta: dict) -> str:
    """Build a RAG prompt combining retrieved context with the user question."""
    repo_name = repo_meta.get("name", "Unknown")
    owner = repo_meta.get("owner", "")
    tech = repo_meta.get("tech_stack", {})

    # Build context string from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        file_ref = chunk.get("file", "unknown")
        chunk_type = chunk.get("type", "general")
        text = chunk.get("text", "")
        context_parts.append(f"[{i}] ({file_ref})\n{text}")

    context_str = "\n\n".join(context_parts)

    # Build primary language info
    primary_lang = ""
    if tech:
        primary_lang = tech.get("primary_language", "")
        frameworks = [f["name"] for f in tech.get("frameworks", [])][:5]
        tech_str = f"{primary_lang}" + (f", {', '.join(frameworks)}" if frameworks else "")
    else:
        tech_str = "Unknown"

    prompt = f"""Repository: {owner}/{repo_name}
Tech Stack: {tech_str}

=== RELEVANT CONTEXT FROM REPOSITORY ===
{context_str}

=== USER QUESTION ===
{question}

=== YOUR ANSWER ==="""

    return prompt


class QAEngine:
    """Repository Q&A engine using RAG (FAISS + Ollama)."""

    async def answer_stream(
        self,
        question: str,
        repo_id: str,
        repo_meta: dict,
    ) -> AsyncGenerator[str, None]:
        """
        Stream an answer to a question about the repository.
        Uses FAISS to retrieve relevant context, then Ollama to generate.
        """
        # Check Ollama availability
        if not await ollama.is_available():
            yield (
                "❌ **Ollama is not running.**\n\n"
                "To enable AI chat:\n"
                "1. Install Ollama: https://ollama.ai\n"
                f"2. Pull the model: `ollama pull {ollama.model}`\n"
                "3. Start Ollama and refresh the page.\n\n"
                "Other features (tree view, tech detection, docs, security) still work without Ollama."
            )
            return

        # Retrieve relevant chunks from FAISS
        vector_store = VectorStore(repo_id)
        context_chunks = vector_store.search(question, k=8)

        if not context_chunks:
            logger.warning(f"No FAISS context found for repo {repo_id}. Answering without context.")
            context_chunks = []

        # Build the prompt
        prompt = build_prompt(question, context_chunks, repo_meta)

        logger.info(
            f"Answering question for {repo_id}: '{question[:60]}...' "
            f"with {len(context_chunks)} context chunks"
        )

        # Stream from Ollama
        async for token in ollama.generate_stream(prompt, system=SYSTEM_PROMPT):
            yield token

    async def answer(
        self,
        question: str,
        repo_id: str,
        repo_meta: dict,
    ) -> str:
        """Non-streaming version of answer (for internal use)."""
        if not await ollama.is_available():
            return "Ollama is not running. Start Ollama to enable AI chat."

        vector_store = VectorStore(repo_id)
        context_chunks = vector_store.search(question, k=6)
        prompt = build_prompt(question, context_chunks, repo_meta)

        return await ollama.generate(prompt, system=SYSTEM_PROMPT)


# Singleton
qa_engine = QAEngine()
