# Lessons Learned

Actionable rules derived from debugging sessions. Each rule describes the mistake, why it happens, and how to prevent it.

---

## Rule 1: Never use a generative LLM query engine as a KB-miss detector

**Mistake:** `rag_chat_pipeline` used `agent.chat(query)` (a LlamaIndex `VectorStoreIndex` query engine) to detect whether a word existed in the knowledge base. The pipeline treated any response that did not contain `"I don't know"` as a KB hit.

**Why it fails:** LlamaIndex's default query engine wraps an LLM synthesizer. The synthesizer is given the retrieved document as context, but it does not restrict itself to that context — it draws on its own general knowledge to produce a confident, well-formatted answer even when the retrieved document is completely unrelated to the query. For a translation use case, this means the LLM will always return a plausible French/Italian translation, regardless of whether the word is in the KB. The `"I don't know"` sentinel is never triggered.

**Rule:** Use the LLM query engine for _generation_, not for _existence checks_. For KB-miss detection, always perform a direct exact-match lookup against the underlying data store (e.g., a dict key lookup on `kb.json`) before touching any LLM-powered component. The gate must be deterministic; LLM output is not deterministic.

```python
# Correct pattern
entry = get_kb_entry(word)          # O(1) dict lookup — deterministic
if entry is not None:
    return format_entry(entry)      # KB hit: no LLM involved
response = llm_fallback(word)       # KB miss: call LLM only here
```

---

## Rule 2: Normalize queries before any KB lookup or storage operation

**Mistake:** The notebook sent queries as `"Translate water bottle"` but the KB stored and looked up entries under the bare key `"water bottle"`. There was no normalization step, so lookup always missed even for words that had been previously stored.

**Why it happens:** Notebook cells are written for readability (`"Translate dog"` is a natural instruction) but the KB is a data store that should use canonical keys. Without an explicit normalization step at the boundary, the two formats drift.

**Rule:** Define a single `normalize_query(query)` function and call it as the first step in the pipeline, before any KB read or write. Normalization must at minimum:
- Strip known instruction prefixes (`"translate "`, `"what is "`, `"define "`)
- Lowercase the result
- Strip surrounding whitespace

The same normalized form must be used for both lookup (`get_kb_entry`) and storage (`update_kb`). Never write a raw user-facing query string as a KB key.

---

## Rule 3: Parse LLM responses defensively — never assume a fixed token count

**Mistake:** `update_kb` parsed LLM output with `split(" ", 1)` and immediately accessed index `[0]` (article) and `[1]` (word). When the LLM returned a word without an article (e.g., `"French: bouteille"` instead of `"French: la bouteille"`), the split produced a list of length 1 and `[1]` raised `IndexError`, silently crashing the KB write.

**Why it happens:** LLM output format is not guaranteed. Even with an explicit format instruction in the prompt, the model may omit the article for proper nouns, acronyms, or words it considers invariable. The code assumed a two-token structure with no fallback.

**Rule:** Always check `len(parts)` before indexing into a split of LLM output. Extract parsing into a dedicated helper that returns a safe default and never raises. Wrap the entire parse block in a `try/except` that logs a warning and skips the write rather than propagating an exception:

```python
def _parse_translation_line(line, lang_prefix):
    value = line.replace(f"{lang_prefix}:", "").strip()
    parts = value.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]   # article, word
    return "", parts[0]             # no article — store empty string
```

Also validate that the expected language lines are present in the response before attempting to parse them. If either is missing, log and return early — do not write a partial entry to the KB.

---

## Rule 4: Never instantiate API clients at module level

**Mistake:** `llm_fallback.py` created `client = OpenAI()` at module scope (top level, outside any function). This caused an `OpenAIError` whenever the module was imported without `OPENAI_API_KEY` already set in the environment — including during notebook setup cells that run before `load_dotenv()`.

**Why it happens:** Module-level code executes at import time. Any module in the import chain that instantiates an API client will fail if the environment is not yet fully configured. This is especially common in notebooks where environment setup cells may run in a different order than imports.

**Rule:** Always instantiate API clients (OpenAI, Anthropic, etc.) _inside_ the function that uses them, not at module level. The client is cheap to construct and the key is read from the environment at call time, which is when the environment is guaranteed to be configured:

```python
# Wrong — fails at import time if key not set
client = OpenAI()

def llm_fallback(query):
    return client.chat.completions.create(...)

# Correct — key required only when the function is actually called
def llm_fallback(query):
    client = OpenAI()
    return client.chat.completions.create(...)
```

---

## Rule 5: Validate KB schema assumptions against the actual file format before writing notebook cells

**Mistake:** A notebook cell validated the KB on startup by checking `"entries" not in kb_data`, assuming the KB was structured as `{"entries": [...]}`. The actual format is a flat word-keyed dict `{"word": {"fr": {...}, "it": {...}}}`. The schema mismatch caused a misleading warning and reset `kb_data` to an incorrect empty structure.

**Why it happens:** Notebook validation cells are often written speculatively (before the KB format is finalized) or copied from a different project. The actual `configs/kb.json` file is the source of truth, but it was not consulted when writing the cell.

**Rule:** Before writing any notebook cell that reads or validates the KB, open `configs/kb.json` and confirm its top-level structure. Use the existing `load_kb()` function from `src/knowledge_base.py` rather than re-implementing the read inline — this keeps validation in sync with the module's own parsing logic. Validate the type and top-level key shape of the loaded dict, not the presence of internal keys that may change:

```python
# Correct — uses the module's own loader and validates actual format
from src.knowledge_base import load_kb

kb_data = load_kb()
assert isinstance(kb_data, dict), f"Expected dict, got {type(kb_data)}"
print(f"Loaded KB with {len(kb_data)} word(s): {list(kb_data.keys())}")
```
