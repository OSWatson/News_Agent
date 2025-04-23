# tools/prices.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key
load_dotenv()
FINANCIAL_DATASETS_API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY")

def get_crypto_prices(symbol="BTC-USD", start_date=None, end_date=None, interval="day", interval_multiplier=1):
    """
    Fetches historical cryptocurrency prices from financialdatasets.ai.
    """
    if not start_date or not end_date:
        end = datetime.today().date()
        start = end - timedelta(days=365)
        start_date = start.isoformat()
        end_date = end.isoformat()

    url = "https://api.financialdatasets.ai/crypto/prices"
    headers = {
        "x-api-key": FINANCIAL_DATASETS_API_KEY
    }
    params = {
        "ticker": symbol.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "interval": interval,
        "interval_multiplier": interval_multiplier
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        raise Exception(f"Failed to fetch crypto prices: {response.status_code} - {response.text}")


def get_crypto_price_for_date(symbol="BTC-USD", date=None):
    """
    Returns price data for a single day (or today if date is None).
    """
    if not date:
        date = datetime.today().date().isoformat()

    return get_crypto_prices(
        symbol=symbol,
        start_date=date,
        end_date=date,
        interval="day",
        interval_multiplier=1
    )
