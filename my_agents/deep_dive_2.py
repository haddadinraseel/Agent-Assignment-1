"""Deep-dive agent: enrich company records using an LLM tool.

This module attempts to use LangChain if available; if LangChain API
shapes differ in the environment, it falls back to a simple local tool
call so the package remains importable and functional for tests.
"""

import os
import json
from typing import List, Dict
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.tools import tool
try:
    # Newer/older LangChain layouts may differ; attempt imports and fall back gracefully
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    _LANGCHAIN_AVAILABLE = True
except Exception:
    # If LangChain has changed in this environment, avoid hard failure on import
    _LANGCHAIN_AVAILABLE = False
    AgentExecutor = None
    create_openai_tools_agent = None
    ChatPromptTemplate = None
    MessagesPlaceholder = None
    ChatOpenAI = None


# ------------------------------
# Helper decorator to wrap tool calls
# ------------------------------
def wrap_tool_call(handler):
    """Wrap a tool call to catch exceptions and return a friendly error."""
    @wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            return {"error": f"Tool error: {str(e)}"}
    return wrapper


# ------------------------------
# Define Deep Dive Tool
# ------------------------------
@tool
@wrap_tool_call
def deep_dive_tool(company_json: str, criteria: str, attributes: str) -> Dict:
    """
    A tool that takes a JSON-serialized company, criteria, and attributes,
    and returns enriched company info.
    """
    try:
        company = json.loads(company_json)
    except Exception:
        company = {"raw_input": company_json}

    attrs = [a.strip() for a in attributes.split(",") if a.strip()]

    # Simulated enrichment (replace with real API / LLM calls)
    enriched = company.copy() if isinstance(company, dict) else {}
    enriched.update({
        "Deep Dive Year Founded": "2021 (LLM)",
        "Deep Dive Funding": "$10M (LLM)",
        "Founders": "Alice & Bob (LLM)",
        "Notes": f"Deep dive based on criteria: {criteria}"
    })

    for attr in attrs:
        if attr not in enriched:
            enriched[attr] = "N/A"
    return enriched


# ------------------------------
# Initialize the LLM (if available)
# ------------------------------
llm = None
if _LANGCHAIN_AVAILABLE and ChatOpenAI is not None:
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0.2)
    except Exception:
        llm = None


# ------------------------------
# Create prompt template and agent executor (if LangChain available)
# ------------------------------
prompt = None
deep_dive_agent_executor = None
if _LANGCHAIN_AVAILABLE and ChatPromptTemplate is not None:
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an investment deep-dive analyst. "
                       "When given a company (in JSON), criteria, and attributes, "
                       "you should call the deep_dive_tool to enrich the company data."),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        if create_openai_tools_agent is not None and AgentExecutor is not None and llm is not None:
            try:
                agent = create_openai_tools_agent(llm, [deep_dive_tool], prompt)
                deep_dive_agent_executor = AgentExecutor(agent=agent, tools=[deep_dive_tool], verbose=True)
            except Exception:
                deep_dive_agent_executor = None
    except Exception:
        prompt = None
        deep_dive_agent_executor = None


# ------------------------------
# Wrapper function for a single company
# ------------------------------
def _process_single_company(company: Dict, criteria: str, attributes: List[str]) -> Dict:
    comp_json = json.dumps(company)
    attrs_str = ", ".join(attributes)

    user_input = f"Company: {comp_json}\nCriteria: {criteria}\nAttributes: {attrs_str}"

    try:
        if deep_dive_agent_executor is not None:
            result = deep_dive_agent_executor.invoke({"input": user_input})
            # result may be a dict or object depending on langchain; attempt extraction
            if isinstance(result, dict) and "output" in result:
                output_text = result["output"]
            else:
                output_text = str(result)
        else:
            # Fallback: call the tool function directly
            tool_result = deep_dive_tool(comp_json, criteria, attrs_str)
            if isinstance(tool_result, dict):
                # If tool returned enriched dict, use it
                output_text = json.dumps(tool_result)
            else:
                output_text = str(tool_result)

        # Extract JSON if present
        if "{" in output_text and "}" in output_text:
            start = output_text.find("{")
            end = output_text.rfind("}") + 1
            try:
                enriched_company = json.loads(output_text[start:end])
            except Exception:
                enriched_company = company
                enriched_company["agent_note"] = output_text
        else:
            enriched_company = company
            enriched_company["agent_note"] = output_text

    except Exception as e:
        print(f"Agent failed: {e}")
        enriched_company = company  # fallback if anything fails

    return enriched_company


# ------------------------------
# Main deep dive function (parallel)
# ------------------------------
def deep_dive_parallel(companies: List[Dict], criteria: str, attributes: List[str], max_workers: int = 5) -> List[Dict]:
    """
    Runs the deep-dive agent in parallel for all companies using threads.
    Returns a list of enriched company dicts.
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_company = {
            executor.submit(_process_single_company, comp, criteria, attributes): comp for comp in companies
        }

        for future in as_completed(future_to_company):
            try:
                enriched = future.result()
                results.append(enriched)
            except Exception as e:
                company = future_to_company[future]
                results.append({
                    "Company Name": company.get("Company Name", "N/A"),
                    "error": f"Deep dive failed: {str(e)}"
                })

    return results


# Expose public symbols
__all__ = ["deep_dive_parallel", "deep_dive_tool"]


# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    sample_companies = [
        {"Company Name": "Startup A", "Website": "https://a.com"},
        {"Company Name": "Startup B", "Website": "https://b.com"},
        {"Company Name": "Startup C", "Website": "https://c.com"},
    ]

    enriched = deep_dive_parallel(
        sample_companies,
        criteria="AI infrastructure",
        attributes=["Founders", "Year Founded"]
    )
    print(enriched)
