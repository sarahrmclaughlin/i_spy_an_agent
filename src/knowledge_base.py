import logging
import os
import json
from pathlib import Path

# Use an absolute path relative to this file so it resolves correctly
# regardless of the caller's working directory.
_SRC_DIR = Path(__file__).parent
KB_PATH = _SRC_DIR.parent / "configs" / "kb.json"

logger = logging.getLogger(__name__)


def load_kb() -> dict:
    """Load and return the knowledge base as a dict.

    Returns an empty dict if the file does not exist yet (first run).
    """
    if not KB_PATH.exists():
        logger.warning("KB file not found at %s — returning empty KB.", KB_PATH)
        return {}
    with open(KB_PATH, "r") as f:
        return json.load(f)


def save_kb(kb: dict) -> None:
    """Persist the knowledge base dict to disk.

    Args:
        kb: The full knowledge base dictionary to write.
    """
    KB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KB_PATH, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)


def word_in_kb(english_word: str) -> bool:
    """Return True if the word (case-insensitive) is already in the KB.

    Args:
        english_word: The English word to look up.
    """
    kb = load_kb()
    return english_word.lower().strip() in kb


def get_kb_entry(english_word: str) -> dict | None:
    """Return the KB entry for a word, or None if not found.

    Args:
        english_word: The English word to look up.

    Returns:
        A dict with 'fr' and 'it' sub-dicts, or None.
    """
    kb = load_kb()
    return kb.get(english_word.lower().strip())


def _parse_translation_line(line: str, lang_prefix: str) -> tuple[str, str]:
    """Parse a single 'Language: [article] word' line from LLM output.

    Handles both 'French: le livre' (with article) and 'French: livre' (no article).

    Args:
        line: The raw line, e.g. 'French: le livre'.
        lang_prefix: The language label to strip, e.g. 'French'.

    Returns:
        A (article, word) tuple. article is '' when not present.
    """
    value = line.replace(f"{lang_prefix}:", "").strip()
    parts = value.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    # No article detected — store empty string so schema stays consistent.
    return "", parts[0]


def update_kb(english_word: str, response: str) -> None:
    """Save new word translations to the KB.

    Parses LLM output formatted like::

        French: le livre
        Italian: il libro

    Both lines are required. If parsing fails the function logs a warning
    and skips the write rather than raising.

    Args:
        english_word: The English source word (will be lowercased).
        response: The raw LLM response string containing French and Italian lines.
    """
    key = english_word.lower().strip()

    kb = load_kb()
    if key in kb:
        logger.info("'%s' already exists in KB — skipping update.", key)
        return

    fr_lines = [l for l in response.splitlines() if l.strip().startswith("French")]
    it_lines = [l for l in response.splitlines() if l.strip().startswith("Italian")]

    if not fr_lines or not it_lines:
        logger.warning(
            "Could not parse French/Italian lines from LLM response for '%s'. "
            "Response was: %r",
            key,
            response,
        )
        return

    try:
        fr_article, fr_word = _parse_translation_line(fr_lines[0], "French")
        it_article, it_word = _parse_translation_line(it_lines[0], "Italian")
    except Exception as exc:
        logger.warning("Failed to parse translation for '%s': %s", key, exc)
        return

    kb[key] = {
        "fr": {"article": fr_article, "word": fr_word},
        "it": {"article": it_article, "word": it_word},
    }

    save_kb(kb)
    logger.info("KB updated with '%s': %s", key, kb[key])