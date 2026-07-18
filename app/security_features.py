from __future__ import annotations

import re
from urllib.parse import urlparse

SUSPICIOUS_TERMS = {
    "urgent": "Urgency language",
    "verify": "Verification request",
    "password": "Password-related language",
    "account suspended": "Account suspension threat",
    "click here": "Direct click instruction",
    "confirm your identity": "Identity verification request",
    "limited time": "Time-pressure language",
    "payment failed": "Payment failure claim",
    "invoice attached": "Unexpected invoice language",
    "gift card": "Gift-card request",
    "bank account": "Banking information request",
    "security alert": "Security-alert language",
    "unusual activity": "Unusual-activity claim",
    "reset now": "Immediate reset instruction",
}

URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)
IP_URL_PATTERN = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}", re.IGNORECASE)
PUNYCODE_PATTERN = re.compile(r"xn--", re.IGNORECASE)
SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
}


def find_indicators(sender: str, subject: str, body: str) -> list[str]:
    text = f"{subject}\n{body}".lower()
    indicators: list[str] = []

    for term, description in SUSPICIOUS_TERMS.items():
        if term in text:
            indicators.append(description)

    urls = URL_PATTERN.findall(body)
    if len(urls) >= 3:
        indicators.append("Multiple external links")
    elif urls:
        indicators.append("Contains an external link")

    if IP_URL_PATTERN.search(body):
        indicators.append("Link uses an IP address")

    if PUNYCODE_PATTERN.search(body):
        indicators.append("Punycode domain detected")

    for url in urls:
        try:
            host = (urlparse(url).hostname or "").lower()
        except ValueError:
            continue
        if host in SHORTENER_DOMAINS:
            indicators.append("Shortened link detected")
            break

    if sender and "@" in sender:
        domain = sender.rsplit("@", 1)[-1].lower()
        if domain in {"gmail.com", "outlook.com", "yahoo.com", "proton.me"} and any(
            brand in text for brand in ("microsoft", "paypal", "amazon", "netflix", "bank")
        ):
            indicators.append("Brand claim sent from a public email domain")

    if subject.isupper() and len(subject) >= 8:
        indicators.append("All-caps subject line")

    if body.count("!") >= 4:
        indicators.append("Excessive exclamation marks")

    # Keep the response concise and deterministic.
    return list(dict.fromkeys(indicators))[:7]
