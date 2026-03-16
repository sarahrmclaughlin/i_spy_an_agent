---
name: KB lookup bug - LlamaIndex query engine synthesizes answers
description: Root cause of false KB hits and missing KB updates; how the pipeline was fixed
type: feedback
---

## The Core Bug (fixed 2026-03-16)

The original `rag_chat_pipeline` relied on the LlamaIndex `VectorStoreIndex.as_query_engine()` to detect KB misses. This was fundamentally broken:

- LlamaIndex's default query engine wraps an LLM synthesizer. Even when `similarity_top_k=1` retrieves a completely unrelated document, the LLM synthesizes a valid-looking answer using its own general knowledge.
- The "I don't know" sentinel check (`if "I don't know" in response`) therefore never triggered — the LLM always produced a response — so the LLM fallback path was never reached and the KB was never updated.

## Fix Applied

Replaced the vector store check with a direct O(1) exact-match lookup against `kb.json` BEFORE touching the vector store or LLM:

```
query -> normalize (strip "Translate " prefix) -> get_kb_entry(word)
       -> found: format and return (no LLM, no vector store)
       -> not found: llm_fallback(word) -> update_kb() -> rebuild_agent()
```

The vector store / query engine is still built and persisted for future semantic search capability, but the routing decision is now made by the direct KB dict lookup.

## Related Bugs Fixed in the Same Session

1. **Query normalization missing**: Notebook sent "Translate water bottle" but KB stored "water bottle". Added `_normalize_query()` to strip known prefixes and lowercase.

2. **`update_kb` IndexError on no-article responses**: `split(" ", 1)` on a word without an article (e.g. "French: bouteille") returns a list of length 1; accessing `[1]` crashed. Fixed by extracting `_parse_translation_line()` that returns `("", word)` when no article is present.

3. **Module-level `client = OpenAI()`**: Instantiating the client at import time in `llm_fallback.py` caused an `OpenAIError` when any module in the import chain was loaded without `OPENAI_API_KEY` set. Moved client instantiation inside the function.

4. **Notebook cell 8 schema mismatch**: Checked for `"entries"` key that does not exist in the flat-dict KB format. Replaced with a correct check that counts top-level word keys.

5. **Relative KB path**: `"./configs/kb.json"` in `knowledge_base.py` depends on cwd. Changed to `Path(__file__).parent.parent / "configs" / "kb.json"` for consistent resolution regardless of caller cwd.

## Key lesson

Never use a generative LLM query engine as a "does this document exist?" gate. The LLM will always generate something. Use an exact dict lookup for that gate, and reserve the LLM for generation only.
