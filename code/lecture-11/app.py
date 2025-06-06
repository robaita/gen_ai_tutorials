import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Read OpenAI API key
with open("data/key.txt", "r") as f:
    api_key = f.read().strip()

# Define vector DB directory
database_name = "chroma_db"

# Load embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)

# Load vector store
if os.path.exists(database_name) and os.listdir(database_name):
    vectorstore = Chroma(persist_directory=database_name, embedding_function=embedding_model)
    print("✅ Loaded existing vector store.")
else:
    raise Exception("❌ No existing vector store found. Please run the indexing script first.")

# Prompt template
PROMPT_TEMPLATE = """
You are a helpful assistant answering questions based on the provided context.

### Context Chunks:
{context}

### Task:
Using the context above, answer the user's question **precisely** and **cite the page numbers** you used in square brackets like this: [Page 2], [Page 44].

### Question:
{question}

### Answer:
"""

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=PROMPT_TEMPLATE
)

# Model for generation
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=api_key)

# Request schema
class QueryRequest(BaseModel):
    query: str

def format_context(chunks):
    formatted = ""
    for doc in chunks:
        page = doc.metadata.get("page", "N/A")
        summary = doc.page_content.strip().split("\n")[0][:300]
        formatted += f"[Page {page}]: {summary}...\n"
    return formatted

@app.post("/rag")
async def rag_query(request: QueryRequest):
    query = request.query
    retrieved_docs = vectorstore.similarity_search(query, k=3)
    context_block = format_context(retrieved_docs)
    final_prompt = prompt_template.format(context=context_block, question=query)
    response = llm.predict(final_prompt)
    return {"response": response}

@app.post("/v1/chat/completions")
async def chat_completion(request: dict):
    messages = request["messages"]
    query = messages[-1]["content"]  # get the latest user query

    # Perform RAG steps
    retrieved_docs = vectorstore.similarity_search(query, k=3)
    context_block = format_context(retrieved_docs)
    final_prompt = prompt_template.format(context=context_block, question=query)
    answer = llm.predict(final_prompt)

    return {
        "id": "chatcmpl-rag001",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }
        ],
        "model": "rag-api"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
