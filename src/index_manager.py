"""Index manager for LlamaIndex vector store. We build the dictionary here."""

import os
import json
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
# agent utilities changed between versions — we'll wrap the query engine
# with a simple object that exposes a `.chat()` method used by the notebook.

KB_PATH = "./configs/kb.json"
STORAGE_DIR = "./storage"

embed_model = OpenAIEmbedding()
llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# 🧩 STEP 1: Prepare KB into LlamaIndex Documents
def prep_data(kb_path: str = KB_PATH):
    """Load KB JSON and turn into LlamaIndex documents"""
    with open(kb_path, "r") as f:
        kb = json.load(f)

    docs = []
    for eng, translations in kb.items():
        fr = f"{translations['fr']['article']} {translations['fr']['word']}"
        it = f"{translations['it']['article']} {translations['it']['word']}"
        text = f"English: {eng}\nFrench: {fr}\nItalian: {it}"
        docs.append(Document(text=text))

    return docs

# 🧩 STEP 2: Build or load index (RAG vector store)
def build_or_load_agent():
    """Load index if exists, otherwise build. Wrap with FunctionAgent."""
    if os.path.exists(STORAGE_DIR):
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    else:
        docs = prep_data()
        index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
        index.storage_context.persist(persist_dir=STORAGE_DIR)

    # Build a query engine and return a light wrapper with a `chat` method
    query_engine = index.as_query_engine(similarity_top_k=1)

    class _SimpleAgent:
        def __init__(self, qe):
            self._qe = qe

        def chat(self, prompt: str):
            # delegate to the query engine's query method
            return self._qe.query(prompt)

    return _SimpleAgent(query_engine)

# 🧩 STEP 3: Rebuild index after KB changes
def rebuild_agent():
    """Rebuild index from KB and return a fresh FunctionAgent"""
    docs = prep_data()
    index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
    index.storage_context.persist(persist_dir=STORAGE_DIR)

    query_engine = index.as_query_engine(similarity_top_k=1)

    class _SimpleAgent:
        def __init__(self, qe):
            self._qe = qe

        def chat(self, prompt: str):
            return self._qe.query(prompt)

    return _SimpleAgent(query_engine)