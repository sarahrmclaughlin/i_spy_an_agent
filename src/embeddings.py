"""Embeddings and FAISS index management."""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
from src.knowledge_base import TranslationKB

_model = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_FILE = "faiss_index.bin"
WORDS_FILE = "faiss_words.pkl"

def build_faiss_index():
    """Build FAISS index from KB words"""
    words = list(TranslationKB.DATA.keys())
    vectors = _model.encode(words)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors, dtype=np.float32))
    return index, words

def save_faiss_index(index, words, index_path=INDEX_FILE, words_path=WORDS_FILE):
    """Save FAISS index + words list"""
    faiss.write_index(index, index_path)
    with open(words_path, "wb") as f:
        pickle.dump(words, f)

def load_faiss_index(index_path=INDEX_FILE, words_path=WORDS_FILE):
    """Load FAISS index + words list"""
    if not (os.path.exists(index_path) and os.path.exists(words_path)):
        return None, None
    index = faiss.read_index(index_path)
    with open(words_path, "rb") as f:
        words = pickle.load(f)
    return index, words

def search_faiss(query: str, index, words, top_k=1):
    """Return the closest KB word using FAISS"""
    q_vec = _model.encode([query])
    distances, idxs = index.search(np.array(q_vec, dtype=np.float32), top_k)
    return words[idxs[0][0]], distances[0][0]