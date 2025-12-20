# src/data_manager.py
import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer

class URLDataManager:
    def __init__(self, model_name="google-bert/bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.raw_path = "data/raw"
        self.output_path = "data/processed_dataset.csv"

    def is_valid_url(self, url):
        if not isinstance(url, str) or len(url) < 4:
            return False
        if not all(ord(c) < 128 for c in url):
            return False
        if '.' not in url and '/' not in url:
            return False
        return True

    def process_and_merge(self):
        print("🛠️  Merging raw datasets...")
        df1 = pd.read_csv(os.path.join(self.raw_path, "malicious_phish.csv"))
        df1['label'] = df1['type'].apply(lambda x: 0 if x == 'benign' else 1)
        df1 = df1.rename(columns={'url': 'url'})[['url', 'label']]
        df1['source_priority'] = 2

        df2 = pd.read_csv(os.path.join(self.raw_path, "phishing_site_urls.csv"))
        df2['label'] = df2['Label'].apply(lambda x: 0 if x == 'good' else 1)
        df2 = df2.rename(columns={'URL': 'url'})[['url', 'label']]
        df2['source_priority'] = 3

        with open(os.path.join(self.raw_path, "online-valid.json"), 'r') as f:
            df3 = pd.DataFrame(json.load(f))[['url']]
            df3['label'] = 1
            df3['source_priority'] = 1

        combined = pd.concat([df1, df2, df3], ignore_index=True)
        combined = combined[combined['url'].apply(self.is_valid_url)]
        combined = combined.sort_values(by='source_priority').drop_duplicates(subset=['url'], keep='first')

        phish_df = combined[combined['label'] == 1]
        safe_df = combined[combined['label'] == 0]
        n_samples = min(len(phish_df), len(safe_df))
        
        balanced_df = pd.concat([
            phish_df.sample(n_samples, random_state=42),
            safe_df.sample(n_samples, random_state=42)
        ]).sample(frac=1, random_state=42)

        balanced_df[['url', 'label']].to_csv(self.output_path, index=False)
        return balanced_df

    def get_hf_dataset(self, is_baby_run=False):
        if not os.path.exists(self.output_path):
            df = self.process_and_merge()
        else:
            df = pd.read_csv(self.output_path)

        if is_baby_run:
            print("👶 BABY RUN: Sampling 1,000 rows for smoke test...")
            df = df.sample(n=min(1000, len(df)), random_state=42)

        # 1. Rename column to 'labels' (Hugging Face standard)
        df = df.rename(columns={'label': 'labels'})

        train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['labels'], random_state=42)
        val_df, test_df = train_test_split(test_df, test_size=0.5, stratify=test_df['labels'], random_state=42)

        ds = DatasetDict({
            'train': Dataset.from_pandas(train_df),
            'validation': Dataset.from_pandas(val_df),
            'test': Dataset.from_pandas(test_df)
        })

        def tokenize_func(examples):
            return self.tokenizer(examples["url"], padding="max_length", truncation=True, max_length=256)

        # 2. FIX: Remove 'url' and junk columns, but KEEP 'labels'
        # We find all columns that are NOT 'labels' and remove them
        cols_to_remove = [col for col in ds['train'].column_names if col != 'labels']
        
        return ds.map(
            tokenize_func, 
            batched=True, 
            remove_columns=cols_to_remove
        )

        def tokenize_func(examples):
            return self.tokenizer(examples["url"], padding="max_length", truncation=True, max_length=256)

        # Bug fix: Remove all columns except what BERT needs
        cols_to_remove = ds['train'].column_names
        return ds.map(tokenize_func, batched=True, remove_columns=cols_to_remove)