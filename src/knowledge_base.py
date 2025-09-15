class TranslationKB:
    """Static bilingual dictionary for English → French & Italian with articles"""
    DATA = {
        "table": {
            "fr": {"article": "la", "word": "table"},
            "it": {"article": "il", "word": "tavolo"}
        },
        "chair": {
            "fr": {"article": "la", "word": "chaise"},
            "it": {"article": "la", "word": "sedia"}
        },
        "bank": {
            "fr": {"article": "la'", "word": "banque"},
            "it": {"article": "la", "word": "banca"}
        },
        "car": {
            "fr": {"article": "la", "word": "voiture"},
            "it": {"article": "la", "word": "macchina"}
        }
    }

    @staticmethod
    def add_word(word: str, translations: dict):
        """Add new word with translations into KB"""
        TranslationKB.DATA[word.lower()] = translations