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
    st.session_state.criteria_value = ""

# --------------------------------------------------------------------------
# 1. Investment Thesis Section
# --------------------------------------------------------------------------
st.subheader("1. Define Investment Thesis")

st.info("""
💡 **Examples:**
- *AI startups in London*
- *Enterprise SaaS AI startups based in San Francisco*
- *Fintech startups in London at Series A*
- *Climate tech startups in Berlin with $1M+ ARR*
- *B2B payments companies in Europe, Seed stage*
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
# 2. Additional Criteria (Optional)
# --------------------------------------------------------------------------
st.subheader("2. Additional Criteria (Optional)")
st.caption("These will be added to your investment thesis to help narrow down results")

col1, col2 = st.columns(2)
with col1:
    funding_stage = st.selectbox(
        "💰 Funding Stage", 
        ["Any", "Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth"]
    )
    min_arr = st.selectbox(
        "📈 Minimum ARR",
        ["Any", "$100K+", "$500K+", "$1M+", "$5M+", "$10M+", "$50M+"]
    )
with col2:
    funding_raised = st.selectbox(
        "💵 Total Funding Raised",
        ["Any", "<$1M", "$1M-$5M", "$5M-$20M", "$20M-$50M", "$50M+"]
    )
    company_stage = st.selectbox(
        "🏢 Company Stage",
        ["Any", "Early Stage", "Growth Stage", "Late Stage"]
    )

st.markdown("---")

# --------------------------------------------------------------------------
# 3. Data to Extract (Deep Dive)
# --------------------------------------------------------------------------
st.subheader("3. Data to Extract (Deep Dive)")

attributes_input = st.text_input(
    "🔍 Select data points to research for each company",
    value="Website, Founders, Total Funding, ARR, Valuation, Key Competitors, Location, Industry, Technology Stack, Year Founded"
)
attributes = [a.strip() for a in attributes_input.split(",")]

st.markdown("---")

# --------------------------------------------------------------------------
# 4. Execution
# --------------------------------------------------------------------------
run_btn = st.button("🚀 Launch Scout Agent", type="primary", use_container_width=True)

status_container = st.container()
results_container = st.container()

if run_btn:
    with status_container:
        with st.status("🤖 Agent Workflow Running...", expanded=True) as status:
            st.write(f"📡 Connecting to Scout Agent...")

            # Build enhanced search criteria from all inputs
            search_criteria = st.session_state.criteria_value
            additional_criteria = []
            
            if funding_stage != "Any":
                additional_criteria.append(f"{funding_stage} funding")
            if min_arr != "Any":
                additional_criteria.append(f"ARR {min_arr}")
            if funding_raised != "Any":
                additional_criteria.append(f"raised {funding_raised}")
            if company_stage != "Any":
                additional_criteria.append(f"{company_stage}")
            
            if additional_criteria:
                search_criteria = f"{search_criteria}, {', '.join(additional_criteria)}"
            
            st.write(f"🔍 Searching for: *{search_criteria}*")

            payload = {
                "search_criteria": search_criteria,
                "location": "",  # No separate location filter - included in thesis
                "funding_stage": funding_stage if funding_stage != "Any" else "",
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
                "Location": company.get("Location", "N/A"),
                "Industry": company.get("Industry", "N/A"),
                "Funding Stage": company.get("Funding Stage", company.get("funding_stage", "N/A")),
                "Total Funding": company.get("Total Funding", company.get("Funding", "N/A")),
                "ARR": company.get("ARR", "N/A"),
                "Valuation": company.get("Valuation", company.get("Latest Valuation", "N/A")),
                "Founders": company.get("Founders", "N/A"),
                "Year Founded": company.get("Year Founded", "N/A"),
                "Technology Stack": company.get("Technology Stack", "N/A")
            })
        
        df = pd.DataFrame(table_data)
        
        # Display as interactive dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(500, 50 + len(df) * 40),
            column_config={
                "Company Name": st.column_config.TextColumn("Company", width=140),
                "Description": st.column_config.TextColumn("Description", width=300),
                "Website": st.column_config.LinkColumn("Website", width=120),
                "Location": st.column_config.TextColumn("Location", width=120),
                "Industry": st.column_config.TextColumn("Industry", width=120),
                "Funding Stage": st.column_config.TextColumn("Stage", width=90),
                "Total Funding": st.column_config.TextColumn("Funding", width=100),
                "ARR": st.column_config.TextColumn("ARR", width=80),
                "Valuation": st.column_config.TextColumn("Valuation", width=100),
                "Founders": st.column_config.TextColumn("Founders", width=180),
                "Year Founded": st.column_config.TextColumn("Founded", width=80),
                "Technology Stack": st.column_config.TextColumn("Tech Stack", width=160),
            }
        )
        
        # Download buttons
        st.markdown("### 📥 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name="startup_scout_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel download
            from io import BytesIO
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name="startup_scout_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
