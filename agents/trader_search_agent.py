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
            # We also get numeric data for charts
            traders = self.apify.get_polymarket_leaderboard(limit=limit)
            structured_traders = []
            for t in traders:
                pnl = float(t.get('pnl') or t.get('profit') or 0)
                addr = t.get('proxyWalletAddress') or t.get('makerAddress') or 'Unknown'
                structured_traders.append({
                    "address": addr,
                    "pnl": pnl,
                    "source": "Polymarket"
                })
            
            self.learn_skill("Search Polymarket Month", str(structured_traders), "Identified whale-tier addresses for analysis mapping.")
            return structured_traders
        except Exception as e:
            self.logger.error(f"Polymarket search failed: {e}")
            return []

    def search_kalshi_traders(self):
        """
        Searches for consistent traders on Kalshi using direct API tool.
        """
        self.logger.info("Searching Kalshi consistent traders...")
        try:
            # In a real scenario, this would use the Kalshi API
            # For assessment demo, we use the tool's mock/scraped data
            traders = self.kalshi.search_consistent_traders()
            structured_traders = []
            for t in traders:
                # Clean PNL string "$45,000" to float
                pnl_str = t['pnl'].replace('$', '').replace(',', '')
                structured_traders.append({
                    "address": t['username'],
                    "pnl": float(pnl_str),
                    "source": "Kalshi"
                })

            self.learn_skill("Search Kalshi", str(structured_traders), "Targeted niche event traders for cross-platform mapping.")
            return structured_traders
        except Exception as e:
            self.logger.error(f"Kalshi search failed: {e}")
            return []
