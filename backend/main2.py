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


try:
    from openai import AzureOpenAI
except Exception:
    AzureOpenAI = None

# make agents importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Load environment early so agent modules can read env vars during import
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# -------------------------
# Import the agents
# -------------------------
load_dotenv("./.env")
from my_agents import final_agents 
from my_agents.conversational_agent import conversational_agent
LINKUP_API_KEY = os.getenv('LINKUP_API_KEY')
AZURE_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_GPT_ENDPOINT')
# Prefer the generic deployment name if present, otherwise fall back to the GPT-specific var
AZURE_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

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
    location: str = ""  # Optional location filter
    funding_stage: str = ""  # Optional funding stage filter
    attributes: List[str]
    email: str  # required for SSE but not actually used

class EnhanceRequest(BaseModel):
    user_query: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[dict] = []

# -------------------------
# Helper: simple AI enhancement fallback
# -------------------------
def _simple_enhance(text: str) -> str:
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
        # linkup-sdk 0.9.0 exports from linkup._client
        try:
            from linkup._client import LinkupClient
        except ImportError:
            from linkup import LinkupClient
        client = LinkupClient(api_key=LINKUP_API_KEY)
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
async def run_agent_and_stream(criteria: str, location: str, funding_stage: str, attributes: List[str], email: str):
    """
    Main pipeline:
    1. Build investment thesis from user input
    2. Call Discovery Agent (Linkup structured search)
    3. Call Deep Dive Agent (Linkup fetch + LLM enrichment)
    4. Return results (NO post-filtering - filtering is done by Linkup based on the thesis)
    """
    yield 'event: status\ndata: 🚀 Starting Startup Scout...\n\n'
    await asyncio.sleep(0.1)

    # Build the investment thesis from user input
    # The thesis is the ONLY filter - Linkup will search for companies matching it
    investment_thesis = criteria
    if location:
        investment_thesis += f" in {location}"
    if funding_stage and funding_stage.lower() != "any":
        investment_thesis += f", {funding_stage} stage"
    
    print(f"\n{'='*60}")
    print(f"📋 Investment Thesis: {investment_thesis}")
    print(f"📊 Attributes to extract: {attributes}")
    print(f"{'='*60}\n")

    yield f'event: status\ndata: 🔍 Searching for: {investment_thesis}\n\n'

    # Use consolidated pipeline from my_agents.final_agents
    results = []
    try:
        yield f'event: status\ndata: 🔍 Running consolidated pipeline...\n\n'
        results = await final_agents.run_pipeline(investment_thesis, attributes)
        if not isinstance(results, list):
            # Ensure results is a list
            results = results if results is not None else []
            if isinstance(results, dict):
                results = [results]
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        results = []

    print(f"✅ Pipeline returned {len(results)} companies")
    yield f'event: status\ndata: 📦 Found {len(results)} companies\n\n'

    # Clean up None values
    cleaned_results = []
    for c in results:
        cleaned = {k: (v if v is not None else "N/A") for k, v in c.items()}
        cleaned_results.append(cleaned)
    results = cleaned_results

    print(f"✅ Final results: {len(results)} companies")
    yield f'event: status\ndata: ✅ Complete! Found {len(results)} companies\n\n'

    final_payload = json.dumps({"success": True, "results": results})
    yield f'event: complete\ndata: {final_payload}\n\n'

# -------------------------
# Run Startup Finder (SSE)
# -------------------------

@app.post('/run_scout')
async def run_scout(payload: StartupFinderRequest):
    """Compatibility route: some frontends post to /run_scout — forward to the same SSE pipeline."""
    return StreamingResponse(
        run_agent_and_stream(payload.search_criteria, payload.location, payload.funding_stage, payload.attributes, payload.email),
        media_type='text/event-stream'
    )


# -------------------------
# Chat endpoint (Conversational Agent) - SSE Streaming
# -------------------------
async def chat_stream_generator(message: str, conversation_history: List[dict]):
    """
    SSE generator for chat endpoint with status updates.
    """
    import time
    
    try:
        yield 'event: status\ndata: 🤖 Processing your request...\n\n'
        await asyncio.sleep(0.1)
        
        # Build messages list with history
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append({"role": "user", "content": msg.get("content", "")})
            elif msg.get("role") == "assistant":
                messages.append({"role": "assistant", "content": msg.get("content", "")})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        yield 'event: status\ndata: 🔍 Analyzing query and selecting tools...\n\n'
        await asyncio.sleep(0.1)
        
        # Invoke agent with full conversation history
        result = conversational_agent.invoke({"messages": messages})
        
        # Extract the final response from messages
        response_messages = result.get("messages", [])
        
        # Check if any tools were used and report
        tool_used = None
        for msg in response_messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_used = msg.tool_calls[0].get('name') if isinstance(msg.tool_calls[0], dict) else msg.tool_calls[0].name
                yield f'event: status\ndata: 🛠️ Using tool: {tool_used}...\n\n'
                await asyncio.sleep(0.1)
                break
        
        if response_messages:
            last_message = response_messages[-1]
            # Get content from the last message
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        else:
            response_text = "No response generated."
        
        yield 'event: status\ndata: ✅ Response ready!\n\n'
        await asyncio.sleep(0.1)
        
        # Send final response
        final_payload = json.dumps({
            "success": True,
            "response": response_text,
            "tool_used": tool_used
        })
        yield f'event: complete\ndata: {final_payload}\n\n'
        
    except Exception as e:
        error_payload = json.dumps({
            "success": False,
            "response": f"Error: {str(e)}",
            "tool_used": None
        })
        yield f'event: error\ndata: {error_payload}\n\n'


@app.post('/chat')
async def chat(payload: ChatRequest):
    """
    Conversational endpoint with SSE streaming.
    Agent decides which tool to use.
    Supports conversation history for context.
    """
    return StreamingResponse(
        chat_stream_generator(payload.message, payload.conversation_history),
        media_type='text/event-stream'
    )


# -------------------------
# Non-streaming chat endpoint (for compatibility)
# -------------------------
@app.post('/chat_sync')
async def chat_sync(payload: ChatRequest):
    """
    Non-streaming conversational endpoint - returns JSON directly.
    """
    try:
        # Build messages list with history
        messages = []
        
        # Add conversation history
        for msg in payload.conversation_history:
            if msg.get("role") == "user":
                messages.append({"role": "user", "content": msg.get("content", "")})
            elif msg.get("role") == "assistant":
                messages.append({"role": "assistant", "content": msg.get("content", "")})
        
        # Add current message
        messages.append({"role": "user", "content": payload.message})
        
        # Invoke agent with full conversation history
        result = conversational_agent.invoke({"messages": messages})
        
        # Extract the final response from messages
        response_messages = result.get("messages", [])
        if response_messages:
            last_message = response_messages[-1]
            # Get content from the last message
            if hasattr(last_message, 'content'):
                response_text = last_message.content
            else:
                response_text = str(last_message)
        else:
            response_text = "No response generated."
        
        # Check if any tools were used
        tool_used = None
        for msg in response_messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_used = msg.tool_calls[0].get('name') if isinstance(msg.tool_calls[0], dict) else msg.tool_calls[0].name
                break
        
        return {
            "success": True,
            "response": response_text,
            "tool_used": tool_used
        }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "tool_used": None
        }


# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return {"message": "Startup Finder Backend — LangChain discovery & deep dive agents"}