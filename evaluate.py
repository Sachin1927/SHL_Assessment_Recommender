import requests
import pandas as pd
from urllib.parse import urlparse

TRAIN_DATA_FILE = "data/train_labeled.csv"
API_URL = "http://localhost:8000/recommend"

def get_slug(url):
    """
    Extracts the last part of the URL (the ID).
    e.g. "https://shl.com/view/java-test/" -> "java-test"
    """
    if not isinstance(url, str): return ""
    clean = url.strip().rstrip('/')
    return clean.split('/')[-1]

def calculate_recall_at_k(predictions, ground_truth, k=10):
    if not ground_truth: return 0.0
    
    # Match based on SLUGS only (Ignore domain and folders)
    pred_slugs = {get_slug(p) for p in predictions[:k]}
    truth_slugs = {get_slug(t) for t in ground_truth}
    
    # Count matches
    hits = pred_slugs.intersection(truth_slugs)
    return len(hits) / len(ground_truth)

def run_evaluation():
    try:
        df = pd.read_csv(TRAIN_DATA_FILE)
    except FileNotFoundError:
        print(" Error: Train data not found.")
        return

    grouped_df = df.groupby('Query')['Assessment_url'].apply(list).reset_index()
    recalls = []
    
    print(f" Running SLUG evaluation on {len(grouped_df)} queries...")
    
    for index, row in grouped_df.iterrows():
        query = row['Query']
        truth_urls = row['Assessment_url']
        
        try:
            resp = requests.post(API_URL, json={"query": query})
            if resp.status_code == 200:
                results = resp.json().get("recommended_assessments", [])
                pred_urls = [res['url'] for res in results]
                
                score = calculate_recall_at_k(pred_urls, truth_urls, k=10)
                recalls.append(score)
                print(f"   Query {index+1}: Recall@10 = {score:.2f}")

                # DEBUG: Show mismatches if score is 0
                if index == 0 and score == 0:
                    print("\n    DEBUG (Query 1):")
                    print(f"   Wanted: {[get_slug(u) for u in truth_urls[:3]]}")
                    print(f"   Found:  {[get_slug(u) for u in pred_urls[:3]]}")
                    print("   (If 'Found' doesn't look relevant, you need to re-crawl data.)")
                    print("   ------------------------------------------------")
            else:
                recalls.append(0)
        except Exception:
            recalls.append(0)

    if recalls:
        mean_recall = sum(recalls) / len(recalls)
        print("\n" + "="*40)
        print(f" FINAL MEAN RECALL@10: {mean_recall:.4f}")
        print("="*40)

if __name__ == "__main__":
    run_evaluation()