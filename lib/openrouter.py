"""Wrapper around OpenRouter's chat completions endpoint."""
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
    res = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://relu-company-research.example",
            "X-Title": "Relu Company Research Assistant",
        },
        json={
            "model": model or "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    if not res.ok:
        raise RuntimeError(f"OpenRouter request failed ({res.status_code}): {res.text[:500]}")

    data = res.json()
    return data["choices"][0]["message"]["content"] if data.get("choices") else ""


def extract_json(text):
    """Extract the first JSON object found in a string (handles ```json fences etc.)."""
    fenced = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE) or re.search(r"```\s*([\s\S]*?)```", text)
    candidate = fenced.group(1) if fenced else text

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in AI response")

    return json.loads(candidate[start:end + 1])
