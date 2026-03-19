import pandas as pd

df = pd.read_parquet("data/outages.parquet")

print("Shape:", df.shape)
print(df.head())
print(df.columns)
print(df.dtypes)
print(pd.read_parquet("data/outages_clean.parquet").head())
print(pd.read_parquet("data/outage_stats.parquet").head())
print(df["period"].duplicated().sum())