import pandas as pd
import json
import matplotlib.pyplot as plt

df = pd.read_csv("resultat.csv", encoding="utf-8")

print("=== alla artiklar från CSV ===")
print(df)

print("\n=== alla artiklar från CSV ===")
print(df["Kategori"].value_counts())

df.to_json("resultat.json", orient="records", force_ascii=False, indent=2)

print("\nData sparad som resultat.json")

with open("resultat.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    
print("\n=== Data från JSON ===")
print(data)

counts = df["Kategori"].value_counts()
total = counts.sum()

#stapeldiagram
counts.plot(kind="bar")
plt.title(f"Antal artiklar per kategori (totalt: {total})")
plt.xlabel("Kategori")
plt.ylabel("Antal Artiklar")
plt.tight_layout()
plt.show()

#Cirkeldiagram
counts.plot(kind="pie", autopct="%1.1f%%")
plt.title(f"Fördelning av artiklar per kategori (totalt: {total})")
plt.ylabel("")
plt.tight_layout()
plt.show()

counts = df["Sammanfattning"].value_counts()

counts.plot(kind="pie", autopct="%1.1f%%")
plt.title(f"Fördelning av artiklarna (totalt: {total})")
plt.ylabel("")
plt.tight_layout()
plt.show()

