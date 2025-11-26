"""
deep_dive_experiment.py — LLM Agent that uses Linkup SDK to enrich company data

For each company found by discovery, this agent fetches the company website
and uses LLM to extract additional details based on user-selected attributes.
"""

import os
import json
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# ===========================
# Load environment
# ===========================
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")


# ===========================
# Initialize Linkup Client
# ===========================
from linkup import LinkupClient

linkup_client = LinkupClient(api_key=LINKUP_API_KEY)


# ===========================
# Linkup Fetch Tool
# ===========================
@tool
def linkup_fetch_company(website_url: str) -> str:
    """
    Fetch content from a company's website using Linkup API.
    
    Args:
        website_url: The company's website URL to fetch
    
    Returns:
        The webpage content in markdown format
    """
    if not website_url or website_url == "N/A":
        return "No website available"
    
    print(f"🌐 Fetching: {website_url}")
    
    try:
        # Use client.fetch() to get webpage content
        response = linkup_client.fetch(url=website_url)
        
        # Extract content from response
        if hasattr(response, 'content'):
            content = response.content[:5000]  # Limit to 5000 chars
        elif isinstance(response, str):
            content = response[:5000]
        else:
            content = str(response)[:5000]
        
        print(f"✅ Fetched {len(content)} chars from {website_url}")
        return content
        
    except Exception as e:
        print(f"⚠️ Failed to fetch {website_url}: {e}")
        return f"Could not fetch website: {str(e)}"


# ===========================
# Linkup Search Tool
# ===========================
@tool
def linkup_search_company(query: str) -> str:
    """
    Search for additional information about a company using Linkup API.
    
    Args:
        query: Search query about the company (e.g., "DeepMind funding rounds investors")
    
    Returns:
        Search results as text
    """
    print(f"🔎 Searching: {query}")
    
    try:
        # Use client.search() for research queries
        response = linkup_client.search(
            query=query,
            depth="standard",
            output_type="searchResults"
        )
        
        # Extract results
        results_text = []
        if hasattr(response, 'results'):
            for r in response.results[:5]:  # Top 5 results
                title = getattr(r, 'title', getattr(r, 'name', 'N/A'))
                content = getattr(r, 'content', getattr(r, 'snippet', ''))[:500]
                results_text.append(f"**{title}**\n{content}")
        else:
            results_text.append(str(response)[:2000])
        
        output = "\n\n---\n\n".join(results_text)
        print(f"✅ Found {len(results_text)} results")
        return output
        
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        return f"Search failed: {str(e)}"


# ===========================
# Initialize LLM
# ===========================
def _init_llm() -> Optional[object]:
    az_key = os.getenv("AZURE_OPENAI_KEY")
    az_endpoint = os.getenv("AZURE_OPENAI_GPT_ENDPOINT")
    az_deploy = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")
    
    if az_key and az_endpoint and az_deploy:
        print("🔧 Using Azure OpenAI for deep dive")
        return AzureChatOpenAI(
            azure_deployment=az_deploy,
            api_key=az_key,
            azure_endpoint=az_endpoint,
            api_version="2024-02-15-preview",
            temperature=0.2,
        )

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("🔧 Using OpenAI for deep dive")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_key,
            temperature=0.2,
        )

    return None


# Initialize LLM once
llm = _init_llm()
if llm:
    print("✅ Deep Dive Agent ready")
else:
    print("⚠️ No LLM configured for deep dive")


