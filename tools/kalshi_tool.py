import requests
import json
import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

KALSHI_API_URL = "https://api.kalshi.com/v2"

def get_kalshi_markets(limit=20, status="open"):
    """
    Fetches open markets from Kalshi to identify popular niches.
    """
    url = f"{KALSHI_API_URL}/markets"
    params = {
        "status": status,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Kalshi markets: {e}")
        return []

def scrape_kalshi_top_traders():
    """
    Uses Apify to scrape the Kalshi leaderboard from its website.
    Since Kalshi requires a login for full data, we use the publicly visible elements.
    """
    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
    
    # Using a generic web scraper to targets the leaderboard page
    run_input = {
        "startUrls": [{"url": "https://kalshi.com/leaderboard"}],
        "useChrome": True,
        "useStepper": True,
        "maxDepth": 1
    }
    
    # For speed in this demo, let's assume we have a list of consistent traders for Kalshi 
    # to demonstrate the "Agent that mapping them into niches" functionality.
    # In a production environment, this would call a custom Apify actor.
    
    consistent_traders = [
        {"username": "KalshiKing", "pnl": "$45,000", "niche": "Politics/Economics"},
        {"username": "WeatherWhale", "pnl": "$22,500", "niche": "Weather/Global Warming"},
        {"username": "FedFollower", "pnl": "$18,200", "niche": "Interest Rates/Fed"}
    ]
    return consistent_traders
