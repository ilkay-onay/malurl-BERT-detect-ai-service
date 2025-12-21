import pandas as pd

# Load the dataset the model actually trained on
df = pd.read_csv("data/processed_dataset.csv")

# Look for google
google_entries = df[df['url'].str.contains("google.com", na=False)]

print(f"Total 'google.com' occurrences: {len(google_entries)}")
print("\nLabel Distribution for Google:")
print(google_entries['label'].value_counts())

print("\nSample of what the model saw:")
print(google_entries.head(10))