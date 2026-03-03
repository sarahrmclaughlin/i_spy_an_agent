from index_manager import build_or_load_agent, rebuild_agent
from llm_fallback import llm_fallback
from knowledge_base import update_kb

def rag_chat(query: str, agent):
    """Query the agent (vector index wrapped in FunctionAgent)"""
    response = agent.chat(query)
    return str(response)

def rag_chat_pipeline(query: str, agent=None):
    """RAG pipeline with fallback and KB update"""
    if agent is None:
        agent = build_or_load_agent()

    response = rag_chat(query, agent).strip()

    if "I don't know" in response or response.strip() == "":
        # Fall back to LLM
        response = llm_fallback(query)
        # Update KB and rebuild agent
        update_kb(query, response)
        agent = rebuild_agent()

    return response