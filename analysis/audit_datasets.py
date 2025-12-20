import pandas as pd
import json
import os

def run_audit():
    print("\n\U0001f575\ufe0f DATASET INTEGRITY & COLLISION AUDIT")
    print("="*60)
    
    raw_path = "data/raw"
    
    # --- 1. Load and Normalize malicious_phish.csv ---
    print("Reading malicious_phish.csv...")
    df1 = pd.read_csv(os.path.join(raw_path, "malicious_phish.csv"))
    df1['label'] = df1['type'].apply(lambda x: 0 if x == 'benign' else 1)
    df1 = df1.rename(columns={'url': 'url'})[['url', 'label']]
    
    # --- 2. Load and Normalize phishing_site_urls.csv ---
    print("Reading phishing_site_urls.csv...")
    df2 = pd.read_csv(os.path.join(raw_path, "phishing_site_urls.csv"))
    df2['label'] = df2['Label'].apply(lambda x: 0 if x == 'good' else 1)
    df2 = df2.rename(columns={'URL': 'url'})[['url', 'label']]
    
    # --- 3. Load online-valid.json ---
    print("Reading online-valid.json...")
    with open(os.path.join(raw_path, "online-valid.json"), 'r') as f:
        data = json.load(f)
        df3 = pd.DataFrame(data)[['url']]
        df3['label'] = 1 # All Phishtank entries are malicious
    
    sets = {
        "Kaggle_Phish": df1,
        "Site_URLs": df2,
        "PhishTank_Live": df3
    }

    # --- ANALYSIS 1: CLASS BALANCE ---
    print("\n\U0001f4ca CLASS BALANCE (Are the Red Herrings of imbalance real?)")
    print("-" * 40)
    total_samples = 0
    for name, df in sets.items():
        counts = df['label'].value_counts()
        safe = counts.get(0, 0)
        phish = counts.get(1, 0)
        total = len(df)
        total_samples += total
        print(f"{name:15} | Total: {total:8,} | Safe: {safe:8,} | Phish: {phish:8,} | Ratio: {phish/total:.1%}")

    # --- ANALYSIS 2: INTERNAL DUPLICATES ---
    print("\n\u267b\ufe0f  INTERNAL REDUNDANCY (Duplicates within the same file)")
    print("-" * 40)
    for name, df in sets.items():
        dupes = df.duplicated(subset=['url']).sum()
        print(f"{name:15} | Duplicates: {dupes:8,}")

    # --- ANALYSIS 3: CROSS-FILE COLLISIONS ---
    print("\n\U0001f91d CROSS-FILE COLLISIONS (URLs found in multiple datasets)")
    print("-" * 40)
    urls1 = set(df1['url'])
    urls2 = set(df2['url'])
    urls3 = set(df3['url'])

    overlap12 = urls1.intersection(urls2)
    overlap13 = urls1.intersection(urls3)
    overlap23 = urls2.intersection(urls3)

    print(f"Kaggle_Phish <-> Site_URLs     | Overlap: {len(overlap12):8,}")
    print(f"Kaggle_Phish <-> PhishTank_Live | Overlap: {len(overlap13):8,}")
    print(f"Site_URLs    <-> PhishTank_Live | Overlap: {len(overlap23):8,}")

    # --- ANALYSIS 4: LABEL CONFLICTS (The Critical Check) ---
    print("\n\U0001f6ab LABEL CONFLICTS (Same URL, different labels!)")
    print("-" * 40)
    # Combine everything to find if a URL has both 0 and 1 labels
    combined = pd.concat([df1, df2, df3])
    # Group by URL and count unique labels
    conflicts = combined.groupby('url')['label'].nunique()
    conflict_urls = conflicts[conflicts > 1]
    
    if len(conflict_urls) > 0:
        print(f"CRITICAL: Found {len(conflict_urls):,} URLs with conflicting labels!")
        print("Example Conflicts:")
        print(combined[combined['url'].isin(conflict_urls.head(3).index)].sort_values('url'))
    else:
        print("\u2705 Clean: No URLs have conflicting labels across files.")

    print("\n" + "="*60)

if __name__ == "__main__":
    run_audit()