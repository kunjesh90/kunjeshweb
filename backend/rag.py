#rag.py

import pickle
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate
import os
import uvicorn
from langchain_core.messages import AIMessage, HumanMessage
import re

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Add this utility function ---
def resolve_pronouns(query: str) -> str:
    # Replace common pronoun references to "Kunjesh"
    query = re.sub(r"\b(he|his|sir)\b", "Kunjesh", query, flags=re.IGNORECASE)
    return query

# Initialize FastAPI app
app = FastAPI()
print("✅ FastAPI app initialized 🚀")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load Together.ai model
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "c51c9bcaa6bf7fae3ce684206311564828c13fa2e91553f915fee01d517ccee9")
if not TOGETHER_API_KEY:
    raise ValueError("❌ Together.ai API key is missing.")

chat_model = ChatTogether(
    together_api_key=TOGETHER_API_KEY,
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
)

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are Kunjesh AI, a smart, composed, and reliable virtual assistant. You must follow these core instructions:\n\n"

        "**Strict Context-Only Responses:**\n"
        "- Respond only based on the information provided in the current context.\n"
        "- Do not use any external or general knowledge.\n\n"

        "**Avoid Hallucination:**\n"
        "- If a question is asked that is not covered by the context, respond with:\n"
        "  \"I don’t have information regarding that topic based on the current context.\"\n\n"

        "**Persona Behavior – Kunjesh AI:**\n"
        "- Maintain a calm, intelligent, and helpful tone.\n"
        "- Stay consistent with your identity as Kunjesh AI.\n\n"

        "**Identity Response (When asked 'Who are you?')**\n"
        "- Say: \"I am Kunjesh AI, your intelligent assistant designed to answer only based on the given context. How can I assist you today?\"\n\n"

       "**Reference Clarification:**\n"
        "- If the user refers to 'he', 'his', or 'sir' in the question, always interpret it as a reference to Kunjesh unless stated otherwise.\n"
        "- Always answer as though 'he' or 'sir' means 'Kunjesh', even if the name 'Kunjesh' is not explicitly used in the question.\n"

        "Context:\n{context}\n\n"
        "Question:\n{question}\n"
        "Answer:"
    )
)


print("\n🧾 PROMPT TEMPLATE PREVIEW:\n")
print(prompt_template)

# Load the embeddings model
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
print("✅ Embedding model loaded: all-MiniLM-L6-v2 🧠")

# Load docstore
try:
    with open("docstore.pkl", "rb") as f:
        docstore = pickle.load(f)
    if not isinstance(docstore, InMemoryDocstore):
        raise ValueError("❌ docstore.pkl is not an InMemoryDocstore.")
    print("✅ Document store loaded successfully! 📚")
    stored_ids = list(docstore._dict.keys())
    print("📂 Stored Document IDs:", stored_ids)
except Exception as e:
    print(f"❌ Error loading docstore.pkl: {e}")
    docstore = None

# Load FAISS index
try:
    faiss_index_path = "faiss_index/index.faiss"
    faiss_index = faiss.read_index(faiss_index_path)
    print(f"✅ FAISS index loaded from {faiss_index_path} 📌")
    print("📊 FAISS index size:", faiss_index.ntotal)
except Exception as e:
    print(f"❌ Error loading FAISS index: {e}")
    faiss_index = None

@app.get("/ask")
async def ask_question(query: str):
    print(f"\n🔍 New query received: {query}")

    if not faiss_index:
        raise HTTPException(status_code=500, detail="❌ FAISS index is not loaded.")
    if not docstore:
        raise HTTPException(status_code=500, detail="❌ Docstore is not loaded.")

    # 🔄 Preprocess the query for pronouns
    resolved_query = resolve_pronouns(query)
    print(f"🔄 Resolved query: {resolved_query}")

    # Generate embedding
    try:
        query_embedding = embedding_model.embed_query(resolved_query)
        print("✅ Query embedding created 🧩")
    except Exception as e:
        print(f"❌ Error generating query embedding: {e}")
        raise HTTPException(status_code=500, detail="Error generating query embedding.")

    # Search in FAISS
    try:
        D, I = faiss_index.search(np.array([query_embedding]), k=3)
        print(f"📌 Retrieved document IDs: {I[0]}")
        print("📌 FAISS distances:", D)
    except Exception as e:
        print(f"❌ Error searching FAISS index: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving documents from FAISS index.")

    # Filter by threshold
    threshold = 0.8
    valid_docs = [(docstore._dict.get(int(doc_id)), distance) for doc_id, distance in zip(I[0], D[0]) if doc_id != -1]

    if not valid_docs:
        print("⚠️ No relevant documents found.")
        return {"response": "No relevant information found in the knowledge base."}

    # Build context
    retrieved_docs = [doc.page_content for doc, _ in valid_docs if doc]
    context_text = "\n".join(retrieved_docs) if retrieved_docs else "No relevant information found."
    print("📄 Retrieved document content:", retrieved_docs)

    # Format prompt
    formatted_prompt = prompt_template.format(context=context_text, question=resolved_query)

    try:
        response = chat_model.invoke([HumanMessage(content=formatted_prompt)])
        response_text = response.content
    except Exception as e:
        print(f"❌ Error generating response with Together.ai: {e}")
        raise HTTPException(status_code=500, detail="Error generating chatbot response.")

    return {"response": response_text}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)