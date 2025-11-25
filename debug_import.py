
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import my_agents.discovery_agent...")
    import my_agents.discovery_agent
    print("Module imported successfully.")
    
    print("Attributes in module:", dir(my_agents.discovery_agent))
    
    from my_agents.discovery_agent import search
    print("Successfully imported 'search'.")
except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
