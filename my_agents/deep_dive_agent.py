# my_agents/deep_dive_agent.py
"""
Deep Dive Agents: Run parallel sub-agents for each startup to gather specific attributes.
This agent enriches startup data with requested attributes using async/concurrent processing.
"""
import asyncio
from typing import List, Dict

async def deep_dive_company(company: Dict, criteria: str, attributes: List[str]) -> Dict:
    """
    Deep Dive Agent: Enriches a single startup with specific attributes.
    Runs asynchronously to allow parallel processing of multiple startups.
    
    Args:
        company (Dict): The startup data from the discovery agent.
        criteria (str): The original search criteria (for context).
        attributes (List[str]): List of attributes to enrich for this startup.
    
    Returns:
        Dict: The enriched startup data with requested attributes.
    """
    enriched = company.copy()
    
    # Simulate async I/O (in real scenario, this would be API calls, LLM processing, etc.)
    await asyncio.sleep(0.5)
    
    # Enrich with requested attributes
    for attr in attributes:
        if attr not in enriched:
            # Simulate gathering data for this attribute
            enriched[attr] = f"Processed: {attr}"
    
    # Add metadata
    enriched["Analysis_Status"] = "Deep Dive Complete"
    enriched["Criteria_Match"] = criteria
    
    return enriched


async def run_concurrent_deep_dive(
    companies: List[Dict], 
    criteria: str, 
    attributes: List[str], 
    max_companies: int = 5
) -> List[Dict]:
    """
    Deep Dive Agent Coordinator: Runs parallel deep dive sub-agents for each startup.
    
    Args:
        companies (List[Dict]): List of startups from the discovery agent.
        criteria (str): The original search criteria.
        attributes (List[str]): Attributes to gather for each startup.
        max_companies (int): Maximum number of startups to analyze (default: 5).
    
    Returns:
        List[Dict]: List of enriched startup data with all requested attributes.
    """
    # Limit to max_companies to avoid overload
    companies_to_process = companies[:max_companies]
    
    # Create concurrent tasks for each startup
    tasks = [
        deep_dive_company(company, criteria, attributes)
        for company in companies_to_process
    ]
    
    # Run all deep dive sub-agents concurrently
    enriched_companies = await asyncio.gather(*tasks)
    
    print(f"Deep Dive Agent: Processed {len(enriched_companies)} startups in parallel")
    
    return enriched_companies
