import os
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from langchain.tools import tool

# Defensive imports to avoid crashes
try:
    from langchain.agents import create_agent
except Exception:
    create_agent = None

try:
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
except Exception:
    AzureChatOpenAI = None
    ChatOpenAI = None


# ===========================
# Load .env
# ===========================
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


# ===========================
# Deep Dive Tool
# ===========================
@tool
def deep_dive_tool(company_json: str, criteria: str, attributes: str) -> str:
    """
    Enrich a company by running a deep-dive search (LLM, APIs, etc.)
    Input values are JSON strings due to LangChain tool I/O.
    """
    try:
        company = json.loads(company_json)
        attrs = [a.strip() for a in attributes.split(",")]

        # Simulated enhancement — replace with real APIs
        enriched = {
            **company,
            "Deep Dive Year Founded": "2021 (LLM)",
            "Deep Dive Funding": "$10M (LLM)",
            "Founders": "Alice & Bob (LLM)",
            "Notes": f"Deep dive for criteria: {criteria}"
        }

        # Ensure all attributes exist
        for attr in attrs:
            enriched.setdefault(attr, "N/A")

        return json.dumps(enriched)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ===========================
# Initialize LLM
# ===========================
def _init_llm() -> Optional[object]:
    """
    Initialize AzureChatOpenAI or fallback to ChatOpenAI.
    """
    if not (AzureChatOpenAI or ChatOpenAI):
        return None

    # --- Azure ---
    az_key = os.getenv("AZURE_OPENAI_KEY")
    az_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    az_deploy = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if az_key and az_endpoint and az_deploy and AzureChatOpenAI:
        return AzureChatOpenAI(
            azure_deployment=az_deploy,
            api_key=az_key,
            azure_endpoint=az_endpoint,
            api_version="2024-02-15-preview",
            temperature=0.2,
        )

    # --- Fallback: OpenAI ---
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and ChatOpenAI:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_key,
            temperature=0.2,
        )

    return None


# ===========================
# Create Agent
# ===========================
llm = _init_llm()
deep_dive_agent = None

if llm and create_agent:
    try:
        deep_dive_agent = create_agent(
            model=llm,
            tools=[deep_dive_tool],
            system_prompt=(
                "You are a senior investment research analyst. "
                "Use the deep_dive_tool to enrich and analyze each company. "
                "Return ONLY the JSON output from the tool."
            ),
        )
        print("✅ Deep Dive Agent created successfully.")
    except Exception as e:
        print(f"⚠️ Deep Dive Agent creation failed: {e}")
else:
    print("⚠️ Missing LLM or agent factory. Using only raw tool fallback.")


# ===========================
# Internal helper (single company)
# ===========================
def _process_single_company(company: Dict, criteria: str, attributes: List[str]) -> Dict:
    """
    Runs deep dive for ONE company using the agent.
    """
    comp_json = json.dumps(company)
    attrs_str = ", ".join(attributes)

    # ------- Agent path -------
    if deep_dive_agent:
        try:
            prompt = (
                f"Use deep_dive_tool to enrich this company.\n"
                f"COMPANY_JSON: {comp_json}\n"
                f"CRITERIA: {criteria}\n"
                f"ATTRIBUTES: {attrs_str}\n"
                f"Return only JSON."
            )

            response = deep_dive_agent.invoke({"input": prompt})
            output_str = response.get("output", "")

            return json.loads(output_str)
        except Exception as e:
            print(f"⚠️ Agent failed for {company.get('Company Name')}: {e}")

    # ------- Tool fallback -------
    try:
        result_json = deep_dive_tool.invoke({"company_json": comp_json, "criteria": criteria, "attributes": attrs_str})
        return json.loads(result_json)
    except Exception as e:
        print(f"⚠️ Tool fallback failed: {e}")
        return company


# ===========================
# Public API: Parallel Deep Dive
# ===========================
def deep_dive_parallel(
    companies: List[Dict],
    criteria: str,
    attributes: List[str],
    max_workers: int = 5
) -> List[Dict]:
    """
    Runs deep-dive on all companies using threading.
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_process_single_company, c, criteria, attributes): c
            for c in companies
        }

        for future in as_completed(futures):
            try:
                enriched = future.result()
                results.append(enriched)
            except Exception as e:
                comp = futures[future]
                print(f"Deep dive failed for {comp.get('Company Name', 'N/A')}: {e}")

    return results


# ===========================
# Manual test
# ===========================
if __name__ == "__main__":
    sample = [
        {"Company Name": "Startup A", "Website": "https://a.com"},
        {"Company Name": "Startup B", "Website": "https://b.com"},
        {"Company Name": "Startup C", "Website": "https://c.com"},
    ]

    print("\n--- Running Deep Dive ---")
    enriched = deep_dive_parallel(sample, "AI infra", ["Founders", "Year Founded"])

    print("\n--- Results ---")
    for c in enriched:
        print(json.dumps(c, indent=2))
