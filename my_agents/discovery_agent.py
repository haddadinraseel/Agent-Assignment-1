# my_agents/discovery_agent.py
"""
Discovery Agent: Finds a raw list of potential startups based on search criteria.
This agent interfaces with the Linkup API to retrieve startup candidates.
"""
import requests
from typing import List, Dict, Optional

BACKEND_URL = "http://localhost:8000"

def find_companies(
    criteria: str,
    location: Optional[str] = None,
    funding_stage: Optional[str] = None
) -> List[Dict]:
    """
    Discovery Agent: Searches for startups matching the given criteria.
    
    Args:
        criteria (str): The search criteria for finding startups.
        location (str, optional): Filter by location (country/city).
        funding_stage (str, optional): Filter by funding stage (Seed, Series A, etc.).
    
    Returns:
        List[Dict]: A list of startup dictionaries with basic information.
    """
    payload = {
        "search_criteria": criteria,
        "location": location,
        "funding_stage": funding_stage
    }

    try:
        response = requests.post(f"{BACKEND_URL}/linkup_search", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                companies = data.get("results", [])
                print(f"Discovery Agent: Found {len(companies)} potential startups")
                return companies
            else:
                print(f"Discovery Agent Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception in Discovery Agent: {e}")
    
    return []
