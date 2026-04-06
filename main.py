import os
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import custom agents
from agents.trader_search_agent import TraderSearchAgent
from agents.niche_mapping_agent import NicheMappingAgent
from agents.rag_enrichment_agent import RAGEnrichmentAgent
from agents.trader_chat_agent import TraderChatAgent

load_dotenv()

console = Console()

class CrowdWisdomSystem:
    def __init__(self):
        self.search_agent = TraderSearchAgent()
        self.mapping_agent = NicheMappingAgent()
        self.enrich_agent = RAGEnrichmentAgent()
        self.chat_agent = TraderChatAgent()
        
        self.current_traders = {}
        self.current_niches = {}
        self.event_context = None

    def display_header(self):
        console.print(Panel.fit(
            "[bold cyan]CrowdWisdomTrading: Prediction Market Intelligence Agent[/bold cyan]\n"
            "[italic]Real-time Trader Analysis, Niche Mapping, and Event Enrichment[/italic]",
            border_style="cyan"
        ))

    def run_workflow(self, event_query="2024 Presidential Election"):
        """
        Runs the full agent flow: search -> map -> enrich -> chat
        """
        # 1. Search consistent traders (Polymarket & Kalshi)
        console.print(f"\n[bold yellow]Step 1: Searching for consistent traders on Polymarket...[/bold yellow]")
        poly_traders = self.search_agent.search_polymarket_traders(time_period="MONTH", limit=5)
        
        # Format poly_traders for the next step (list of strings or dicts)
        trader_summary = []
        if isinstance(poly_traders, list):
            for t in poly_traders:
                addr = t.get('proxyWalletAddress') or t.get('makerAddress') or 'Unknown'
                pnl = t.get('pnl') or t.get('profit') or 0
                trader_summary.append(f"{addr} (PNL: ${pnl})")
        
        console.print(f"[bold yellow]Step 2: Searching for consistent traders on Kalshi...[/bold yellow]")
        kalshi_traders = self.search_agent.search_kalshi_traders()
        for t in kalshi_traders:
            trader_summary.append(f"{t['username']} (PNL: {t['pnl']})")
        
        # 2. Map traders to Niches
        console.print(f"\n[bold yellow]Step 3: Mapping traders to niches using LLM reasoning...[/bold yellow]")
        self.current_niches = self.mapping_agent.map_traders_to_niches(trader_summary)
        
        # 3. Enrich with Apify RAG
        console.print(f"\n[bold yellow]Step 4: Enriching knowledge about event: '{event_query}' using APIFY...[/bold yellow]")
        self.event_context = self.enrich_agent.enrich_about_event(event_query)

        # Output the results so far
        self.display_summary_table()

    def display_summary_table(self):
        table = Table(title="Predictive Market Intelligence Summary", show_header=True, header_style="bold magenta")
        table.add_column("Trader Address/User", style="dim", width=30)
        table.add_column("Mapped Niche", justify="center")
        
        if isinstance(self.current_niches, dict):
            for trader, niche in self.current_niches.items():
                table.add_row(trader, niche)
        
        console.print(table)

    def interactive_chat(self):
        console.print("\n[bold green]System ready! You can now chat with the data and discuss which trader to copy.[/bold green]")
        console.print("[italic]Type 'exit' to quit or 'flow' to re-run the research pipeline.[/italic]\n")
        
        while True:
            user_input = console.input("[bold blue]User:[/bold blue] ")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'flow':
                new_event = console.input("[yellow]Enter event to research (e.g., 'NBA Finals', 'US Interest Rates'): [/yellow]")
                self.run_workflow(new_event)
                continue
            
            # Interactive response from TraderChatAgent
            response = self.chat_agent.chat_with_data(user_input, self.current_traders, self.current_niches, self.event_context)
            console.print(Panel(response, title="[bold cyan]Agent Response[/bold cyan]", border_style="cyan"))

if __name__ == "__main__":
    system = CrowdWisdomSystem()
    system.display_header()
    
    # Run the initial flow to load data
    system.run_workflow("US 2024 Presidential Election")
    
    # Enter interactive chat
    system.interactive_chat()
