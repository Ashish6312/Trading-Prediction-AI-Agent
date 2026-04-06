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
        
        prompt = f"""Based on the following data, discuss the user's query: '{user_query}'. 
If the user wants to know who to copy, consider their profit, and the niche.

Context: 
{context_str}

{learned_skills_summary}

Provide a clear, analytical response in markdown format with recommendations.
If you found specific niche traders in 'additional_found_traders', highlight them!
        """
        
        system_prompt = "You are a professional trading analyst. Provide clear and grounded advice for copy trading. Never say 'None' if you can provide general advice."
        response = self.chat(prompt, system_prompt=system_prompt)
        
        if not response:
            response = "I encountered an error analyzing the data, but I recommend checking the leaderboard directly for high-volume traders in that niche."
            
        # Closed Learning Loop: Store user preferences or insights
        if "copy" in user_query.lower() or "trader" in user_query.lower() or "best" in user_query.lower():
            self.learn_skill(f"Inquiry: {user_query[:30]}", response[:500], "Storing user query patterns for better future recommendations.")
            
        return response
