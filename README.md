Investment Sourcing Agent

Arab Bank Ventures — AI-powered startup discovery and analysis platform

An intelligent investment sourcing tool that helps venture capital teams discover, analyze, and evaluate potential startup investments across global markets using AI agents.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51-red.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-Agents-orange.svg)

---

## Features

- Discovery Agent — Finds real startups matching your investment thesis using web search
- Deep Dive Agent — Researches detailed company information (funding, ARR, sector, etc.)
- AI Query Enhancement — Improves search queries using Azure OpenAI
- Multiple View Modes — Card view for exploration, table view for data analysis
- Export Results — Download as CSV or Excel for further analysis
- Modern UI — Glassmorphism design with Arab Bank branding

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    FastAPI      │────▶│   LangChain     │
│   Frontend      │ SSE │    Backend      │     │    Agents       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  Linkup Search  │
                                               │      API        │
                                               └─────────────────┘
```

### Components

| Component | Technology | Description |
|-----------|------------|-------------|
| Frontend | Streamlit | Interactive UI with glassmorphism styling |
| Backend | FastAPI | REST API with SSE streaming |
| Agents | LangChain | Discovery & Deep Dive AI agents |
| LLM | Azure OpenAI | GPT model for reasoning |
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
│   ├── frontend_copy.py      # Streamlit app (main UI)
│   └── assets/               # Images, logos
├── my_agents/
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
streamlit run frontend/frontend_copy.py --server.port 8502
```

Open your browser at `http://localhost:8502`

---

## Usage

1. **Define Investment Thesis** — Describe the type of startups you're looking for
   - Example: *"AI startups in healthcare based in Germany at Series A stage"*

2. **Refine Filters** — Optionally narrow by funding stage, ARR, company stage

3. **Configure Output** — Select which data points to research

4. **Launch Scout** — Click to start the AI agents

5. **Review Results** — Toggle between card view and table view

6. **Export** — Download results as CSV or Excel

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/run_scout` | POST | Run discovery + deep dive pipeline (SSE) |
| `/enhance_query` | POST | AI-enhance an investment thesis |
| `/health` | GET | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/run_scout \
  -H "Content-Type: application/json" \
  -d '{
    "search_criteria": "AI startups in London",
    "location": "",
    "funding_stage": "Series A",
    "attributes": [],
    "email": "user@example.com"
  }'
```

---

## AI Agents

### Discovery Agent
Finds real startup companies matching an investment thesis using Linkup web search.

**Output:** List of companies with name, URL, and country

### Deep Dive Agent
Researches detailed information for each discovered company.

**Output:** Expanded company details including:
- Description
- Founding year
- Funding stage
- ARR (Annual Recurring Revenue)
- Market sector

---

## Tech Stack

- **Frontend:** Streamlit 1.51
- **Backend:** FastAPI 0.121, Uvicorn
- **AI/ML:** LangChain, Azure OpenAI (GPT)
- **Search:** Linkup API
- **Data:** Pandas, Pydantic
- **Styling:** Custom CSS (Glassmorphism)

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

- Arab Bank Branding — Custom color palette (Curious Blue, Persian Blue)
- Card View — Expandable company cards with external links
- Table View — Sortable spreadsheet with expand option
- External Links — Quick access to LinkedIn, Crunchbase, News

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

---

## License

This project is proprietary to Arab Bank Ventures.

---
