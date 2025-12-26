# validate_external.py
import pandas as pd
import torch
from tqdm import tqdm
from sklearn.metrics import classification_report, confusion_matrix
from src.inference import URLAnalyzer
import os

# 1. Configuration
KAGGLE_PATH = "data/raw/malicious_phish.csv"
MODEL_PATH = "outputs/phiusiil_v1/production_model" # or "outputs/phiusiil_v1/production_model"
SAMPLE_SIZE = 20000 # Testing on 20k rows is enough for a sanity check

def run_validation():
    if not os.path.exists(KAGGLE_PATH):
        print(f"❌ Kaggle dataset not found at {KAGGLE_PATH}")
        return

    # 2. Load Kaggle Data
    print(f"📖 Loading {KAGGLE_PATH}...")
    df = pd.read_csv(KAGGLE_PATH)
    
    # Map Kaggle labels to our format (0: Safe, 1: Phish/Malicious)
    # Kaggle 'type' column: benign, phishing, malware, defacement
    df['true_label'] = df['type'].apply(lambda x: 0 if x == 'benign' else 1)
    
    # Take a balanced sample for fair testing
    df_sample = df.groupby('true_label').sample(n=SAMPLE_SIZE//2, random_state=42)
    
    # 3. Initialize Model
    analyzer = URLAnalyzer(MODEL_PATH)
    
    # 4. Run Inference
    print(f"🚀 Running inference on {len(df_sample)} external samples...")
    y_true = df_sample['true_label'].tolist()
    y_pred = []
    
    # Using a simple loop (URLAnalyzer handles GPU/Logic)
    for url in tqdm(df_sample['url']):
        result = analyzer.analyze(url)
        # Map 'PHISHING' and 'SUSPICIOUS' to 1, 'LEGITIMATE' to 0
        pred = 1 if result['category'] in ['PHISHING', 'SUSPICIOUS'] else 0
        y_pred.append(pred)

    # 5. Final Report
    print("\n" + "="*60)
    print("📊 EXTERNAL VALIDATION REPORT (Model trained on PhiUSIIL -> Tested on Kaggle)")
    print("="*60)
    print(classification_report(y_true, y_pred, target_names=['Safe', 'Malicious']))
    
    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(f"True Safe: {cm[0][0]} | False Phish: {cm[0][1]}")
    print(f"False Safe: {cm[1][0]} | True Phish: {cm[1][1]}")
    print("="*60)

if __name__ == "__main__":
    run_validation()