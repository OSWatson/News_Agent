# tools/news_alt.py

import os
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

BASE_URL = "https://cryptopanic.com/api/v1/posts/"
NEWS_LOG_PATH = "data/news_log.csv"

def get_crypto_news(max_results=25):
    """
    Pull the most recent crypto news from CryptoPanic.
    Saves all articles to the CSV log.
    Returns only the fields needed for display.
    """
    if not API_KEY:
        raise ValueError("CryptoPanic API key not found in environment.")

    params = {
        "auth_token": API_KEY,
        "public": "true"
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: {response.status_code} - {response.text}")

    raw_news = response.json().get("results", [])[:max_results]
    
    # ⭐ Only return needed fields (cleaned for Streamlit display)
    news = []
    for item in raw_news:
        news.append({
            "title": item.get("title", "No Title"),
            "url": item.get("url", "#"),
            "domain": item.get("domain", "unknown")
        })

    save_news_to_log(raw_news)
    return news

def save_news_to_log(news_list):
    """
    Save the full raw news results into a CSV log file.
    """
    os.makedirs("data", exist_ok=True)
    is_new_file = not os.path.exists(NEWS_LOG_PATH)

    with open(NEWS_LOG_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(["title", "published_at", "domain", "url", "votes", "timestamp_logged"])

        for post in news_list:
            title = post.get("title", "")
            published_at = post.get("published_at", "")
            domain = post.get("domain", "")
            url = post.get("url", "")
            votes = post.get("votes", {}).get("important", 0)
            timestamp_logged = datetime.utcnow().isoformat()

            writer.writerow([title, published_at, domain, url, votes, timestamp_logged])
