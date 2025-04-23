# tools/sentiment.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_sentiment(text):
    """
    Uses OpenAI to determine sentiment of a given text.
    Returns: 'Positive', 'Negative', or 'Neutral'
    """
    prompt = f"What is the sentiment of the following text? Respond with only one word: Positive, Negative, or Neutral.\n\nText: {text}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    sentiment = response['choices'][0]['message']['content'].strip()
    return sentiment
