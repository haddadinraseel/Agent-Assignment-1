"""
Conversational Streamlit App for Startup Scouting
Clean professional UI with SSE support and enhanced UX
"""
import streamlit as st
import requests
import json
import pandas as pd
import io
import re
import markdown
from datetime import datetime

# ==========================================================================
# PAGE CONFIGURATION
# ==========================================================================
st.set_page_config(
    page_title="AB Scout - Arab Bank Startup Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================================
# CUSTOM CSS - Clean White & Blue Ombre Professional Theme
# ==========================================================================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background - white with subtle blue ombre */
    .main {
        background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 50%, #e8f4fd 100%);
    }
    
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 50%, #e8f4fd 100%);
    }
    
    /* Header - minimal */
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    
    .main-header h1 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 0.75rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Message row with avatar */
    .message-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin: 12px 0;
        animation: fadeIn 0.25s ease-out;
    }
    
    .message-row.user {
        flex-direction: row-reverse;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Avatars */
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    .avatar.user {
        background: #0671FF;
        color: #ffffff;
    }
    
    .avatar.bot {
        background: #2B1CA9;
        color: #ffffff;
    }
    
    /* Simple chat bubble - same style for both */
    .chat-bubble {
        background: #ffffff;
        color: #374151;
        padding: 16px 20px;
        border-radius: 12px;
        max-width: 85%;
        font-size: 0.9rem;
        line-height: 1.7;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    
    .chat-bubble.user {
        background: linear-gradient(135deg, #1680E4 0%, #0671FF 100%);
        color: #ffffff;
        border: none;
    }
    
    /* Numbered list styling for company results */
    .chat-bubble ol {
        padding-left: 0;
        margin: 0.5rem 0;
        list-style: none;
        counter-reset: item;
    }
    
    .chat-bubble ol > li {
        counter-increment: item;
        margin-bottom: 1.25rem;
        padding-left: 2rem;
        position: relative;
    }
    
    .chat-bubble ol > li::before {
        content: counter(item) ".";
        position: absolute;
        left: 0;
        font-weight: 700;
        color: #2B1CA9;
        font-size: 1rem;
    }
    
    .chat-bubble ol > li > strong:first-child,
    .chat-bubble ol > li > p:first-child > strong:first-child {
        font-size: 1rem;
        color: #1e293b;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    /* Nested unordered list (details) */
    .chat-bubble ul {
        list-style: disc;
        padding-left: 1.25rem;
        margin: 0.5rem 0;
    }
    
    .chat-bubble ul li {
        margin-bottom: 0.35rem;
        color: #555354;
        font-size: 0.875rem;
        line-height: 1.6;
    }
    
    .chat-bubble ul li strong {
        color: #374151;
        font-weight: 600;
    }
    
    /* Links styling */
    .chat-bubble a {
        color: #0671FF;
        text-decoration: none;
    }
    
    .chat-bubble a:hover {
        text-decoration: underline;
    }
    
    /* Paragraphs */
    .chat-bubble p {
        margin: 0.5rem 0;
    }
    
    .chat-bubble p:first-child {
        margin-top: 0;
    }
    
    /* Message timestamp */
    .msg-time {
        font-size: 0.7rem;
        color: #9ca3af;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #f1f5f9;
    }
    
    .chat-bubble.user .msg-time {
        color: rgba(255,255,255,0.7);
        border-top-color: rgba(255,255,255,0.2);
    }
    
    /* Tool badge */
    .tool-badge {
        display: inline-block;
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f0ff 100%);
        color: #2B1CA9;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 12px;
        border: 1px solid #c7d2fe;
    }
    
    /* Status message */
    .status-msg {
        color: #6b7280;
        font-size: 0.85rem;
        font-style: italic;
    }
    
    /* Table styling */
    .chat-bubble table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.75rem 0;
        font-size: 0.85rem;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    
    .chat-bubble th {
        background: #f8fafc;
        color: #374151;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .chat-bubble td {
        padding: 10px 12px;
        border-bottom: 1px solid #f1f5f9;
        color: #374151;
    }
    
    .chat-bubble tr:last-child td {
        border-bottom: none;
    }
    
    .chat-bubble tr:hover td {
        background: #f8fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 0.75rem;
    }
    
    .sidebar-header {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 0.75rem;
        background: #ffffff;
    }
    
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .sidebar-logo {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #2B1CA9 0%, #0671FF 100%);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .sidebar-logo svg {
        width: 14px;
        height: 14px;
    }
    
    .sidebar-brand-text {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .sidebar-section-title {
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.5rem 1rem 0.25rem 1rem;
    }
    
    .chat-history-item {
        padding: 8px 12px;
        margin: 2px 8px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s ease;
        color: #475569;
        font-size: 0.8rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background: #ffffff;
        border: 1px solid #e2e8f0;
    }
    
    .chat-history-item:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    .chat-history-item.active {
        background: #e8f4fd;
        border-color: #0671FF;
        color: #2B1CA9;
    }
    
    /* Tool badge */
    .tool-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #0671FF;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 500;
        margin-bottom: 6px;
        border: 1px solid #c7e4fd;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    /* Status/SSE message */
    .status-msg {
        background: #f8fafc;
        color: #0671FF;
        padding: 8px 12px;
        border-radius: 10px;
        font-size: 0.8rem;
        border-left: 3px solid #0671FF;
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 80%;
    }
    
    .status-msg::before {
        content: '';
        width: 6px;
        height: 6px;
        background: #0671FF;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }
    
    /* Streaming text animation */
    .streaming-text {
        overflow: hidden;
    }
    
    @keyframes typewriter {
        from { max-height: 0; }
        to { max-height: 2000px; }
    }
    
    .typing-cursor {
        display: inline-block;
        width: 2px;
        height: 1em;
        background: #0671FF;
        margin-left: 2px;
        animation: blink 0.8s infinite;
        vertical-align: text-bottom;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    
    /* Input area styling */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        color: #1e293b !important;
        font-size: 0.9rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0671FF !important;
        box-shadow: 0 0 0 3px rgba(6, 113, 255, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1680E4 0%, #0671FF 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(6, 113, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0671FF 0%, #2B1CA9 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(6, 113, 255, 0.4) !important;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: #ffffff !important;
        color: #0671FF !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: #f8fafc !important;
        border-color: #0671FF !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 5px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.7rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    /* Welcome section - compact */
    .welcome-section {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
    }
    
    .welcome-title {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    
    .welcome-subtitle {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    
    /* Quick start chips - horizontal bright pills */
    .quick-start-bar {
        display: flex;
        justify-content: center;
        gap: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    
    .quick-chip {
        background: linear-gradient(135deg, #e8f4fd 0%, #f0f7ff 100%);
        border: 1px solid #c7e4fd;
        color: #2B1CA9;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .quick-chip:hover {
        background: linear-gradient(135deg, #1680E4 0%, #0671FF 100%);
        border-color: #0671FF;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(6, 113, 255, 0.25);
    }
    
    .quick-chip.alt1 {
        background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
        border-color: #bbf7d0;
        color: #166534;
    }
    
    .quick-chip.alt1:hover {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        border-color: #22c55e;
        color: #ffffff;
    }
    
    .quick-chip.alt2 {
        background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%);
        border-color: #fde68a;
        color: #92400e;
    }
    
    .quick-chip.alt2:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-color: #f59e0b;
        color: #ffffff;
    }
    
    /* Message timestamp */
    .msg-time {
        font-size: 0.65rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    .user-msg .msg-time {
        text-align: right;
        color: rgba(255,255,255,0.7);
    }
    
    /* Search input in sidebar */
    .search-container {
        padding: 0 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Quick actions */
    .quick-actions {
        display: flex;
        gap: 6px;
        margin-top: 8px;
        flex-wrap: wrap;
    }
    
    .quick-action-btn {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        color: #64748b;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    
    .quick-action-btn:hover {
        background: #e8f4fd;
        border-color: #0671FF;
        color: #0671FF;
    }
    
    /* ========== STYLE NATIVE STREAMLIT CHAT MESSAGES ========== */
    
    /* Style assistant messages (white card look) */
    [data-testid="stChatMessage"][data-testid-role="assistant"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 20px 24px !important;
        margin: 16px 0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Style user messages (blue pill on right) */
    [data-testid="stChatMessage"][data-testid-role="user"] {
        background: linear-gradient(135deg, #1680E4 0%, #0671FF 100%) !important;
        color: #ffffff !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 10px 18px !important;
        margin: 12px 0 !important;
        max-width: 70% !important;
        margin-left: auto !important;
        box-shadow: 0 2px 6px rgba(22, 128, 228, 0.25) !important;
    }
    
    [data-testid="stChatMessage"][data-testid-role="user"] * {
        color: #ffffff !important;
    }
    
    /* Hide default avatar for cleaner look */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* Style content inside chat messages */
    [data-testid="stChatMessage"] p {
        margin: 0.5rem 0;
        line-height: 1.7;
    }
    
    /* Numbered list styling */
    [data-testid="stChatMessage"] ol {
        list-style: decimal;
        padding-left: 1.5rem;
        margin: 1rem 0;
    }
    
    [data-testid="stChatMessage"] ol > li {
        margin-bottom: 1.25rem;
        color: #2B1CA9;
        font-weight: 500;
    }
    
    /* Nested bullet list */
    [data-testid="stChatMessage"] ul {
        list-style: circle;
        padding-left: 1.5rem;
        margin: 0.5rem 0;
    }
    
    [data-testid="stChatMessage"] ul li {
        margin-bottom: 0.35rem;
        color: #555354;
        font-size: 0.9rem;
        font-weight: 400;
    }
    
    /* Tool badge inline code styling */
    [data-testid="stChatMessage"] code {
        background: #e8f4fd !important;
        color: #2B1CA9 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
    }
    
    /* Caption (timestamp) styling */
    [data-testid="stChatMessage"] [data-testid="stCaptionContainer"] {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 12px;
        padding-top: 8px;
        border-top: 1px solid #f3f4f6;
    }
    
    /* Status message */
    .stAlert {
        background: #f8fafc !important;
        border-radius: 8px !important;
        border-left: 3px solid #1680E4 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================================
# BACKEND URL
# ==========================================================================
BACKEND_URL = "http://localhost:8000"

# ==========================================================================
# SESSION STATE
# ==========================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "enhanced_query" not in st.session_state:
    st.session_state.enhanced_query = ""

if "current_status" not in st.session_state:
    st.session_state.current_status = ""

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

if "default_input" not in st.session_state:
    st.session_state.default_input = ""

# Chat history - stores all conversations
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  # List of {"id": int, "title": str, "messages": list}

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "streaming_response" not in st.session_state:
    st.session_state.streaming_response = ""

# ==========================================================================
# HELPER FUNCTIONS
# ==========================================================================
def parse_companies_from_response(response_text: str) -> list:
    """
    Parse company data from assistant response text for CSV/Excel export.
    Handles multiple response formats including numbered lists and single company.
    """
    companies = []
    
    if not response_text:
        return companies
    
    # Split by numbered entries (1. Company, 2. Company, etc.)
    # Handle both "1. Name" and "**1. Name**" formats
    blocks = re.split(r'\n(?=\*?\*?\d+\.)', response_text)
    
    for block in blocks:
        if not block.strip():
            continue
        
        company = {}
        
        # Extract company name from header (e.g., "1. Company Name" or "**1. Company Name**")
        name_match = re.search(r'^\*?\*?\d+\.?\s*\*?\*?\s*([^\n\*:]+)', block)
        if name_match:
            name = name_match.group(1).strip()
            if name and len(name) > 1:
                company['Name'] = name
        
        # Field extraction patterns - check for various formats
        patterns = {
            'Website': [r'Website[:\s]+([^\n]+)', r'URL[:\s]+([^\n]+)'],
            'Description': [r'Description[:\s]+([^\n]+)'],
            'Country': [r'Country[:\s]+([^\n]+)'],
            'Founding Year': [r'Founding\s*Year[:\s]+([^\n]+)', r'Founded[:\s]+([^\n]+)'],
            'Funding Stage': [r'Funding\s*Stage[:\s]+([^\n]+)', r'Funding[:\s]+([^\n]+)'],
            'ARR': [r'ARR[:\s]+([^\n]+)'],
            'Market Sector': [r'Sector[:\s]+([^\n]+)', r'Market\s*Sector[:\s]+([^\n]+)'],
            'Relevance Score': [r'(?:Global\s*)?Relevance\s*Score[:\s]+([^\n]+)'],
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, block, re.IGNORECASE)
                if match:
                    value = match.group(1).strip().strip('*').strip()
                    if value and value.lower() not in ['n/a', 'none', 'unknown', 'not available', 'not publicly available', 'not specified']:
                        company[field] = value
                        break
        
        if company.get('Name'):
            companies.append(company)
    
    # If no numbered companies found, try single company format (e.g., "Name: Opus")
    if not companies:
        company = {}
        name_match = re.search(r'[•\-\*]?\s*Name[:\s]+([^\n]+)', response_text, re.IGNORECASE)
        if name_match:
            company['Name'] = name_match.group(1).strip().strip('*')
            
            single_patterns = {
                'Website': r'Website[:\s]+([^\n]+)',
                'Description': r'Description[:\s]+([^\n]+)',
                'Country': r'Country[:\s]+([^\n]+)',
                'Founding Year': r'Founding\s*Year[:\s]+([^\n]+)',
                'Funding Stage': r'Funding\s*Stage[:\s]+([^\n]+)',
                'ARR': r'ARR[:\s]+([^\n]+)',
                'Market Sector': r'Sector[:\s]+([^\n]+)',
                'Relevance Score': r'(?:Global\s*)?Relevance\s*Score[:\s]+([^\n]+)',
            }
            
            for field, pattern in single_patterns.items():
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip().strip('*')
                    if value and value.lower() not in ['n/a', 'none', 'unknown', 'not available', 'not publicly available', 'not specified']:
                        company[field] = value
            
            if company.get('Name'):
                companies.append(company)
    
    return companies


def create_csv_download(companies: list) -> bytes:
    """Create CSV from company data."""
    if not companies:
        return b""
    df = pd.DataFrame(companies)
    return df.to_csv(index=False).encode('utf-8')


def create_excel_download(companies: list) -> bytes:
    """Create Excel file from company data."""
    if not companies:
        return b""
    df = pd.DataFrame(companies)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Companies')
    return output.getvalue()


def stream_chat_response(message: str, history: list):
    """
    Stream chat response using SSE.
    Yields status updates and final response.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "conversation_history": history
            },
            stream=True,
            timeout=180
        )
        
        final_data = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('event:'):
                    event_type = line_str.split(':', 1)[1].strip()
                elif line_str.startswith('data:'):
                    data = line_str.split(':', 1)[1].strip()
                    
                    if event_type == 'status':
                        yield {'type': 'status', 'content': data}
                    elif event_type in ['complete', 'error']:
                        try:
                            final_data = json.loads(data)
                            yield {'type': 'complete', 'content': final_data}
                        except json.JSONDecodeError:
                            yield {'type': 'error', 'content': data}
        
    except requests.exceptions.Timeout:
        yield {'type': 'error', 'content': 'Request timed out. Please try again.'}
    except requests.exceptions.ConnectionError:
        yield {'type': 'error', 'content': 'Cannot connect to backend. Make sure the server is running.'}
    except Exception as e:
        yield {'type': 'error', 'content': f'Error: {str(e)}'}


def save_current_conversation():
    """Save current messages to conversation history."""
    if st.session_state.messages and len(st.session_state.messages) > 0:
        # Get title from first user message
        title = "New Chat"
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                title = msg["content"][:40] + "..." if len(msg["content"]) > 40 else msg["content"]
                break
        
        if st.session_state.current_conversation_id is not None:
            # Update existing conversation
            for conv in st.session_state.conversation_history:
                if conv["id"] == st.session_state.current_conversation_id:
                    conv["messages"] = st.session_state.messages.copy()
                    conv["title"] = title
                    break
        else:
            # Create new conversation
            new_id = len(st.session_state.conversation_history) + 1
            st.session_state.conversation_history.append({
                "id": new_id,
                "title": title,
                "messages": st.session_state.messages.copy()
            })
            st.session_state.current_conversation_id = new_id


def load_conversation(conv_id):
    """Load a conversation from history."""
    for conv in st.session_state.conversation_history:
        if conv["id"] == conv_id:
            st.session_state.messages = conv["messages"].copy()
            st.session_state.current_conversation_id = conv_id
            break


def start_new_conversation():
    """Start a fresh conversation."""
    save_current_conversation()
    st.session_state.messages = []
    st.session_state.current_conversation_id = None


# ==========================================================================
# SIDEBAR - Chat History with Search
# ==========================================================================
with st.sidebar:
    # Brand header
    st.markdown('''
    <div class="sidebar-header">
        <div class="sidebar-brand">
            <div class="sidebar-logo">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
            <span class="sidebar-brand-text">AB Scout</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # New Chat button
    if st.button("+ New Conversation", use_container_width=True, key="new_chat"):
        start_new_conversation()
        st.rerun()
    
    st.markdown('<div class="sidebar-section-title">Recent</div>', unsafe_allow_html=True)
    
    # Search conversations
    search_query = st.text_input(
        "Search",
        placeholder="Search...",
        label_visibility="collapsed",
        key="search_chats"
    )
    
    # Filter and display conversation history (newest first)
    if st.session_state.conversation_history:
        filtered_convs = st.session_state.conversation_history
        if search_query:
            filtered_convs = [
                c for c in st.session_state.conversation_history 
                if search_query.lower() in c['title'].lower()
            ]
        
        if filtered_convs:
            for conv in reversed(filtered_convs):
                is_active = conv["id"] == st.session_state.current_conversation_id
                btn_type = "primary" if is_active else "secondary"
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(
                            f"{conv['title']}", 
                            key=f"conv_{conv['id']}", 
                            use_container_width=True,
                            type=btn_type
                        ):
                            save_current_conversation()
                            load_conversation(conv["id"])
                            st.rerun()
                with col2:
                    if st.button("×", key=f"del_{conv['id']}", help="Delete conversation"):
                        st.session_state.conversation_history = [
                            c for c in st.session_state.conversation_history if c["id"] != conv["id"]
                        ]
                        if st.session_state.current_conversation_id == conv["id"]:
                            st.session_state.messages = []
                            st.session_state.current_conversation_id = None
                        st.rerun()
        else:
            st.markdown('<p style="color: #94a3b8; font-size: 0.8rem; text-align: center; padding: 1rem;">No matching conversations</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #94a3b8; font-size: 0.8rem; text-align: center; padding: 1rem;">No conversations yet</p>', unsafe_allow_html=True)

# ==========================================================================
# HEADER
# ==========================================================================
# ==========================================================================
# QUICK START PROMPTS - Define before use
# ==========================================================================
QUICK_START_PROMPTS = [
    {"label": "Discover Startups", "query": "Find emerging startups in AI healthcare sector"},
    {"label": "Competitor Analysis", "query": "Analyze competitors of Stripe in payments"},
    {"label": "Market Research", "query": "Research fintech opportunities in MENA region"}
]

# ==========================================================================
# QUICK START BAR (always visible at top when no messages)
# ==========================================================================
if not st.session_state.messages:
    st.markdown('''
    <div class="welcome-section">
        <div class="welcome-title">What can I help you find?</div>
        <div class="welcome-subtitle">Discover startups, analyze markets, and research opportunities</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Quick start chips - horizontal row
    chip_cols = st.columns([1, 1, 1, 1, 1])
    with chip_cols[1]:
        if st.button("Discover Startups", key="qs_0", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": QUICK_START_PROMPTS[0]["query"], "timestamp": datetime.now().strftime("%H:%M")})
            st.session_state.processing = True
            st.rerun()
    with chip_cols[2]:
        if st.button("Competitor Analysis", key="qs_1", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": QUICK_START_PROMPTS[1]["query"], "timestamp": datetime.now().strftime("%H:%M")})
            st.session_state.processing = True
            st.rerun()
    with chip_cols[3]:
        if st.button("Market Research", key="qs_2", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": QUICK_START_PROMPTS[2]["query"], "timestamp": datetime.now().strftime("%H:%M")})
            st.session_state.processing = True
            st.rerun()

# ==========================================================================
# HELPER: Fix flat numbered list to nested structure
# ==========================================================================
def fix_flat_list_to_nested(text: str) -> str:
    """
    Converts a flat numbered list where details are separate items into a proper nested structure.
    
    Input format:
    1. CompanyName
    2. Website: url
    3. Description: text
    4. Founded: year
    5. NextCompany
    ...
    
    Output format:
    1. **CompanyName**
       - Website: url
       - Description: text
       - Founded: year
    
    2. **NextCompany**
    ...
    """
    import re
    
    lines = text.strip().split('\n')
    result_lines = []
    company_counter = 0
    in_company = False
    
    # Keywords that indicate a detail line (not a company name)
    detail_keywords = ['website:', 'description:', 'founded:', 'founding year:', 
                       'market sector:', 'funding:', 'arr:', 'employees:', 
                       'location:', 'country:', 'sector:']
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this line starts with a number (numbered list item)
        num_match = re.match(r'^(\d+)\.\s*(.+)$', line_stripped)
        
        if num_match:
            item_text = num_match.group(2).strip()
            item_lower = item_text.lower()
            
            # Check if this is a detail line (Website:, Description:, etc.)
            is_detail = any(item_lower.startswith(kw) for kw in detail_keywords)
            
            if is_detail:
                # Convert to bullet point under current company
                result_lines.append(f"   - {item_text}")
            else:
                # This is a company name
                company_counter += 1
                if company_counter > 1:
                    result_lines.append("")  # Blank line between companies
                result_lines.append(f"{company_counter}. **{item_text}**")
                in_company = True
        elif line_stripped.startswith('-'):
            # Already a bullet point, just preserve it with proper indentation
            result_lines.append(f"   {line_stripped}")
        else:
            # Regular text, preserve as-is
            result_lines.append(line)
    
    return '\n'.join(result_lines)

# ==========================================================================
# CHAT CONTAINER
# ==========================================================================
chat_container = st.container()

with chat_container:
    # Display chat messages (or empty state message)
    if not st.session_state.messages:
        st.markdown('''
        <div style="text-align: center; padding: 3rem 1rem; color: #94a3b8;">
            <p style="font-size: 0.85rem;">Start a conversation or select a quick action above</p>
        </div>
        ''', unsafe_allow_html=True)
    
    else:
        # Display chat messages
        for idx, msg in enumerate(st.session_state.messages):
            timestamp = msg.get("timestamp", "")
            
            if msg["role"] == "user":
                # User message - using native Streamlit chat_message
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
                    st.caption(timestamp)
            elif msg["role"] == "status":
                st.info(msg["content"])
            else:
                # Assistant message - using native Streamlit chat_message
                content = msg["content"]
                
                # Get clean plain text (strip any HTML that might be in cached messages)
                content_clean = re.sub(r'<[^>]+>', '', content)
                content_clean = content_clean.replace('&lt;', '<').replace('&gt;', '>')
                content_clean = content_clean.replace('&amp;', '&')
                content_clean = content_clean.replace('&nbsp;', ' ').strip()
                
                # Fix flat numbered lists to proper nested structure
                if msg.get("tool_used"):
                    content_clean = fix_flat_list_to_nested(content_clean)
                
                with st.chat_message("assistant", avatar="🏦"):
                    # Show tool badge if used
                    if msg.get("tool_used"):
                        st.markdown(f"**🔧 Tool:** `{msg['tool_used']}`")
                    
                    # Display content as markdown
                    st.markdown(content_clean)
                    
                    # Show timestamp
                    st.caption(timestamp)
                
                # Download buttons for responses with company data
                if msg.get("tool_used"):
                    companies = parse_companies_from_response(msg["content"])
                    if companies:
                        col_spacer1, col_csv, col_excel, col_spacer2 = st.columns([0.5, 0.8, 0.8, 3.9])
                        with col_csv:
                            csv_data = create_csv_download(companies)
                            st.download_button(
                                label="Export CSV",
                                data=csv_data,
                                file_name=f"companies_{idx}.csv",
                                mime="text/csv",
                                key=f"csv_{idx}"
                            )
                        with col_excel:
                            excel_data = create_excel_download(companies)
                            st.download_button(
                                label="Export Excel",
                                data=excel_data,
                                file_name=f"companies_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"excel_{idx}"
                            )

# ==========================================================================
# SSE STATUS PLACEHOLDER (appears in chat area while processing)
# ==========================================================================
status_placeholder = st.empty()

# ==========================================================================
# INPUT AREA
# ==========================================================================
st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

# Hide buttons completely when processing
if st.session_state.processing:
    st.markdown('''
    <style>
    div[data-testid="stHorizontalBlock"]:has(button) { display: none !important; }
    </style>
    ''', unsafe_allow_html=True)

# Text input - use dynamic key to clear after submission
user_input = st.text_input(
    "Message",
    value=st.session_state.default_input,
    placeholder="Ask about startups, companies, or market intelligence...",
    label_visibility="collapsed",
    key=f"user_input_{st.session_state.input_key}",
    disabled=st.session_state.processing
)

# Clear the default_input after it's been used
if st.session_state.default_input:
    st.session_state.default_input = ""

# Buttons row - only show when not processing
if not st.session_state.processing:
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1.8])
    
    with col1:
        send_btn = st.button("Send", type="primary", use_container_width=True)
    
    with col2:
        enhance_btn = st.button("Enhance Query", use_container_width=True)
    
    with col3:
        if st.session_state.messages:
            if st.button("Clear", use_container_width=True):
                start_new_conversation()
                st.rerun()
else:
    send_btn = False
    enhance_btn = False

# ==========================================================================
# ENHANCE QUERY
# ==========================================================================
if enhance_btn and user_input:
    with st.spinner("Enhancing..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/enhance_query",
                json={"user_query": user_input},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                enhanced = data.get("refined_query", user_input)
                # Set the enhanced query as the new input value
                st.session_state.default_input = enhanced
                st.session_state.enhanced_query = enhanced
                st.session_state.input_key += 1  # Force input refresh
                st.rerun()
        except Exception as e:
            st.error(f"Enhancement failed: {str(e)}")

# ==========================================================================
# SEND MESSAGE
# ==========================================================================
if send_btn and user_input:
    # Use enhanced query if available, otherwise use original
    message_to_send = st.session_state.enhanced_query if st.session_state.enhanced_query else user_input
    
    # Add user message to chat with timestamp
    st.session_state.messages.append({
        "role": "user", 
        "content": message_to_send,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    st.session_state.processing = True
    st.session_state.enhanced_query = ""
    st.session_state.input_key += 1  # Increment key to clear input
    st.rerun()

# ==========================================================================
# PROCESS MESSAGE (call backend with SSE streaming)
# ==========================================================================
if st.session_state.processing:
    # Get the last user message
    last_message = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_message = msg["content"]
            break
    
    if last_message:
        try:
            # Build conversation history (exclude status messages and current message)
            history = []
            for msg in st.session_state.messages[:-1]:  # Exclude last user message
                if msg["role"] in ["user", "assistant"]:
                    history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Stream the response with status updates
            final_response = None
            tool_used = None
            
            for update in stream_chat_response(last_message, history):
                if update['type'] == 'status':
                    # Show SSE status in the chat area
                    status_placeholder.markdown(f'''
                    <div class="message-row">
                        <div class="avatar bot">S</div>
                        <div class="status-msg">{update["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif update['type'] == 'complete':
                    data = update['content']
                    final_response = data.get("response", "No response received.")
                    tool_used = data.get("tool_used")
                    
                    # Clear status
                    status_placeholder.empty()
                    
                elif update['type'] == 'error':
                    final_response = update['content']
            
            if final_response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_response,
                    "tool_used": tool_used,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                # Auto-save conversation after receiving response
                save_current_conversation()
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "No response received.",
                    "tool_used": None,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
        except Exception as e:
            status_placeholder.empty()
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "tool_used": None,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    st.session_state.processing = False
    st.rerun()

# ==========================================================================
# FOOTER
# ==========================================================================
st.markdown('''
<div class="footer">
    © 2025 AB Scout  •  Arab Bank Investment Intelligence  •  Confidential
</div>
''', unsafe_allow_html=True)