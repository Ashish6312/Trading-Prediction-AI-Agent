import json
import os
from .base_agent import BaseAgent

class TraderChatAgent(BaseAgent):
    def __init__(self):
        super().__init__("TraderChatAgent", "An agent responsible for interacting with the user and discussing which traders to copy.")

    def chat_with_data(self, user_query, current_traders_data, niches_data, event_context=None):
        """
        Discusses trader statistics, niches, and event context with the user to provide advice.
        """
        # Build the context string
        context_str = f"Current top traders: {current_traders_data}\n\nMapping to niches: {niches_data}\n"
        if event_context:
            context_str += f"\nExternal Event Enrichment: {event_context}\n"
        
        # Check for learned skills/memories (simple RAG)
        learned_skills_summary = ""
        if os.path.exists(self.skills_dir):
            skills = os.listdir(self.skills_dir)
            if skills:
                learned_skills_summary = "Stored Knowledge (RAG): " + ", ".join(skills[:5])
        
        prompt = f"""Based on the following data, discuss the user's query: '{user_query}'. 
If the user wants to know who to copy, consider their profit, and the niche.

Context: 
{context_str}

{learned_skills_summary}

Provide a clear, analytical response in markdown format with recommendations.
        """
        
        system_prompt = "You are a professional trading analyst. Provide clear and grounded advice for copy trading."
        response = self.chat(prompt, system_prompt=system_prompt)
        
        # Closed Learning Loop: Store user preferences or insights
        if "copy" in user_query.lower() or "trader" in user_query.lower():
            self.learn_skill(f"User Query: {user_query[:30]}", response[:500], "Storing user query patterns for better future recommendations.")
            
        return response
