# backend/main2.py — Startup Finder / Scout backend with LangChain agents, AI query enhancement, SSE
import asyncio
import sys
import os
import json
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# optional Azure OpenAI
try:
    from openai import AzureOpenAI
except Exception:
    AzureOpenAI = None

# make agents importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# -------------------------
# Import the agents
# -------------------------
from my_agents.discovery_agent import find_companies as discovery_search
from my_agents.deep_dive_agent import deep_dive_parallel as run_concurrent_deep_dive

# -------------------------
# Load environment
# -------------------------
load_dotenv("./.env")
LINKUP_API_KEY = os.getenv('LINKUP_API_KEY')
AZURE_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_GPT_ENDPOINT')
AZURE_DEPLOYMENT = os.getenv('AZURE_OPENAI_GPT_DEPLOYMENT_NAME')

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Startup Finder / Scout Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

# -------------------------
# Request models
# -------------------------
class LinkupSearchRequest(BaseModel):
    search_criteria: str

class StartupFinderRequest(BaseModel):
    search_criteria: str
    attributes: List[str]
    email: str  # required for SSE but not actually used

class EnhanceRequest(BaseModel):
    user_query: str

# -------------------------
# Helper: simple AI enhancement fallback
# -------------------------
def _simple_enhance(text: str) -> str:
    # Basic grammar fix + short keywords enhancement
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
    # Only one sentence output
    return f"{text.strip()} with focus on {', '.join(list(keywords)[:6])}"

# -------------------------
# AI query enhancement endpoint (STRICT ONE SENTENCE)
# -------------------------
@app.post("/enhance_query")
async def enhance_query(payload: EnhanceRequest) -> Dict[str, str]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger(__name__)
    text = payload.user_query or ""
    logger.info(f"Enhance query request received: {text[:100]}")

    if AZURE_KEY and AZURE_ENDPOINT and AZURE_DEPLOYMENT and AzureOpenAI:
        try:
            client = AzureOpenAI(
                azure_endpoint=AZURE_ENDPOINT,
                api_key=AZURE_KEY,
                api_version="2024-02-01",
            )
            response = client.chat.completions.create(
                model=AZURE_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query enhancement assistant. "
                            "Output ONLY ONE CONCISE SENTENCE. "
                            "Fix grammar and spelling. "
                            "Clarify the user's input. "
                            "Do NOT add examples, lists, or explanations."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Enhance this query: {text}"
                    }
                ],
                max_tokens=50,
                temperature=0.0
            )
            refined = response.choices[0].message.content.strip()
            return {"refined_query": refined}
        except Exception as e:
            logger.warning(f"Azure OpenAI failed, using fallback: {e}")
            fallback = _simple_enhance(text)
            return {"refined_query": fallback}

    # fallback if Azure not configured
    fallback = _simple_enhance(text)
    return {"refined_query": fallback}

# -------------------------
# Linkup search endpoint 
# -------------------------
@app.post('/linkup_search')
async def linkup_search(payload: LinkupSearchRequest) -> Dict:
    if not LINKUP_API_KEY:
        return {'success': False, 'error': 'LINKUP_API_KEY not configured in environment', 'results': []}

    try:
        from linkup import LinkupClient
        client = LinkupClient(api_key="")
        response = client.search(
            query=payload.search_criteria,
            depth="standard",
            output_type="searchResults",
            include_images=False,
        )
        if isinstance(response, list):
            return {'success': True, 'results': response}
        if isinstance(response, dict):
            return {'success': True, 'results': response.get('results', [])}
        return {'success': True, 'results': []}

    except ImportError:
        return {'success': False, 'error': "linkup package not installed. Run: pip install linkup-sdk", 'results': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'results': []}

# -------------------------
# SSE runner for Startup Finder / Scout
# -------------------------
async def run_agent_and_stream(criteria: str, attributes: List[str], email: str):
    yield 'event: status\ndata: Starting Startup Finder...\n\n'
    await asyncio.sleep(0.1)

    # Discovery
    results = []
    try:
        raw_result = discovery_search(criteria)
        if isinstance(raw_result, list):
            results = raw_result
        elif isinstance(raw_result, dict):
            output_str = raw_result.get("output") or raw_result.get("result") or raw_result.get("text") or ""
            if output_str:
                try:
                    results = json.loads(output_str)
                except Exception:
                    results = []
        elif isinstance(raw_result, str):
            try:
                results = json.loads(raw_result)
            except Exception:
                results = []
    except Exception as e:
        print(f"Discovery agent failed: {str(e)}")
        results = []

    yield f'event: status\ndata: Found {len(results)} companies\n\n'

    # Deep dive (parallel)
    if results:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, run_concurrent_deep_dive, results, criteria, attributes)
        except Exception as e:
            print("Deep dive agent failed:", str(e))

    yield f'event: status\ndata: 🔹 Enriched results ready\n\n'

    final_payload = json.dumps({"success": True, "results": results})
    yield f'event: complete\ndata: {final_payload}\n\n'

# -------------------------
# Run Startup Finder (SSE)
# -------------------------
@app.post('/run_startup_finder')
async def run_startup_finder(payload: StartupFinderRequest):
    return StreamingResponse(
        run_agent_and_stream(payload.search_criteria, payload.attributes, payload.email),
        media_type='text/event-stream'
    )

# -------------------------
# Backwards-compatible alias
# -------------------------
@app.post('/run_scout')
async def run_scout(payload: StartupFinderRequest):
    return StreamingResponse(
        run_agent_and_stream(payload.search_criteria, payload.attributes, payload.email),
        media_type='text/event-stream'
    )

# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return {"message": "Startup Finder Backend — LangChain discovery & deep dive agents"}
