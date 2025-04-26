import streamlit as st
import os
import openai
from dotenv import load_dotenv

# Load API keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import tools
from tools.news_alt import get_crypto_news
from tools.prices import get_crypto_prices, get_crypto_price_for_date
from tools.regulations import search_regulations, get_document_details
from tools.sentiment import analyze_sentiment

# Set Streamlit page config
st.set_page_config(page_title="Crypto AI Agent", page_icon="🧠", layout="wide")

import streamlit.components.v1 as components
import requests

# --- Crypto Price Ticker using financialdatasets.ai ---

# Top 25 coins you want
coins = [
    "BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "SOL-USD", "USDC-USD", "XRP-USD", "DOGE-USD", "TON-USD", "ADA-USD",
    "AVAX-USD", "SHIB-USD", "WBTC-USD", "DOT-USD", "TRX-USD", "LINK-USD", "BCH-USD", "NEAR-USD", "LTC-USD", "ICP-USD",
    "MATIC-USD", "DAI-USD", "UNI-USD", "LEO-USD", "ETC-USD"
]

# Pull sentiment for each coin
# Pull ALL articles first (not just 10)
articles = get_crypto_news(max_results=200)  # Get more news so we have enough data

# Helper: Analyze sentiment score per coin AND count articles
def get_sentiment_score_for_coin(coin_name, articles):
    related_articles = [article for article in articles if coin_name.lower().replace("-usd", "") in article.get("title", "").lower()]
    
    if not related_articles:
        return 0, 0  # No articles → Neutral score, 0 articles
    
    scores = []
    for article in related_articles:
        sentiment = analyze_sentiment(article.get("title", ""))
        if sentiment == "Positive":
            scores.append(1)
        elif sentiment == "Negative":
            scores.append(-1)
        else:
            scores.append(0)
    
    average_score = sum(scores) / len(scores)
    return round(average_score, 2), len(related_articles)   # <<<<< see? returns TWO things


# Now actually calculate sentiment per coin
sentiments = {}
article_counts = {}  # <-- NEW dictionary

for coin in coins:
    avg_score, num_articles = get_sentiment_score_for_coin(coin, articles)
    sentiments[coin] = avg_score
    article_counts[coin] = num_articles



# Build the ticker text
ticker_text = "   •   ".join([
    f"{coin}: {'🟢' if sentiments[coin] > 0.2 else '⚪' if sentiments[coin] >= -0.2 else '🔴'} {sentiments[coin]:+.2f} ({article_counts[coin]} articles)"
    for coin in coins
])




# Show the moving ticker
components.html(f"""
    <style>
        .ticker-container {{
            width: 100%;
            overflow: hidden;
            background-color: #111;
            padding: 8px 0;
        }}
        .ticker-text {{
            display: inline-block;
            white-space: nowrap;
            animation: tickerMove 100s linear infinite;
            font-size: 16px;
            color: #00ff99;
            font-weight: bold;
        }}
        @keyframes tickerMove {{
            0% {{ transform: translateX(20%); }}
            100% {{ transform: translateX(-20%); }}
        }}
    </style>
    <div class="ticker-container">
        <div class="ticker-text">
    {ticker_text}   {ticker_text}
    </div>

    </div>
""", height=50)


# --- Horizontal Top Banner ---
# --- Horizontal Top Banner ---
st.markdown("## 🗞️Recent Crypto Headlines")


# Analyze sentiment for each article
for article in articles:
    title = article.get("title", "")
    article["sentiment"] = analyze_sentiment(title)

news_boxes = ""
for article in articles:
    title = article.get("title", "No title")
    link = article.get("url", "#")
    domain = article.get("domain", "unknown")
    news_boxes += f"""
    <div class="news-box">
        <a href="{link}" target="_blank">{title}</a>
        <div class="domain">Source: {domain}</div>
        <div class="sentiment">
            {"🟢" if article.get('sentiment') == "Positive" else "⚪" if article.get('sentiment') == "Neutral" else "🔴"}
            {article.get('sentiment', 'Neutral')}
        </div>
    </div>
"""


import streamlit.components.v1 as components

with st.container():
    components.html(f"""
        <style>
            .news-banner {{
                display: flex;
                flex-direction: row;
                overflow-x: auto;
                gap: 20px;
                padding: 1rem 0;
                margin-bottom: 2rem;
                white-space: nowrap;
                flex-wrap: nowrap;
                scrollbar-width: none; /* Firefox */
            }}
            .news-banner::-webkit-scrollbar {{
                display: none; /* Chrome, Safari, Opera */
            }}
            .news-box {{
                flex: 0 0 auto;
                width: 180px;
                height: 140px;
                background-color: #333;
                border: 1px solid #555;
                padding: 12px;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            .news-box:hover {{
                transform: scale(1.05);
                box-shadow: 0 6px 18px rgba(0,0,0,0.6);
                border-color: #888;
            }}
            .news-box a {{
                color: #ffffff;
                text-decoration: none;
                font-weight: 700;
                font-size: 14px;
                white-space: normal;
                word-wrap: break-word;
            }}
            .news-box .domain {{
                font-size: 13px;
                color: #bbb;
                margin-top: 10px;
            }}
            .sentiment {{
                font-size: 11px;
                color: #aaa;
                margin-top: auto;
                text-align: right;
            }}
        </style>
        <div class="news-banner">
            {news_boxes}
        </div>
    """, height=250, scrolling=True)

