def build_prompt(query: str):
    """Builds prompt for LLM fallback"""
    return f"""
    Pretend you are an expert translator, fluent in English, French, and Italian.
    Please translate the following English word into French and Italian, 
    including the correct article for each:

    Word: {query}
    Format:
    French: [article + word]
    Italian: [article + word]
    """