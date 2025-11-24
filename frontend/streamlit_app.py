# frontend/streamlit_app.py

import streamlit as st
import requests
import re
import sseclient
import requests

st.set_page_config(page_title="Investment Sourcing Agent", layout="wide")

def stream_agent_updates(criteria: str, attributes: list, email: str):
    """
    Connects to backend /run_scout and yields log messages.
    """
    url = "http://localhost:8000/run_scout"
    payload = {
        "search_criteria": criteria,
        "attributes": attributes,
        "email": email
    }

    # Stream the response
    with requests.post(url, json=payload, stream=True) as response:
        client = sseclient.SSEClient(response)
        for event in client.events():
            # event.data is the text from backend
            yield event.data
# -------------------------
# PAGE HEADER
# -------------------------
st.title("💼 Investment Sourcing Agent")
st.write("Fill in the criteria below and the agent will search the market on your behalf.")

# -------------------------
# SEARCH CRITERIA SECTION
# -------------------------
st.header("1️⃣ Search Criteria")

# Example presets
example_queries = {
    "Crypto Infra Example": "Infra space for crypto and web3, Saudi presence, Seed stage",
    "AI Healthcare Example": "Agentic AI in healthcare, $5M+ ARR, Series A or B funding"
}

col1, col2 = st.columns([3, 1])

with col1:
    initial_text = st.session_state.get("search_criteria", "")
    search_criteria = st.text_area(
        "Describe your investment thesis or criteria:",
        value=initial_text,
        height=150,
        placeholder="e.g., AI-powered compliance tools, Middle East presence, Series A–B..."
    )
    st.session_state["search_criteria"] = search_criteria

with col2:
    st.write("#### Examples")
    for label, query in example_queries.items():
        if st.button(label):
            st.session_state["search_criteria"] = query
            # Immediately show in the text area
            st.experimental_rerun() if hasattr(st, "experimental_rerun") else None

# -------------------------
# Backend call for Enhance with AI
# -------------------------
BACKEND_URL = "http://localhost:8000"  # adjust if backend runs elsewhere

def enhance_with_ai_call(text: str) -> str:
    if not text or not text.strip():
        return "Please provide search criteria to enhance."
    try:
        resp = requests.post(
            f"{BACKEND_URL}/enhance_query",
            json={"user_query": text},
            timeout=20
        )
        if resp.status_code == 200:
            return resp.json().get("refined_query", "No refined text returned.")
        else:
            return f"Error from backend: {resp.status_code} {resp.text}"
    except Exception as e:
        return f"Error calling backend: {e}"

# -------------------------
# Enhance with AI Button
# -------------------------
if st.button("✨ Enhance with AI"):
    current = st.session_state.get("search_criteria", "") or search_criteria
    st.info("Contacting enhancement service...")
    enhanced = enhance_with_ai_call(current)
    st.session_state["search_criteria"] = enhanced

    # Display the enhanced query immediately
    st.subheader("Enhanced Query")
    st.text_area("Enhanced Search Criteria:", value=enhanced, height=150)

    # Debug output to verify backend response
    st.subheader("Debug Info")
    st.json({"backend_response": enhanced})

# -------------------------
# DATA COLLECTION SECTION
# -------------------------
st.header("2️⃣ Data Points to Collect for Each Startup")

preset_attributes = [
    "Company Name", "Website", "Year Founded", "Founders",
    "Location", "Funding Stage", "Latest Funding Amount"
]

selected_presets = st.multiselect(
    "Choose standard data attributes:",
    options=preset_attributes,
)

custom_attributes = st.text_input(
    "Add up to 20 custom attributes (comma-separated):",
    placeholder="e.g., revenue, customer count, competitors..."
)

custom_attributes_list = [attr.strip() for attr in custom_attributes.split(",") if attr.strip()]

# -------------------------
# EMAIL SECTION
# -------------------------
st.header("3️⃣ Email Delivery")

user_email = st.text_input(
    "Enter your email address (report will be sent here):",
    placeholder="name@example.com",
)


# -------------------------
# SUBMIT BUTTON AND AGENT RUNNER
# -------------------------

# State to store streaming logs
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []

# Function to run the agent and handle SSE
def run_scout_agent_sse(criteria, attributes, email):
    st.session_state.log_messages = []
    
    # Combine all attributes into a single list
    all_attributes = selected_presets + [attr.strip() for attr in custom_attributes.split(",") if attr.strip()]

    # Data payload for the backend
    payload = {
        "search_criteria": criteria,
        "attributes": all_attributes,
        "email": email,
    }

    try:
        # 1. Start the connection to the backend's streaming endpoint
        with requests.post(
            f"{BACKEND_URL}/run_scout",
            json=payload,
            stream=True, # MUST be True for streaming
            timeout=300 
        ) as response:
            
            if response.status_code != 200:
                st.error(f"Error starting agent: {response.status_code} - {response.text}")
                return

            # This is where the status updates will appear!
            status_placeholder = st.empty()
            
            # --- 2. Listen for the streaming messages (SSE) ---
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    # Look for the 'data:' part of the SSE message
                    if decoded_line.startswith("data:"):
                        data_content = decoded_line[len("data:"):].strip()
                        
                        # Save the message
                        st.session_state.log_messages.append(data_content)
                        
                        # Show all the saved messages in the UI
                        log_output = "\n".join(st.session_state.log_messages)
                        status_placeholder.markdown(f"**Agent Status Log:**\n```markdown\n{log_output}\n```")

                        # Stop if the backend says the job is 'complete'
                        if decoded_line.startswith("event: complete"):
                            st.success("Investment Scout Agent completed successfully!")
                            break
                        
    except Exception as e:
        st.error(f"A connection error occurred: {e}")
        st.session_state.log_messages.append(f"ERROR: {e}")


if st.button("🚀 Run Investment Scout Agent"):
    st.success("Agent started! See live updates below:")
    
    # Use placeholders to show logs
    log_placeholder = st.empty()

    criteria = st.session_state.get("search_criteria", "")
    all_attributes = selected_presets + custom_attributes_list
    user_email_value = user_email

    for msg in stream_agent_updates(criteria, all_attributes, user_email_value):
        # Just display each message
        log_placeholder.text(msg)
