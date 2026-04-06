import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from agents.trader_search_agent import TraderSearchAgent
from agents.niche_mapping_agent import NicheMappingAgent
from agents.rag_enrichment_agent import RAGEnrichmentAgent
from agents.trader_chat_agent import TraderChatAgent

# Configure Page
st.set_page_config(
    page_title="CrowdWisdomTrading | AI Swarm Dashboard",
    page_icon="💸",
    layout="wide"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trader_data" not in st.session_state:
    st.session_state.trader_data = [] # Structured list of dicts
if "niche_mapping" not in st.session_state:
    st.session_state.niche_mapping = None
if "rag_context" not in st.session_state:
    st.session_state.rag_context = ""

# Professional CSS
st.markdown("""
<style>
    /* Glassmorphism Effect */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
    }
    
    div[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Fix Table Cutoff in Chat */
    table {
        display: block;
        overflow-x: auto !important;
        width: 100% !important;
        border-collapse: collapse;
        margin: 10px 0;
        border-radius: 8px;
        font-size: 0.85rem;
    }
    
    th, td {
        padding: 12px !important;
        text-align: left !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Chat Bubble Styling */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .skill-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    
    .stHeader {
        background: transparent;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: PERSISTENCE & CONTROL ---
with st.sidebar:
    # Logo Placeholder / Title
    st.title("🛡️ Swarm Hub")
    st.caption("CrowdWisdom Persistence Engine")
    
    # 1. Controls
    with st.expander("🛠️ Control Panel", expanded=True):
        event_query = st.text_input("Target Event (RAG)", "US 2024 Presidential Election")
        run_btn = st.button("🔥 Launch Intelligent Sweep", use_container_width=True)

    # 2. Knowledge Graph (Persistent Skills)
    st.divider()
    st.subheader("📚 Learned Skills")
    skills_dir = "skills"
    if os.path.exists(skills_dir):
        files = os.listdir(skills_dir)
        for f in files:
            if f.endswith(".md"):
                if st.button(f"📄 {f.replace('.md','').title()}", use_container_width=True, key=f):
                    with open(os.path.join(skills_dir, f), "r") as skf:
                        content = skf.read()
                        st.session_state.selected_skill = content

    if "selected_skill" in st.session_state:
        st.info("Skill Preview Active (See Right Column)")

# --- MAIN WORKFLOW EXECUTION ---
if run_btn:
    with st.status("🚀 Swarm Orchestrator Active...", expanded=True) as status:
        st.write("Initializing Agents...")
        search_agent = TraderSearchAgent()
        mapping_agent = NicheMappingAgent()
        enrich_agent = RAGEnrichmentAgent()

        # Step 1: Search
        st.write("🔍 Searching across Polymarket & Kalshi...")
        poly = search_agent.search_polymarket_traders()
        kalshi = search_agent.search_kalshi_traders()
        st.session_state.trader_data = poly + kalshi
        
        # Step 2: Map
        st.write("🏷️ Mapping Traders to Profit Niches...")
        # Format for mapping agent string processing
        trader_strs = [f"{t['address']} (PNL: ${t['pnl']})" for t in st.session_state.trader_data]
        st.session_state.niche_mapping = mapping_agent.map_traders_to_niches(trader_strs)
        
        # Step 3: Enrich
        st.write(f"🌐 Running RAG Enrichment for '{event_query}'...")
        st.session_state.rag_context = enrich_agent.enrich_about_event(event_query)
        
        status.update(label="✅ Sweep Complete!", state="complete", expanded=False)

# --- UI LAYOUT ---
col_left, col_right = st.columns([2, 1], gap="medium")

with col_left:
    st.header("📊 Market Intelligence Workspace")
    
    if st.session_state.trader_data:
        # Plotly Chart (Interactive)
        df = pd.DataFrame(st.session_state.trader_data)
        fig = px.bar(df, x="address", y="pnl", color="source", title="Trader Performance Index ($ PNL)",
                     template="plotly_dark", color_discrete_sequence=["#00d2ff", "#ff4b4b"])
        fig.update_layout(xaxis_title="Trader Wallet / ID", yaxis_title="PnL ($)")
        st.plotly_chart(fig, use_container_width=True)

        # Tabs for details
        tab_list, tab_niches, tab_rag = st.tabs(["📝 Raw Ledger", "🧩 Niche Matrix", "🗞️ RAG Synthesis"])
        
        with tab_list:
            st.dataframe(df, use_container_width=True)
            
        with tab_niches:
            if st.session_state.niche_mapping:
                for trader, niche in st.session_state.niche_mapping.items():
                    with st.expander(f"**{trader}** Strategy"):
                        st.markdown(f"**Niche:** `{niche}`")
                        st.markdown(f"**Rationale:** Analyzing consistency in `{niche}` markets.")
        
        with tab_rag:
            st.markdown(st.session_state.rag_context if st.session_state.rag_context else "No RAG context loaded.")
    else:
        st.info("Connect to the Swarm using the 'Launch Intelligent Sweep' button to populate data.")

with col_right:
    # 1. Persistent Skill Viewer
    if "selected_skill" in st.session_state:
        st.header("📖 Skill Insight")
        st.markdown(st.session_state.selected_skill)
        if st.button("Close Viewer"):
            del st.session_state.selected_skill
            st.rerun()
    else:
        # 2. Chat Interface
        st.header("💬 Intelligence Analyst")
        st.caption("Ask questions about the traders or the enriched event data.")
        
        # Container for chat
        chat_box = st.container(height=500)
        for msg in st.session_state.messages:
            with chat_box.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_prompt := st.chat_input("Analyze trader ROI..."):
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with chat_box.chat_message("user"):
                st.write(user_prompt)
            
            with chat_box.chat_message("assistant"):
                with st.spinner("Analyzing swarm data..."):
                    chat_agent = TraderChatAgent()
                    response = chat_agent.chat_with_data(
                        user_prompt, 
                        [f"{t['address']} PNL: {t['pnl']}" for t in st.session_state.trader_data],
                        st.session_state.niche_mapping,
                        st.session_state.rag_context
                    )
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

