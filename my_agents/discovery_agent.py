"""
discovery_agent.py — Clean minimal Discovery Agent using LangChain + Linkup
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI, AzureChatOpenAI


# ============================
# Load environment
# ============================
load_dotenv()

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")


# ============================
# Linkup Search Tool
# ============================
@tool
def linkup_search(query: str) -> List[Dict]:
    """
    Use Linkup API to search the web with sourcedAnswer mode, then extract structured company data using LLM.
    Returns a list of company dicts with: Company Name, Website, Description.
    """
    try:
        from linkup import LinkupClient

        client = LinkupClient(api_key=LINKUP_API_KEY)
        
        # Use sourcedAnswer to get a comprehensive answer with sources
        response = client.search(
            query=query,
            depth="deep",  # Most exhaustive search
            output_type="sourcedAnswer",  # Get natural language answer with sources
            include_images=False,
        )

        # Extract the answer and sources from sourcedAnswer response
        answer_text = ""
        sources = []
        
        if hasattr(response, "answer"):
            answer_text = response.answer
            print(f"📝 Got sourced answer: {len(answer_text)} chars")
        
        if hasattr(response, "sources"):
            for src in response.sources[:10]:
                sources.append({
                    "name": getattr(src, "name", ""),
                    "url": getattr(src, "url", ""),
                    "snippet": getattr(src, "snippet", "")[:200] if hasattr(src, "snippet") else ""
                })
            print(f"📚 Got {len(sources)} sources")

        if not answer_text:
            print("⚠️ No answer from Linkup")
            return []

        # Use LLM to extract structured company data from the answer
        llm_instance = init_llm()
        if not llm_instance:
            print("⚠️ No LLM available")
            return []

        # Build source context
        sources_text = "\n".join([f"- {s['name']}: {s['url']}" for s in sources])
        
        prompt = f"""Extract company information from this research answer about: {query}

ANSWER FROM WEB RESEARCH:
{answer_text}

SOURCES:
{sources_text}

Instructions:
- Extract ONLY actual company names mentioned in the answer
- Include companies that match the search criteria (location, industry, funding stage if mentioned)
- For each company provide:
  * Company Name (just the name, no suffixes)
  * Website (from sources if available, otherwise "N/A")
  * Description (1-2 sentence summary of what they do)
- Output valid JSON array: [{{"Company Name": "...", "Website": "...", "Description": "..."}}]
- Limit to 8-10 most relevant companies
- If no actual companies found, return empty array []

Output ONLY the JSON array, nothing else:"""

        response = llm_instance.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        # Parse JSON from response
        try:
            # Try to find JSON array in response
            import re
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
            if json_match:
                companies = json.loads(json_match.group(0))
                print(f"✅ Extracted {len(companies)} companies from sourced answer")
                return companies
            else:
                print("⚠️ No JSON found in LLM response")
                return []
        except Exception as e:
            print(f"❌ Failed to parse LLM response: {e}")
            return []

    except Exception as e:
        print("❌ Linkup search failed:", e)
        return []


# ============================
# Initialize LLM (Azure or OpenAI)
# ============================
def init_llm():
    if os.getenv("AZURE_OPENAI_KEY"):
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_GPT_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            temperature=0.0,
        )

    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0,
        )

    return None


llm = init_llm()


# ============================
# Create Agent
# ============================
if llm:
    discovery_agent = create_agent(
        model=llm,
        tools=[linkup_search],
        system_prompt=(
            "You are a tool-calling agent. You have access to the linkup_search tool.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. When the user provides search criteria, IMMEDIATELY call linkup_search with those criteria\n"
            "2. Do NOT respond with text\n"
            "3. Do NOT explain what you're doing\n"
            "4. Do NOT format or create JSON yourself\n"
            "5. Your ONLY action is to call the tool - nothing else\n\n"
            "Example:\n"
            "User: 'AI startups in healthcare'\n"
            "You: [call linkup_search with 'AI startups in healthcare']\n\n"
            "NEVER say 'I am searching' or 'Please provide criteria' - just call the tool immediately."
        ),
    )
    print("✅ Agent created successfully.")
else:
    discovery_agent = None
    print("⚠️ No LLM configured — tool fallback only.")


# ============================
# Public function to call from backend
# ============================
def find_companies(criteria: str) -> List[Dict]:
    """Return a clean list of company dicts."""
    print(f"🔍 Discovery agent triggered with criteria: {criteria}")

    # 1. Agent path
    if discovery_agent:
        try:
            result = discovery_agent.invoke({"input": criteria})
            print(f"🔍 Agent result type: {type(result)}, keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

            # Handle create_agent response: {'messages': [...]}
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                # Look for tool call results in messages
                for msg in messages:
                    # Check if message has tool_calls attribute (tool invocation)
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"✅ Found tool call in message")
                        continue
                    # Check for ToolMessage with actual results
                    if hasattr(msg, 'type') and msg.type == 'tool':
                        tool_result = msg.content
                        print(f"✅ Found tool result, type: {type(tool_result)}")
                        if isinstance(tool_result, str):
                            return json.loads(tool_result)
                        elif isinstance(tool_result, list):
                            return tool_result
                    # Fallback: check message content for list/dict
                    if hasattr(msg, 'content'):
                        try:
                            parsed = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                            if isinstance(parsed, list):
                                print(f"✅ Extracted list from message content")
                                return parsed
                        except:
                            pass

            # Old pattern: check for 'output' key
            tool_output = result.get("output", None)
            if tool_output:
                return json.loads(tool_output) if isinstance(tool_output, str) else tool_output

            print("⚠️ Could not extract results from agent, using tool fallback")

        except Exception as e:
            print(f"❌ Agent failed: {e}, using fallback")

    # 2. Fallback: direct tool call (no LLM)
    print("📞 Calling linkup_search directly")
    return linkup_search(criteria)


# ============================
# Local test
# ============================
if __name__ == "__main__":
    test = "AI startups in healthcare, seed stage"
    companies = find_companies(test)

    print(f"Found {len(companies)} companies.")
    if companies:
        print(companies[0])
