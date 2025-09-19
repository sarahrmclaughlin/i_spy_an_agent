from src.index_manager import build_or_load_chat_engine, rebuild_index
from src.llm_fallback import llm_fallback
from src.knowledge_base import update_kb

# Create chat engine (load or build)
chat_engine = build_or_load_chat_engine()

def rag_chat(query: str, chat_engine=chat_engine):
    """Query the index and return response"""
    response = chat_engine.chat(query)
    return response.response.strip()

def rag_chat_pipeline(query: str):
    """
    Full pipeline:
    1. Try RAG
    2. If no useful result, fallback to LLM
    3. Save new word in KB + rebuild index
    """
    response = rag_chat(query)

    if "I don't know" in response or response.strip() == "":
        # fallback to LLM
        response = llm_fallback(query)

        # save into KB + rebuild index
        update_kb(query, response)
        rebuild_index()

    return response