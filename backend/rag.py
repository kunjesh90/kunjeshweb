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


# Initialize FastAPI app
app = FastAPI()
print("Py")
print("wd",os.getcwd())

# Enable CORS for the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Allow only this frontend URL (your frontend is running on this port)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize Together.ai model (make sure you replace the API key with your actual one)
chat_model = ChatTogether(
    together_api_key="c51c9bcaa6bf7fae3ce684206311564828c13fa2e91553f915fee01d517ccee9",  # Replace with your actual Together.ai API key
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",  # Specify the model you want to use
)

# Load the embeddings model and FAISS index
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Load docstore and FAISS index from pickle file
with open('docstore.pkl', 'rb') as f:
    docstore = pickle.load(f)

with open('faiss_index.pkl', 'rb') as f:
    faiss_index = pickle.load(f)

# Define the RAG logic to process the query
@app.get("/ask")
async def ask_question(query: str):
    # Create embedding for the query
    query_embedding = embedding_model.embed_query(query)
    print("query_embedding")
    # Perform the search
    D, I = faiss_index.search(np.array([query_embedding]), k=1)

    if len(I[0]) == 0:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    # Retrieve the most relevant document
    doc_id = I[0][0]
    document = docstore[doc_id]

    # Use Together.ai to generate a response based on the retrieved document
    # Pass the document content and the user's query to Together.ai for further processing
    response = chat_model.ask(query=query, context=document.page_content)
    print("response")
    return {"response": response}
# Only run the server if this script is executed directly (useful for debugging locally)
if __name__ == "__main__":
    # Retrieve the port from environment variable, default to 10000 if not set (Render assigns this dynamically)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
