# frontend_copy.py — Modern Startup Scout UI

import streamlit as st
import requests
import json
import pandas as pd
from io import BytesIO

# ==========================================================================
# PAGE CONFIGURATION
# ==========================================================================
st.set_page_config(
    page_title="Investment Sourcing Agent | Arab Bank Ventures",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================================
# CUSTOM CSS - Professional Enterprise Theme
# ==========================================================================
st.markdown("""
<style>
    /* ===== Root Variables - Custom Color Palette ===== */
    :root {
        --curious-blue: #1680E4;
        --blue-ribbon: #0671FF;
        --oslo-gray: #939598;
        --emperor: #555354;
        --persian-blue: #2B1CA9;
        --surface: #ffffff;
        --border: #e2e8f0;
        --border-light: #f1f3f5;
        --text-primary: #555354;
        --text-secondary: #939598;
    }
    
    /* ===== Global Styles - Subtle Gradient Background ===== */
    .main { 
        background: linear-gradient(180deg, #f8faff 0%, #f0f4ff 50%, #ffffff 100%) !important;
    }
    
    .stApp {
        background: linear-gradient(180deg, #f8faff 0%, #f0f4ff 50%, #ffffff 100%) !important;
    }
    
    .block-container {
        padding: 2rem 2rem 4rem 2rem !important;
        max-width: 800px !important;
        margin: 0 auto !important;
        background: transparent;
    }
    
    /* ===== Section Wrapper - Subtle Frosted White ===== */
    .section-wrapper {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        padding: 1.75rem 2rem 1.25rem 2rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 24px rgba(43, 28, 169, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
    }
    
    .section-wrapper:hover {
        box-shadow: 0 8px 32px rgba(22, 128, 228, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03);
        border-color: rgba(22, 128, 228, 0.15);
    }
    
    /* Section Divider/Spacer */
    .section-divider {
        height: 2.5rem;
        margin: 0;
    }
    
    /* ===== Typography ===== */
    h1, h2, h3 { 
        color: var(--emperor) !important;
        font-weight: 700 !important;
    }
    
    /* ===== Hero Header ===== */
    .hero {
        background: linear-gradient(135deg, var(--persian-blue) 0%, var(--blue-ribbon) 100%);
        border-radius: 0;
        padding: 2.5rem 3rem;
        margin-bottom: 0;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-inner {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(22, 128, 228, 0.25) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        position: relative;
        color: white !important;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
        position: relative;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.2);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 1rem;
        position: relative;
    }
    
    /* ===== Form Elements - Glass Style ===== */
    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(22, 128, 228, 0.2) !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--curious-blue) !important;
        box-shadow: 0 0 0 4px rgba(22, 128, 228, 0.1), 0 4px 20px rgba(22, 128, 228, 0.15) !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1px solid rgba(22, 128, 228, 0.2) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--curious-blue) !important;
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* ===== Buttons - Glass Style ===== */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--blue-ribbon) 0%, var(--curious-blue) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(6, 113, 255, 0.4) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(6, 113, 255, 0.45) !important;
        background: linear-gradient(135deg, var(--curious-blue) 0%, var(--persian-blue) 100%) !important;
    }
    
    .stButton > button[kind="secondary"], 
    .stButton > button:not([kind="primary"]) {
        background: #ffffff !important;
        color: var(--emperor) !important;
        border: 2px solid var(--border) !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--curious-blue) !important;
        color: var(--curious-blue) !important;
        background: rgba(22, 128, 228, 0.05) !important;
    }
    
    /* ===== Multiselect ===== */
    .stMultiSelect span[data-baseweb="tag"] {
        background: var(--curious-blue) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    .stMultiSelect > div > div {
        border-radius: 10px !important;
        border: 2px solid var(--border) !important;
        background: #ffffff !important;
    }
    
    .stMultiSelect > div > div:hover,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--curious-blue) !important;
    }
    
    /* ===== Section Header ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
    }
    
    .section-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--blue-ribbon) 0%, var(--curious-blue) 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--emperor);
        margin: 0;
    }
    
    /* ===== Section Divider ===== */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border) 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* ===== Status Messages ===== */
    .stSuccess {
        border-radius: 12px !important;
        background-color: rgba(22, 128, 228, 0.1) !important;
        border-left: 4px solid var(--curious-blue) !important;
    }
    
    .stWarning {
        border-radius: 12px !important;
    }
    
    .stError {
        border-radius: 12px !important;
    }
    
    .stInfo {
        border-radius: 12px !important;
        background-color: rgba(43, 28, 169, 0.08) !important;
        border-left: 4px solid var(--persian-blue) !important;
    }
    
    /* ===== Data Table ===== */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid var(--border) !important;
    }
    
    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: var(--emperor) !important;
        background: #ffffff !important;
        padding: 1rem 1.25rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        color: var(--curious-blue) !important;
        background: #f8fafc !important;
    }
    
    /* Make expander content wider */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stExpander"] > div {
        padding: 0 !important;
    }
    
    .streamlit-expanderContent {
        padding: 1.25rem !important;
        background: #ffffff !important;
        border-top: 1px solid var(--border-light) !important;
    }
        color: var(--emperor) !important;
        background: #ffffff !important;
    }
    
    .streamlit-expanderHeader:hover {
        color: var(--curious-blue) !important;
    }
    
    /* ===== Tooltip Styling ===== */
    .tooltip-text {
        font-size: 0.8rem;
        color: var(--oslo-gray);
        font-style: italic;
    }
    
    /* ===== Animation ===== */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* ===== Company Cards ===== */
    .company-cards-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin: 1.5rem 0;
    }
    
    .company-card-wrapper {
        background: var(--surface);
        border-radius: 14px;
        border: 1px solid var(--border);
        overflow: hidden;
        transition: all 0.2s ease;
    }
    
    .company-card-wrapper:hover {
        border-color: var(--curious-blue);
        box-shadow: 0 4px 16px rgba(22, 128, 228, 0.1);
    }
    
    .company-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.25rem;
        cursor: pointer;
        background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
    }
    
    .company-card-header:hover {
        background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%);
    }
    
    .company-card-title-section {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .company-avatar {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--curious-blue) 0%, var(--persian-blue) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .company-card-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--emperor);
        margin: 0;
    }
    
    .company-card-tags {
        display: flex;
        gap: 8px;
        margin-top: 4px;
    }
    
    .company-tag {
        font-size: 0.7rem;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 500;
    }
    
    .company-tag.sector {
        background: rgba(43, 28, 169, 0.1);
        color: var(--persian-blue);
    }
    
    .company-tag.country {
        background: rgba(22, 128, 228, 0.1);
        color: var(--curious-blue);
    }
    
    .company-tag.stage {
        background: rgba(147, 149, 152, 0.15);
        color: var(--emperor);
    }
    
    .company-card-details {
        padding: 0 1.25rem 1.25rem 1.25rem;
        border-top: 1px solid var(--border-light);
        background: #ffffff;
    }
    
    .company-detail-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-top: 1rem;
    }
    
    .company-detail-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .company-detail-label {
        font-size: 0.7rem;
        color: var(--oslo-gray);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .company-detail-value {
        font-size: 0.9rem;
        color: var(--emperor);
        font-weight: 500;
    }
    
    .company-detail-value a {
        color: var(--curious-blue);
        text-decoration: none;
    }
    
    .company-detail-value a:hover {
        text-decoration: underline;
    }
    
    .company-description {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-light);
    }
    
    .company-description-text {
        font-size: 0.9rem;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* View toggle buttons */
    .view-toggle-container {
        display: flex;
        gap: 8px;
        margin-bottom: 1rem;
    }
    
    .view-toggle-btn {
        padding: 8px 16px;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: #ffffff;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--oslo-gray);
        transition: all 0.2s ease;
    }
    
    .view-toggle-btn:hover {
        border-color: var(--curious-blue);
        color: var(--curious-blue);
    }
    
    .view-toggle-btn.active {
        background: var(--curious-blue);
        color: white;
        border-color: var(--curious-blue);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================================
# HELPER FUNCTIONS
# ==========================================================================
def _to_str(val):
    """Convert any value to a display string."""
    if val is None:
        return "—"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val) if val else "—"

def render_kpi_cards(metrics: list):
    """Render beautiful KPI cards using Streamlit columns for reliability."""
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
                border-radius: 16px;
                padding: 1.5rem 1rem;
                text-align: center;
                border: 1px solid #e2e8f0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            ">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">{metric['icon']}</div>
                <div style="font-size: 2rem; font-weight: 800; color: #2B1CA9; line-height: 1; margin-bottom: 6px;">{metric['value']}</div>
                <div style="font-size: 0.75rem; color: #939598; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{metric['label']}</div>
            </div>
            ''', unsafe_allow_html=True)

def render_section_end():
    """Add spacing after a section."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

def render_section_header(number: int, title: str):
    """Render a numbered section header with wrapper."""
    st.markdown(f'''
    <div class="section-wrapper">
        <div class="section-header">
            <div class="section-number">{number}</div>
            <p class="section-title">{title}</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def get_company_initials(name: str) -> str:
    """Get initials from company name for avatar."""
    if not name:
        return "?"
    words = name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return name[:2].upper()

def render_company_card(company: dict, index: int):
    """Render an expandable company card using Streamlit expander."""
    name = _to_str(company.get('name', 'Unknown Company'))
    country = _to_str(company.get('country', ''))
    sector = _to_str(company.get('market_sector', ''))
    stage = _to_str(company.get('funding_stage', ''))
    description = _to_str(company.get('description', ''))
    website = _to_str(company.get('url', ''))
    founded = _to_str(company.get('founding_year', ''))
    arr = _to_str(company.get('ARR', ''))
    
    # Build tags for the header
    tags = []
    if sector and sector != '—':
        tags.append(f'<span class="company-tag sector">{sector}</span>')
    if country and country != '—':
        tags.append(f'<span class="company-tag country">🌍 {country}</span>')
    if stage and stage != '—':
        tags.append(f'<span class="company-tag stage">{stage}</span>')
    
    tags_html = ''.join(tags[:3])  # Limit to 3 tags
    
    initials = get_company_initials(name)
    
    with st.expander(f"🏢 {name}", expanded=False):
        # Company details in a nice grid
        st.markdown(f'''
        <div style="margin: -1rem -1rem 0 -1rem; padding: 1.25rem; background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); border-radius: 8px;">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 1rem;">
                <div class="company-avatar" style="width: 48px; height: 48px; font-size: 1.1rem;">{initials}</div>
                <div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #555354;">{name}</div>
                    <div class="company-card-tags" style="margin-top: 8px;">{tags_html}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Description section
        if description and description != '—':
            st.markdown(f'''
            <div style="margin: 1.25rem 0; padding: 1.25rem; background: #f8fafc; border-radius: 12px; border-left: 4px solid #1680E4;">
                <div style="font-size: 0.75rem; color: #939598; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 8px;">About</div>
                <div style="font-size: 1rem; color: #555354; line-height: 1.7;">{description}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Details grid
        col1, col2 = st.columns(2)
        
        with col1:
            if website and website != '—':
                st.markdown(f'''
                <div class="company-detail-item">
                    <div class="company-detail-label" style="font-size: 0.75rem;">🌐 Website</div>
                    <div class="company-detail-value" style="font-size: 0.95rem;"><a href="{website}" target="_blank">{website}</a></div>
                </div>
                ''', unsafe_allow_html=True)
            
            if founded and founded != '—':
                st.markdown(f'''
                <div class="company-detail-item" style="margin-top: 14px;">
                    <div class="company-detail-label" style="font-size: 0.75rem;">📅 Founded</div>
                    <div class="company-detail-value" style="font-size: 0.95rem;">{founded}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        with col2:
            if stage and stage != '—':
                st.markdown(f'''
                <div class="company-detail-item">
                    <div class="company-detail-label" style="font-size: 0.75rem;">💰 Funding Stage</div>
                    <div class="company-detail-value" style="font-size: 0.95rem;">{stage}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            if arr and arr != '—':
                st.markdown(f'''
                <div class="company-detail-item" style="margin-top: 14px;">
                    <div class="company-detail-label" style="font-size: 0.75rem;">📈 ARR</div>
                    <div class="company-detail-value" style="font-size: 0.95rem;">{arr}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # External Links Section
        company_name_encoded = name.replace(' ', '%20')
        linkedin_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name_encoded}"
        crunchbase_url = f"https://www.crunchbase.com/textsearch?q={company_name_encoded}"
        google_news_url = f"https://news.google.com/search?q={company_name_encoded}"
        
        st.markdown(f'''
        <div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
            <div style="font-size: 0.75rem; color: #939598; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 10px;">🔗 Research Links</div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="{linkedin_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: #0077B5; color: white; border-radius: 8px; text-decoration: none; font-size: 0.8rem; font-weight: 500;">
                    <span>in</span> LinkedIn
                </a>
                <a href="{crunchbase_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: #0288D1; color: white; border-radius: 8px; text-decoration: none; font-size: 0.8rem; font-weight: 500;">
                    📊 Crunchbase
                </a>
                <a href="{google_news_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: #555354; color: white; border-radius: 8px; text-decoration: none; font-size: 0.8rem; font-weight: 500;">
                    📰 News
                </a>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ==========================================================================
# STATE MANAGEMENT
# ==========================================================================
if "criteria_value" not in st.session_state:
    st.session_state.criteria_value = ""
if "found_companies" not in st.session_state:
    st.session_state.found_companies = []
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False

# ==========================================================================
# HERO HEADER
# ==========================================================================
import base64

# Load Arab Bank logo
logo_path = "frontend/assets/arab_bank_logo.png"
try:
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Arab Bank" style="height: 55px;">'
except:
    logo_html = '<div style="font-size: 1.5rem; font-weight: bold;">Arab Bank</div>'

st.markdown(f"""
<div class="hero">
    <div class="hero-inner">
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 16px;">
            {logo_html}
            <div style="height: 40px; width: 1px; background: rgba(255,255,255,0.3);"></div>
            <div style="font-size: 0.9rem; opacity: 0.9; font-weight: 500; color: white;">Ventures</div>
        </div>
        <div class="hero-title">Investment Sourcing Agent</div>
        <div class="hero-subtitle">Your AI-powered scout for discovering and analyzing potential startup investments across global markets</div>
        <div style="display: flex; gap: 12px; margin-top: 1.25rem; flex-wrap: wrap;">
            <div class="hero-badge">
                <span>🔍</span> Live Web Search
            </div>
            <div class="hero-badge">
                <span>📊</span> Deep-Dive Analysis
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================================
# SECTION 1: INVESTMENT THESIS
# ==========================================================================
render_section_header(1, "Define Your Investment Thesis")

st.markdown("""
<p style="color: #939598; font-size: 0.9rem; margin-bottom: 1rem;">
    Describe the type of startups you're looking for. Be specific about industry, location, funding stage, and other criteria.
</p>
""", unsafe_allow_html=True)

criteria_input = st.text_area(
    "Investment Thesis",
    value=st.session_state.criteria_value,
    height=120,
    placeholder="e.g., AI startups in healthcare based in Germany at Series A stage, B2B SaaS companies in the MENA region with $1M+ ARR...",
    label_visibility="collapsed",
    help="Be specific about industry, location, stage, and any other criteria"
)

if criteria_input != st.session_state.criteria_value:
    st.session_state.criteria_value = criteria_input

# Example queries expander
with st.expander("💡 See example investment theses", expanded=False):
    st.markdown("""
    <p style="color: #939598; font-size: 0.85rem; margin-bottom: 1rem;">
        Click any example below to use it as your investment thesis:
    </p>
    """, unsafe_allow_html=True)
    
    # Define example theses with descriptions
    example_theses = [
        ("AI startups in London", "Broad AI search in a specific city"),
        ("Enterprise SaaS in San Francisco, Series B+", "Stage-specific search"),
        ("Climate tech startups in Berlin with $1M+ ARR", "Revenue filter"),
        ("Fintech companies in MENA region", "Regional search"),
        ("B2B payments startups in Europe, Seed stage", "Industry + stage combo"),
    ]
    
    for thesis, description in example_theses:
        col_ex1, col_ex2 = st.columns([3, 2])
        with col_ex1:
            if st.button(f"📌 {thesis}", key=f"ex_{thesis[:20]}", use_container_width=True):
                st.session_state.criteria_value = thesis
                st.rerun()
        with col_ex2:
            st.markdown(f'<p style="color: #939598; font-size: 0.85rem; margin: 8px 0;">{description}</p>', unsafe_allow_html=True)

# Action buttons - equal width columns
col_btn1, col_btn2 = st.columns([1, 1], gap="medium")
with col_btn1:
    if st.button("✨ Enhance with AI", use_container_width=True, help="Use AI to improve your search"):
        if criteria_input:
            with st.spinner("Enhancing..."):
                try:
                    resp = requests.post(
                        "http://localhost:8000/enhance_query",
                        json={"user_query": criteria_input}
                    )
                    if resp.status_code == 200:
                        refined = resp.json().get("refined_query", "")
                        if refined:
                            st.session_state.criteria_value = refined
                            st.rerun()
                except Exception as e:
                    st.error(f"Enhancement failed: {e}")
        else:
            st.warning("Enter a thesis first")

with col_btn2:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.criteria_value = ""
        st.session_state.found_companies = []
        st.session_state.search_completed = False
        st.rerun()

render_section_end()

# ==========================================================================
# SECTION 2: SEARCH FILTERS
# ==========================================================================
render_section_header(2, "Refine Search Filters")

st.markdown("""
<p style="color: #939598; font-size: 0.9rem; margin-bottom: 1rem;">
    Narrow down your search with additional criteria. These filters will be combined with your investment thesis.
</p>
""", unsafe_allow_html=True)

# Filter row 1
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown("**💰 Funding Stage**")
    st.caption("Pre-Seed (<$500K) → Seed ($500K-$2M) → Series A ($2M-$15M) → Series B+ ($15M+)")
    funding_stage = st.selectbox(
        "Funding Stage",
        ["Any", "Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth"],
        label_visibility="collapsed"
    )

with col_f2:
    st.markdown("**📈 Minimum ARR**")
    st.caption("ARR = Annual Recurring Revenue (yearly subscription income)")
    min_arr = st.selectbox(
        "Minimum ARR",
        ["Any", "$100K+", "$500K+", "$1M+", "$5M+", "$10M+", "$50M+"],
        label_visibility="collapsed"
    )

# Filter row 2
col_f3, col_f4 = st.columns(2)

with col_f3:
    st.markdown("**💵 Total Funding Raised**")
    st.caption("Total capital raised from investors across all funding rounds")
    funding_raised = st.selectbox(
        "Total Funding",
        ["Any", "<$1M", "$1M-$5M", "$5M-$20M", "$20M-$50M", "$50M+"],
        label_visibility="collapsed"
    )

with col_f4:
    st.markdown("**🏢 Company Stage**")
    st.caption("Early = building product | Growth = scaling | Late = established")
    company_stage = st.selectbox(
        "Company Stage",
        ["Any", "Early Stage", "Growth Stage", "Late Stage"],
        label_visibility="collapsed"
    )

render_section_end()

# ==========================================================================
# SECTION 3: OUTPUT CONFIGURATION
# ==========================================================================
render_section_header(3, "Configure Output")

st.markdown("""
<p style="color: #939598; font-size: 0.9rem; margin-bottom: 1rem;">
    Select which data points you want to see in your results. All selected attributes will be researched for each company.
</p>
""", unsafe_allow_html=True)

ALL_ATTRIBUTES = [
    "Company Name",
    "Website", 
    "Country",
    "Description",
    "Founded",
    "Funding Stage",
    "ARR",
    "Market Sector"
]

selected_attributes = st.multiselect(
    "Select Data Points",
    options=ALL_ATTRIBUTES,
    default=["Company Name", "Website", "Country", "Market Sector"],
    label_visibility="collapsed",
    help="Choose which columns appear in your results"
)

if not selected_attributes:
    st.warning("⚠️ Please select at least one attribute to display in results.")

render_section_end()

# ==========================================================================
# SECTION 4: LAUNCH
# ==========================================================================
render_section_header(4, "Launch Scout Agent")

# Search preview
if st.session_state.criteria_value:
    st.markdown(f"""
    <div style="background: rgba(22, 128, 228, 0.06); border-radius: 10px; padding: 14px 16px; margin-bottom: 1rem; border-left: 4px solid #1680E4;">
        <div style="font-size: 0.75rem; color: #1680E4; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;">
            📋 Search Preview
        </div>
        <div style="font-size: 0.95rem; color: #555354; line-height: 1.5;">
            {st.session_state.criteria_value}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("👆 Enter an investment thesis above to get started.")

# Launch button
run_btn = st.button(
    "🎯 Launch Scout Agent",
    type="primary",
    use_container_width=True,
    disabled=not st.session_state.criteria_value or not selected_attributes
)



# ==========================================================================
# SEARCH EXECUTION
# ==========================================================================
if run_btn:
    with st.status("🤖 Scout Agent Active...", expanded=True) as status:
        st.write("📡 Initializing connection...")
        
        # Build search criteria
        search_criteria = st.session_state.criteria_value
        additional = []
        
        if funding_stage != "Any":
            additional.append(f"{funding_stage} funding")
        if min_arr != "Any":
            additional.append(f"ARR {min_arr}")
        if funding_raised != "Any":
            additional.append(f"raised {funding_raised}")
        if company_stage != "Any":
            additional.append(f"{company_stage}")
        
        if additional:
            search_criteria = f"{search_criteria}, {', '.join(additional)}"
        
        st.write(f"🔍 Searching: *{search_criteria}*")
        
        payload = {
            "search_criteria": search_criteria,
            "location": "",
            "funding_stage": funding_stage if funding_stage != "Any" else "",
            "attributes": [],
            "email": "user@example.com"
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/run_scout",
                json=payload,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        content = decoded.replace("data: ", "")
                        try:
                            data_json = json.loads(content)
                            if "success" in data_json:
                                st.session_state.found_companies = data_json.get("results", [])
                                st.session_state.search_completed = True
                                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                                break
                        except:
                            st.write(f"📌 {content}")
            
            if st.session_state.found_companies:
                st.success(f"Found {len(st.session_state.found_companies)} companies!")
            else:
                st.warning("No companies matched your criteria.")
                
        except Exception as e:
            status.update(label="❌ Connection Error", state="error")
            st.error(f"Failed to connect: {e}")

render_section_end()

# ==========================================================================
# RESULTS DISPLAY
# ==========================================================================
if st.session_state.search_completed and st.session_state.found_companies:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Results header with KPI cards
    st.markdown("## 📊 Analysis Results")
    
    # Calculate metrics
    companies_found = len(st.session_state.found_companies)
    data_points = len(selected_attributes)
    countries = len(set(c.get("country", "Unknown") for c in st.session_state.found_companies))
    sectors = len(set(c.get("market_sector", "Unknown") for c in st.session_state.found_companies))
    
    # Render beautiful KPI cards
    render_kpi_cards([
        {"icon": "🏢", "value": companies_found, "label": "Companies Found"},
        {"icon": "📋", "value": data_points, "label": "Data Points"},
        {"icon": "🌍", "value": countries, "label": "Countries"},
        {"icon": "📈", "value": sectors, "label": "Sectors"},
    ])
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # ==========================================================================
    # VIEW TOGGLE: Cards vs Table
    # ==========================================================================
    
    # Initialize view state
    if "results_view" not in st.session_state:
        st.session_state.results_view = "cards"
    
    # View toggle buttons
    st.markdown("### 👁️ View Results")
    
    view_col1, view_col2, view_spacer = st.columns([1, 1, 3])
    
    with view_col1:
        if st.button("🏢 Card View", use_container_width=True, 
                     type="primary" if st.session_state.results_view == "cards" else "secondary"):
            st.session_state.results_view = "cards"
            st.rerun()
    
    with view_col2:
        if st.button("📊 Table View", use_container_width=True,
                     type="primary" if st.session_state.results_view == "table" else "secondary"):
            st.session_state.results_view = "table"
            st.rerun()
    
    st.markdown("")
    
    # ==========================================================================
    # CARD VIEW - Expandable Company Cards
    # ==========================================================================
    if st.session_state.results_view == "cards":
        st.markdown('''
        <div style="background: rgba(22, 128, 228, 0.06); border-radius: 10px; padding: 12px 16px; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.1rem;">💡</span>
            <span style="font-size: 0.85rem; color: #555354;">Click on any company card below to expand and view full details</span>
        </div>
        ''', unsafe_allow_html=True)
        
        # Render each company as an expandable card
        for idx, company in enumerate(st.session_state.found_companies):
            render_company_card(company, idx)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Show table option hint
        st.info("📊 Switch to **Table View** above for a compact spreadsheet view that's optimized for exporting.")
    
    # ==========================================================================
    # TABLE VIEW - Data Table
    # ==========================================================================
    
    # Attribute mapping (needed for both views for export)
    ATTRIBUTE_MAPPING = {
        "Company Name": "name",
        "Website": "url",
        "Country": "country",
        "Description": "description",
        "Founded": "founding_year",
        "Funding Stage": "funding_stage",
        "ARR": "ARR",
        "Market Sector": "market_sector"
    }
    
    COLUMN_CONFIGS = {
        "Company Name": st.column_config.TextColumn("Company", width=150),
        "Website": st.column_config.LinkColumn("Website", width=200),
        "Country": st.column_config.TextColumn("Country", width=130),
        "Description": st.column_config.TextColumn("Description", width=350),
        "Founded": st.column_config.TextColumn("Founded", width=90),
        "Funding Stage": st.column_config.TextColumn("Stage", width=120),
        "ARR": st.column_config.TextColumn("ARR", width=100),
        "Market Sector": st.column_config.TextColumn("Sector", width=160),
    }
    
    # Build filtered dataframe (always needed for export)
    table_data = []
    for company in st.session_state.found_companies:
        row = {}
        for attr in selected_attributes:
            key = ATTRIBUTE_MAPPING.get(attr)
            if key:
                row[attr] = _to_str(company.get(key))
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    active_config = {attr: COLUMN_CONFIGS[attr] for attr in selected_attributes if attr in COLUMN_CONFIGS}
    
    # Show table only in table view
    if st.session_state.results_view == "table":
        # Table header with expand option
        table_header_col1, table_header_col2 = st.columns([3, 1])
        with table_header_col1:
            st.markdown('''
            <div style="background: rgba(22, 128, 228, 0.06); border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.1rem;">📊</span>
                <span style="font-size: 0.85rem; color: #555354;">Spreadsheet view — optimized for exporting and data analysis</span>
            </div>
            ''', unsafe_allow_html=True)
        with table_header_col2:
            expand_table = st.checkbox("🔍 Expand Table", value=False, help="Show full-height table")
        
        # Calculate table height based on expand state
        if expand_table:
            table_height = max(600, 60 + len(df) * 45)  # Full height
        else:
            table_height = min(400, 60 + len(df) * 45)  # Compact height
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=table_height,
            column_config=active_config
        )
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Download section (always visible)
    st.markdown("### 📥 Export Results")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📄 Download CSV",
            data=csv_data,
            file_name="investment_scout_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl2:
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        st.download_button(
            "📊 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="investment_scout_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
