"""
discovery2.py — Minimal discovery agent with Azure/OpenAI + Linkup tool
"""

import os
import json
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

from langchain.tools import tool
try:
    from langchain.agents import create_agent
except Exception:
    create_agent = None

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

# -------------------------
# Load .env
# -------------------------
dotenv_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'scripts', '.env'),
    os.path.join(os.path.dirname(__file__), '..', '.env')
]
for path in dotenv_paths:
    load_dotenv(path)

# Normalize LINKUP_API_KEY if present
if os.getenv('LINKUP_API_KEY'):
    os.environ['LINKUP_API_KEY'] = os.getenv('LINKUP_API_KEY').strip()

LINKUP_BASE = os.getenv('LINKUP_BASE_URL', 'https://api.linkup.so')


# -------------------------
# Linkup search tool
# -------------------------
@tool
def linkup_search_tool(query: str) -> List[Dict]:
    """Query Linkup and return a list of company dicts."""
    key = os.getenv("LINKUP_API_KEY")
    if not key:
        print("⚠️ LINKUP_API_KEY not set. Returning empty results.")
        return []

    # Updated endpoint: check current Linkup API
    url = f"{LINKUP_BASE}/v2/jobs"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    try:
        print(f"📡 Searching Linkup for '{query}'...")
        resp = requests.post(url, json={"query": query, "limit": 20}, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"API Error {resp.status_code}: {resp.text[:200]}...")
            return []
        data = resp.json()
        results = data.get("jobs", data.get("results", []))
        print(f"✅ Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"❌ Tool call failed: {e}")
        return []


# -------------------------
# Initialize LLM (Azure/OpenAI)
# -------------------------
def _init_llm() -> Optional[ChatOpenAI]:
    az_key = os.getenv("AZURE_OPENAI_KEY")
    az_endpoint = os.getenv("AZURE_OPENAI_GPT_ENDPOINT")
    az_deploy = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")
    openai_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4")

    if ChatOpenAI is None:
        return None

    if az_key and az_endpoint and az_deploy:
        # Use model_kwargs for Azure endpoint
        return ChatOpenAI(
            model=az_deploy,
            openai_api_key=az_key,
            model_kwargs={"azure_endpoint": az_endpoint},
            temperature=0.2
        )
    elif openai_key:
        return ChatOpenAI(
            model=model_name,
            openai_api_key=openai_key,
            temperature=0.2
        )
    return None


llm = _init_llm()
agent = None
agent_executor = None
if create_agent and llm:
    try:
        system_prompt = (
            "You are a startup sourcing agent. Use the linkup_search_tool to find companies. "
            "Return ONLY the raw JSON list from the tool, no extra text."
        )
        agent = create_agent(model=llm, tools=[linkup_search_tool], system_prompt=system_prompt)
        agent_executor = agent
        print("✅ Agent created successfully.")
    except Exception as e:
        print("⚠️ Agent creation failed, falling back to tool:", e)
else:
    print("⚠️ Azure/OpenAI not configured or create_agent missing. Using tool-only fallback.")


# -------------------------
# Main discovery function
# -------------------------
def find_companies(criteria: str) -> Dict:
    """Run agent or fallback to tool and return JSON-compatible dict."""
    print(f"--- find_companies called for: '{criteria}' ---")
    json_instruction = (
        "You are a startup scout. Use linkup_search_tool and output ONLY the raw JSON list of companies."
    )
    full_input = f"{json_instruction}\n\nSearch Criteria: {criteria}"

    if agent_executor:
        try:
            return agent_executor.invoke({"input": full_input})
        except Exception as e:
            print("Agent invocation failed, falling back to tool:", e)

    # Tool fallback
    try:
        results = linkup_search_tool(criteria)
        return {"output": json.dumps(results), "input": criteria, "status": "tool-fallback"}
    except Exception as e:
        return {"output": json.dumps([]), "input": criteria, "error": str(e), "status": "tool-fallback"}


# -------------------------
# Test block
# -------------------------
if __name__ == "__main__":
    test_query = "AI startups in healthcare"
    print(f"\n--- Running test for: '{test_query}' ---")
    output = find_companies(test_query)
    raw_output = output.get("output", "")

    try:
        companies = json.loads(raw_output)
        print(f"✅ Parsed {len(companies)} companies.")
        if companies:
            print(f"First company: {companies[0]}")
    except Exception as e:
        print("❌ Failed to parse JSON output:", e)
        print(f"Raw output (start): {raw_output[:300]}...")
