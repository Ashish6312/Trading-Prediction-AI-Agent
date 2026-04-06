# CrowdWisdomTrading - Prediction Market Intelligence Swarm

A production-ready, multi-agent AI framework for decentralized prediction market research (Polymarket & Kalshi). This project fulfills all technical requirements for the CrowdWisdomTrading AI Agent Assessment.

## 🚀 Key Features

- **Multi-Agent Swarm**: Four specialized agents orchestrate the research flow (Search -> Niche Mapping -> RAG Enrichment -> Analyst Chat).
- **Persistent Closed Learning Loop**: Agents document successful strategies as "Skills" (Markdown) on disk, allowing them to improve across sessions without a database.
- **RAG-Powered Intelligence**: Uses Apify for real-time web enrichment (Google Search) to ground market trades in current news events.
- **Resilient LLM Gateway**: Automatic provider fallback logic (OpenRouter -> Pollinations AI) to handle rate limits or regional outages.
- **High-End Interactive Dashboard**: A professional Streamlit UI with Plotly analytics and a native-bubble chat interface.

## 🛠️ Tech Stack & Requirements

- **Language**: Python 3.10+
- **Inference**: OpenRouter / Pollinations AI
- **RAG / Scraping**: Apify (Google Search & Polymarket Leaderboard Scraping)
- **UI**: Streamlit & Plotly
- **Framework Architecture**: Inspired by MiroShark & Hermes Agent

## 📦 Setup & Installation

1. **Clone & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Create a `.env` file at the root (see `.env.example` in this repo's documentation/prompt) and add:
   - `OPENROUTER_API_KEY`
   - `APIFY_API_TOKEN`
   - `APIFY_USER_ID`
   - `POLLINATIONS_API_KEY`

3. **Launch the Intelligence Swarm**:
   
   **Option A: Interactive Dashboard (Recommended)**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   **Option B: CLI Pipeline**
   ```bash
   python main.py
   ```

## 🧠 Multi-Agent Workflow
1. **TraderSearchAgent**: Scrapes Polymarket and Kalshi leaderboards to find consistent PnL leaders.
2. **NicheMappingAgent**: Analyzes trader behaviors to map them into niches (NBA, US Politics, Weather).
3. **RAGEnrichmentAgent**: Fetches the latest global news regarding search queries via Apify.
4. **TraderChatAgent**: Provides an interactive terminal/chat for ROI discussion and copy-trading advice.

---
Developed for **CrowdWisdomTrading** by **Antigravity**.
