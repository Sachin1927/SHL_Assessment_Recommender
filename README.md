# SHL Assessment Recommender System

## 📌 Overview
This project is an AI-powered recommendation engine designed to match Job Descriptions (JDs) or natural language queries with relevant **SHL Assessments**.

It utilizes a **Retrieval-Augmented Generation (RAG)** pipeline, leveraging **FAISS** for vector similarity search and **Playwright** for robust data scraping. The system provides both a **REST API** (FastAPI) and a user-friendly **Frontend** (Streamlit).

## 🚀 Key Features
* **Hybrid Scraping Engine:** A custom Playwright scraper (`fix_data_final.py`) designed to handle "Lazy Loading" and infinite scrolling on the SHL catalog to retrieve ~350+ assessments.
* **Vector Search:** Uses `sentence-transformers/all-MiniLM-L6-v2` embeddings and FAISS to perform semantic search on assessment descriptions.
* **Dual Interface:**
    * **Backend:** FastAPI server matching the strict JSON schema requirements.
    * **Frontend:** Streamlit UI for interactive testing and demonstration.
* **Compliance:** Fully compliant with the assignment's API contracts (including `adaptive_support`, `remote_support`, etc.).

---

## 📂 Project Structure

```bash
SHL_Assessment_Recommender/
├── data/
│   ├── raw/assessments.json       # Scraped data
│   └── vector_store/              # FAISS Index (Generated)
├── src/
│   ├── api.py                     # FastAPI Backend
│   ├── ingestion.py               # Vector Database Builder
│   └── llm_engine.py              # Core RAG & Recommendation Logic
├── fix_data_final.py              # The "Clicker" Scraper (Playwright)
├── generate_submission.py         # Generates submission.csv
├── run.py                         # Launcher (Starts API + UI together)
├── requirements.txt               # Dependencies
└── README.md                      # Documentation


🛠️ Installation & Setup
1. Prerequisites
Python 3.9+

Git

2. Clone & Install Dependencies

git clone <YOUR_REPO_URL>
cd SHL_Assessment_Recommender

# Create Virtual Environment (Optional but Recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Libraries
pip install -r requirements.txt

3. Install Browser Drivers
This project uses Playwright for scraping. You must install the browser binaries:

playwright install

⚡ How to Run
Step 1: Scrape Data (If data/raw is empty)
If you need to fetch fresh data from the SHL website, run the scraper. This script automatically scrolls and clicks "Next" to capture the full catalog.

python src/crawler.py

Step 2: Build the Vector Database
This processes the JSON data and creates the FAISS index.

python src/ingestion.py

Step 3: Launch the Application
This single command starts both the FastAPI Backend (Port 8000) and Streamlit Frontend (Port 8501).

python run.py

Frontend: Open http://localhost:8501 in your browser.

API Docs: Open http://localhost:8000/docs.

📡 API Documentation
The API follows the strict requirements outlined in the assignment.

1. Health Check
Endpoint: GET /health

Response: {"status": "healthy"}

2. Get Recommendations
Endpoint: POST /recommend

Request Body:

{
  "query": "Looking for a Java Developer with good communication skills"
}

Response:

{
  "recommended_assessments": [
    {
      "url": "[https://www.shl.com/](https://www.shl.com/)...",
      "name": "Java (Standard) - Knowledge & Skills",
      "adaptive_support": "No",
      "description": "Measures proficiency in Java programming...",
      "duration": 30,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}

📊 Evaluation & Submission
python generate_submission.py

🧠 Approach & Design Decisions
Data Acquisition: The SHL website uses complex lazy-loading. Standard request-based crawlers failed to retrieve technical tests (like Java/Python). A Playwright-based "Clicker" bot was implemented to physically simulate user navigation, ensuring high Recall.

Search Strategy: We utilize semantic search rather than keyword matching. This allows a query like "hiring a coder" to correctly find "Software Engineer" assessments even if the word "coder" isn't present.

Strict Compliance: The data model was explicitly mapped to the assignment's required fields (e.g., hard-typing duration to Integer and ensuring adaptive_support presence) to prevent automated evaluation failures.