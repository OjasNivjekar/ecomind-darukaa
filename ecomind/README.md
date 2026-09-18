# EcoMind — Biodiversity Intelligence Advisor

EcoMind turns site observations into biodiversity interventions by combining transparent environmental relationships, local scientific retrieval, and an optional locally running Llama synthesis.

## Architecture

`React query UI → FastAPI → environmental extraction + session memory → structured relationship rules → local RAG → grounded Llama prompt → cited recommendations`

The relationship knowledge base contains 20 rules across soil organic carbon, rainfall, soil moisture, temperature, land use, habitat connectivity, biodiversity and pollution. Rules identify risk factors and interactions before the model is called.

The local RAG corpus is `data/documents/curated_evidence.json`. It preserves title, organization, year, URL, topic and text per record; `rag/retriever.py` ranks relevant documents and passes only their metadata/excerpts with the deterministic reasoning context to Llama. Displayed citations are restricted to retrieved source IDs.

## Local setup

Prerequisites: Python 3.11+ and Node.js 20+.

```powershell
cd ecomind
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd ecomind\frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## Llama setup

The development adapter expects an Ollama-compatible Llama server at `LLAMA_BASE_URL` and calls `/api/chat` with JSON mode. Set `LLAMA_MODEL` to the locally installed model name. If Llama is unavailable, the API still returns the deterministic, evidence-backed assessment; it does not use OpenAI, Gemini, or any hosted replacement.

## API

- `GET /api/health` — service health.
- `POST /api/analyze` — accepts `{ "query": "...", "environmental_data": {}, "session_id": "..." }` and returns assessment, interactions, citations and recommendations.

## Production deployment

Deploy `backend/` as the API service and build `frontend/` as static assets. Set `VITE_API_URL` to the public API URL and restrict FastAPI CORS to the frontend origin. A cloud backend cannot reach a Llama instance on a developer's `localhost`; production needs a Llama server in the same private network/VPC, or a securely authenticated remote endpoint/tunnel configured as `LLAMA_BASE_URL`.

## Limitations

The corpus is intentionally small and curated for a hackathon; recommendations are decision support, not a substitute for field surveys, soil testing or regulatory advice. The in-memory conversation store is suitable for a single deployment process only.
