import pandas as pd

df = pd.read_csv("resultat.csv")
print(df)

print("Artiklar per kategori:")
print(df["Kategori"].value_counts())