# streamlit_app.py — Frontend for Startup Finder using SSE

import streamlit as st
import requests
import json
import time

# --------------------------------------------------------------------------
# Page Config & Custom CSS
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Agentic Startup Scout",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; padding: 0.5rem 1rem; }
    .card { background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eee; }
    .company-title { font-size: 1.4rem; font-weight: 700; color: #1a1a1a; margin-bottom: 5px; }
    .company-desc { color: #555; font-size: 1rem; line-height: 1.5; margin-bottom: 15px; }
    .metric-container { display: flex; gap: 20px; background: #f8f9fa; padding: 10px 15px; border-radius: 8px; }
    .metric-item { flex: 1; }
    .metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
    .metric-value { font-size: 0.95rem; font-weight: 600; color: #333; }
    .stTextArea textarea { border-radius: 10px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.title("🚀 Agentic Startup Scout")
st.markdown("##### AI-powered sourcing & deep-dive analysis for investors")
st.markdown("---")

# --------------------------------------------------------------------------
# State Management
# --------------------------------------------------------------------------
if "criteria_value" not in st.session_state:
    st.session_state.criteria_value = "Agentic AI in healthcare, Series A, >$5M ARR"

# --------------------------------------------------------------------------
# 1. Investment Thesis Section
# --------------------------------------------------------------------------
st.subheader("1. Define Investment Thesis")

st.info("""
💡 **Examples:**
- *Infra space for crypto and web3, Saudi presence, Seed stage*
- *Agentic AI in healthcare, $5M+ ARR, Series A or B funding*
""")

criteria_input = st.text_area(
    "Describe your investment thesis:",
    value=st.session_state.criteria_value,
    height=120,
    help="Describe what you are looking for in natural language."
)

if criteria_input != st.session_state.criteria_value:
    st.session_state.criteria_value = criteria_input

col_enhance, col_dummy = st.columns([1, 3])
with col_enhance:
    if st.button("✨ Enhance with AI", help="Refine your query using AI to add synonyms and industry terms"):
        with st.spinner("Refining your criteria..."):
            try:
                enhance_url = "http://localhost:8000/enhance_query"
                resp = requests.post(enhance_url, json={"user_query": criteria_input})
                if resp.status_code == 200:
                    refined = resp.json().get("refined_query", "")
                    if refined:
                        st.session_state.criteria_value = refined
                        st.rerun()
                else:
                    st.error("Failed to enhance query.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --------------------------------------------------------------------------
# 2. Filters & Deep Dive
# --------------------------------------------------------------------------
st.subheader("2. Filters & Deep Dive")

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍 Location", placeholder="e.g. San Francisco, London")
with col2:
    funding_stage = st.selectbox("💰 Funding Stage", ["Any", "Seed", "Series A", "Series B", "Growth"])

attributes_input = st.text_input(
    "🔍 Data to Extract (Deep Dive)",
    value="Website, Founders, Total Funding, Latest Valuation, Key Competitors, Location, Industry, Technology Stack"
)
attributes = [a.strip() for a in attributes_input.split(",")]

st.markdown("---")

# --------------------------------------------------------------------------
# 3. Execution
# --------------------------------------------------------------------------
run_btn = st.button("🚀 Launch Scout Agent", type="primary", use_container_width=True)

status_container = st.container()
results_container = st.container()

if run_btn:
    with status_container:
        with st.status("🤖 Agent Workflow Running...", expanded=True) as status:
            st.write(f"📡 Connecting to Scout Agent...")

            payload = {
                "search_criteria": f"{st.session_state.criteria_value} {location if location else ''} {funding_stage if funding_stage != 'Any' else ''}",
                "attributes": attributes,
                "email": "user@example.com"
            }

            url = "http://localhost:8000/run_scout"
            found_companies = []

            try:
                response = requests.post(url, json=payload, stream=True)

                for line in response.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: "):
                            content = decoded.replace("data: ", "")
                            try:
                                data_json = json.loads(content)
                                if "success" in data_json:
                                    found_companies = data_json.get("results", [])
                                    status.update(label="✅ Mission Complete!", state="complete", expanded=False)
                                    break
                            except:
                                st.write(f"🔹 {content}")

                if found_companies:
                    st.success(f"Successfully analyzed {len(found_companies)} companies!")
                else:
                    st.warning("No companies found or analysis failed.")

            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Connection failed: {e}")

# --------------------------------------------------------------------------
# Results Display - Clean Table Format
# --------------------------------------------------------------------------
with results_container:
    if run_btn and found_companies:
        st.markdown("### 📊 Analysis Results")
        
        import pandas as pd
        
        # Build a clean table from company data
        table_data = []
        for company in found_companies:
            table_data.append({
                "Company Name": company.get("Company Name", "Unknown"),
                "Description": company.get("Description", "N/A"),
                "Website": company.get("Website", "N/A"),
                "Funding": company.get("Funding", company.get("Total Funding", "N/A")),
                "Valuation": company.get("Valuation", company.get("Latest Valuation", "N/A")),
                "Founders": company.get("Founders", "N/A"),
                "Location": company.get("Location", "N/A"),
                "Industry": company.get("Industry", "N/A"),
                "Technology Stack": company.get("Technology Stack", "N/A")
            })
        
        df = pd.DataFrame(table_data)
        
        # Display as interactive dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Website": st.column_config.LinkColumn("Website"),
                "Description": st.column_config.TextColumn("Description", width="large"),
                "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
            }
        )
