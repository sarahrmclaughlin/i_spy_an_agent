import logging

from src.index_manager import build_or_load_agent, rebuild_agent
from src.llm_fallback import llm_fallback
from src.knowledge_base import update_kb

logger = logging.getLogger(__name__)

def rag_chat(query: str, agent):
    """Query the agent (vector index wrapped in FunctionAgent)"""
    response = agent.chat(query)
    return str(response)

def rag_chat_pipeline(query: str, agent=None):
    """RAG pipeline with fallback and KB update"""
    if agent is None:
        agent = build_or_load_agent()

    logger.info("Checking whether '%s' exists in Knowledge Base...", query)
    response = rag_chat(query, agent).strip()

    if "I don't know" in response or response.strip() == "":
        logger.info("'%s' not found in Knowledge Base — calling LLM API", query)
        response = llm_fallback(query)
        update_kb(query, response)
        agent = rebuild_agent()
    else:
        logger.info("'%s' found in Knowledge Base", query)

    return response