from openai import OpenAI
from src.prompt_builder import build_prompt

client = OpenAI()

def llm_fallback(query: str):
    """Call LLM when KB has no answer"""
    prompt = build_prompt(query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()