# ===========================
# Enrich a single company
# ===========================
def _enrich_company(company: Dict, investment_thesis: str, attributes: List[str]) -> Dict:
    """
    Enrich a company with additional data using Linkup fetch + LLM.
    """
    company_name = company.get("Company Name", company.get("name", "Unknown"))
    company_website = company.get("Website", company.get("url", "N/A"))
    company_desc = company.get("Description", "")
    company_location = company.get("Location", "N/A")
    company_industry = company.get("Industry", "N/A")
    company_funding = company.get("Funding Stage", "N/A")
    
    print(f"\n{'─'*40}")
    print(f"🔍 DEEP DIVE: {company_name}")
    print(f"   📍 Location: {company_location}")
    print(f"   🌐 Website: {company_website}")
    print(f"   🏢 Industry: {company_industry}")
    
    # Fetch website content if available
    website_content = ""
    if company_website and company_website != "N/A":
        try:
            website_content = linkup_fetch_company.invoke(company_website)
        except Exception as e:
            print(f"⚠️ Could not fetch website for {company_name}: {e}")
    
    # Use LLM to extract additional info
    enriched_data = {}
    if llm:
        try:
            # Build the attributes list for the prompt
            attrs_text = "\n".join([f"- {attr}" for attr in attributes])
            
            prompt = f"""Extract information about this company based on the provided data.

COMPANY: {company_name}
WEBSITE: {company_website}
KNOWN DESCRIPTION: {company_desc}
KNOWN LOCATION: {company_location}
KNOWN INDUSTRY: {company_industry}
KNOWN FUNDING STAGE: {company_funding}

WEBSITE CONTENT:
{website_content[:3000] if website_content else "No website content available"}

INVESTMENT THESIS CONTEXT: {investment_thesis}

Please extract the following information:
{attrs_text}

Return ONLY a valid JSON object with these fields. Use "N/A" if information is not available.
Do NOT include markdown code blocks, just the raw JSON."""

            response = llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                enriched_data = json.loads(json_match.group(0))
                
        except Exception as e:
            print(f"⚠️ LLM enrichment failed for {company_name}: {e}")
    
    # Build final enriched company object
    result = {
        "Company Name": company_name,
        "Website": company_website,
        "Description": enriched_data.get("Description", company_desc) or company_desc or "N/A",
        "Location": enriched_data.get("Location", company_location) or company_location or "N/A",
        "Industry": enriched_data.get("Industry", company_industry) or company_industry or "N/A",
        "Funding Stage": enriched_data.get("Funding Stage", company_funding) or company_funding or "N/A",
    }
    
    # Add any additional requested attributes
    for attr in attributes:
        if attr not in result:
            result[attr] = enriched_data.get(attr, "N/A")
    
    return result


# ===========================
# Public API: Parallel Deep Dive
# ===========================
def deep_dive_parallel(
    companies: List[Dict],
    investment_thesis: str,
    attributes: List[str],
    max_workers: int = 3
) -> List[Dict]:
    """
    Enrich multiple companies in parallel.
    
    Args:
        companies: List of company dicts from discovery
        investment_thesis: The original search criteria
        attributes: List of attributes to extract (e.g., ["Founders", "Total Funding"])
    
    Returns:
        List of enriched company dicts
    """
    print("\n" + "="*60)
    print("🔧 DEEP DIVE AGENT - ENRICHING COMPANIES")
    print("="*60)
    print(f"📊 Companies to enrich: {len(companies)}")
    print(f"📋 Attributes to extract: {attributes}")
    print(f"🔄 Max parallel workers: {max_workers}")
    print("-"*60)
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_enrich_company, c, investment_thesis, attributes): c 
            for c in companies
        }
        
        for future in as_completed(futures):
            try:
                enriched = future.result()
                results.append(enriched)
                print(f"✅ Enriched: {enriched.get('Company Name', 'Unknown')}")
            except Exception as e:
                comp = futures[future]
                print(f"❌ Failed for {comp.get('Company Name', 'N/A')}: {e}")
                # Keep original company data on failure
                results.append(comp)
    
    print(f"\n✅ Deep dive complete: {len(results)} companies enriched")
    return results


# ===========================
# Test
# ===========================
if __name__ == "__main__":
    sample_companies = [
        {
            "Company Name": "DeepMind",
            "Website": "https://deepmind.com",
            "Description": "AI research company",
            "Location": "London, UK",
            "Industry": "AI"
        },
        {
            "Company Name": "Revolut",
            "Website": "https://revolut.com",
            "Description": "Digital banking",
            "Location": "London, UK",
            "Industry": "Fintech"
        }
    ]
    
    print("\n" + "="*60)
    print("Testing Deep Dive Agent")
    print("="*60)
    
    enriched = deep_dive_parallel(
        companies=sample_companies,
        investment_thesis="AI startups in London",
        attributes=["Founders", "Total Funding", "Year Founded", "Technology Stack"]
    )
    
    print("\n" + "="*60)
    print("Results:")
    print("="*60)
    for c in enriched:
        print(json.dumps(c, indent=2))

