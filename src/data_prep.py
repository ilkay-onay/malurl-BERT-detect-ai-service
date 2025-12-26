# src/data_prep.py
import pandas as pd
import os
from sklearn.model_selection import GroupShuffleSplit

class DataPipeline:
    def __init__(self, raw_dir="data/raw", output_dir="data"):
        self.raw_dir = raw_dir
        self.output_dir = output_dir

    def sanitize(self, url):
        if not isinstance(url, str): return None
        # Protokol ve www temizliği (Tekilleştirme için en önemli adım)
        url = url.lower().strip()
        url = url.replace("https://", "").replace("http://", "").replace("www.", "")
        if url.endswith('/'): url = url[:-1]
        
        # Domain'i ayır (GroupSplit için)
        domain = url.split('/')[0]
        return domain, url

    def run(self):
        print("🏗️  Hibrit Veri Havuzu ve Global Tekilleştirme Başlatılıyor...")
        all_data = []

        # 1. PhiUSIIL Yükle
        phi_path = os.path.join(self.raw_dir, "PhiUSIIL_Phishing_URL_Dataset.csv")
        if os.path.exists(phi_path):
            print("📦 PhiUSIIL okunuyor...")
            df_phi = pd.read_csv(phi_path, usecols=['URL', 'label'])
            df_phi['label'] = df_phi['label'].apply(lambda x: 0 if x == 1 else 1)
            df_phi = df_phi.rename(columns={'URL': 'url_raw'})
            all_data.append(df_phi)

        # 2. Kaggle Yükle
        kag_path = os.path.join(self.raw_dir, "malicious_phish.csv")
        if os.path.exists(kag_path):
            print("📦 Kaggle Malicious Phish okunuyor...")
            df_kag = pd.read_csv(kag_path)
            df_kag['label'] = df_kag['type'].apply(lambda x: 0 if x == 'benign' else 1)
            df_kag = df_kag.rename(columns={'url': 'url_raw'})[['url_raw', 'label']]
            all_data.append(df_kag)

        # --- BİRLEŞTİRME ---
        combined = pd.concat(all_data, ignore_index=True)
        print(f"📊 Ham birleşik veri boyutu: {len(combined):,}")

        # --- SANITIZE VE DOMAIN AYRIŞTIRMA ---
        print("🧹 URL'ler temizleniyor ve domainler ayrıştırılıyor...")
        temp_results = combined['url_raw'].apply(self.sanitize).apply(pd.Series)
        combined['domain'] = temp_results[0]
        combined['url_clean'] = temp_results[1]

        # --- GLOBAL DEDUPLICATION (TEKİLLEŞTİRME) ---
        # Önce veriyi label'a göre büyükten küçüğe sıralıyoruz (1'ler yukarı).
        # Böylece aynı URL bir yerde 1 bir yerde 0 ise, 1 olanı (Zararlı) tutarız.
        # Güvenlik önceliği!
        combined = combined.sort_values(by=['url_clean', 'label'], ascending=[True, False])
        
        initial_count = len(combined)
        combined = combined.drop_duplicates(subset=['url_clean'], keep='first')
        print(f"♻️  Tekilleştirme tamamlandı: {initial_count - len(combined):,} kopya URL silindi.")

        # --- SINIF DENGELEME ---
        phish = combined[combined['label'] == 1]
        safe = combined[combined['label'] == 0]
        n_samples = min(len(phish), len(safe))
        
        balanced = pd.concat([
            phish.sample(n_samples, random_state=42),
            safe.sample(n_samples, random_state=42)
        ]).sample(frac=1, random_state=42)
        print(f"⚖️  Dengelenmiş veri: {len(balanced):,} satır (%50 Safe, %50 Phish)")

        # --- FİZİKSEL DOMAİN SPLIT (%80, %10, %10) ---
        print("✂️  Domain tabanlı fiziksel bölme (Train/Val/Test) yapılıyor...")
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, temp_idx = next(gss.split(balanced, groups=balanced['domain']))
        
        train_df = balanced.iloc[train_idx]
        temp_df = balanced.iloc[temp_idx]

        gss_val = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
        val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df['domain']))

        val_df = temp_df.iloc[val_idx]
        test_df = temp_df.iloc[test_idx]

        # Sadece Model için gerekli sütunları kaydet
        # 'url_clean' sütununu 'url' olarak kaydediyoruz
        for name, df in [("train", train_df), ("val", val_df), ("test", test_df)]:
            df[['url_clean', 'label']].rename(columns={'url_clean': 'url'}).to_csv(
                os.path.join(self.output_dir, f"{name}.csv"), index=False
            )
            print(f"💾 {name}.csv kaydedildi ({len(df):,} satır).")

if __name__ == "__main__":
    DataPipeline().run()