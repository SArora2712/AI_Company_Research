# Company Research Assistant (Flask / Python)
**AI-Powered Company Research Tool** built for the **Relu Consultancy AI & Automation Developer Hiring Hackathon**.

Enter a company name or website URL to get a comprehensive research report — company information, AI-generated insights, pain points, competitors, and a professional downloadable PDF — through a modern ChatGPT-style interface.

##  Features

- **Dual Input**: Company name or direct website URL
- **Intelligent Website Crawling**: Discovers key pages (About, Products, Services, Contact, Pricing), skips duplicates and login pages
- **Serper.dev Integration**: Official website discovery, contact info, and competitor research
- **OpenRouter AI**: Model selection (GPT-4o, Llama, Mistral, etc.) with structured JSON output
- **AI Insight Scores**: Overall, Market Position, Digital Presence, Growth Potential
- **Competitor Analysis**: 4–6 relevant competitors with names and websites
- **Professional PDF Report**: Clean, well-formatted, single-click download
- **Modern Chat Interface**: Progress indicators, research history, responsive design
- **Bonus: Discord Integration**: Auto-sends report + PDF with applicant details

## Tech Stack

- **Backend**: Flask (Python)
- **Crawling**: BeautifulSoup4 + requests
- **Search**: Serper.dev
- **AI**: OpenRouter
- **PDF Generation**: reportlab
- **Frontend**: Vanilla HTML/CSS/JS
## Project Structure

```
app.py                 # Flask app: routes for /, /api/research, /api/pdf, /api/discord
lib/
  company.py
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
.env
README.md
```

## Setup (local)

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create `.env` file and fill in your keys:
   ```bash
   cp .env
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

## Deploying 

### Render.com (recommended, free tier, ~5 min)
1. Push this project to a GitHub repo.
2. Go to https://render.com/ → New → Web Service → connect your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables `SERPER_API_KEY` and `OPENROUTER_API_KEY` in the Render dashboard.
6. Deploy — Render gives you a public URL immediately.

### Alternative
— Railway.app 

No database, no authentication, and no persistent storage are required — everything runs per-request, in memory.

## Supported AI Models

* openai/gpt-4o-mini (Fast & Reliable)
* openai/gpt-4o (Best Quality)
* meta-llama/llama-3.1-70b-instruct
* mistralai/mistral-large
  
Additional Features Implemented

✅ Discord Integration (Full bonus - settings + auto-send PDF)
✅ Modern Responsive ChatGPT-style UI
✅ Progress indicators during research
✅ Clickable research history
✅ Professional PDF report with insight scores

## How it works (workflow)

1. User submits a company name or URL in the chat input.
2. If a name was given, Serper.dev resolves the official website (via Knowledge Graph or filtered organic search results) — `lib/serper.py::find_official_website`.
3. The crawler (`lib/crawler.py`) does a keyword-prioritized BFS crawl of the site (About, Products, Services, Contact, Pricing first), skipping login/duplicate/irrelevant pages, and extracts clean text.
4. Serper.dev is queried again for public contact info and competitor signals.
5. All of this is passed to the selected OpenRouter model, prompted to return strict JSON: summary, products, pain points, and 3-6 competitors.
6. The result renders as a structured report card in the chat.
7. The user can download a polished PDF with one click.
8. (If configured) Report is automatically sent to Discord

## Known Limitations / Future Improvements

- Crawler is capped at 6 pages per site to keep response times reasonable — configurable via `crawl_website(url, max_pages=...)`.
- No persistent database (as per requirements)

## Links
* **Deployed URL:** [https://ai-company-research-v8n0.onrender.com/](https://ai-company-research-v8n0.onrender.com/)
* **GitHub Repository:** https://github.com/SArora2712/AI_Company_Research

