"""Functions to be used in Prompt eval project."""

from difflib import SequenceMatcher
from typing import Dict
import re
import yaml
import json

def load_prompt(prompt_path: str) -> Dict:
    with open(prompt_path, 'r') as f:
        return yaml.safe_load(f)

def load_eval_set(eval_path: str) -> Dict:
    with open(eval_path, 'r') as f:
        return json.load(f)

def calculate_translation_similarity(expected: str, actual: str) -> float:
    """
    Compare two translations using multiple strategies.
    Returns a score between 0 and 1.
    """
    # Strategy 1: Exact match (best case)
    if expected.lower().strip() == actual.lower().strip():
        return 1.0
    
    # Strategy 2: Sequence matching (handles minor variations)
    sequence_ratio = SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
    
    # Strategy 3: Word-level overlap (handles reordering)
    expected_words = set(re.findall(r'\b\w+\b', expected.lower()))
    actual_words = set(re.findall(r'\b\w+\b', actual.lower()))
    
    if not expected_words:  # Empty string edge case
        return 1.0 if not actual_words else 0.0
    
    word_overlap = len(expected_words & actual_words) / len(expected_words | actual_words)
    
    # Combine strategies: sequence matching is more strict, word overlap is more lenient
    combined_score = (sequence_ratio * 0.7) + (word_overlap * 0.3)
    
    return combined_score

def calculate_score(expected: Dict, actual: Dict, category: str) -> float:
    """
    Score logic:
    - Italian translation similarity: 0.3 weight
    - French translation similarity: 0.3 weight
    - Sentiment classification: exact match, 0.2 weight
    - Sentence type classification: exact match, 0.15 weight
    - Notes quality: presence check, 0.05 weight
    """
    
    scores = {}
    
    # 1. Italian translation comparison
    if 'italian' in expected and 'italian' in actual:
        italian_score = calculate_translation_similarity(
            expected['italian'],
            actual['italian']
        )
        scores['italian'] = italian_score
    else:
        scores['italian'] = 0.0
    
    # 2. French translation comparison
    if 'french' in expected and 'french' in actual:
        french_score = calculate_translation_similarity(
            expected['french'],
            actual['french']
        )
        scores['french'] = french_score
    else:
        scores['french'] = 0.0
    
    # 3. Sentiment classification (exact match)
    sentiment_match = 1.0 if (
        expected.get('sentiment', '').lower().strip() == 
        actual.get('sentiment', '').lower().strip()
    ) else 0.0
    scores['sentiment'] = sentiment_match
    
    # 4. Sentence type classification (exact match)
    sentence_type_match = 1.0 if (
        expected.get('sentence_type', '').lower().strip() == 
        actual.get('sentence_type', '').lower().strip()
    ) else 0.0
    scores['sentence_type'] = sentence_type_match
    
    # 5. Notes presence (0 or 1 - just checking if notes exist)
    notes_present = 1.0 if actual.get('notes', '').strip() else 0.0
    scores['notes'] = notes_present
    
    # Weighted average
    weights = {
        'italian': 0.30,
        'french': 0.30,
        'sentiment': 0.20,
        'sentence_type': 0.15,
        'notes': 0.05
    }
    
    total_score = sum(scores[key] * weights[key] for key in scores)
    
    return total_score, scores  # Return both total and breakdown


def parse_output(response_text: str) -> Dict:
    """
    Parse LLM response into structured output.
    Expected format: language: word with article
    Example: "French: le mot"
    """
    result = {
        "output_context": None,
        "fr": None,
        "it": None
    }
    
    lines = response_text.strip().split('\n')
    
    for line in lines:
        if 'French' in line or 'fr' in line.lower():
            # Extract French translation
            parts = line.split(':')
            if len(parts) > 1:
                result['fr'] = parts[1].strip()
        elif 'Italian' in line or 'it' in line.lower():
            # Extract Italian translation
            parts = line.split(':')
            if len(parts) > 1:
                result['it'] = parts[1].strip()
    
    # Set output_context (adjust based on your actual prompt structure)
    result['output_context'] = response_text.strip()
    
    return result