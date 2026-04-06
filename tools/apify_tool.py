import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def scrape_polymarket_leaderboard(time_period="MONTH", limit=20):
    """
    Scrapes the Polymarket leaderboard using Apify actor: saswave/polymarket-leaderboard-scraper
    """
    run_input = {
        "limit": limit,
        "timePeriod": time_period, # "DAY", "WEEK", "MONTH", "ALL"
    }
    
    # Call the actor
    run = client.actor("saswave/polymarket-leaderboard-scraper").call(run_input=run_input)
    
    # Fetch results from the dataset
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    return results

def scrape_kalshi_leaderboard():
    """
    Scrapes the Kalshi leaderboard. Since there is no dedicated actor for leaderboard specifically,
    we can use a generic web scraper or a search actor to find top traders mentioned in news/discussions,
    but for this task we will attempt to find a workaround or use the kalshi-scraper for market data.
    """
    # For now, let's use a generic search to find consistent traders mentioned online.
    run_input = {
        "queries": "Kalshi top traders consistent wallets leaderboard",
        "maxPagesPerQuery": 1
    }
    run = client.actor("apify/google-search-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    return results

def enrich_event_data(query):
    """
    Enriches our RAG about a specific event using Apify search.
    """
    run_input = {
        "queries": f"{query} prediction market news analysis",
        "maxPagesPerQuery": 1
    }
    run = client.actor("apify/google-search-scraper").call(run_input=run_input)
    
    content = ""
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        if "organicResults" in item:
            for res in item["organicResults"]:
                content += f"\nTitle: {res.get('title')}\nSnippet: {res.get('snippet')}\nSource: {res.get('url')}\n"
    
    return content
