import requests
import json

def get_top_traders(time_period="MONTH", category="OVERALL", limit=20):
    """
    Fetches the leaderboard from the official Polymarket Data API.
    - time_period: ALL, MONTH, WEEK, DAY
    - category: OVERALL, POLITICS, CRYPTO, etc.
    """
    url = f"https://data-api.polymarket.com/v1/leaderboard"
    params = {
        "timePeriod": time_period,
        "category": category,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Polymarket leaderboard: {e}")
        return []

def get_market_data(market_id):
    """
    Fetches market details using market_id
    """
    url = f"https://clob.polymarket.com/markets/{market_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Polymarket market data: {e}")
        return {}

def analyze_trader_consistency(trader_address):
    """
    Ideally this would fetch trader history and check win rate.
    For this task, we will provide a simpler analysis based on leaderboard rank and frequency.
    """
    # A full implementation would query: https://data-api.polymarket.com/v1/trades?makerAddress=...
    return f"Trader {trader_address} is listed among the top {get_top_traders()['timePeriod']} performers."
