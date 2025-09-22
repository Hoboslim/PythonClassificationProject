import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os

def scrape_bloomberg():
    url = "https://www.bloomberg.com/"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  

    html = driver.page_source
    driver.quit()

    
    with open("bloomberg_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    articles = []

   
    story_blocks = soup.find_all("a", class_="StoryBlock_storyLink__5nXw8")
    print(f"Found {len(story_blocks)} story blocks")
    for i, block in enumerate(story_blocks[:10]):
        
        headline_tag = block.find("div", attrs={"data-component": "headline"})
        headline = headline_tag.get_text(strip=True) if headline_tag else "No headline"

        
        link = block.get("href")
        if link and not link.startswith("http"):
            link = "https://www.bloomberg.com" + link

        
        summary_tag = block.find("section", attrs={"data-component": "summary"})
        summary = summary_tag.get_text(strip=True) if summary_tag else "No summary"

        articles.append({
            "Headline": headline,
            "Link": link,
            "Summary": summary
        })

    
    df = pd.DataFrame(articles)
    os.makedirs("bloomberg_articles", exist_ok=True)
    df.to_csv("bloomberg_articles/bloomberg_articles.csv", index=False, encoding="utf-8")
    print("Saved bloomberg_articles/bloomberg_articles.csv")

if __name__ == "__main__":
    scrape_bloomberg()