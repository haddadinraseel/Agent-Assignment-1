"""
discovery_experiment.py — LLM Agent that uses Linkup SDK as a tool to find startups

The agent receives an investment thesis (e.g., "AI startups in London") and uses
Linkup's structured output to find matching companies.
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# ============================
# Load environment
# ============================
load_dotenv()

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")


# ============================
# Linkup Search Tool
# ============================
@tool
def linkup_startup_search(investment_thesis: str) -> str:
    """
    Search for startups matching an investment thesis using Linkup API.
    The investment thesis should include location, industry, and any other criteria.
    Example: "AI startups in London" or "fintech seed stage companies in New York"
    
    Args:
        investment_thesis: The search criteria describing what companies to find
    
    Returns:
        JSON string with list of companies matching the criteria
    """
    print("\n" + "="*60)
    print("🔧 DISCOVERY AGENT - LINKUP SEARCH TOOL")
    print("="*60)
    print(f"📝 Investment Thesis: {investment_thesis}")
    print("-"*60)
    
    from linkup import LinkupClient

    # Initialize the Linkup client
    client = LinkupClient(api_key=LINKUP_API_KEY)
    
    # Perform a search query using sourcedAnswer for comprehensive results
    search_query = f"""Find startups that match this investment thesis: {investment_thesis}

STRICT REQUIREMENTS:
- If a city is mentioned (e.g., "Berlin"), ONLY return companies HEADQUARTERED in that specific city
- Do NOT include companies that merely have offices or operations there - headquarters must be in that city
- Only include companies at the funding stage mentioned (if any)
- Only include companies meeting ARR/revenue criteria (if any)
- For each company provide: name, website, description, HEADQUARTERS location (city, country), industry, funding stage, and ARR if known

Focus on finding companies that match ALL criteria, not just some."""
    
    print(f"🔍 Sending to Linkup API (depth=deep, output_type=sourcedAnswer)...")
    print(f"📤 Query: {search_query[:200]}...")
    
    search_response = client.search(
        query=search_query,
        depth="deep",
        output_type="sourcedAnswer",
    )
    
    print(f"\n📦 Linkup API Response Received!")
    
    # Extract the answer text from the response
    answer_text = ""
    if hasattr(search_response, "answer"):
        answer_text = search_response.answer
    elif isinstance(search_response, dict):
        answer_text = search_response.get("answer", str(search_response))
    else:
        answer_text = str(search_response)
    
    print(f"📝 Got answer: {len(answer_text)} chars")
    print(f"📄 Answer preview: {answer_text[:500]}...")
    print("-"*60)
    
    # Use LLM to extract structured company data from the answer
    print("\n🤖 Using LLM to extract structured company data...")
    llm_instance = init_llm()
    if not llm_instance:
        print("⚠️ No LLM available for extraction")
        return json.dumps([])
    
    extraction_prompt = f"""Extract company information from this research answer.

SEARCH QUERY: {investment_thesis}

RESEARCH ANSWER:
{answer_text}

CRITICAL FILTERING INSTRUCTIONS:
- If the search query mentions a SPECIFIC CITY (e.g., "Berlin", "London", "San Francisco"), ONLY include companies with HEADQUARTERS in that exact city
- Do NOT include companies that just have an "office" or "presence" in that city - they must be HEADQUARTERED there
- If a company's headquarters location is unknown or different from the requested city, EXCLUDE IT
- If a funding stage is mentioned (e.g., "Series A"), only include companies at that stage
- If ARR/revenue criteria is mentioned, only include companies meeting that criteria

For each qualifying company extract:
  * Company Name
  * Website (URL if available, otherwise "N/A")
  * Description (1-2 sentences)
  * Location (headquarters city, country - must match the search query location if specified)
  * Industry
  * Funding Stage
  * ARR (Annual Recurring Revenue if mentioned)

Return a JSON array: [{{"Company Name": "...", "Website": "...", "Description": "...", "Location": "...", "Industry": "...", "Funding Stage": "...", "ARR": "..."}}]

