# 👀 SPY AN AGENT 🤖
#### *Creating my own LLM API Calls and (hopefully) AI Agents using LLMs*
- This is a repo of learning
- This repo creates agents by using agents (.claude > agents)

### *Contents*
- CLAUDE: Claude.md, a specific Claude agent created to work on this repo, lessons learned about this project that Claude adds to.
- **My First RAG Language Agent notebook**
- User Prompt is an English word with goal of translating it to Italian and French
    - If the word exists in the Knowledge Base (KB), it will reference the translation from there.
    - If it does not exists in KB, call LLM(OpenAI) and store response in KB.
- **My First Language Agent notebook**
    - a simple notebook testing out calling the LLM for translations


### General Notes 🎶 ♫ about working with LLMs and Agents:

#### Clarify LLM API call v. Agent
- Currently my_first_language_agent notebook is setting up a LLM API call
- If we want to build an Agent (see RAG Agent), it would include the entire system of:
    - Knowing when to use an LLM
    - Pulling knowledge from prior interactions/similar situations
    - Decide on strategies to update or fix things or just run in general
    - Goes beyond all of this to do more

#### LLM API Call - What this means:
- This is a programmatic way to ask ChatGPT to "translate "Bicycle" into Italian and French"
```
    response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": "You are a Language Translation assistant. You will translate any English text I provide into French and Italian with corresponding articles "
        ""},
        {"role": "user", "content": "Bicycle!"},
    ],
)
```
- Similar to a RESTAPI call, we first query/call the LLM model
- Then, we focus on the message array which essentially drives everything here.
    - ```{"role" : "system", "content":prompt}```
        - system_prompt = """You are a Language Translation assistant. You will translate this word to English."""
            - This helps the AI understand how to respond. Similar to using ChatGPT UI and typing "Pretend you are a doctor"
    - ```{"role": "user", "content": user_content}```
        - user_content = """Bicycle"""
            - This is where we as users provide the info need for the API call. In this case, we want the word bicyle to be translated.

#### OpenAI Key Set-Up
- Retrieve your OpenAI key 
```platform.openai.com/api-keys```
- Create a .env file and store your key there
    - MAKE SURE .env is in your .gitignore file
    - !!! BE CAUTIOUS OF THIS AND MAYBE DO A TEST RUN FIRST IF YOU PLAN ON PUSHING THIS TO GIT!
- Activate your virtual environment
- ```pip install openai```
    - check that it is > 1 
    - ```pip install --upgrade openai```
- Install dot env to pull the api key ```pip install python-dotenv```

#### RAG portion of the project
- The overall goal is to give an English word and have it translate to French and Italian
- When we run the query for this, we want it to use the Knowledge Base first, then go to the LLM.
- For anything not in the KB, (using LLM), we then want the KB to be updated
- First we build a Knowledge Base of the words.
    ```python
    # This will be a JSON file that looks like this:
    DATA = {
        "book": {
            "fr": {"article": "le", "word": "livre"},
            "it": {"article": "il", "word": "libro"}
        },
        "school": {
            "fr": {"article": "l'", "word": "école"},
            "it": {"article": "la", "word": "scuola"}
        }
    }
    ```
- We then turn the KB into a LlamaIndex. This means that:
- First we call an embedded model from OpenAi and convert our text/word to numbers (words are replaced with words).
    - This is called vectorization
    - The embedded model is the instructions for how to convert the word to numbers, essentially it is the mapping for it.
- Ex.
    ```python
    from llama_index.embeddings.openai import OpenAIEmbedding
    embed_model = OpenAIEmbedding()

    vec = embed_model.get_text_embedding("book")
    print(len(vec), vec[:10])
    # Returns -> 1536 [0.012, -0.034, 0.291, 0.004, ...]
    # A computer will read "book" and "library" as being related b/c the numbers(vectors) are close together
    # A computer will read "book" and "orange" as being unrelated b/c the numbers(vectors) are NOT close together
    # By embedded a model, we create a vector where words are characterized semantically.
    # This essentially gives a computer an understanding of how the words are related.
    ```
- Next, we set up an index. Similar to DE principals of indexing for efficiency, we are doing the same thing.
- When we index, we can search faster.
         
#### Additional Helpful Documentation
- Prompt/Context Engineering
    - Anthropic Tutorial https://github.com/anthropics/prompt-eng-interactive-tutorial
    

