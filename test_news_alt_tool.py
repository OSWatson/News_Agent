# test_news_alt_tool.py

from tools.news_alt import get_crypto_news

def main():
    print("\n📰 Fetching the most recent crypto news...\n")
    news_items = get_crypto_news(max_results=10)

    if not news_items:
        print("No news articles found.")
        return

    for i, item in enumerate(news_items, 1):
        print(f"{i}. {item.get('title', 'No title')}")
        print(f"   URL: {item.get('url')}")
        print(f"   Source: {item.get('domain')} | Published: {item.get('published_at')}\n")

    print("✅ News saved to data/news_log.csv")

if __name__ == "__main__":
    main()
