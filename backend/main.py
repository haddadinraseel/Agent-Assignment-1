"""Backend main module for Investment Sourcing Agent.

Provides:
- /linkup_search: proxy to Linkup API
- /enhance_query: simple query enhancer (fallback)
- /run_scout: SSE endpoint that runs discovery + deep dive + email
"""

import asyncio
import sys
import os
from typing import Dict, List

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except Exception:
    SendGridAPIClient = None
    Mail = None

# make my_agents importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from my_agents.discovery_agent import find_companies
from my_agents.deep_dive_agent import run_concurrent_deep_dive

load_dotenv()

SENDGRID_KEY = os.getenv("SENDGRID_API_KEY")
REPORT_FROM_EMAIL = os.getenv("REPORT_FROM_EMAIL")
LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")

app = FastAPI(title="Investment Sourcing Agent - Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:8502"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# helpers
def build_email_content(criteria: str, attributes: List[str], results: List[Dict]) -> str:
    html = f"<h2>Investment Scout Report</h2>"
    html += f"<p><strong>Search Criteria:</strong> {criteria}</p>"
    html += "<table border='1' cellpadding='5' cellspacing='0'>"
    html += "<tr>" + "".join([f"<th>{attr}</th>" for attr in attributes]) + "</tr>"
    for r in results:
        html += "<tr>" + "".join([f"<td>{r.get(attr, '-')}</td>" for attr in attributes]) + "</tr>"
    html += "</table>"
    return html


def send_email_report(to_email: str, subject: str, html_content: str):
    if not SENDGRID_KEY or not REPORT_FROM_EMAIL or SendGridAPIClient is None:
        return None, "SendGrid not configured or client not installed"
    message = Mail(from_email=REPORT_FROM_EMAIL, to_emails=to_email, subject=subject, html_content=html_content)
    try:
        sg = SendGridAPIClient(SENDGRID_KEY)
        response = sg.send(message)
        return response.status_code, getattr(response, 'body', '')
    except Exception as e:
        return None, str(e)


# simple enhancer
def _generate_keywords(text: str):
    words = [w.strip('.,()') for w in text.split() if len(w) > 2]
    return list(dict.fromkeys(words))[:12]


def _simple_enhance(text: str) -> str:
    if not text:
        return ""
    return text + " | expanded"


class EnhanceRequest(BaseModel):
    user_query: str


@app.post('/enhance_query')
async def enhance_query(payload: EnhanceRequest) -> Dict[str, str]:
    return {"refined_query": _simple_enhance(payload.user_query)}


class LinkupSearchRequest(BaseModel):
    search_criteria: str
    location: str | None = None
    funding_stage: str | None = None


@app.post('/linkup_search')
async def linkup_search(payload: LinkupSearchRequest) -> Dict:
    if not LINKUP_API_KEY:
        return {"success": False, "error": "LINKUP_API_KEY not configured", "results": []}
    try:
        linkup_url = 'https://api.linkup.so/v2/job_search'
        headers = {"Authorization": f"Bearer {LINKUP_API_KEY}", "Content-Type": "application/json"}
        query = payload.search_criteria
        if payload.location:
            query += f" location:{payload.location}"
        if payload.funding_stage:
            query += f" funding_stage:{payload.funding_stage}"
        resp = requests.post(linkup_url, json={"query": query, "limit": 20}, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('jobs', data.get('results', []))
            return {"success": True, "results": jobs if isinstance(jobs, list) else []}
        return {"success": False, "error": f"Linkup status {resp.status_code}" , "results": []}
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}


async def run_agent_and_stream(criteria: str, attributes: List[str], email: str):
    yield "event: status\ndata: Starting scout...\n\n"
    await asyncio.sleep(0.2)
    try:
        results = find_companies(criteria=criteria)
    except Exception:
        results = []
    yield f"event: status\ndata: Found {len(results)} companies\n\n"
    if results:
        try:
            enriched = await run_concurrent_deep_dive(results, criteria, attributes)
            results = enriched
        except Exception:
            pass
    yield "event: status\ndata: Preparing email...\n\n"
    email_html = build_email_content(criteria, attributes, results)
    status_code, body = send_email_report(email, 'Investment Scout Report', email_html)
    if status_code:
        yield f"event: status\ndata: Email sent ({status_code})\n\n"
    else:
        yield f"event: status\ndata: Email failed: {body}\n\n"
    yield "event: complete\ndata: {\"success\": true}\n\n"


class ScoutRequest(BaseModel):
    search_criteria: str
    attributes: List[str]
    email: str


@app.post('/run_scout')
async def run_scout(payload: ScoutRequest):
    return StreamingResponse(run_agent_and_stream(payload.search_criteria, payload.attributes, payload.email), media_type='text/event-stream')
