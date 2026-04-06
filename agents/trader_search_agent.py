import json
from .base_agent import BaseAgent
from tools.polymarket_tool import get_top_traders
from tools.kalshi_tool import scrape_kalshi_top_traders

class TraderSearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("TraderSearchAgent", "An agent responsible for identifying consistent traders on prediction markets.")

    def search_polymarket_traders(self, limit=5):
        """
        Searches for consistent traders on Polymarket using Apify.
        """
        self.logger.info("Searching Polymarket top traders for MONTH...")
        try:
            # Using the official tool function for top traders
            traders = get_top_traders(time_period="MONTH", limit=limit)
            structured_traders = []
            
            if traders and isinstance(traders, list):
                for t in traders:
                    pnl = float(t.get('pnl') or t.get('profit') or 0)
                    addr = t.get('proxyWalletAddress') or t.get('makerAddress') or t.get('address') or 'Unknown'
                    structured_traders.append({
                        "address": addr,
                        "pnl": pnl,
                        "source": "Polymarket"
                    })
            
            # Fallback to Apify if needed (if official data API is unreachable)
            if not structured_traders:
                from tools.apify_tool import scrape_polymarket_leaderboard
                apify_traders = scrape_polymarket_leaderboard(limit=limit)
                for t in apify_traders:
                    structured_traders.append({
                        "address": t.get('address') or 'Unknown',
                        "pnl": float(t.get('pnl') or 0),
                        "source": "Polymarket (Apify)"
                    })

            self.learn_skill("Search Polymarket Month", str(structured_traders), "Identified whale-tier addresses for analysis mapping.")
            return structured_traders
        except Exception as e:
            self.logger.error(f"Polymarket search failed: {e}")
            return []

    def search_kalshi_traders(self):
        """
        Searches for consistent traders on Kalshi using the scraper tool.
        """
        self.logger.info("Searching Kalshi consistent traders...")
        try:
            # Using the correctly imported function
            traders = scrape_kalshi_top_traders()
            structured_traders = []
            for t in traders:
                # Clean PNL string "$45,000" to float
                pnl_str = t.get('pnl', '0').replace('$', '').replace(',', '')
                structured_traders.append({
                    "address": t.get('username') or t.get('address') or 'Unknown',
                    "pnl": float(pnl_str),
                    "source": "Kalshi"
                })

            self.learn_skill("Search Kalshi", str(structured_traders), "Targeted niche event traders for cross-platform mapping.")
            return structured_traders
        except Exception as e:
            self.logger.error(f"Kalshi search failed: {e}")
            return []
