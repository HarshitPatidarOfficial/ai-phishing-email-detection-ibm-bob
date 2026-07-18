from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "training_emails.csv"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "phishing_pipeline.joblib"
MODEL_VERSION = "1.0.0"


@dataclass
class TrainingResult:
    accuracy: float
    report: str
    samples: int
    model_path: str


def combine_fields(sender: str, subject: str, body: str) -> str:
    return f"SENDER: {sender}\nSUBJECT: {subject}\nBODY: {body}".strip()


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=12000,
                    strip_accents="unicode",
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def train_model(
    dataset_path: Path = DEFAULT_DATASET,
    model_path: Path = DEFAULT_MODEL,
) -> TrainingResult:
    frame = pd.read_csv(dataset_path)
    required = {"sender", "subject", "body", "label"}
    if not required.issubset(frame.columns):
        missing = required.difference(frame.columns)
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    frame = frame.fillna("")
    texts = [
        combine_fields(row.sender, row.subject, row.body)
        for row in frame.itertuples(index=False)
    ]
    labels = frame["label"].astype(int).tolist()

    # A fixed split keeps demo results reproducible.
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, digits=3, zero_division=0)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "model_version": MODEL_VERSION,
            "training_samples": len(frame),
            "validation_accuracy": accuracy,
        },
        model_path,
    )

    return TrainingResult(
        accuracy=float(accuracy),
        report=report,
        samples=len(frame),
        model_path=str(model_path),
    )


def load_or_train_model(model_path: Path = DEFAULT_MODEL) -> dict:
    force_retrain = os.getenv("FORCE_RETRAIN", "false").lower() == "true"
    if force_retrain or not model_path.exists():
        train_model(model_path=model_path)
    return joblib.load(model_path)
