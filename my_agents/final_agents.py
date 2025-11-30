import os
import json
import asyncio
import logging
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from my_agents.linkup_tools import linkup_search_tool

from pydantic import BaseModel

# -------------------------
# Load environment
# -------------------------

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")
if not LINKUP_API_KEY:
    raise RuntimeError("LINKUP_API_KEY not found in environment")

AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")

if not (AZURE_KEY and AZURE_ENDPOINT and AZURE_DEPLOYMENT):
    raise RuntimeError("Azure OpenAI environment variables not configured (AZURE_OPENAI_KEY/ENDPOINT/DEPLOYMENT)")

# -------------------------
# LLM Model
# -------------------------
model = AzureChatOpenAI(
    azure_deployment=AZURE_DEPLOYMENT,
    api_key=AZURE_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=os.getenv('OPENAI_API_VERSION', '2025-03-01-preview'),
    temperature=0.0,
)

class CompanyInfo(BaseModel):
    name: str
    url: str
    country: str

class CompaniesInfoResponse(BaseModel):
    companies: list[CompanyInfo]


class CompanyDetails(BaseModel):
    name: str  # The official name of the company
    url: str  # The company's website URL
    country: str  # The country where the company is headquartered
    description: str  # A brief description of the company
    founding_year: str  # The year the company was founded
    funding_stage: str | None = None  # The current funding stage (optional)
    ARR: str | None = None  # Annual Recurring Revenue (optional)
    market_sector: str  # The market sector or industry the company operates in

class CompanyDetailsResponse(BaseModel):
    CompanyExpanded: list[CompanyDetails]

# -------------------------
# Discovery Agent
# -------------------------
discovery_agent = create_agent(
    model,
    tools=[linkup_search_tool],
    system_prompt=(
        "You are a Discovery Agent that finds REAL startup companies matching an investment thesis.\n\n"
        "INSTRUCTIONS:\n"
        "1. Use the linkup_search tool to search for startups matching the user's criteria\n"
        "2. Extract ONLY real company names from Linkup results\n"
        "3. No hallucinations, no generic terms\n\n"
        "RULES:\n"
        "- Only include REAL companies found via Linkup search\n"
        "- No filler, no commentary, only JSON"
    ),
    response_format=CompaniesInfoResponse
)

# -------------------------
# Deep Dive Agent
# -------------------------
deep_dive_agent = create_agent(
    model,
    tools=[linkup_search_tool],
    system_prompt=(
        "You are a Deep Dive Agent that researches detailed information about a startup.\n\n"
        "Must use linkup_search for ALL information.\n"
        "Keep searching until you have found all required information.\n"
        "Dont make up any information.\n"
    ),
    response_format=CompanyDetailsResponse
)

# -------------------------
# Deep Dive (Parallel)
# -------------------------
async def _deep_dive_single(startup: CompanyInfo) -> CompanyDetails | None:
    """Deep dive a single company asynchronously."""
    try:
        result = await asyncio.to_thread(
            deep_dive_agent.invoke,
            {"messages": [{"role": "user", "content": f"Research the company: {startup.name}, URL: {startup.url}"}]}
        )
        return result['structured_response'].CompanyExpanded[0]
    except Exception as e:
        print(f"Deep dive failed for {startup.name}: {e}")
        return None

async def deep_dive_all(companies: list[CompanyInfo]) -> list[CompanyDetails | None]:
    """Run deep dives for all companies in parallel."""
    tasks = [_deep_dive_single(company) for company in companies]
    return await asyncio.gather(*tasks)

# -------------------------
# Agents Pipeline
# -------------------------
async def run_pipeline(investment_thesis: str, attributes: list[str] = None) -> list[dict]:
    """
    Main pipeline: Discovery → Deep Dive (parallel)
    Returns list of company details as dictionaries.
    """
    # Step 1: Discovery
    discovery_result = discovery_agent.invoke(
        {"messages": [{"role": "user", "content": investment_thesis}]}
    )
    companies = discovery_result['structured_response'].companies
    
    if not companies:
        return []
    
    # Step 2: Deep Dive (parallel)
    details_list = await deep_dive_all(companies)
    
    # Step 3: Convert to dictionaries for JSON response
    results = []
    for details in details_list:
        if details:
            results.append({
                "name": details.name,
                "url": details.url,
                "country": details.country,
                "description": details.description,
                "founding_year": details.founding_year,
                "funding_stage": details.funding_stage,
                "ARR": details.ARR,
                "market_sector": details.market_sector
            })
    
    return results

################################################################

# if __name__ == "__main__":
#     async def main():
#         query = "Find HR Tech Startups in Jordan."

#         result = discovery_agent.invoke(
#             {"messages": [{"role": "user", "content": query}]}
#         )

#         print("Discovery Agent Result:")
#         print(f"Found {len(result['structured_response'].companies)} companies:\n")

#         for company in result['structured_response'].companies:
#             print(f"Name: {company.name}, URL: {company.url}, Country: {company.country}")

#         print("\nRunning Deep Dive Agent in parallel...\n")

#         # Test parallel deep dive
#         details_list = await deep_dive_all(result['structured_response'].companies)

#         for details in details_list:
#             if details:
#                 print(f"Details for {details.name}:")
#                 print(f"  URL: {details.url}")
#                 print(f"  Country: {details.country}")
#                 print(f"  Description: {details.description}")
#                 print(f"  Founding Year: {details.founding_year}")
#                 print(f"  Funding Stage: {details.funding_stage}")
#                 print(f"  ARR: {details.ARR}")
#                 print(f"  Market Sector: {details.market_sector}")
#                 print("--------------------------------------------------\n")

#     asyncio.run(main())
    

