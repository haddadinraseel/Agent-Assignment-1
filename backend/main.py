"""Minimal backend/main.py - compact, conflict-free.

Keeps only essential endpoints: /linkup_search and /run_scout (SSE).
"""

import asyncio
import sys
import os
from typing import Dict, List

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# optional sendgrid imports
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except Exception:
    SendGridAPIClient = None
    Mail = None

# allow importing my_agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from my_agents.discovery_agent import find_companies
from my_agents.deep_dive_agent import run_concurrent_deep_dive

load_dotenv()
SENDGRID_KEY = os.getenv('SENDGRID_API_KEY')
REPORT_FROM_EMAIL = os.getenv('REPORT_FROM_EMAIL')
LINKUP_API_KEY = os.getenv('LINKUP_API_KEY')

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


class LinkupSearchRequest(BaseModel):
    search_criteria: str
    location: str | None = None
    funding_stage: str | None = None


@app.post('/linkup_search')
async def linkup_search(payload: LinkupSearchRequest) -> Dict:
    if not LINKUP_API_KEY:
        return {'success': False, 'error': 'LINKUP_API_KEY not configured', 'results': []}
    try:
        url = 'https://api.linkup.so/v2/job_search'
        query = payload.search_criteria
        if payload.location:
            query += f' location:{payload.location}'
        if payload.funding_stage:
            query += f' funding_stage:{payload.funding_stage}'
        resp = requests.post(url, json={'query': query, 'limit': 20}, headers={'Authorization': f'Bearer {LINKUP_API_KEY}'}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('jobs', data.get('results', []))
            return {'success': True, 'results': jobs if isinstance(jobs, list) else []}
        return {'success': False, 'error': f'Linkup status {resp.status_code}', 'results': []}
    except Exception as e:
        return {'success': False, 'error': str(e), 'results': []}


class ScoutRequest(BaseModel):
    search_criteria: str
    attributes: List[str]
    email: str


def _safe_send_email(to_email: str, subject: str, html: str):
    if not SENDGRID_KEY or SendGridAPIClient is None:
        return None, 'SendGrid not configured'
    try:
        msg = Mail(from_email=REPORT_FROM_EMAIL, to_emails=to_email, subject=subject, html_content=html)
        sg = SendGridAPIClient(SENDGRID_KEY)
        resp = sg.send(msg)
        return resp.status_code, getattr(resp, 'body', '')
    except Exception as e:
        return None, str(e)


async def run_agent_and_stream(criteria: str, attributes: List[str], email: str):
    yield 'event: status\ndata: starting\n\n'
    await asyncio.sleep(0.1)
    try:
        results = find_companies(criteria=criteria)
    except Exception:
        results = []
    yield f'event: status\ndata: found {len(results)} companies\n\n'
    if results:
        try:
            results = await run_concurrent_deep_dive(results, criteria, attributes)
        except Exception:
            pass
    # minimal email payload
    html = f'<h3>Report — {len(results)} companies</h3>'
    status, body = _safe_send_email(email, 'Scout Report', html)
    if status:
        yield f'event: status\ndata: email sent ({status})\n\n'
    else:
        yield f'event: status\ndata: email failed: {body}\n\n'
    yield 'event: complete\ndata: {"success": true}\n\n'


@app.post('/run_scout')
async def run_scout(payload: ScoutRequest):
    return StreamingResponse(run_agent_and_stream(payload.search_criteria, payload.attributes, payload.email), media_type='text/event-stream')
