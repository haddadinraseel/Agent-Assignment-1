# backend/main.py
import os
import asyncio
from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

# Load .env variables
load_dotenv()

# Azure OpenAI config (minimal)
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")

try:
    import openai
except ImportError:
    openai = None

app = FastAPI(title="Investment Sourcing Agent - Backend")

# Allow Streamlit frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Request model
# -------------------------
class EnhanceRequest(BaseModel):
    user_query: str

# -------------------------
# Endpoint
# -------------------------
@app.post("/enhance_query")
async def enhance_query(payload: EnhanceRequest) -> Dict[str, str]:
    text = payload.user_query or ""

    # Only call Azure if key, endpoint, and deployment are present
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

        except Exception as e:
            # fallback if Azure call fails
            refined = _simple_enhance(text)
            return {"refined_query": refined}

    # fallback if Azure not configured
    refined = _simple_enhance(text)
    return {"refined_query": refined}

# -------------------------
# Simple fallback enhancer
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
# SSE AGENT STREAMING GENERATOR
# -------------------------
# This function sends progress updates over time
async def run_agent_and_stream(criteria: str, attributes: list[str], email: str):
    
    # 1. Start setup
    yield "event: status\ndata: Setting up agent environment...\n\n"
    await asyncio.sleep(1) # Wait 1 second (simulating work)
    
    # 2. Discovery Phase
    yield "event: status\ndata: 🔍 Running Discovery Agent with criteria...\n\n"
    await asyncio.sleep(3) # Wait 3 seconds
    
    yield "event: status\ndata: ✅ Found **5** potential startups for deep dive.\n\n"
    await asyncio.sleep(1) 

    # 3. Deep Dive Phase
    yield "event: status\ndata: ⚙️ Analyzing startup 1 of 5 (Deep Dive Agent)...\n\n"
    await asyncio.sleep(2) 
    yield "event: status\ndata: ⚙️ Analyzing startup 2 of 5 (Deep Dive Agent)...\n\n"
    await asyncio.sleep(2) 
    
    # 4. Reporting Phase
    yield "event: status\ndata: 📧 Generating final report and preparing email for delivery...\n\n"
    await asyncio.sleep(3)
    
    yield "event: status\ndata: 📬 Report successfully generated and sent to your email!\n\n"
    
    # 5. Completion signal (this tells the frontend to stop listening)
    yield "event: complete\ndata: {\"success\": true}\n\n"


# -------------------------
# SSE AGENT STREAMING ENDPOINT
# -------------------------
class ScoutRequest(BaseModel):
    search_criteria: str
    attributes: list[str]
    email: str

@app.post("/run_scout")
async def run_scout(payload: ScoutRequest):
    """Starts the scouting process and streams real-time updates."""
    
    # The generator function returns the stream of messages
    return StreamingResponse(
        run_agent_and_stream(
            criteria=payload.search_criteria,
            attributes=payload.attributes,
            email=payload.email
        ),
        media_type="text/event-stream" # THIS IS THE CRITICAL SSE HEADER
    )