"""
Test script to run agents directly with logging
"""
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

from my_agents.final_agents import run_pipeline

print('='*60)
print('Testing run_pipeline tool')
print('='*60)

# run_pipeline is a @tool, so we call .invoke()
results = run_pipeline.invoke({
    'investment_thesis': 'AI startups in MENA region', 
    'attributes': ['name', 'url', 'description', 'founding_year']
})

print(f'\nResults ({len(results)} companies):')
for i, company in enumerate(results, 1):
    print(f'\n{i}. {company.get("name", "Unknown")}')
    for k, v in company.items():
        if k != 'name':
            print(f'   - {k}: {v}')
