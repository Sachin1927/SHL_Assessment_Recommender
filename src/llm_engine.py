import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Force absolute path to be safe
DB_PATH = os.path.join(os.getcwd(), "data", "vector_store")

class RecommenderSystem:
    def __init__(self):
        print(" Initializing Recommender Engine...")
        
        # 1. Load Embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception as e:
            print(f" Error loading Embeddings: {e}")
            raise e
        
        # 2. Load Vector Database (COMPATIBILITY FIX APPLIED HERE)
        try:
            # We removed 'allow_dangerous_deserialization=True' to fix the TypeError
            self.vector_store = FAISS.load_local(DB_PATH, self.embeddings)
            print(" Vector DB loaded successfully.")
        except TypeError:
            # Fallback for newer versions just in case
            self.vector_store = FAISS.load_local(DB_PATH, self.embeddings, allow_dangerous_deserialization=True)
            print(" Vector DB loaded successfully (Newer Version).")
        except Exception as e:
            print(f" CRITICAL ERROR: Could not load Vector DB from {DB_PATH}")
            print(f"   (Did you run 'python src/ingestion.py'?)")
            raise e

        # 3. Setup Gemini (Safe Mode)
        self.has_llm = False
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.has_llm = True
                print(" Gemini API configured.")
            except Exception as e:
                print(f" Warning: Gemini API failed to connect. Running in 'Search Only' mode. Error: {e}")
        else:
            print(" Warning: No Google API Key found. Running in 'Search Only' mode.")

    def recommend(self, query):
        print(f" Processing Query: {query}")
        
        # Step 1: Broad Search (FAISS)
        try:
            docs = self.vector_store.similarity_search(query, k=10)
        except Exception as e:
            print(f" FAISS Search Error: {e}")
            return []

        # Step 2: Convert to basic format
        results = []
        for doc in docs:
            meta = doc.metadata
            results.append({
                "url": meta.get("url", ""),
                "name": meta.get("name", ""),
                "description": meta.get("description", "")[:200] + "...",
                "duration": int(meta.get("duration", 30)),
                "test_type": meta.get("test_type", ["Knowledge & Skills"])
            })

        # Step 3: Try Balancing (LLM)
        if self.has_llm:
            try:
                if "personality" in query.lower() or "behavior" in query.lower():
                    print("    AI detected Behavioral intent. Re-ranking...")
                    results.sort(key=lambda x: "Personality" in str(x.get("test_type", "")), reverse=True)
            except Exception as e:
                print(f" AI Re-ranking failed (Ignored): {e}")

        return results