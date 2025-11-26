"""API Diagnostics Script - Test each API independently to identify failures."""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from linkup import LinkupClient


# Load environment variables
load_dotenv('.env')

print("=" * 70)
print("API DIAGNOSTICS - Testing each component independently")
print("=" * 70)

# Test 1: Environment Variables
print("\n[1] CHECKING ENVIRONMENT VARIABLES")
print("-" * 70)

env_vars = {
    'LINKUP_API_KEY': os.getenv('LINKUP_API_KEY'),
    'AZURE_OPENAI_KEY': os.getenv('AZURE_OPENAI_KEY'),
    'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
    'AZURE_OPENAI_DEPLOYMENT_NAME': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
}

for key, value in env_vars.items():
    if value:
        masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
        print(f"✓ {key}: {masked}")
    else:
        print(f"✗ {key}: NOT SET")

# Test 2: Linkup API
print("\n[2] TESTING LINKUP API")
print("-" * 70)

linkup_key = os.getenv('LINKUP_API_KEY')
if linkup_key:
    # Try different endpoint paths
    endpoints_to_test = [
        '/v2/job_search',
        '/v1/job_search', 
        '/jobs/search',
        '/search',
        '/v2/search'
    ]
    
    for endpoint in endpoints_to_test:
        url = f"https://api.linkup.so{endpoint}"
        headers = {
            "Authorization": f"Bearer {linkup_key}",
            "Content-Type": "application/json"
        }
        payload = {"query": "AI startups", "limit": 5}
        
        try:
            print(f"\nTrying: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ SUCCESS! Found {len(data.get('jobs', data.get('results', [])))} results")
                print(f"Response keys: {list(data.keys())}")
                break
            else:
                print(f"✗ Failed: {response.text[:200]}")
        except Exception as e:
            print(f"✗ Exception: {str(e)[:200]}")
else:
    print("✗ LINKUP_API_KEY not set - skipping Linkup test")

# Test 3: Azure OpenAI
print("\n[3] TESTING AZURE OPENAI")
print("-" * 70)

az_key = os.getenv('AZURE_OPENAI_KEY')
az_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
az_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

if az_key and az_endpoint and az_deployment:
    try:
        from langchain_openai import AzureChatOpenAI
        
        print(f"Endpoint: {az_endpoint}")
        print(f"Deployment: {az_deployment}")
        
        llm = AzureChatOpenAI(
            azure_deployment=az_deployment,
            api_key=az_key,
            azure_endpoint=az_endpoint,
            api_version="2024-02-15-preview",
            temperature=0.2
        )
        
        # Simple test call
        print("\nSending test message...")
        response = llm.invoke("Say 'API test successful' if you can read this.")
        print(f"✓ SUCCESS! Response: {response.content[:100]}")
        
    except Exception as e:
        print(f"✗ Azure OpenAI Error: {str(e)}")
        print(f"Full traceback:")
        import traceback
        traceback.print_exc()
else:
    print("✗ Azure OpenAI credentials incomplete")
    if not az_key:
        print("  Missing: AZURE_OPENAI_KEY")
    if not az_endpoint:
        print("  Missing: AZURE_OPENAI_ENDPOINT")
    if not az_deployment:
        print("  Missing: AZURE_OPENAI_DEPLOYMENT_NAME")

# Test 4: Backend Endpoints (if running)
print("\n[4] TESTING BACKEND ENDPOINTS (if server is running)")
print("-" * 70)

backend_url = "http://127.0.0.1:8000"

# Test /linkup_search
try:
    print(f"\nTesting: {backend_url}/linkup_search")
    response = requests.post(
        f"{backend_url}/linkup_search",
        json={"query": "AI startups"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Response: {json.dumps(data, indent=2)[:300]}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except requests.exceptions.ConnectionError:
    print("✗ Backend not running at http://127.0.0.1:8000")
except Exception as e:
    print(f"✗ Exception: {str(e)[:200]}")

# Test discovery agent directly
print("\n[5] TESTING LINKUP SDK DIRECTLY")
print("-" * 70)

try:
    print("Importing LinkupClient...")
    from linkup import LinkupClient
    
    print("Creating client and searching...")
    client = LinkupClient(api_key=os.getenv('LINKUP_API_KEY'))
    result = client.search(
        query="AI startups in healthcare",
        depth="standard",
        output_type="searchResults",
        include_images=False
    )
    
    print(f"✓ Linkup SDK returned: {type(result)}")
    
    # LinkupSearchResults object has .results attribute
    if hasattr(result, 'results'):
        results = result.results
        print(f"✓ SUCCESS! Found {len(results)} results from Linkup SDK")
        if results:
            first = results[0]
            print(f"First result type: {type(first)}")
            if hasattr(first, 'name'):
                print(f"  Name: {first.name[:80]}")
            if hasattr(first, 'url'):
                print(f"  URL: {first.url[:80]}")
    elif isinstance(result, dict):
        print(f"Response keys: {result.keys()}")
        results = result.get('results', [])
        print(f"✓ Found {len(results)} results")
    elif isinstance(result, list):
        print(f"✓ Found {len(result)} results")
    else:
        print(f"Response: {str(result)[:200]}")
        
except Exception as e:
    print(f"✗ Discovery agent error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)
