import json
from .base_agent import BaseAgent

class NicheMappingAgent(BaseAgent):
    def __init__(self):
        super().__init__("NicheMappingAgent", "An agent responsible for mapping traders to specific niches like NBA, Politics, Weather, etc.")

    def map_traders_to_niches(self, traders_list):
        """
        Uses LLM to analyze trader metadata and map them to niches.
        """
        prompt = f"""Analyze the following list of traders and map each to a niche based on their username or metadata if present. 
If unsure, use 'Generalist'.
        Traders: {traders_list}
        Return a JSON object where the keys are trader identifiers and the values are their niches.
        Example: {{"0x123...": "Politics", "NBAWhale": "Sports/NBA"}}
        """
        
        system_prompt = "You are a specialist in prediction market niches. Return ONLY clean JSON."
        response = self.chat(prompt, system_prompt=system_prompt)
        
        try:
            # Basic cleanup in case of markdown formatting
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            mapping = json.loads(response)
            if not isinstance(mapping, dict):
                mapping = {t: "Generalist" for t in traders_list}
            
            rationale = "Categorizing traders allows for niche-based copy trading, reducing risk."
            self.learn_skill("Categorize Traders", str(mapping), rationale)
            return mapping
        except Exception as e:
            print(f"Error mapping niches: {e}. Raw response: {response}")
            return {"error": "Could not parse JSON response."}
