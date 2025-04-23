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

# CSS for side-by-side horizontal scrolling top banner
st.markdown("""
    <style>
    .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .news-banner {
        display: flex;
        flex-direction: row;
        overflow-x: auto;
        gap: 16px;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .news-box {
        flex: 0 0 auto;
        width: 240px;
        height: 120px;
        background-color: #1e1e1e;
        border: 1px solid #444;
        padding: 12px;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .news-box a {
        color: #f3f3f3;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
    }
    .news-box .domain {
        font-size: 12px;
        color: #aaa;
    }
    </style>
""", unsafe_allow_html=True)

# --- Horizontal Top Banner ---
st.markdown("## 🗞️ Top 10 Recent Crypto Headlines")

articles = get_crypto_news(max_results=10)

news_boxes = ""
for article in articles:
    title = article.get("title", "No title")
    link = article.get("url", "#")
    domain = article.get("domain", "unknown")
    news_boxes += f"""
        <div class="news-box">
            <a href="{link}" target="_blank">{title}</a>
            <div class="domain">Source: {domain}</div>
        </div>
    """

news_html = f'<div class="news-banner">{news_boxes}</div>'
import streamlit.components.v1 as components
components.html(news_html, height=180)

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
            result = search_regulations(**fn_args)
            return fn_name, f"🏛️ Found {len(result)} government documents mentioning '{fn_args['query']}'."

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
