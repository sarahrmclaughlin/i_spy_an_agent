from openai import OpenAI
from src.prompt_builder import build_prompt


def llm_fallback(query: str) -> str:
    """Call the LLM when the KB has no entry for the given word.

    The OpenAI client is instantiated here (not at module level) so that
    importing this module does not require OPENAI_API_KEY to already be set.
    The key is read from the environment at call time via the OpenAI client default.

    Args:
        query: The English word or phrase to translate.

    Returns:
        The raw LLM response string, expected to contain 'French: ...' and
        'Italian: ...' lines as specified by the prompt template.
    """
    client = OpenAI()
    prompt = build_prompt(query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()