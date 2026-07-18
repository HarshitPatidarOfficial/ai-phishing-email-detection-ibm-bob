from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.model import MODEL_VERSION, combine_fields, load_or_train_model
from app.schemas import EmailPrediction, EmailRequest
from app.security_features import find_indicators

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(_: FastAPI):
    global MODEL_BUNDLE
    MODEL_BUNDLE = load_or_train_model()
    yield


app = FastAPI(
    title="AI-Powered Phishing Email Detection System",
    description="Machine-learning API for phishing email risk analysis.",
    version=MODEL_VERSION,
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

MODEL_BUNDLE: dict | None = None


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "phishing-email-detector",
        "model_loaded": MODEL_BUNDLE is not None,
        "model_version": MODEL_VERSION,
    }


@app.get("/api/model-info")
def model_info() -> dict:
    if not MODEL_BUNDLE:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {
        "model_version": MODEL_BUNDLE.get("model_version", MODEL_VERSION),
        "algorithm": "TF-IDF + Logistic Regression",
        "training_samples": MODEL_BUNDLE.get("training_samples"),
        "validation_accuracy": round(
            float(MODEL_BUNDLE.get("validation_accuracy", 0.0)), 4
        ),
        "note": "Demo model. Retrain with a larger, reviewed dataset before production use.",
    }


@app.post("/api/predict", response_model=EmailPrediction)
def predict_email(payload: EmailRequest) -> EmailPrediction:
    if not MODEL_BUNDLE:
        raise HTTPException(status_code=503, detail="Model is not ready")

    pipeline = MODEL_BUNDLE["pipeline"]
    text = combine_fields(payload.sender, payload.subject, payload.body)
    phishing_probability = float(pipeline.predict_proba([text])[0][1])

    indicators = find_indicators(payload.sender, payload.subject, payload.body)

    # Blend the learned probability with a small, transparent heuristic adjustment.
    # The adjustment helps surface obvious URL and impersonation signals in a tiny demo dataset.
    heuristic_boost = min(len(indicators) * 0.025, 0.15)
    risk_score = min(phishing_probability + heuristic_boost, 0.99)
    is_phishing = risk_score >= 0.55

    if is_phishing:
        recommendation = (
            "Do not click links or open attachments. Verify the request through an "
            "independent, trusted channel and report the message to your security team."
        )
    else:
        recommendation = (
            "No strong phishing pattern was detected, but verify unexpected requests, "
            "links, and attachments before acting."
        )

    if not indicators:
        indicators = ["No high-confidence rule-based indicator found"]

    confidence = risk_score if is_phishing else 1.0 - risk_score
    return EmailPrediction(
        label="Phishing" if is_phishing else "Legitimate",
        risk_score=round(risk_score * 100, 2),
        confidence=round(confidence * 100, 2),
        indicators=indicators,
        recommendation=recommendation,
        model_version=MODEL_BUNDLE.get("model_version", MODEL_VERSION),
    )
