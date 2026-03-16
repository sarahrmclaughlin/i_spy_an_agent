import logging

from src.index_manager import build_or_load_agent, rebuild_agent
from src.llm_fallback import llm_fallback
from src.knowledge_base import update_kb, word_in_kb, get_kb_entry

logger = logging.getLogger(__name__)


def _normalize_query(query: str) -> str:
    """Strip common instruction prefixes and return just the word/phrase.

    E.g. 'Translate water bottle' -> 'water bottle'.

    Args:
        query: The raw query string from the notebook or user.

    Returns:
        The cleaned word/phrase in lowercase.
    """
    stripped = query.strip().lower()
    for prefix in ("translate ", "what is ", "define "):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    return stripped.strip()


def _format_kb_entry(word: str, entry: dict) -> str:
    """Format a KB entry as a human-readable translation string.

    Args:
        word: The English source word.
        entry: The KB dict with 'fr' and 'it' sub-dicts.

    Returns:
        A formatted string, e.g. 'French: le livre\\nItalian: il libro'.
    """
    fr = entry.get("fr", {})
    it = entry.get("it", {})
    fr_article = fr.get("article", "").strip()
    it_article = it.get("article", "").strip()
    fr_str = f"{fr_article} {fr.get('word', '')}".strip()
    it_str = f"{it_article} {it.get('word', '')}".strip()
    return f"French: {fr_str}\nItalian: {it_str}"


def rag_chat(query: str, agent) -> str:
    """Query the vector index agent.

    Args:
        query: The user query string.
        agent: A _SimpleAgent wrapping a LlamaIndex query engine.

    Returns:
        The agent's response as a plain string.
    """
    response = agent.chat(query)
    return str(response)


def rag_chat_pipeline(query: str, agent=None) -> str:
    """RAG pipeline: direct KB lookup -> vector store -> LLM fallback -> KB update.

    Flow:
    1. Normalize the query to extract just the word/phrase.
    2. Check the KB directly (exact match, O(1)) — if found, return immediately
       without touching the vector store or LLM.
    3. If not in KB, call the LLM for a translation.
    4. Persist the new translation to KB and rebuild the vector index.

    Args:
        query: The raw user query, e.g. 'Translate water bottle'.
        agent: An optional pre-built agent. Built on demand if not provided.

    Returns:
        A translation string formatted as 'French: ...\\nItalian: ...'.
    """
    if agent is None:
        agent = build_or_load_agent()

    word = _normalize_query(query)
    logger.info("Checking whether '%s' exists in Knowledge Base...", word)

    # --- Step 1: Direct exact-match lookup in kb.json ---
    entry = get_kb_entry(word)
    if entry is not None:
        logger.info("'%s' found in Knowledge Base (direct lookup) — skipping LLM.", word)
        return _format_kb_entry(word, entry)

    # --- Step 2: Word not in KB — call LLM for translation ---
    logger.info("'%s' not found in Knowledge Base — calling LLM API.", word)
    response = llm_fallback(word)

    # --- Step 3: Persist to KB and rebuild the vector index ---
    update_kb(word, response)
    agent = rebuild_agent()
    logger.info("KB and vector index updated with '%s'.", word)

    return response