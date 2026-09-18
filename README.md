🌱 EcoMind — AI Biodiversity Intelligence Advisor

«Evidence-grounded AI for understanding environmental conditions and generating actionable biodiversity interventions.»

EcoMind combines structured environmental knowledge, multi-metric ecological reasoning, retrieval-augmented generation (RAG), Llama-based synthesis, conversational memory, and curated evidence to turn environmental observations into practical, traceable recommendations.

It connects soil health, moisture, rainfall, land use, habitat quality, and biodiversity indicators to explain ecological interactions and identify interventions.

🚀 Links

- Live application: Coming soon
- API: Coming soon
- Repository: "https://github.com/<your-username>/<your-repository>"

🎯 Problem and Solution

Environmental decisions depend on interacting variables rather than isolated measurements:

Low soil organic carbon + low rainfall
        ↓
Reduced moisture retention
        ↓
Plant stress and lower habitat quality
        ↓
Reduced biodiversity support

Generic LLMs can also produce plausible but unsupported advice. EcoMind addresses both challenges through an evidence-grounded pipeline:

Environmental observation
        ↓
Input understanding
        ↓
Structured knowledge and multi-metric reasoning
        ↓
Scientific evidence retrieval
        ↓
Grounded Llama synthesis
        ↓
Actionable recommendation with metrics, timeline, confidence, and citations

✨ Features

Environmental analysis

Users describe environmental conditions in natural language. EcoMind extracts relevant context and identifies biodiversity risks.

Multi-metric reasoning

The system models relationships between:

Soil health ↔ water availability
Water availability ↔ species survival
Land use ↔ habitat quality and fragmentation
Climate ↔ soil moisture
Soil conditions ↔ vegetation ↔ pollinators

Evidence-grounded recommendations

A curated evidence layer supports recommendations with:

- Evidence ID
- Source title and organization
- Publication year
- URL
- Relevant excerpt

Recommendations are omitted when supporting evidence is unavailable. The synthesis layer is instructed not to invent sources, statistics, measurements, relationships, or unsupported benefits.

Structured outputs

Each recommendation can include:

Field| Description
Action| Recommended intervention
Why it works| Ecological reasoning
Impacted metrics| Environmental variables affected
Time horizon| Expected implementation horizon
Confidence| Confidence level
Citations| Supporting evidence

Conversational memory

Session-based conversations retain environmental context and apply follow-up constraints to updated assessments.

🏗️ Architecture

React frontend
    ↓
FastAPI validation and session handling
    ↓
Structured environmental knowledge
    ↓
Multi-metric ecological reasoning
    ↓
RAG with curated evidence and FAISS
    ↓
Llama synthesis
    ↓
Assessment, recommendations, metrics, confidence, and sources

EcoMind separates:

1. Environmental context interpretation
2. Structured knowledge
3. Evidence retrieval
4. Ecological reasoning
5. Natural-language synthesis

📚 Knowledge and RAG

data/
├── environmental_knowledge.json
└── documents/
    └── curated_evidence.json

- "environmental_knowledge.json": predefined environmental relationships.
- "curated_evidence.json": scientific sources used to ground recommendations.

🛠️ Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI, Pydantic, Uvicorn
- AI: Llama, RAG, FAISS, structured environmental knowledge
- Deployment: Vercel frontend, Render backend, hosted Llama inference

📂 Project Structure

ecomind/
├── backend/
│   ├── main.py
│   ├── service.py
│   ├── llama.py
│   ├── extractor.py
│   └── schemas.py
├── data/
│   ├── environmental_knowledge.json
│   └── documents/
│       └── curated_evidence.json
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt
├── .env.example
├── README.md
└── render.yaml

⚙️ Local Development

Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Git

Clone and install

git clone https://github.com/<your-username>/<your-repository>.git
cd ecomind

python -m venv .venv

Activate the environment on Windows:

.venv\Scripts\activate

Install backend dependencies:

pip install -r requirements.txt

Install frontend dependencies:

cd frontend
npm install
cd ..

Configure environment variables

Create ".env" from ".env.example":

LLAMA_BASE_URL=<llama-endpoint>
LLAMA_MODEL=<llama-model>
LLAMA_TIMEOUT_SECONDS=45
VITE_API_URL=<backend-url>

Configure provider credentials as required. Never commit secrets or API keys.

Run the application

Start the backend:

uvicorn backend.main:app --reload

API: "http://127.0.0.1:8000"

Start the frontend in another terminal:

cd frontend
npm run dev

📡 API

Health check

GET /api/health

Response:

{
  "status": "ok",
  "service": "ecomind-api"
}

Analyze an environmental situation

POST /api/analyze

Request:

{
  "query": "My orchard has low soil organic carbon, declining summer moisture and fewer pollinators.",
  "environmental_data": {},
  "session_id": "example-session-id"
}

The response includes an assessment, environmental interactions, recommendations, impacted metrics, time horizon, confidence, scientific sources, and LLM usage status.

🧪 Validation

Representative scenarios cover:

- Orchards: soil carbon, pH, rainfall, moisture, pollinators, and irrigation constraints
- Rivers: flow, riparian vegetation, runoff, erosion, aquatic biodiversity, and development constraints
- Conversational memory: follow-up constraints applied to prior environmental context

🎯 Design Principles

1. Evidence before generation
2. Reason across environmental variables
3. Avoid generic advice
4. Explain supported causal chains
5. Make recommendations traceable
6. Adapt interventions to real-world constraints

📈 Future Extensions

- Geospatial and GIS-based habitat analysis
- Live climate and weather data
- Satellite land-cover analysis
- Hydrological integration
- Species-specific indicators
- Environmental trend monitoring
- Automated evidence updates
- Ecosystem-specific knowledge graphs

🔐 Security

Supply environment-specific values through environment variables:

LLAMA_BASE_URL
LLAMA_MODEL
LLAMA_TIMEOUT_SECONDS
VITE_API_URL

Never commit API credentials or secrets to Git.

📜 License

This project was developed for the Darukaa.Earth AI Biodiversity Intelligence Chatbot Challenge. Add an appropriate project license if required.

👥 Team

EcoMind — AI Biodiversity Intelligence Advisor

Built by:

- Ojas Nivjekar

Independent project

🌍 Vision

«Make biodiversity intelligence more accessible by turning complex environmental interactions and scientific evidence into understandable, actionable decisions.»

🌱 Understand the ecosystem. Connect the variables. Act on evidence.