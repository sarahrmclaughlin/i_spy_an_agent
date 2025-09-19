"""Index manager for LlamaIndex vector store. We build the dictionary here."""

import os
import json
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()

def prep_data(kb_path: str = "./configs/kb.json"):
    """Load KB JSON and turn into LlamaIndex documents"""
    with open(kb_path, "r") as f:
        kb = json.load(f)

    # Convert into text docs for embedding
    docs = []
    for eng, translations in kb.items():
        fr = f"{translations['fr']['article']} {translations['fr']['word']}"
        it = f"{translations['it']['article']} {translations['it']['word']}"
        text = f"English: {eng}\nFrench: {fr}\nItalian: {it}"
        docs.append(text)

    from llama_index.core import Document
    return [Document(text) for text in docs]

def build_or_load_chat_engine():
    """Load index if exists, else build new one from KB"""
    if os.path.exists("./storage"):
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    else:
        docs = prep_data()
        index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
        index.storage_context.persist(persist_dir="./storage")
    return index.as_chat_engine(similarity_top_k=1)

def rebuild_index():
    """Rebuild index after KB update"""
    docs = prep_data()
    index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
    index.storage_context.persist(persist_dir="./storage")
    return index.as_chat_engine(similarity_top_k=1)