import pandas as pd

infile = "./european-city-data/data-sources/wikivoyage/listings/wikivoyage-listings-raw.csv"
outfile = "./european-city-data/data-sources/wikivoyage/listings/wikivoyage-listings-cleaned.csv"

df = pd.read_csv(infile, low_memory=False)

# 按你的实际列名修改右边
df = df.rename(columns={
    "article": "city"
})

# 只保留程序需要的核心列
needed = ["city", "type", "title", "description"]
missing = [c for c in needed if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

for col in needed:
    df[col] = df[col].fillna("").astype(str).str.strip()

df = df[needed]
df.to_csv(outfile, index=False)
print("Saved to:", outfile)