# CLAUDE.md

## Project Overview

**i_spy_an_agent** is a learning project for building LLM API calls and RAG (Retrieval-Augmented Generation) agents. The core use case is English-to-French/Italian word translation using a knowledge base with LLM fallback.

## Key Files

- `my_first_language_agent.ipynb` — basic LLM API call notebook (OpenAI)
- `my_first_RAG_language_agent.ipynb` — RAG pipeline notebook using LlamaIndex + OpenAI
- `src/index_manager.py` — builds/loads LlamaIndex vector store from the KB
- `src/rag_chat.py` — RAG query pipeline with LLM fallback and KB auto-update
- `src/knowledge_base.py` — load/save/update `configs/kb.json`
- `src/embeddings.py` — FAISS-based embedding index (sentence-transformers)
- `src/llm_fallback.py` — OpenAI fallback when KB has no answer
- `src/prompt_builder.py` — builds translation prompt for the LLM
- `configs/kb.json` — the translation knowledge base (English → French/Italian)
- `storage/` — persisted LlamaIndex vector store

## Architecture

```
Query → RAG (LlamaIndex vector store) → answer found? return it
                                      → not found? → LLM fallback (gpt-4o-mini)
                                                    → update KB + rebuild index
```

## Environment Setup

Requires an OpenAI API key in `.env`:
```
OPENAI_API_KEY=sk-...
```

Dependencies are managed via `pyproject.toml` with `uv`. Install with:
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

The project uses a `.venv` virtual environment — activate before running notebooks.

## Models Used

- **LLM**: `gpt-4o-mini` (OpenAI) via `llama-index-llms-openai`
- **Embeddings**: `OpenAIEmbedding` (LlamaIndex) for the vector store; `all-MiniLM-L6-v2` (sentence-transformers) for the FAISS index

## Key Constraints

- `llama-index` is pinned to `>=0.9.14, <0.10.0` — do not upgrade past 0.10 without significant refactoring
- Python `>=3.10` required
- Never commit `.env` — it is gitignored

## Linting / Style

Run style checks with:
```bash
make check-style   # black, isort, flake8, pylint, pydocstyle on notebooks
make style         # auto-format with black
```

CI runs flake8 on push/PR to `main` (see `.github/workflows/python-package.yml`). Tests are present but currently commented out in CI.

## Knowledge Base Format

`configs/kb.json` structure:
```json
{
  "word": {
    "fr": {"article": "le", "word": "mot"},
    "it": {"article": "il", "word": "parola"}
  }
}
```

The RAG pipeline auto-updates this file when the LLM handles an unknown word, then rebuilds the vector index.

# Workflow Orchestration

### 1. Work in Plan Mode first (by defaults)
- Start plan mode first for non easy, straightforward tasks
- Ask questions

### 2. Self-improvement Loop (lessons_learned.md)

- Update lessons_learned.md:
  - After any user corrections or clarifications 
  - After debugging failures
- Create rules to prevent same mistakes
- Make sure to review at start of each session
