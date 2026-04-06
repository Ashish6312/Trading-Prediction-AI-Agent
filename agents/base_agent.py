import os
import json
import logging
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configure logging for the agent framework
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_system.log"),
        logging.StreamHandler()
    ]
)

class BaseAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(self.name)
        
        # Initialize Primary LLM (OpenRouter)
        try:
            self.client = OpenAI(
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
            self.model = os.getenv("MODEL_NAME", "meta-llama/llama-3.3-70b-instruct:free")
            # The gemini-2.0-flash-exp model was deprecated/removed from free tier. We override with llama 3.3.
            if "gemini-2.0-flash-exp:free" in self.model:
                self.model = "meta-llama/llama-3.3-70b-instruct:free"
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter client: {e}")
            self.client = None
            
        # Pollinations AI fallback
        self.pollinations_api_key = os.getenv("POLLINATIONS_API_KEY", "pk_wnQgqIOSuFwKZdEI")
        self.skills_dir = "skills"
        os.makedirs(self.skills_dir, exist_ok=True)
        
        # Tool access
        import tools.apify_tool as apify
        import tools.polymarket_tool as polymarket
        import tools.kalshi_tool as kalshi
        self.apify = apify
        self.polymarket = polymarket
        self.kalshi = kalshi

    def chat(self, prompt, system_prompt=None):
        """
        Sends a message to the LLM with fallback mechanisms and error handling.
        """
        if not system_prompt:
            system_prompt = f"You are {self.name}, {self.role}."
            
        self.logger.info(f"Initiating chat. Prompt length: {len(prompt)}")
        
        # Try OpenRouter first
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                self.logger.info("Successfully generated response via OpenRouter.")
                return response.choices[0].message.content
            except Exception as e:
                self.logger.warning(f"OpenRouter failed ({e}). Falling back to Pollinations AI...")
        else:
            self.logger.warning("OpenRouter client not initialized. Using Pollinations AI...")

        # Fallback to Pollinations AI Text generation using native OpenAI format
        try:
            self.logger.info("Using Pollinations AI as LLM provider.")
            pollinations_client = OpenAI(
                api_key=self.pollinations_api_key, 
                base_url="https://text.pollinations.ai/openai"
            )
            response = pollinations_client.chat.completions.create(
                model="mistral",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            self.logger.info("Successfully generated response via Pollinations AI.")
            content = response.choices[0].message.content
            return content if content else "I'm currently synthesizing new market insights. Please refresh in a moment."
        except Exception as e:
            self.logger.error(f"Critical error: Both OpenRouter and Pollinations LLM failed. {e}")
            return f"Analysis Offline: The intelligence swarm is currently undergoing maintenance (LLM connectivity issue). Please try again in 30 seconds. Details: {str(e)[:100]}"

    def learn_skill(self, task, solution, rationale):
        """
        Implements the Closed Learning Loop by writing a skill file.
        """
        try:
            skill_name = task.lower().replace(" ", "_")[:50]
            # Sanitize filename
            skill_name = "".join([c for c in skill_name if c.isalpha() or c.isdigit() or c=='_']).rstrip()
            
            skill_content = f"# SKILL: {task}\n## Role: {self.role}\n## Solution:\n{solution}\n## Rationale:\n{rationale}\n"
            
            file_path = os.path.join(self.skills_dir, f"{skill_name}.md")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(skill_content)
                
            self.logger.info(f"Learned a new skill successfully: {skill_name}.md")
        except Exception as e:
            self.logger.error(f"Failed to learn skill '{task}': {e}")

    def get_learned_skill(self, task_query):
        """
        Retrieves relevant skills based on query.
        """
        best_skill = None
        try:
            if os.path.exists(self.skills_dir):
                for filename in os.listdir(self.skills_dir):
                    if task_query.lower() in filename.lower():
                        with open(os.path.join(self.skills_dir, filename), "r", encoding='utf-8') as f:
                            best_skill = f.read()
                            break
        except Exception as e:
            self.logger.error(f"Error reading skills: {e}")
            
        return best_skill
