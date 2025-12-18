def __init__(self):
        # 1. Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.db_path = os.path.join("data", "vector_store")
        
        # 2. Load Vector Database (The Fix is here!)
        if os.path.exists(self.db_path):
            try:
                # We removed 'allow_dangerous_deserialization=True' because your version doesn't support it
                self.vector_store = FAISS.load_local(self.db_path, self.embeddings)
                print("✅ Vector Store Loaded Successfully.")
            except Exception as e:
                print(f"❌ Error loading FAISS: {e}")
                raise e
        else:
            raise Exception(f"Vector store not found at {self.db_path}. Please run src/ingestion.py first.")

        # 3. Initialize LLM (Optional)
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
                self.has_llm = True
            else:
                print("⚠️ No GEMINI_API_KEY found. Running in Retrieval-Only mode.")
                self.has_llm = False
        except Exception as e:
            print(f"⚠️ LLM Init Failed: {e}")
            self.has_llm = False