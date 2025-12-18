import pandas as pd
import requests
import json
import os

TEST_DATA_FILE = "data/test_unlabeled.csv"
OUTPUT_FILE = "submission.csv"
API_URL = "http://localhost:8000/recommend"

def generate_csv():
    if not os.path.exists(TEST_DATA_FILE):
        print(" Error: Test data not found. Run 'setup_data.py' first.")
        return

    df = pd.read_csv(TEST_DATA_FILE)
    submission_data = []

    print(f" Generating predictions for {len(df)} queries...")
    
    for index, row in df.iterrows():
        # Handle both 'Query' and 'query' column names safely
        query = row.get('Query', row.get('query', ''))
        
        if not query:
            continue
            
        try:
            resp = requests.post(API_URL, json={"query": query})
            results = resp.json().get("recommended_assessments", [])
            
            # Format required: Repeat the query for every recommendation row
            for item in results:
                submission_data.append({
                    "Query": query,
                    "Assessment_url": item['url']
                })
            
            print(f"   Processed Query {index+1}")
                
        except Exception as e:
            print(f"   Error on Query {index+1}: {e}")

    # Create Final DataFrame
    if submission_data:
        submission_df = pd.DataFrame(submission_data)
        submission_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n Submission file generated successfully: {OUTPUT_FILE}")
    else:
        print(" No predictions were generated.")

if __name__ == "__main__":
    generate_csv()