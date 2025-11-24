import streamlit as st

st.set_page_config(page_title="Investment Sourcing Agent", layout="wide")

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
    search_criteria = st.text_area(
        "Describe your investment thesis or criteria:",
        height=150,
        placeholder="e.g., AI-powered compliance tools, Middle East presence, Series A–B..."
    )

with col2:
    st.write("#### Examples")
    for label, query in example_queries.items():
        if st.button(label):
            search_criteria = query
            st.session_state["search_criteria"] = query  # store for display


# Enhance with AI button (functionality added later)
if st.button("✨ Enhance with AI"):
    st.info("AI enhancement will be implemented in Step 2.")


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

# Convert comma-separated → list
custom_attributes_list = [
    attr.strip() for attr in custom_attributes.split(",") if attr.strip()
]


# -------------------------
# EMAIL SECTION
# -------------------------
st.header("3️⃣ Email Delivery")

user_email = st.text_input(
    "Enter your email address (report will be sent here):",
    placeholder="name@example.com",
)


# -------------------------
# SUBMIT BUTTON (placeholder)
# -------------------------
if st.button("🚀 Run Investment Scout Agent"):
    st.success("Form submitted! Backend integration coming in later steps.")
    st.write("**Search Criteria:**", search_criteria)
    st.write("**Preset Attributes:**", selected_presets)
    st.write("**Custom Attributes:**", custom_attributes_list)
    st.write("**Email:**", user_email)
