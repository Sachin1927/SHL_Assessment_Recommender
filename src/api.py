from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.llm_engine import RecommenderSystem
import uvicorn

app = FastAPI()

# Initialize Engine
# NOTE: This will fail if you haven't run src/ingestion.py yet!
try:
    engine = RecommenderSystem()
except Exception as e:
    print(f"Error initializing engine: {e}")
    print("Did you run 'python src/ingestion.py' to create the database?")
    engine = None

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend_assessments(request: QueryRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Engine not initialized. Run ingestion first.")
    
    try:
        results = engine.recommend(request.query)
        if not results:
            return {"recommended_assessments": []}
        return {"recommended_assessments": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)