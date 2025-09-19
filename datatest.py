import pandas as pd
import subprocess
import time
import platform
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog

def run_classification(output_widget, progress_bar, run_btn):
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), "DataSets", "bbc_text_cls.csv"))
    except Exception as e:
        messagebox.showerror("Error", f"Could not read CSV file:\n{e}")
        run_btn.config(state=tk.NORMAL)
        return

    rows = []
    total = min(len(df), 50)
    progress_bar["maximum"] = total
    run_btn.config(state=tk.DISABLED)
    output_widget.insert(tk.END, f"Processing {total} articles...\n")
    output_widget.update()

    for i, row in df.iterrows():
        text = row["text"]
        korrekt_kategori = row["labels"]
        output_widget.insert(tk.END, f"Processing article {i+1}/{total}...\n")
        output_widget.see(tk.END)
        output_widget.update()

        prompt = f"""
        Läs följande nyhetsartikel och kategorisera den i EN enkel kategori:
        {text}
        Viktigt:
        - Svara endast med en kategori (t.ex. Politik, Sport, Hälsa, Ekonomi, Kultur, etc.)
        - Svara bara med en kategori, skriv ej Bussiness (economy) exempelvis utan endast svara med EN kategori
        - Svara på Engelska
        - Om du tänker klassifiera kategorin som ekonomi skriv istället "business".
        """

        t0 = time.time()
        try:
            result = subprocess.run(
                ["ollama", "run", "gemma3:12b", prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )
            modell_kategori = result.stdout.strip()
        except Exception as e:
            modell_kategori = "ERROR"
            output_widget.insert(tk.END, f"Error processing article {i+1}: {e}\n")
            output_widget.see(tk.END)
            output_widget.update()

        t1 = time.time()

        rows.append({
            "Text": text[:120] + "...",
            "Rätt Kategori": korrekt_kategori,
            "Modell_Kategori": modell_kategori,
            "Tid (s)": round(t1 - t0,2)
        })

        progress_bar["value"] = i+1
        progress_bar.update()

        if i+1 >= total:
            break

    df_resultat = pd.DataFrame(rows)
    df_resultat["Rätt"] = df_resultat["Rätt Kategori"].str.lower() == df_resultat["Modell_Kategori"].str.lower()
    antal_ratt = df_resultat["Rätt"].sum()
    accuracy = antal_ratt / len(df_resultat) if len(df_resultat) > 0 else 0

    from sklearn.metrics import precision_score, recall_score
    y_true = df_resultat["Rätt Kategori"].str.lower()
    y_pred = df_resultat["Modell_Kategori"].str.lower()
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_true, y_pred, average="macro", zero_division=0)
    snitt_tid = df_resultat["Tid (s)"].mean()

    summary_row = {
        "Model": "Gemma3:12b",
        "Antal Artiklar": len(df_resultat),
        "Korrekt Klassifikation": antal_ratt,
        "Accuracy": f"{accuracy*100:.2f}%",
        "Precision": f"{precision*100:.2f}%",
        "Recall": f"{recall*100:.2f}%",
        "CPU": "AMD Ryzen 7 9800X3D 8-Core Processor(4.70 GHz)",
        "GPU": "RTX 4080-SUPER 16GB VRAM",
        "Genomsnitt tid för artiklar": f"{snitt_tid:.2f} s"
    }

    csv_file = "DataTestResultat/dataTestResultatGemma3.csv"
    file_exists = os.path.isfile(csv_file)
    pd.DataFrame([summary_row]).to_csv(
        csv_file,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8"
    )

    output_widget.insert(tk.END, "Klar! Sammanfattning har lagts till.\n")
    output_widget.see(tk.END)
    output_widget.update()
    run_btn.config(state=tk.NORMAL)

    
    summary_text = (
        f"Model: {summary_row['Model']}\n"
        f"Antal Artiklar: {summary_row['Antal Artiklar']}\n"
        f"Korrekt Klassifikation: {summary_row['Korrekt Klassifikation']}\n"
        f"Accuracy: {summary_row['Accuracy']}\n"
        f"Precision: {summary_row['Precision']}\n"
        f"Recall: {summary_row['Recall']}\n"
        f"Genomsnitt tid för artiklar: {summary_row['Genomsnitt tid för artiklar']}\n"
    )
    messagebox.showinfo("Sammanfattning", summary_text)

def select_and_show_csv():
    file_path = filedialog.askopenfilename(
        title="Välj CSV-fil",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not file_path:
        return
    try:
        df = pd.read_csv(file_path)
        output.delete(1.0, tk.END)
        output.insert(tk.END, f"Visar data från: {file_path}\n\n")
        output.insert(tk.END, df.to_string(index=False))
        output.see(tk.END)
    except Exception as e:
        messagebox.showerror("Fel", f"Kunde inte läsa CSV:\n{e}")

root = tk.Tk()
root.title("Gemma3:12b News Classifier")
root.geometry("500x500")

output = scrolledtext.ScrolledText(root, font=("Arial", 12), wrap=tk.WORD)
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress.pack(pady=10)

def on_run():
    output.delete(1.0, tk.END)
    progress["value"] = 0
    run_btn.config(state=tk.DISABLED)
    root.after(100, run_classification, output, progress, run_btn)

run_btn = tk.Button(root, text="Start Classification", font=("Arial", 14), command=on_run)
run_btn.pack(pady=10)

csv_btn = tk.Button(root, text="Välj och visa CSV-fil", font=("Arial", 12), command=select_and_show_csv)
csv_btn.pack(pady=5)

root.mainloop()