# src/data_manager.py
import pandas as pd
import os
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer
from .config import Config

class URLDataManager:
    def __init__(self, model_name=Config.MODEL_NAME):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def get_hf_dataset(self, is_baby_run=False):
        # BURASI ÖNEMLİ: Fiziksel dosyaları okuyoruz
        train_df = pd.read_csv("data/train.csv")
        val_df = pd.read_csv("data/val.csv")
        test_df = pd.read_csv("data/test.csv")

        if is_baby_run:
            train_df = train_df.sample(800); val_df = val_df.sample(100); test_df = test_df.sample(100)

        ds = DatasetDict({
            'train': Dataset.from_pandas(train_df),
            'validation': Dataset.from_pandas(val_df),
            'test': Dataset.from_pandas(test_df)
        })

        def tokenize(batch):
            return self.tokenizer(batch['url'], padding="max_length", truncation=True, max_length=Config.MAX_LENGTH)

        # 'label' -> 'labels' çevrimi ve gereksiz sütun temizliği
        return ds.map(tokenize, batched=True, remove_columns=['url']).rename_column('label', 'labels')