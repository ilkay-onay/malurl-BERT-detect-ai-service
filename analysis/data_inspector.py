import pandas as pd
import json
import os

def inspect_datasets(directory="data/raw"):
    print("🔍 DATASET STRUCTURE INSPECTOR")
    print("="*50)

    if not os.path.exists(directory):
        print(f"❌ Directory '{directory}' not found.")
        return

    files = [f for f in os.listdir(directory) if f.endswith(('.csv', '.json'))]
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"\n📄 FILE: {filename}")
        print("-" * 30)

        try:
            # --- HANDLE CSV ---
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath, nrows=5) # Only load 5 rows for speed
                full_df_info = pd.read_csv(filepath, usecols=[0]) # Count total rows
                
                print(f"Type: CSV")
                print(f"Total Rows (est): {len(full_df_info)}")
                print(f"Columns Found: {list(df.columns)}")
                print("\nSample Data (First 2 rows):")
                print(df.head(2).to_string())
                
                # Check for label-like columns
                potential_labels = [c for c in df.columns if 'label' in c.lower() or 'type' in c.lower() or 'target' in c.lower()]
                if potential_labels:
                    print(f"Potential Label Columns: {potential_labels}")

            # --- HANDLE JSON ---
            elif filename.endswith('.json'):
                with open(filepath, 'r') as jfile:
                    first_line = jfile.readline()
                    jfile.seek(0)
                    
                    # Check if it's JSON Lines (JSONL) or standard JSON
                    try:
                        data = json.loads(first_line)
                        print("Type: JSON (Line-delimited or Single Object)")
                    except:
                        data = json.load(jfile)
                        print("Type: Standard JSON Array")

                if isinstance(data, list):
                    sample = data[0]
                    print(f"Total Records: {len(data)}")
                elif isinstance(data, dict):
                    sample = data
                    # If it's a dict with keys like 'data' or 'urls'
                    for key in data.keys():
                        if isinstance(data[key], list):
                            print(f"Found list under key: '{key}' (Length: {len(data[key])})")
                            sample = data[key][0]
                
                print(f"Root Keys/Fields: {list(sample.keys()) if isinstance(sample, dict) else 'Primitive Value'}")
                print("\nSample Object Preview:")
                print(json.dumps(sample, indent=2)[:500] + "...")

        except Exception as e:
            print(f"❌ Error analyzing {filename}: {e}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    inspect_datasets()