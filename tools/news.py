# tools/news.py

import os
import requests
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Get the News API key from environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_crypto_news(query="cryptocurrency", language="en"):
    url = "https://newsapi.org/v2/everything"
    headers = {
        "Authorization": NEWS_API_KEY
    }
    all_articles = []
    page = 1
    page_size = 100  # max allowed by NewsAPI

    while True:
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "sortBy": "publishedAt",
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch news: {response.status_code} - {response.text}")

        articles = response.json().get("articles", [])
        if not articles:
            break

        all_articles.extend(articles)
        if len(articles) < page_size:
            break  # No more articles to fetch

        page += 1

    return all_articles
