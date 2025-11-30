import os
import json
import asyncio
import traceback
from dotenv import load_dotenv

# Load .env from project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(ROOT, '.env'))

print('Loaded .env from', os.path.join(ROOT, '.env'))
print('LINKUP_API_KEY present:', bool(os.getenv('LINKUP_API_KEY')))
print('AZURE_OPENAI_KEY present:', bool(os.getenv('AZURE_OPENAI_KEY')))

# Import the agents and tools
try:
    import sys
    # Ensure project root is on sys.path so `my_agents` imports work
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from my_agents import final_agents_copy as fac
    from my_agents import linkup_tools
except Exception as e:
    print('Failed to import agents or tools:', e)
    traceback.print_exc()
    raise

async def run():
    thesis = 'AI startups in London'
    attributes = ['Website', 'Founders', 'Total Funding']

    print('\n--- Running discovery_agent.invoke(...) ---')
    try:
        # discovery_agent.invoke may accept a string or dict; try both
        res = None
        try:
            res = await asyncio.to_thread(fac.discovery_agent.invoke, thesis)
        except Exception as e:
            print('discovery_agent.invoke(thesis) failed:', e)
            res = await asyncio.to_thread(fac.discovery_agent.invoke, {'input': thesis})

        print('Discovery raw result type:', type(res))
        print('Discovery raw result repr:\n', res)

    except Exception as e:
        print('Discovery invocation failed:')
        traceback.print_exc()

    # If discovery returned text, try to parse
    candidate_output = None
    if isinstance(res, dict):
        candidate_output = res.get('output') or res.get('text')
        if not candidate_output and 'messages' in res:
            msgs = res['messages']
            if isinstance(msgs, list) and msgs:
                last = msgs[-1]
                candidate_output = getattr(last, 'content', None) or (last.get('content') if isinstance(last, dict) else None)
    elif isinstance(res, str):
        candidate_output = res

    print('\nParsed candidate_output:\n', candidate_output)

    # Try programmatic linkup_search
    print('\n--- Calling programmatic linkup_search(...) ---')
    try:
        req = linkup_tools.LinkupSearchRequest(query=thesis)
        linkup_resp = linkup_tools.linkup_search(req)
        print('LinkupSearchResponse type:', type(linkup_resp))
        print('LinkupSearchResponse success:', getattr(linkup_resp, 'success', None))
        print('LinkupSearchResponse error:', getattr(linkup_resp, 'error', None))
        print('LinkupSearchResponse raw keys:', list(getattr(linkup_resp, 'raw', {}).keys()) if getattr(linkup_resp, 'raw', None) else None)
        print('LinkupSearchResponse results sample:', (getattr(linkup_resp, 'results', None) or [])[:3])
    except Exception as e:
        print('Programmatic linkup_search failed:')
        traceback.print_exc()

    # If results, run one deep dive
    results = getattr(linkup_resp, 'results', None) or []
    if results:
        first = results[0]
        print('\n--- Running deep_dive_agent on first result ---')
        try:
            # Normalize to minimal startup dict expected by deep_dive_agent
            if isinstance(first, dict):
                startup = {'name': first.get('name') or first.get('title') or first.get('company') or first.get('url')}
            else:
                startup = {'name': str(first)}
            deep_res = await asyncio.to_thread(fac.deep_dive_agent.invoke, {'startup': startup, 'attributes': attributes})
            print('Deep dive raw result type:', type(deep_res))
            print('Deep dive raw result repr:\n', deep_res)
        except Exception as e:
            print('Deep dive invocation failed:')
            traceback.print_exc()
    else:
        print('\nNo results from Linkup search to deep-dive.')

if __name__ == '__main__':
    asyncio.run(run())
