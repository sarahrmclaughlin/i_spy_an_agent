# 👀 SPY AN AGENT 🤖
#### Creating my own LLM API Calls and (hopefully) AI Agents using OpenAI
- This is a repo of learning

# Clarify LLM API call v. Agent
- Currently this notebook is setting up a LLM API call
- If we want to build an Agent, it would include the entire system of:
    - Knowing when to use an LLM
    - Pulling knowledge from prior interactions/similar situations
    - Decide on strategies to update or fix things or just run in general
    - Goes beyond all of this to do more

### LLM API Call - What this means:
- This is a programmatic way to ask ChatGPT to "translate "Bicycle" into Italian and French"
```response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": "You are a Language Translation assistant. You will translate any English text I provide into French and Italian with corresponding articles "
        ""},
        {"role": "user", "content": "Bicycle!"},
    ],
)```
- Similar to a RESTAPI call, we first query/call the LLM model
- Then, we focus on the message array which essentially drives everything here.
    - ```{"role" : "system", "content":prompt}```
        - system_prompt = """You are a Language Translation assistant. You will translate this word to English."""
            - This helps the AI understand how to respond. Similar to using ChatGPT UI and typing "Pretend you are a doctor"
    -```{"role": "user", "content": user_content}```
        - user_content = """Bicycle"""
            - This is where we as users provide the info need for the API call. In this case, we want the word bicyle to be translated.

