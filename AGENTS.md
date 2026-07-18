# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack
Python 3.12 · FastAPI · scikit-learn (TF-IDF + Logistic Regression) · Pydantic v2 · pytest · joblib

## Commands

```bash
# All commands must be run from the AI-Phishing-Email-Detection-IBM-Bob/ project root

# Run all tests
pytest -q

# Run a single test by name
pytest -q tests/test_api.py::test_health_endpoint

# Train / retrain the model (required after any data or feature change)
python scripts/train_model.py

# Start the server
uvicorn app.main:app --reload
```

> `pyproject.toml` sets `pythonpath = ["."]` — `app.*` is importable without installation only when pytest is run from the project root.

## Critical Patterns

- **Model bundle**: `models/phishing_pipeline.joblib` is a `dict` with keys `pipeline`, `model_version`, `training_samples`, `validation_accuracy`. Always load via `load_or_train_model()` in `app/model.py`; never unpickle the `Pipeline` directly.
- **Auto-train on startup**: `load_or_train_model()` trains automatically if the `.joblib` file is absent. Set `FORCE_RETRAIN=true` to force a fresh train. The Dockerfile also runs `python scripts/train_model.py` at build time.
- **Text representation**: `combine_fields(sender, subject, body)` produces a fixed `SENDER: …\nSUBJECT: …\nBODY: …` format fed to TF-IDF. Changing this format invalidates the saved `.joblib` — always retrain after editing it.
- **Risk scoring**: `risk_score = predict_proba(phishing class) + min(indicator_count × 0.025, 0.15)`, capped at 0.99. Phishing verdict threshold is **0.55**. Both constants live only in `app/main.py`.
- **`risk_score` and `confidence` are 0–100 percentages** in the API response (multiplied before `EmailPrediction` is returned). Tests assert `>= 55`, not `>= 0.55`.
- **Indicators capped at 7**: `find_indicators()` returns at most 7 de-duplicated strings. If none found, `main.py` substitutes `["No high-confidence rule-based indicator found"]`.
- **CSV label column**: `data/training_emails.csv` uses integer labels (1 = phishing, 0 = legitimate) cast with `.astype(int)`. String values raise during training.
- **TestClient lifespan**: every test must use `with TestClient(app) as client:` to trigger the lifespan hook that loads the model. Skipping the context manager leaves `MODEL_BUNDLE = None` → 503 errors.

## Code Style
- `from __future__ import annotations` at the top of every module in `app/`.
- Pydantic schemas in `app/schemas.py` only; use `BaseModel`, `Field`, and `@field_validator` (Pydantic v2 API).
- All `EmailRequest` text fields are stripped by a shared `@field_validator`; do not duplicate stripping elsewhere.
- Route handlers carry explicit return-type annotations (`dict` or the Pydantic response model).
- `Path(__file__).resolve().parents[N]` for all path construction — never `os.path`.
- No linter/formatter config present; follow PEP 8, snake_case, 4-space indent as seen in existing files.

## Engineering Rules (non-negotiable)
1. Never claim the model is production-ready.
2. No external logging of email content (privacy).
3. All request input must pass through Pydantic (`app/schemas.py`).
4. `POST /api/predict` response shape — `label`, `risk_score`, `confidence`, `indicators`, `recommendation`, `model_version` — must stay backward compatible.
5. Retrain (`python scripts/train_model.py`) after any change to `data/training_emails.csv` or feature extraction logic.
6. `pytest -q` must pass before completing any coding task.
