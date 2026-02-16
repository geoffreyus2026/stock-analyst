import re
import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .web_analyzer import generate_full_analysis

_DB_LOCK = threading.Lock()


class RecommendationRequest(BaseModel):
    stock: str = Field(..., description="Ticker symbol or company name")
    agent_name: str = Field(..., description="Registered agent name")
    agent_token: str = Field(..., description="Registered agent token")


class AgentRegistrationRequest(BaseModel):
    name: str = Field(..., description="Unique agent name")


def _looks_like_ticker(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9\.\-]{0,9}", value.strip()))


def _resolve_symbol(stock: str) -> Optional[str]:
    candidate = stock.strip()
    if not candidate:
        return None

    if _looks_like_ticker(candidate):
        return candidate.upper()

    try:
        import yfinance as yf  # Optional runtime dependency for name lookup.

        search = yf.Search(query=candidate, max_results=5, news_count=0)
        quotes = search.quotes or []
        for quote in quotes:
            symbol = quote.get("symbol")
            if symbol and _looks_like_ticker(symbol):
                return symbol.upper()
    except Exception:
        return None

    return None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Stock Analyst API",
        version="1.0.0",
        description="API endpoint for stock trading recommendations",
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/api/v1/agents/register")
    def register_agent(request: AgentRegistrationRequest) -> dict:
        return _register_agent(request.name)

    @app.get("/api/v1/recommendation")
    def get_recommendation(
        stock: str = Query(..., description="Ticker symbol or company name"),
        agent_name: str = Query(..., description="Registered agent name"),
        agent_token: str = Query(..., description="Registered agent token"),
    ) -> dict:
        _validate_agent(agent_name, agent_token)
        return _build_recommendation_response(stock)

    @app.post("/api/v1/recommendation")
    def post_recommendation(request: RecommendationRequest) -> dict:
        _validate_agent(request.agent_name, request.agent_token)
        return _build_recommendation_response(request.stock)

    return app


def _db_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    return root / "data" / "agents_db.txt"


def _ensure_db_exists() -> None:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        db_path.write_text('{"agents": {}}', encoding="utf-8")


def _load_agents() -> Dict[str, Dict[str, str]]:
    _ensure_db_exists()
    raw = _db_path().read_text(encoding="utf-8").strip()
    if not raw:
        return {}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Agent DB is corrupted: {exc}") from exc

    agents = payload.get("agents", {})
    if not isinstance(agents, dict):
        raise HTTPException(status_code=500, detail="Agent DB has invalid format")
    return agents


def _save_agents(agents: Dict[str, Dict[str, str]]) -> None:
    db_path = _db_path()
    payload = {"agents": agents}
    tmp_path = db_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp_path.replace(db_path)


def _generate_unique_token(agents: Dict[str, Dict[str, str]]) -> str:
    existing_tokens = {record.get("token", "") for record in agents.values()}
    while True:
        token = secrets.token_urlsafe(24)
        if token not in existing_tokens:
            return token


def _register_agent(name: str) -> dict:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=400, detail="Agent name cannot be empty")

    with _DB_LOCK:
        agents = _load_agents()
        if cleaned_name in agents:
            raise HTTPException(
                status_code=409,
                detail=f"Agent '{cleaned_name}' is already registered",
            )

        token = _generate_unique_token(agents)
        created_at = datetime.now(timezone.utc).isoformat()
        agents[cleaned_name] = {"token": token, "created_at": created_at}
        _save_agents(agents)

    return {"name": cleaned_name, "token": token, "created_at": created_at}


def _validate_agent(name: str, token: str) -> None:
    cleaned_name = name.strip()
    cleaned_token = token.strip()
    if not cleaned_name or not cleaned_token:
        raise HTTPException(status_code=401, detail="Agent name and token are required")

    with _DB_LOCK:
        agents = _load_agents()
        record = agents.get(cleaned_name)

    if not record:
        raise HTTPException(status_code=401, detail="Unknown agent")

    expected_token = record.get("token", "")
    if not expected_token or not secrets.compare_digest(expected_token, cleaned_token):
        raise HTTPException(status_code=401, detail="Invalid agent token")


def _build_recommendation_response(stock: str) -> dict:
    resolved_symbol = _resolve_symbol(stock)
    if not resolved_symbol:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not resolve stock input to a ticker. "
                "Provide a valid ticker (for example, AAPL) or a company name."
            ),
        )

    try:
        analysis = generate_full_analysis(resolved_symbol)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate recommendation for {resolved_symbol}: {exc}",
        ) from exc

    if analysis.get("ai_recommendation") is None:
        raise HTTPException(
            status_code=502,
            detail=f"Recommendation unavailable for {resolved_symbol}",
        )

    return {
        "input": stock,
        "resolved_symbol": resolved_symbol,
        "company": analysis.get("company"),
        "recommendation": analysis["ai_recommendation"],
        "generated_at": analysis.get("generated_at"),
    }


app = create_app()
