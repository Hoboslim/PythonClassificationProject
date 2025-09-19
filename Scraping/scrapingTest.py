import requests 
from bs4 import BeautifulSoup
import os
import subprocess
import csv

url ="https://svt.se/nyheter"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

os.makedirs('artiklar', exist_ok=True)

rubriker = soup.find_all("h2")

for i, rubrik in enumerate(rubriker[:30]):
    text = rubrik.get_text(strip=True)
    filename = f"artiklar/artikel{i+1}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print ("sparade {filename}")
    

output_path = os.path.abspath("resultat.csv")
print ("Skriver resultatet till:", output_path)

with open("resultat.csv", "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Filnamn", "Kategori", "Sammanfattning"])    
    
    for filename in os.listdir("artiklar"):
        if filename.endswith(".txt"):
            filepath = os.path.join("artiklar", filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            if not content.strip():
                print(f"Hoppar över tom fil {filename}")
                continue
            
            kategori_prompt = f"Kategorisera följande artikel i en relevant kategori\n\n{content}\n\n Svara endast med en kategori. Är det ex väder/naturkatastrof då kategoriserar du den endast som väder. Väldigt viktigt att du endast kategoriserar artiklen med EN kategori, inte flera. OBS Nyheter är inte en godkänd kategorisering"
            kategori_result = subprocess.run(
               ["ollama", "run", "gemma3:12b", kategori_prompt],
               capture_output=True,
               text=True,
                encoding="utf-8"
            )
            kategori = kategori_result.stdout.strip()
            
            sammanfattning_prompt = f"Sammanfatta följande artikel som Positiv, Negativ eller Neutral, svara endast med en av dessa tre ord.\n\n{content}"
            sammanfattning_result = subprocess.run(
                ["ollama" ,"run", "gemma3:12b", sammanfattning_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            sammanfattning = sammanfattning_result.stdout.strip()

            print(f"{filename}: [{kategori}] {sammanfattning}")
            
            writer.writerow([filename, kategori, sammanfattning])

print ("Ollama har tänkt klart, öppna resultat.csv.")