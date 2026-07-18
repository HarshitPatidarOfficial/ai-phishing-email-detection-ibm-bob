const form = document.getElementById("email-form");
const analyzeButton = document.getElementById("analyze-button");
const emptyState = document.getElementById("empty-state");
const resultContent = document.getElementById("result-content");
const resultLabel = document.getElementById("result-label");
const riskBadge = document.getElementById("risk-badge");
const riskScore = document.getElementById("risk-score");
const scoreFill = document.getElementById("score-fill");
const indicatorList = document.getElementById("indicator-list");
const recommendationText = document.getElementById("recommendation-text");
const modelVersion = document.getElementById("model-version");
const confidenceText = document.getElementById("confidence-text");

const examples = {
  sender: "security-team@account-check.example",
  subject: "URGENT: Your account will be suspended today",
  body: `We detected unusual activity on your account. Verify your password immediately to prevent suspension.\n\nClick here: http://192.168.10.5/verify\n\nThis security alert expires in 30 minutes!`,
};

document.getElementById("load-example").addEventListener("click", () => {
  document.getElementById("sender").value = examples.sender;
  document.getElementById("subject").value = examples.subject;
  document.getElementById("body").value = examples.body;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const originalText = analyzeButton.querySelector("span").textContent;
  analyzeButton.disabled = true;
  analyzeButton.querySelector("span").textContent = "Analyzing patterns...";

  const payload = {
    sender: document.getElementById("sender").value,
    subject: document.getElementById("subject").value,
    body: document.getElementById("body").value,
  };

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const detail = await response.json();
      throw new Error(detail.detail || "Analysis failed");
    }
    const data = await response.json();
    renderResult(data);
  } catch (error) {
    alert(`Could not analyze the email: ${error.message}`);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.querySelector("span").textContent = originalText;
  }
});

function renderResult(data) {
  const safe = data.label === "Legitimate";
  emptyState.classList.add("hidden");
  resultContent.classList.remove("hidden");

  resultLabel.textContent = data.label;
  resultLabel.style.color = safe ? "var(--safe)" : "var(--danger)";
  riskBadge.textContent = `${data.risk_score.toFixed(1)}% risk`;
  riskBadge.classList.toggle("safe", safe);
  riskScore.textContent = `${data.risk_score.toFixed(1)}%`;
  scoreFill.classList.toggle("safe", safe);
  requestAnimationFrame(() => { scoreFill.style.width = `${data.risk_score}%`; });

  indicatorList.innerHTML = "";
  data.indicators.forEach((indicator) => {
    const item = document.createElement("li");
    item.textContent = indicator;
    item.style.borderLeftColor = safe ? "var(--safe)" : "var(--danger)";
    indicatorList.appendChild(item);
  });

  recommendationText.textContent = data.recommendation;
  modelVersion.textContent = data.model_version;
  confidenceText.textContent = `Confidence ${data.confidence.toFixed(1)}%`;
}
