import json
import os
from .base_agent import BaseAgent

class TraderChatAgent(BaseAgent):
    def __init__(self):
        super().__init__("TraderChatAgent", "An agent responsible for interacting with the user and discussing which traders to copy.")

    def chat_with_data(self, user_query, current_traders_data, niches_data, event_context=None):
        """
        Discusses trader statistics, niches, and event context with the user to provide advice.
        Now with improved agentic tool use: if the query asks for a specific niche, the agent can look it up.
        """
        
        # Agentic Discovery: If user asks for a niche NOT in current data
        additional_found_traders = ""
        if any(n in user_query.lower() for n in ["nhl", "nba", "crypto", "politics", "stocks"]):
            niche_hit = next((n for n in ["nhl", "nba", "crypto", "politics", "stocks"] if n in user_query.lower()), "politics")
            self.logger.info(f"Agentic behavior triggered: searching for specific niche: {niche_hit}")
            try:
                # Use the polymarket tool to find specific niche leaders
                niche_traders = self.polymarket.get_top_traders(time_period="MONTH", category=niche_hit.upper(), limit=3)
                if niche_traders:
                    additional_found_traders = f"\nSpecific {niche_hit.upper()} Niche Leaders found: {niche_traders}\n"
            except:
                pass

        # Build the context string
        context_str = f"Current top traders: {current_traders_data}\n\nMapping to niches: {niches_data}\n{additional_found_traders}"
        if event_context:
            context_str += f"\nExternal Event Enrichment: {event_context}\n"
        
        # Check for learned skills/memories (simple RAG)
        learned_skills_summary = ""
        if os.path.exists(self.skills_dir):
            skills = list(set([f for f in os.listdir(self.skills_dir) if f.endswith(".md")]))
            if skills:
                learned_skills_summary = "Stored Knowledge (RAG): " + ", ".join(skills[:5])
        
        prompt = f"""You are a Prediction Market Analyst. Discuss the user's query: '{user_query}'. 

If you have current market data, use it. If not, use your broad general knowledge of prediction markets (Polymarket/Kalshi) to provide an expert opinion.

Context provided to you: 
{context_str}

{learned_skills_summary}

Objectives:
1. Provide a clear, analytical response in markdown.
2. If the query is about a specific niche (like NHL), and you don't have exact data, explain that you recommend following high-volume traders like 'NHLExpert' or 'PuckPro' (sample aliases) while searching for high liquidity markets.
3. Never say 'I can't answer' or 'Error' unless it's a technical crash. Provide value regardless.
"""
        
        system_prompt = "You are a professional trading analyst. Provide clear and grounded advice for copy trading. You are an expert on Polymarket and Kalshi history and logic."
        response = self.chat(prompt, system_prompt=system_prompt)
        
        if not response or len(response.strip()) < 5:
            response = "I'm currently unable to access real-time trader data for this specific niche, but generally, for NHL markets, the best predictors are often those with long histories in 'Sports' sub-categories on Polymarket with >60% win rates."
            
        # Closed Learning Loop: Store user preferences or insights
        if len(user_query) > 5:
            self.learn_skill(f"Domain Talk: {user_query[:20]}", response[:400], "Expanding analyst conversational memory.")
            
        return response
