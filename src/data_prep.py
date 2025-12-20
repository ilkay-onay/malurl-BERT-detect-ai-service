import pandas as pd
import json
import os
from sklearn.utils import resample

class DataPipeline:
    def __init__(self, raw_dir="data/raw", output_path="data/raw_urls.csv"):
        self.raw_dir = raw_dir
        self.output_path = output_path
        self.df_list = []

    def normalize_url(self, url):
        """Standardize URL strings to prevent duplicate leakage."""
        if not isinstance(url, str): return None
        url = url.lower().strip()
        if url.endswith('/'): url = url[:-1]
        return url

    def load_malicious_phish(self):
        """Source: malicious_phish.csv (url, type)"""
        path = os.path.join(self.raw_dir, "malicious_phish.csv")
        df = pd.read_csv(path)
        # Mapping: benign -> 0, all others (phishing, malware, defacement) -> 1
        df['label'] = df['type'].apply(lambda x: 0 if x == 'benign' else 1)
        df = df.rename(columns={'url': 'url_raw'})
        return df[['url_raw', 'label']]

    def load_phishing_site_urls(self):
        """Source: phishing_site_urls.csv (URL, Label)"""
        path = os.path.join(self.raw_dir, "phishing_site_urls.csv")
        df = pd.read_csv(path)
        # Mapping: good -> 0, bad -> 1
        df['label'] = df['Label'].apply(lambda x: 0 if x == 'good' else 1)
        df = df.rename(columns={'URL': 'url_raw'})
        return df[['url_raw', 'label']]

    def load_phishtank_json(self):
        """Source: online-valid.json (Nested JSON)"""
        path = os.path.join(self.raw_dir, "online-valid.json")
        with open(path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['label'] = 1  # All PhishTank entries are verified malicious
        df = df.rename(columns={'url': 'url_raw'})
        return df[['url_raw', 'label']]

    def run(self, balance_ratio=1.0):
        print("🏗️  Starting Data Engineering Pipeline...")
        
        # 1. Load all
        dfs = [
            self.load_malicious_phish(),
            self.load_phishing_site_urls(),
            self.load_phishtank_json()
        ]
        
        # 2. Concatenate
        master_df = pd.concat(dfs, ignore_index=True)
        print(f"   - Total records combined: {len(master_df):,}")

        # 3. Normalization & Deduplication
        master_df['url'] = master_df['url_raw'].apply(self.normalize_url)
        master_df = master_df.dropna(subset=['url'])
        
        # CRITICAL: Drop duplicates to prevent train/test leakage
        initial_count = len(master_df)
        master_df = master_df.drop_duplicates(subset=['url'], keep='first')
        print(f"   - Deduplication removed {initial_count - len(master_df):,} redundant URLs.")

        # 4. Class Balancing
        safe_df = master_df[master_df['label'] == 0]
        phish_df = master_df[master_df['label'] == 1]
        
        print(f"   - Distribution before balancing: Safe: {len(safe_df):,}, Phish: {len(phish_df):,}")

        # Downsample majority class to match the minority class
        minority_count = min(len(safe_df), len(phish_df))
        
        safe_balanced = resample(safe_df, replace=False, n_samples=minority_count, random_state=42)
        phish_balanced = resample(phish_df, replace=False, n_samples=minority_count, random_state=42)
        
        balanced_df = pd.concat([safe_balanced, phish_balanced]).sample(frac=1, random_state=42)

        # 5. Export
        balanced_df[['url', 'label']].to_csv(self.output_path, index=False)
        print(f"✅ Pipeline Complete! Final dataset: {len(balanced_df):,} rows.")
        print(f"📊 Final Distribution: \n{balanced_df['label'].value_counts(normalize=True)}")

if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()