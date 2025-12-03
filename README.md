Investment Sourcing Agent

Arab Bank Ventures — AI-powered startup discovery and analysis chatbot

An intelligent conversational investment sourcing tool that helps venture capital teams discover, analyze, and evaluate potential startup investments across global markets using AI agents.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51-red.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-Agents-orange.svg)

---

## Features

- 💬 **Conversational Interface** — Natural language chat for all startup scouting queries
- 🔍 **Discovery Agent** — Finds real startups matching your investment thesis using Linkup web search
- 📊 **Deep Dive Agent** — Researches detailed company information (funding, ARR, sector, competitors)
- ✨ **AI Query Enhancement** — Improves and expands search queries inline using Azure OpenAI
- 🔄 **Pipeline Orchestration** — Automated discovery → parallel deep dive research workflow
- 🎨 **Arab Bank Branding** — Custom UI with official brand colors (Curious Blue, Blue Ribbon, Persian Blue)
- 🔒 **Focused Conversations** — Agent redirects off-topic questions back to investment research

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    FastAPI      │────▶│   LangChain     │
│   Frontend      │ SSE │    Backend      │     │    Agents       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                               ┌─────────┴─────────┐
                                               │                   │
                                               ▼                   ▼
                                     ┌─────────────────┐  ┌─────────────────┐
                                     │  Linkup Search  │  │   Azure OpenAI  │
                                     │      API        │  │       GPT       │
                                     └─────────────────┘  └─────────────────┘
```

### Components

| Component | Technology | Description |
|-----------|------------|-------------|
| Frontend | Streamlit | Conversational chat UI with Arab Bank branding |
| Backend | FastAPI | REST API with SSE streaming |
| Agents | LangChain/LangGraph | Conversational, Discovery & Deep Dive AI agents |
| LLM | Azure OpenAI | GPT model for reasoning and tool selection |
| Search | Linkup API | Real-time web search for startups |

---

## Project Structure

```
Agent-Assignment-1/
├── backend/
│   ├── main2.py              # FastAPI server with SSE streaming
│   ├── services/             # Business logic services
│   └── utils/                # Utility functions
├── frontend/
│   ├── streamlit_app.py      # Streamlit chat UI (main UI)
│   └── assets/               # Images, logos
├── my_agents/
│   ├── conversational_agent.py  # Main chat agent with tool selection
│   ├── final_agents.py       # Discovery & Deep Dive agents
│   └── linkup_tools.py       # Linkup search tool wrapper
├── scripts/
│   └── run_local.ps1         # Local dev startup script
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables (not in repo)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Azure OpenAI account with GPT deployment
- Linkup API key

### 1. Clone & Setup

```bash
git clone https://github.com/haddadinraseel/Agent-Assignment-1.git
cd Agent-Assignment-1

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# Azure OpenAI
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt_deployment

# Linkup Search API
LINKUP_API_KEY=your_linkup_api_key
```

### 3. Run the Application

**Terminal 1 — Start Backend:**
```bash
cd backend
uvicorn main2:app --reload --port 8000
```

**Terminal 2 — Start Frontend:**
```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

Open your browser at `http://localhost:8501`

---

## Usage

1. **Start a Conversation** — Type your investment query in natural language
   - Example: *"Find AI startups in healthcare based in Germany at Series A stage"*
   - Example: *"Search for fintech companies in London with over $1M ARR"*

2. **AI Query Enhancement** — Click "Enhance" to expand and optimize your search query

3. **Automatic Research** — The agent will:
   - Use Discovery Agent to find matching startups
   - Run Deep Dive Agent in parallel to research each company
   - Return detailed company information

4. **Follow-up Questions** — Ask about specific companies or request more details
   - Example: *"Tell me more about company X"*
   - Example: *"Who are the competitors of this startup?"*

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main conversational endpoint (SSE streaming) |
| `/run_scout` | POST | Run discovery + deep dive pipeline (SSE) |
| `/enhance_query` | POST | AI-enhance an investment thesis |
| `/linkup_search` | POST | Direct Linkup web search |
| `/health` | GET | Health check |

### Example Chat Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find AI startups in healthcare in Germany",
    "history": []
  }'
```

---

## AI Agents

### Conversational Agent
The main chat interface that understands user intent and selects the appropriate tools.

**Capabilities:**
- Natural language understanding for investment queries
- Intelligent tool selection (search, pipeline, deep dive)
- Redirects off-topic questions back to investment research
- Maintains conversation context

**Tools Available:**
- `linkup_search_tool` — Quick web search for specific queries
- `run_pipeline` — Full discovery + deep dive workflow
- `deep_research_company` — Detailed research on a single company
- `research_competitors` — Find and analyze competitors

### Discovery Agent
Finds real startup companies matching an investment thesis using Linkup web search.

**Output:** List of companies with name, URL, and country

### Deep Dive Agent
Researches detailed information for each discovered company in parallel.

**Output:** Expanded company details including:
- Description and founding year
- Funding stage and ARR (Annual Recurring Revenue)
- Market sector and business model
- Key competitors

---

## Tech Stack

- **Frontend:** Streamlit 1.51 with native `st.chat_message` components
- **Backend:** FastAPI 0.121, Uvicorn with SSE streaming
- **AI Framework:** LangChain, LangGraph (`create_react_agent`)
- **LLM:** Azure OpenAI GPT
- **Search:** Linkup API for real-time web search
- **Data:** Pandas, Pydantic
- **Styling:** Custom CSS with Arab Bank brand colors

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_KEY` | ✅ | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | ✅ | GPT model deployment name |
| `LINKUP_API_KEY` | ✅ | Linkup search API key |
| `OPENAI_API_VERSION` | ❌ | API version (default: 2025-03-01-preview) |

---

## UI Features

### Arab Bank Branding
Custom color palette applied throughout the interface:
- **Blue Ribbon** (#0671FF) — Primary accent color
- **Curious Blue** (#1680E4) — Secondary blue
- **Persian Blue** (#2B1CA9) — Dark accent
- **Oslo Gray** (#939598) — Neutral text
- **Emperor** (#555354) — Dark text

### Chat Interface
- Native Streamlit chat messages for proper rendering
- User avatar (👤) and assistant avatar distinction
- Input clears automatically after sending
- "Enhance" button updates query inline

---

## Troubleshooting

**Backend won't start:**
- Check `.env` file exists with all required variables
- Verify Azure OpenAI credentials are valid

**No results returned:**
- Ensure Linkup API key is valid
- Try a broader search query

**Frontend connection error:**
- Verify backend is running on port 8000
- Check CORS settings in `main2.py`

**Azure Content Filter Error:**
- If you see "jailbreak" or content filter errors, soften the agent prompts
- Avoid aggressive language like "NEVER", "CRITICAL", "ALWAYS" in system prompts

**Rate Limiting (429 Error):**
- Reduce parallel requests or add delays between API calls
- Check Azure OpenAI quota limits

---

