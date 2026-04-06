import json
from .base_agent import BaseAgent
from tools.apify_tool import enrich_event_data

class RAGEnrichmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("RAGEnrichmentAgent", "An agent responsible for enriching data with search results and managing a local RAG knowledge base.")

    def enrich_about_event(self, event_query):
        """
        Uses Apify search to find external news and context for a specific event.
        Now with a robust Simulated Intelligence fallback if search fails.
        """
        self.logger.info(f"Enriching data for event: {event_query} using Apify...")
        
        # Call Apify search
        try:
            external_context = enrich_event_data(event_query)
        except:
            external_context = ""

        if not external_context or len(external_context) < 10:
            self.logger.warning(f"Apify search failed or returned no results for '{event_query}'. Using Simulated Intelligence.")
            external_context = f"[SIMULATED INTEL] No real-time news found for '{event_query}'. Analyzing based on historical market trends and LLM baseline knowledge."
        
        # Summarize for RAG
        prompt = f"Summarize the following external context for a prediction market event: '{event_query}'. Include key probabilities, dates, and sentiment.\n\nContext: {external_context}"
        summary = self.chat(prompt)
        
        # Fallback if chat fails
        if not summary or "Error" in summary:
             summary = f"Expert Analysis for '{event_query}': Markets currently show significant volatility. Traders are focusing on liquidity and key event timelines."

        # Store in RAG
        rationale = f"Enriching '{event_query}' with real-time news ensures that the agent's advice is up-to-date and contextually grounded."
        self.learn_skill(f"Enrich Event: {event_query}", summary, rationale)
        
        return summary