# --- Tool Functions ---
function_schemas = [
    {
        "name": "get_crypto_news",
        "description": "Get the most recent crypto news and calculate sentiment scores if asked about mood, sentiment, or tone of articles.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Maximum number of articles to return."}
            },
            "required": ["max_results"]
        }
    },
    {
        "name": "get_crypto_prices",
        "description": "Get historical crypto price data.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "interval": {"type": "string"},
                "interval_multiplier": {"type": "integer"}
            },
            "required": ["symbol", "interval", "interval_multiplier"]
        }
    },
    {
        "name": "search_regulations",
        "description": "Search U.S. regulatory documents about crypto.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer"}
            },
            "required": ["query", "max_results"]
        }
    },
    {
        "name": "get_crypto_price_for_date",
        "description": "Get the price of a cryptocurrency for a specific date (or today).",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "date": {"type": "string", "description": "The date in YYYY-MM-DD format."}
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "analyze_sentiment",
        "description": "Determine the sentiment (Positive, Neutral, Negative) of a given piece of text.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            },
            "required": ["text"]
        }
    }
]

# --- Agent Logic ---
def run_agent_with_trace(user_input, status_box):
    messages = [{"role": "user", "content": user_input}]
    status_box.markdown("🤖 Calling OpenAI to select a tool...")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=function_schemas,
        function_call="auto"
    )

    message = response["choices"][0]["message"]

    if message.get("function_call"):
        fn_name = message["function_call"]["name"]
        fn_args = eval(message["function_call"]["arguments"])
        status_box.markdown(f"📦 Tool Selected: `{fn_name}` — loading...")

        if fn_name == "get_crypto_news":
            result = get_crypto_news(**fn_args)
            if not result:
                return fn_name, "No news found."

            score_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
            scored_articles = []

            for article in result[:10]:
                title = article.get("title", "No title")
                sentiment = analyze_sentiment(title)
                score = score_map.get(sentiment, 0)

                scored_articles.append({
                    "title": title,
                    "link": article.get("url", "#"),
                    "domain": article.get("domain", ""),
                    "sentiment": sentiment,
                    "score": score
                })

            user_lower = user_input.lower()
            sort_reverse = any(word in user_lower for word in ["best", "positive", "highest", "top"])
            scored_articles.sort(key=lambda x: x["score"], reverse=sort_reverse)

            sentiment_scores = [a["score"] for a in scored_articles]
            avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            sentiment_level = (
                "🟢 Positive" if avg_score > 0.2 else
                "⚪ Neutral" if -0.2 <= avg_score <= 0.2 else
                "🔴 Negative"
            )

            summary = [f"**🧠 Average Sentiment Score:** `{avg_score:.2f}` → {sentiment_level}\n"]
            for i, a in enumerate(scored_articles):
                summary.append(
                    f"**{i+1}. [{a['title']}]({a['link']})** — {a['domain']} — *Sentiment:* `{a['sentiment']}`"
                )

            return fn_name, "📰 **Top Crypto News (sorted by Sentiment):**\n\n" + "\n\n".join(summary)

        elif fn_name == "get_crypto_prices":
            fn_args.setdefault("interval", "day")
            fn_args.setdefault("interval_multiplier", 1)
            translations = {"d": "day", "m": "month", "h": "minute", "y": "year", "w": "week"}
            fn_args["interval"] = translations.get(fn_args["interval"], fn_args["interval"])
            result = get_crypto_prices(**fn_args)
            return fn_name, f"📈 Pulled price data for {fn_args['symbol']} ({len(result)} entries)."

        elif fn_name == "search_regulations":
            try:
                result = search_regulations(**fn_args)
                return fn_name, f"🏛️ Found {len(result)} government documents mentioning '{fn_args['query']}'."
            except Exception as e:
                return fn_name, f"❌ Failed to search regulations: {str(e)}"

        elif fn_name == "get_crypto_price_for_date":
            result = get_crypto_price_for_date(**fn_args)
            if result:
                price = result[0].get("close", "N/A")
                return fn_name, f"📈 {fn_args['symbol']} price on {fn_args.get('date', 'today')}: **${price}**"
            else:
                return fn_name, f"⚠️ No price data available for {fn_args['symbol']} on {fn_args.get('date', 'that date')}."

        elif fn_name == "analyze_sentiment":
            sentiment = analyze_sentiment(**fn_args)
            return fn_name, f"🧠 Sentiment: **{sentiment}**"

        else:
            return "unknown", "❌ Unknown tool requested."

    else:
        return "chat", message["content"]

# --- Streamlit Chat UI ---
st.markdown("## 🤖 Crypto AI Agent")
col1, col2 = st.columns([1, 2])

with col1:
    user_input = st.text_input("💬 Ask something about crypto:")

with col2:
    status_box = st.empty()
    if user_input:
        with st.spinner("Thinking..."):
            status_box.markdown("🧠 Thinking about your question...")
            tool, result = run_agent_with_trace(user_input, status_box)
            status_box.markdown(f"✅ Tool selected: `{tool}`")
            st.markdown(result)
