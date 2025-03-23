import pickle
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.docstore.document import Document
from langchain_together import ChatTogether  # Import Together.ai integration
import os
import uvicorn  # Add uvicorn import here

# Initialize FastAPI app
app = FastAPI()
print("FastAPI app initialized")
print("Current working directory:", os.getcwd())

# Enable CORS for the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin, or specify frontend URL like "http://yourfrontend.com"
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly specify methods to be allowed
    allow_headers=["*"],  # Allow all headers
)

# Initialize Together.ai model (ensure you replace the API key with your actual one)
chat_model = ChatTogether(
    together_api_key="c51c9bcaa6bf7fae3ce684206311564828c13fa2e91553f915fee01d517ccee9",  # Replace with your actual Together.ai API key
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Specify the model you want to use
)

# Load the embeddings model and FAISS index
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load docstore and FAISS index from pickle file
with open('docstore.pkl', 'rb') as f:
    docstore = pickle.load(f)

faiss_index = faiss.read_index('faiss_index.index')

# Define the RAG logic to process the query
@app.get("/ask")
async def ask_question(query: str):
    # Create embedding for the query
    query_embedding = embedding_model.embed_query(query)
    print("Query embedding:", query_embedding)
    
    # Perform the search in the FAISS index
    D, I = faiss_index.search(np.array([query_embedding]), k=1)

    # If no relevant documents are found, raise an HTTP exception
    if len(I[0]) == 0:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    # Retrieve the most relevant document from the docstore
    doc_id = I[0][0]
    document = docstore[doc_id]

    # Use Together.ai to generate a response based on the retrieved document
    response = chat_model.ask(query=query, context=document.page_content)
    print("Response from Together.ai:", response)
    
    return {"response": response}

# Only run the server if this script is executed directly (useful for debugging locally)
if __name__ == "__main__":
    # Retrieve the port from environment variable, default to 10000 if not set (Render assigns this dynamically)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
