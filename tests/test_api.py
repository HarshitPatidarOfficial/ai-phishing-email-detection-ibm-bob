from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["model_loaded"] is True


def test_phishing_prediction() -> None:
    payload = {
        "sender": "security@account-check.example",
        "subject": "URGENT: Verify your account",
        "body": (
            "Your account is suspended. Click here and confirm your password now: "
            "http://192.168.1.8/verify"
        ),
    }
    with TestClient(app) as client:
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "Phishing"
        assert data["risk_score"] >= 55
        assert data["indicators"]


def test_legitimate_prediction() -> None:
    payload = {
        "sender": "teacher@school.edu",
        "subject": "Updated class schedule",
        "body": "The class will begin at 10 AM tomorrow. Please bring your notes.",
    }
    with TestClient(app) as client:
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["label"] in {"Legitimate", "Phishing"}
        assert 0 <= data["risk_score"] <= 100
