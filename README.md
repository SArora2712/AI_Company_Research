# Company Research Assistant (Flask / Python)

An AI-powered company research tool built for the Relu Consultancy hiring hackathon. Enter a company name or website URL and get a full research report — company info, products/services, AI-generated pain points, competitor analysis, and a downloadable PDF — through a ChatGPT-style interface.

## Features

- **Dual input**: company name or website URL
- **Website crawler**: discovers About/Products/Services/Contact/Pricing pages, skips duplicates and login pages (`lib/crawler.py`, BeautifulSoup)
- **Serper.dev integration**: resolves official websites, contact info, and competitor research (`lib/serper.py`)
- **OpenRouter integration**: pluggable AI model selection via dropdown, generates structured company insights (`lib/openrouter.py`)
- **Competitor analysis**: 3-6 real competitors with name + website
- **PDF report generation**: single-click download, built with `fpdf2` (pure Python, no system dependencies)
- **ChatGPT-style UI**: input, chat history, progress indicator, download button — plain HTML/CSS/JS, no frontend framework needed
- **Bonus: Discord integration**: settings panel (bot token + channel ID), auto-sends applicant info + report + PDF after each research run

## Tech Stack

- Flask 3 (Python)
- requests + BeautifulSoup4 (crawling)
- fpdf2 (PDF generation)
- Vanilla HTML/CSS/JS frontend (Jinja2 template + static assets)
- gunicorn for production serving

## Project Structure

```
app.py                 # Flask app: routes for /, /api/research, /api/pdf, /api/discord
lib/
  serper.py            # Serper.dev API wrapper
  crawler.py           # Website crawler (BFS, keyword-prioritized)
  openrouter.py         # OpenRouter API wrapper + JSON extraction
  pdf_gen.py            # PDF report generation (fpdf2)
templates/
  index.html            # Chat UI shell (Jinja2)
static/
  style.css
  app.js                # All frontend logic (fetch calls, DOM rendering)
requirements.txt
.env.example
```

## Setup (local)

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `SERPER_API_KEY` | Free key from https://serper.dev — used to find official websites, contact info, and competitors |
   | `OPENROUTER_API_KEY` | Key from https://openrouter.ai/keys — used for all AI analysis, model selectable in the UI |

3. Run locally:
   ```bash
   python app.py
   ```
   Visit http://localhost:5000

## Deploying (pick whichever is fastest for you)

### Option A — Render.com (recommended, free tier, ~5 min)
1. Push this project to a GitHub repo.
2. Go to https://render.com/ → New → Web Service → connect your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables `SERPER_API_KEY` and `OPENROUTER_API_KEY` in the Render dashboard.
6. Deploy — Render gives you a public URL immediately.

### Option B — Railway.app
1. New Project → Deploy from GitHub repo.
2. Add the same two environment variables.
3. Set start command to `gunicorn app:app` (Railway auto-detects Python via `requirements.txt`).
4. Deploy and grab the generated public URL.

### Option C — Vercel (if you want to stay on Vercel)
Vercel can run Flask via its Python serverless runtime, but it needs a small adapter layer (`vercel.json` routing all requests to `app.py`) and doesn't support long-running crawls as gracefully as a normal server. Render/Railway are strongly recommended for this Flask version since they run Flask natively with no adapter needed.

No database, no authentication, and no persistent storage are required — everything runs per-request, in memory.

## Discord Integration (Bonus)

Click **⚙ Discord Settings** in the top bar to enter:
- Discord Bot Token (provided by the evaluator)
- Discord Channel ID (provided by the evaluator)
- Applicant Name / Email

These are saved to the browser's `localStorage` (no server-side storage). After each successful research run, the app automatically:
1. Generates the PDF report
2. Posts a message to the configured Discord channel with applicant details + company name/website
3. Attaches the generated PDF report to that message

This is handled server-side via `/api/discord` (in `app.py`), which authenticates to the Discord REST API (`POST /channels/{channelId}/messages`) using `Authorization: Bot {botToken}` and a multipart form upload for the PDF attachment.

## How it works (workflow)

1. User submits a company name or URL in the chat input.
2. If a name was given, Serper.dev resolves the official website (via Knowledge Graph or filtered organic search results) — `lib/serper.py::find_official_website`.
3. The crawler (`lib/crawler.py`) does a keyword-prioritized BFS crawl of the site (About, Products, Services, Contact, Pricing first), skipping login/duplicate/irrelevant pages, and extracts clean text.
4. Serper.dev is queried again for public contact info and competitor signals.
5. All of this is passed to the selected OpenRouter model, prompted to return strict JSON: summary, products, pain points, and 3-6 competitors.
6. The result renders as a structured report card in the chat.
7. The user can download a polished PDF (`fpdf2`) with one click, and — if Discord is configured — it's automatically shared to the channel.

## Known Limitations / Future Improvements

- Crawler is capped at 6 pages per site to keep response times reasonable — configurable via `crawl_website(url, max_pages=...)`.
- No caching layer; each research run is a fresh crawl + AI call (per the "no database" requirement).
- Competitor accuracy depends on model quality and Serper snippet richness for lesser-known companies.
- `fpdf2`'s built-in fonts are Latin-1 only; non-Latin characters in scraped content are safely replaced rather than crashing the PDF generation.

## Verified

This app was built and smoke-tested locally before delivery:
- `python -m py_compile` passes with no syntax errors on all modules
- Flask server starts and serves the homepage (200 OK)
- `/api/research` correctly validates missing API keys (fails gracefully with a clear error, ready to work the moment real keys are added)
- `/api/pdf` was tested end-to-end and produces a valid PDF 1.3 document
