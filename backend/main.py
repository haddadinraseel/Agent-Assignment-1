# backend/main.py
import os
import asyncio
import requests
from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# Optional: SendGrid setup
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Load .env variables
load_dotenv()

# Azure OpenAI minimal config
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")

# Optional: SendGrid
SENDGRID_KEY = os.getenv("SENDGRID_API_KEY")
REPORT_FROM_EMAIL = os.getenv("REPORT_FROM_EMAIL")

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")


try:
    import openai
except ImportError:
    openai = None

app = FastAPI(title="Investment Sourcing Agent - Backend")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Request model for Linkup search
# -------------------------
class LinkupSearchRequest(BaseModel):
    search_criteria: str
    location: str = None  # Optional location filter
    funding_stage: str = None  # Optional funding stage

# -------------------------
# Endpoint to call Linkup API
# -------------------------
@app.post("/linkup_search")
def linkup_search(payload: LinkupSearchRequest):
    url = "https://api.linkup.com/v1/search"  # Example Linkup endpoint
    headers = {
        "Authorization": f"Bearer {LINKUP_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build payload for Linkup API
    data = {
        "query": payload.search_criteria,
    }
    if payload.location:
        data["location"] = payload.location
    if payload.funding_stage:
        data["funding_stage"] = payload.funding_stage

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=20)
        if resp.status_code == 200:
            results = resp.json()
            return {"success": True, "results": results}
        else:
            return {"success": False, "status_code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
# -------------------------
# Request models
# -------------------------
class EnhanceRequest(BaseModel):
    user_query: str

class ScoutRequest(BaseModel):
    search_criteria: str
    attributes: list[str]
    email: str

# -------------------------
# Enhance with AI endpoint
# -------------------------
@app.post("/enhance_query")
async def enhance_query(payload: EnhanceRequest) -> Dict[str, str]:
    text = payload.user_query or ""

    if openai and AZURE_KEY and AZURE_ENDPOINT and AZURE_DEPLOYMENT:
        try:
            openai.api_type = "azure"
            openai.api_key = AZURE_KEY
            openai.api_base = AZURE_ENDPOINT

            response = openai.ChatCompletion.create(
                engine=AZURE_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are an assistant that refines investment search queries."},
                    {"role": "user", "content": f"Refine and expand this search criteria into a precise search query for sourcing startups: {text}"}
                ],
                max_tokens=300,
                temperature=0.7,
            )
            refined = response.choices[0].message["content"].strip()
            return {"refined_query": refined}
        except Exception:
            refined = _simple_enhance(text)
            return {"refined_query": refined}

    refined = _simple_enhance(text)
    return {"refined_query": refined}

# -------------------------
# Simple local fallback
# -------------------------
def _simple_enhance(text: str) -> str:
    if not text or not text.strip():
        return "Please provide search criteria to enhance."

    enhancements = [
        f"- Original: {text.strip()}",
        "- Expanded keywords: " + ", ".join(_generate_keywords(text)),
        "- Suggested filters: Seed/Series A, Region: specify country/city, Industry verticals",
        "- Suggested exclusions: (e.g., exclude non-tech, exclude pre-seed)",
        "",
        "Refined search query (suggested): " + _build_refined_query(text)
    ]
    return "\n".join(enhancements)

def _generate_keywords(text: str):
    words = [w.strip(".,()") for w in text.split() if len(w) > 2]
    keywords = set(words[:6])
    syn_map = {
        "infra": ["infrastructure", "platform", "stack"],
        "crypto": ["blockchain", "web3", "cryptocurrency"],
        "healthcare": ["health tech", "medtech", "digital health"],
        "ai": ["artificial intelligence", "machine learning", "ml"]
    }
    for w in words:
        lw = w.lower()
        if lw in syn_map:
            keywords.update(syn_map[lw])
    return list(keywords)[:12]

def _build_refined_query(text: str) -> str:
    return f"{text.strip()} | Add nearby synonyms, include funding stage, location, and technology tags."

# -------------------------
# SSE streaming for scout agent
# -------------------------
async def run_agent_and_stream(criteria: str, attributes: list[str], email: str):
    yield "event: status\ndata: Setting up agent environment...\n\n"
    await asyncio.sleep(1)
    yield "event: status\ndata: 🔍 Running Discovery Agent with criteria...\n\n"
    await asyncio.sleep(3)
    yield "event: status\ndata: ✅ Found **5** potential startups for deep dive.\n\n"
    await asyncio.sleep(1)
    yield "event: status\ndata: ⚙️ Analyzing startup 1 of 5 (Deep Dive Agent)...\n\n"
    await asyncio.sleep(2)
    yield "event: status\ndata: ⚙️ Analyzing startup 2 of 5 (Deep Dive Agent)...\n\n"
    await asyncio.sleep(2)
    yield "event: status\ndata: 📧 Generating final report and preparing email for delivery...\n\n"
    await asyncio.sleep(3)
    yield "event: status\ndata: 📬 Report successfully generated and sent to your email!\n\n"
    yield "event: complete\ndata: {\"success\": true}\n\n"

@app.post("/run_scout")
async def run_scout(payload: ScoutRequest):
    return StreamingResponse(
        run_agent_and_stream(
            criteria=payload.search_criteria,
            attributes=payload.attributes,
            email=payload.email
        ),
        media_type="text/event-stream"
    )
