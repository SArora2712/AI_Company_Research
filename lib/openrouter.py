"""Improved OpenRouter wrapper with better model support."""

import json
import os
import re

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return key


def ask_openrouter(model, system_prompt, user_prompt):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    # Some models need extra parameters
    if "claude" in model.lower():
        payload["temperature"] = 0.4
    elif "gemini" in model.lower():
        payload["temperature"] = 0.3

    res = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://company-research-assistant.example",
            "X-Title": "Relu Company Research",
        },
        json=payload,
        timeout=90,   # Increased timeout for slower models
    )

    if not res.ok:
        raise RuntimeError(f"OpenRouter failed ({res.status_code}): {res.text[:400]}")

    data = res.json()
    content = data["choices"][0]["message"]["content"] if data.get("choices") else ""
    return content


def extract_json(text):
    """Extract JSON from AI response."""
    # Try to find JSON block
    match = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        candidate = match.group(1)
    else:
        candidate = text

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in response")

    json_str = candidate[start:end + 1]
    return json.loads(json_str)