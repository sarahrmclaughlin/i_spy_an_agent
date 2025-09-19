# Notes setting this all up
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

# RAG portion of the project
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

