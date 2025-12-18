import json
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Paths
DATA_PATH = "data/raw/assessments.json"
DB_PATH = "data/vector_store"

def ingest_data():
    print("  Loading data for ingestion...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Run crawler.py first. File not found: {DATA_PATH}")

    with open(DATA_PATH, 'r') as f:
        data = json.load(f)

    documents = []
    for item in data:
        # Create a rich text representation for the embedding model
        # We combine Name, Description, and Test Type for better semantic search.
        page_content = f"Name: {item['name']}. Description: {item['description']}. Type: {', '.join(item['test_type'])}"
        
        doc = Document(
            page_content=page_content,
            metadata=item # Store all metadata for the API response
        )
        documents.append(doc)

    print(f" Embedding {len(documents)} documents...")
    
    # Use a standard, efficient model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(DB_PATH)
    print(f" Vector store saved to {DB_PATH}")

if __name__ == "__main__":
    ingest_data()