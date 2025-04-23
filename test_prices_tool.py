from tools.prices import get_crypto_prices
from datetime import datetime, timedelta

def main():
    symbol = "BTC-USD"
    interval = "day"
    interval_multiplier = 1
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=365)

    print("\n🔍 Request Preview:")
    print(f"  Ticker             : {symbol}")
    print(f"  Start Date         : {start_date}")
    print(f"  End Date           : {end_date}")
    print(f"  Interval           : {interval}")
    print(f"  Interval Multiplier: {interval_multiplier}")
    print("\nSending request...")

    data = get_crypto_prices(symbol, start_date.isoformat(), end_date.isoformat(), interval, interval_multiplier)

    # ✅ Extract list from response
    if isinstance(data, dict) and "data" in data:
        prices = data["data"]
        print(f"\n✅ Retrieved {len(prices)} price entries for {symbol}:\n")
        for entry in prices[:5]:  # show first 5 entries
            print(entry)
    else:
        print("⚠️ Unexpected response format:")
        print(data)

if __name__ == "__main__":
    main()
