from tools.news import get_crypto_news

def main():
    news = get_crypto_news()
    print(f"Retrieved {len(news)} articles.")
    for i, article in enumerate(news):
        print(f"{i+1}. {article['title']} - {article['publishedAt']}")

if __name__ == "__main__":
    main()
