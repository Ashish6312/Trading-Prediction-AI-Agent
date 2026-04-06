import json
from .base_agent import BaseAgent
from tools.apify_tool import enrich_event_data

class RAGEnrichmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("RAGEnrichmentAgent", "An agent responsible for enriching data with search results and managing a local RAG knowledge base.")

    def enrich_about_event(self, event_query):
        """
        Uses Apify search to find external news and context for a specific event.
        """
        print(f"Enriching data for event: {event_query} using Apify...")
        
        # Call Apify search
        external_context = enrich_event_data(event_query)
        
        # Summarize for RAG
        prompt = f"Summarize the following external context for a prediction market event: '{event_query}'. Include key probabilities, dates, and sentiment.\n\nContext: {external_context}"
        summary = self.chat(prompt)
        
        # Store in RAG (In this demo, we use the skills/ knowledge base as its 'RAG')
        rationale = f"Enriching '{event_query}' with real-time news ensures that the agent's advice is up-to-date and contextually grounded."
        self.learn_skill(f"Enrich Event: {event_query}", summary, rationale)
        
        return summary
