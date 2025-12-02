import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent  # ✅ Fixed import
from langchain_core.tools import tool
from my_agents.linkup_tools import linkup_search_tool
from my_agents.final_agents import (
    run_pipeline,
    deep_research_company,
    research_competitors
)

# -------------------------
# Load environment
# -------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")

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

# -------------------------
# Define all tools list for conversational agent
# -------------------------
all_tools = [
    linkup_search_tool,
    run_pipeline,
    deep_research_company,
    research_competitors
]

# -------------------------
# Conversational Agent
# -------------------------
conversational_agent = create_react_agent(
    model,
    tools=all_tools,
    prompt=(
        "You are Startup Scout, an AI assistant that helps investors discover and analyze startups.\n\n"
        
        "## Guidelines:\n"
        "1. Use tools when users ask about startups, companies, or competitors\n"
        "2. Make reasonable assumptions rather than asking many questions\n"
        "3. When a user mentions a company name, use deep_research_company\n"
        "4. When a user asks about competitors or alternatives, use research_competitors\n"
        "5. When a user wants to find or discover startups, use run_pipeline\n"
        "6. For simple greetings like 'hello' or 'thanks', respond conversationally\n\n"
        
        "## Tool Selection Guide:\n"
        "- 'find startups in X' or 'search for X companies' → run_pipeline(investment_thesis=X)\n"
        "- 'tell me about [Company]' or 'what is [Company]' → deep_research_company(company_name=[Company])\n"
        "- 'competitors of [Company]' or 'alternatives to [Company]' → research_competitors(company_name=[Company])\n"
        "- 'explore competitors' (no company specified) → research_competitors(company_name='startups', market_sector='technology')\n\n"
        
        "## Response Format:\n"
        "After using a tool, present results using this markdown structure:\n\n"
        "1. **Company Name**\n"
        "   - Website: [url]\n"
        "   - Description: [description]\n"
        "   - Founded: [year]\n"
        "   - Market Sector: [sector]\n\n"
        "2. **Next Company Name**\n"
        "   - Website: [url]\n"
        "   - Description: [description]\n"
        "   - Founded: [year]\n"
        "   - Market Sector: [sector]\n\n"
        "Use numbered list for companies (1. 2. 3.) and bullet points (-) for details indented under each company."
    )
)