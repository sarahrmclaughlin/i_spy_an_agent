from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

# NOTE: For new projects, uv add google-adk, then uv add litellm
# uv run adk web --port 8000,  then view UI at http://localhost:8000

# LiteLLM automatically uses the OpenAI API key from .env
model = LiteLlm(model="openai/gpt-4o-mini")

root_agent = Agent(
    model=model,
    name='root_agent',
    description='A translation assistant focused on translating English sentiment to Italian',
    instruction='Translate user input from English to Italian, ensuring that the sentiment of the original text is preserved. Highlight any Italian nuance.',
)
