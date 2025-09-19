import os
import json

KB_PATH = "./configs/kb.json"

def load_kb():
    with open(KB_PATH, "r") as f:
        return json.load(f)

def save_kb(kb):
    with open(KB_PATH, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

def update_kb(english_word: str, response: str):
    """
    Save new word translations to KB.
    Assumes response is formatted like:
    'French: le livre\nItalian: il libro'
    """
    kb = load_kb()

    fr_line = [line for line in response.splitlines() if line.startswith("French")][0]
    it_line = [line for line in response.splitlines() if line.startswith("Italian")][0]

    fr = fr_line.replace("French:", "").strip().split(" ", 1)
    it = it_line.replace("Italian:", "").strip().split(" ", 1)

    kb[english_word] = {
        "fr": {"article": fr[0], "word": fr[1]},
        "it": {"article": it[0], "word": it[1]},
    }

    save_kb(kb)