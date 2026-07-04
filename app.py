import base64
import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from io import BytesIO

from lib.companies import get_suggestions
from lib.crawler import crawl_website
from lib.openrouter import ask_openrouter, extract_json
from lib.pdf_gen import generate_pdf
from lib.serper import find_official_website, normalize_url, search_competitors, search_contact_info

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Simple in-memory cache so re-researching the same company within a session
# is instant instead of re-crawling + re-calling the AI model. Keyed by
# (lowercased input, model). Cleared on server restart — intentional, no DB.
_RESEARCH_CACHE = {}


def looks_like_url(text):
    return bool(
        text.lower().startswith("http")
        or __import__("re").match(r"^[\w-]+\.[a-z]{2,}(/.*)?$", text, __import__("re").IGNORECASE)
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/research", methods=["POST"])
def research():
    body = request.get_json(force=True, silent=True) or {}
    user_input = (body.get("input") or "").strip()
    model = body.get("model") or "openai/gpt-4o-mini"

    if not user_input:
        return jsonify({"error": "Please provide a company name or website URL."}), 400

    cache_key = (user_input.lower(), model)
    if cache_key in _RESEARCH_CACHE:
        cached = _RESEARCH_CACHE[cache_key]
        return jsonify({**cached, "cached": True})

    try:
        if looks_like_url(user_input):
            website = normalize_url(user_input if user_input.startswith("http") else f"https://{user_input}")
            host = urlparse(website).hostname or user_input
            company_guess = host.replace("www.", "").split(".")[0]
        else:
            company_guess = user_input
            website = find_official_website(user_input)

        # Step 1: crawl the site
        pages, combined_text = crawl_website(website, max_pages=6)

        # Step 2: gather supporting public info via Serper
        contact_snippets = ""
        competitor_snippets = ""
        try:
            contact_data = search_contact_info(company_guess)
            contact_snippets = "\n".join(
                f"{r.get('title', '')}: {r.get('snippet', '')}" for r in contact_data.get("organic", [])[:5]
            )
        except Exception:
            pass
        try:
            competitor_data = search_competitors(company_guess)
            competitor_snippets = "\n".join(
                f"{r.get('title', '')} ({r.get('link', '')}): {r.get('snippet', '')}"
                for r in competitor_data.get("organic", [])[:8]
            )
        except Exception:
            pass

        # Step 3: ask the AI model to synthesize everything into structured JSON
        system_prompt = (
            "You are an expert B2B company research analyst. You will be given raw crawled "
            "website content and public search snippets about a company. Produce a concise, "
            "accurate, well-structured JSON object only, with no extra commentary. If a field "
            "is unknown, use an empty string or empty array — do not invent data."
        )

        user_prompt = f"""
COMPANY (best guess name): {company_guess}
WEBSITE: {website}

=== CRAWLED WEBSITE CONTENT ===
{combined_text or "(no content could be crawled)"}

=== PUBLIC SEARCH SNIPPETS: CONTACT INFO ===
{contact_snippets or "(none found)"}

=== PUBLIC SEARCH SNIPPETS: COMPETITOR RESEARCH ===
{competitor_snippets or "(none found)"}

Return ONLY valid JSON matching exactly this schema:
{{
  "companyName": string,
  "website": string,
  "phone": string,
  "address": string,
  "summary": string,
  "products": [string],
  "painPoints": [string],
  "competitors": [{{"name": string, "website": string}}],
  "insight": {{
    "overallScore": integer (0-100),
    "marketPosition": integer (0-100),
    "digitalPresence": integer (0-100),
    "growthPotential": integer (0-100),
    "insightSummary": string (2-3 sentences explaining the scores)
  }}
}}
Identify 3-6 real competitors operating in the same industry/country with similar products, using the search snippets and your knowledge. Keep painPoints to 3-6 sharp, sales-relevant insights an outbound sales rep could use.
For the "insight" scores: base them on what you can reasonably infer from the crawled content and search snippets (site quality/freshness suggests digitalPresence, competitive density and brand signals suggest marketPosition, hiring/expansion/product-launch signals suggest growthPotential, and overallScore is a holistic average). Never leave these blank — give your best reasoned estimate even with partial data.
"""

        ai_raw = ask_openrouter(model, system_prompt, user_prompt)
        try:
            structured = extract_json(ai_raw)
        except Exception:
            structured = {
                "companyName": company_guess,
                "website": website,
                "phone": "",
                "address": "",
                "summary": ai_raw[:1500],
                "products": [],
                "painPoints": [],
                "competitors": [],
                "insight": {},
            }

        structured["website"] = structured.get("website") or website
        structured["companyName"] = structured.get("companyName") or company_guess
        structured["insight"] = structured.get("insight") or {}

        response_payload = {
            "result": structured,
            "crawledPages": [{"url": p["url"], "title": p["title"]} for p in pages],
            "modelUsed": model,
        }

        _RESEARCH_CACHE[cache_key] = response_payload
        return jsonify({**response_payload, "cached": False})

    except Exception as e:
        return jsonify({"error": str(e) or "Research failed"}), 500


@app.route("/api/suggestions")
def suggestions():
    query = (request.args.get("q") or "").strip()
    return jsonify({"results": get_suggestions(query, limit=8)})


@app.route("/api/pdf", methods=["POST"])
def pdf_report():
    data = request.get_json(force=True, silent=True) or {}
    try:
        pdf_bytes = generate_pdf(data)
        filename = f"{(data.get('companyName') or 'company')}".replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c == "_") + "_report.pdf"
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"error": str(e) or "PDF generation failed"}), 500


@app.route("/api/discord", methods=["POST"])
def discord_notify():
    body = request.get_json(force=True, silent=True) or {}
    bot_token = body.get("botToken")
    channel_id = body.get("channelId")

    if not bot_token or not channel_id:
        return jsonify({"error": "Discord bot token and channel ID are required."}), 400

    try:
        content = (
            "**New Company Research Report Generated**\n"
            f"**Applicant:** {body.get('applicantName') or 'N/A'} ({body.get('applicantEmail') or 'N/A'})\n"
            f"**Company:** {body.get('companyName') or 'N/A'}\n"
            f"**Website:** {body.get('companyWebsite') or 'N/A'}"
        )

        files = None
        pdf_base64 = body.get("pdfBase64")
        if pdf_base64:
            pdf_bytes = base64.b64decode(pdf_base64)
            filename = f"{(body.get('companyName') or 'company')}".replace(" ", "_")
            filename = "".join(c for c in filename if c.isalnum() or c == "_") + "_report.pdf"
            files = {"files[0]": (filename, pdf_bytes, "application/pdf")}

        res = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers={"Authorization": f"Bot {bot_token}"},
            data={"payload_json": __import__("json").dumps({"content": content})},
            files=files,
            timeout=20,
        )
        if not res.ok:
            raise RuntimeError(f"Discord API failed ({res.status_code}): {res.text[:300]}")

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e) or "Discord notification failed"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
