import pandas as pd

# Load the dataset you created
df = pd.read_csv("data/processed_dataset.csv")

# Calculate lengths
url_lengths = df['url'].str.len()

total = len(df)
long_128 = (url_lengths > 128).sum()
long_256 = (url_lengths > 256).sum()

print("\n📊 URL LENGTH ANALYSIS")
print("="*30)
print(f"Total URLs: {total:,}")
print(f"URLs > 128 chars: {long_128:,} ({long_128/total:.2%})")
print(f"URLs > 256 chars: {long_256:,} ({long_256/total:.2%})")

print("\n📈 PERCENTILES:")
print(f"50th (Median): {url_lengths.median():.0f} chars")
print(f"90th percentile: {url_lengths.quantile(0.90):.0f} chars")
print(f"95th percentile: {url_lengths.quantile(0.95):.0f} chars")
print(f"99th percentile: {url_lengths.quantile(0.99):.0f} chars")