Return ONLY the JSON array, nothing else. If no companies match ALL criteria, return []"""

    try:
        response = llm_instance.invoke(extraction_prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            companies = json.loads(json_match.group(0))
            print(f"\n✅ DISCOVERY COMPLETE: Extracted {len(companies)} companies")
            for i, c in enumerate(companies[:5]):
                print(f"   {i+1}. {c.get('Company Name', 'Unknown')} - {c.get('Location', 'N/A')}")
            if len(companies) > 5:
                print(f"   ... and {len(companies) - 5} more")
            print("="*60 + "\n")
            return json.dumps(companies)
        else:
            print("⚠️ No JSON found in LLM response")
            return json.dumps([])
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return json.dumps([])


# ============================
# Initialize LLM
# ============================
def init_llm():
    if os.getenv("AZURE_OPENAI_KEY"):
        print("🔧 Using Azure OpenAI for discovery")
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_GPT_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            temperature=0.0,
        )

    if os.getenv("OPENAI_API_KEY"):
        print("🔧 Using OpenAI for discovery")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0,
        )

    return None


# ============================
# Create the LLM Agent using create_agent
# ============================
llm = init_llm()

SYSTEM_PROMPT = """You are a startup discovery agent. Your ONLY job is to call the linkup_startup_search tool with the user's investment thesis.

INSTRUCTIONS:
1. When the user gives you search criteria (investment thesis), IMMEDIATELY call linkup_startup_search
2. Pass the EXACT criteria the user provided to the tool - do NOT change or substitute it
3. Do NOT add your own commentary
4. Do NOT modify the results
5. Return the tool's output as your final response
"""

if llm:
    discovery_agent = create_agent(
        model=llm,
        tools=[linkup_startup_search],
        system_prompt=SYSTEM_PROMPT,
    )
    print("✅ Discovery Agent created successfully.")
else:
    discovery_agent = None
    print("⚠️ No LLM configured.")


# ============================
# Public API for backend
# ============================
def find_companies(investment_thesis: str) -> List[Dict]:
    """
    Find companies matching the investment thesis.
    
    Args:
        investment_thesis: Search criteria like "AI startups in London, seed stage"
    
    Returns:
        List of company dicts with: Company Name, Website, Description, Location, Industry, Funding Stage
    """
    print(f"\n{'='*60}")
    print(f"🔍 Discovery Agent: {investment_thesis}")
    print(f"{'='*60}")

    # Try agent first
    if discovery_agent:
        try:
            result = discovery_agent.invoke({"input": investment_thesis})
            print(f"📋 Agent result type: {type(result)}")
            
            # Handle create_agent response format: {'messages': [...]}
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                for msg in messages:
                    # Look for ToolMessage with results
                    if hasattr(msg, 'type') and msg.type == 'tool':
                        content = msg.content
                        if isinstance(content, str):
                            try:
                                return json.loads(content)
                            except:
                                pass
                        elif isinstance(content, list):
                            return content
                    # Check message content
                    if hasattr(msg, 'content'):
                        try:
                            parsed = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                            if isinstance(parsed, list) and len(parsed) > 0:
                                return parsed
                        except:
                            pass
            
            # Try output key
            if isinstance(result, dict) and 'output' in result:
                output = result['output']
                if isinstance(output, str):
                    try:
                        return json.loads(output)
                    except:
                        pass
                elif isinstance(output, list):
                    return output
                    
        except Exception as e:
            print(f"❌ Agent failed: {e}")
            import traceback
            traceback.print_exc()

    # Fallback: direct tool call
    print("📞 Falling back to direct Linkup search")
    result = linkup_startup_search.invoke(investment_thesis)
    return json.loads(result) if isinstance(result, str) else result


# ============================
# Test
# ============================
if __name__ == "__main__":
    thesis = "AI startups in London"
    print(f"\n{'='*60}")
    print(f"Testing Discovery Agent")
    print(f"Investment Thesis: {thesis}")
    print('='*60)
    
    companies = find_companies(thesis)
    
    print(f"\n✅ Found {len(companies)} companies\n")
    for c in companies[:5]:
        print(f"• {c.get('Company Name', 'Unknown')}")
        print(f"  Location: {c.get('Location', 'N/A')}")
        print(f"  Industry: {c.get('Industry', 'N/A')}")
        print(f"  {c.get('Description', '')[:80]}...")
        print()

