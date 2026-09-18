from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

from backend.schemas import AnalyzeRequest, AnalyzeResponse
from backend.service import run_assessment

load_dotenv()
app = FastAPI(title="EcoMind API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ecomind-api"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_request(request: AnalyzeRequest) -> AnalyzeResponse:
    return run_assessment(request.query, request.environmental_data, request.session_id)
