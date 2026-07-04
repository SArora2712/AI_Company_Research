"""Curated company dataset + suggestion engine for the search autocomplete.

This powers a Google-style "type and see recommendations" experience without
needing any external API call (fast, free, works offline).
"""

# (name, domain, category) — a reasonably broad curated set across industries
COMPANIES = [
    ("Stripe", "stripe.com", "Fintech / Payments"),
    ("Square", "squareup.com", "Fintech / Payments"),
    ("PayPal", "paypal.com", "Fintech / Payments"),
    ("Razorpay", "razorpay.com", "Fintech / Payments"),
    ("Paytm", "paytm.com", "Fintech / Payments"),
    ("Visa", "visa.com", "Fintech / Payments"),
    ("Mastercard", "mastercard.com", "Fintech / Payments"),
    ("Coinbase", "coinbase.com", "Fintech / Crypto"),
    ("Robinhood", "robinhood.com", "Fintech"),
    ("Google", "google.com", "Technology"),
    ("Microsoft", "microsoft.com", "Technology"),
    ("Apple", "apple.com", "Technology"),
    ("Amazon", "amazon.com", "E-commerce / Cloud"),
    ("Meta", "meta.com", "Technology / Social"),
    ("Netflix", "netflix.com", "Entertainment / Streaming"),
    ("Tesla", "tesla.com", "Automotive / Energy"),
    ("Nvidia", "nvidia.com", "Semiconductors"),
    ("Intel", "intel.com", "Semiconductors"),
    ("AMD", "amd.com", "Semiconductors"),
    ("Salesforce", "salesforce.com", "SaaS / CRM"),
    ("HubSpot", "hubspot.com", "SaaS / Marketing"),
    ("Zoom", "zoom.us", "SaaS / Communication"),
    ("Slack", "slack.com", "SaaS / Communication"),
    ("Notion", "notion.so", "SaaS / Productivity"),
    ("Asana", "asana.com", "SaaS / Productivity"),
    ("Trello", "trello.com", "SaaS / Productivity"),
    ("Atlassian", "atlassian.com", "SaaS / Dev Tools"),
    ("GitHub", "github.com", "Dev Tools"),
    ("GitLab", "gitlab.com", "Dev Tools"),
    ("OpenAI", "openai.com", "AI"),
    ("Anthropic", "anthropic.com", "AI"),
    ("Cohere", "cohere.com", "AI"),
    ("Perplexity", "perplexity.ai", "AI"),
    ("Uber", "uber.com", "Mobility"),
    ("Lyft", "lyft.com", "Mobility"),
    ("Ola", "olacabs.com", "Mobility"),
    ("Airbnb", "airbnb.com", "Travel / Marketplace"),
    ("Booking.com", "booking.com", "Travel"),
    ("MakeMyTrip", "makemytrip.com", "Travel"),
    ("Zomato", "zomato.com", "Food-tech"),
    ("Swiggy", "swiggy.com", "Food-tech"),
    ("DoorDash", "doordash.com", "Food-tech"),
    ("Flipkart", "flipkart.com", "E-commerce"),
    ("Myntra", "myntra.com", "E-commerce"),
    ("Shopify", "shopify.com", "E-commerce / SaaS"),
    ("Etsy", "etsy.com", "E-commerce"),
    ("eBay", "ebay.com", "E-commerce"),
    ("Walmart", "walmart.com", "Retail"),
    ("Target", "target.com", "Retail"),
    ("IBM", "ibm.com", "Technology / Enterprise"),
    ("Oracle", "oracle.com", "Enterprise Software"),
    ("SAP", "sap.com", "Enterprise Software"),
    ("Adobe", "adobe.com", "Software / Creative"),
    ("Figma", "figma.com", "Design / SaaS"),
    ("Canva", "canva.com", "Design / SaaS"),
    ("Zoho", "zoho.com", "SaaS"),
    ("Freshworks", "freshworks.com", "SaaS / CRM"),
    ("Infosys", "infosys.com", "IT Services"),
    ("TCS", "tcs.com", "IT Services"),
    ("Wipro", "wipro.com", "IT Services"),
    ("Accenture", "accenture.com", "Consulting / IT"),
    ("Deloitte", "deloitte.com", "Consulting"),
    ("McKinsey & Company", "mckinsey.com", "Consulting"),
    ("Reliance Industries", "ril.com", "Conglomerate"),
    ("Tata Group", "tata.com", "Conglomerate"),
    ("Adani Group", "adani.com", "Conglomerate"),
    ("HDFC Bank", "hdfcbank.com", "Banking"),
    ("ICICI Bank", "icicibank.com", "Banking"),
    ("JPMorgan Chase", "jpmorganchase.com", "Banking"),
    ("Goldman Sachs", "goldmansachs.com", "Banking / Finance"),
    ("Samsung", "samsung.com", "Electronics"),
    ("Sony", "sony.com", "Electronics / Entertainment"),
    ("LG", "lg.com", "Electronics"),
    ("Xiaomi", "mi.com", "Electronics"),
    ("Dell", "dell.com", "Hardware"),
    ("HP", "hp.com", "Hardware"),
    ("Lenovo", "lenovo.com", "Hardware"),
    ("Cisco", "cisco.com", "Networking"),
    ("Spotify", "spotify.com", "Entertainment / Streaming"),
    ("Disney", "disney.com", "Entertainment"),
    ("Warner Bros Discovery", "wbd.com", "Entertainment"),
    ("Twitter / X", "x.com", "Social Media"),
    ("LinkedIn", "linkedin.com", "Social / Professional Network"),
    ("Pinterest", "pinterest.com", "Social Media"),
    ("Snap Inc", "snap.com", "Social Media"),
    ("ByteDance / TikTok", "tiktok.com", "Social Media"),
    ("Nike", "nike.com", "Apparel"),
    ("Adidas", "adidas.com", "Apparel"),
    ("Puma", "puma.com", "Apparel"),
    ("Starbucks", "starbucks.com", "Food & Beverage"),
    ("McDonald's", "mcdonalds.com", "Food & Beverage"),
    ("Coca-Cola", "coca-cola.com", "Food & Beverage"),
    ("PepsiCo", "pepsico.com", "Food & Beverage"),
    ("Unilever", "unilever.com", "FMCG"),
    ("Procter & Gamble", "pg.com", "FMCG"),
    ("Nestle", "nestle.com", "FMCG"),
    ("Ford", "ford.com", "Automotive"),
    ("General Motors", "gm.com", "Automotive"),
    ("Toyota", "toyota.com", "Automotive"),
    ("BMW", "bmw.com", "Automotive"),
    ("Mercedes-Benz", "mercedes-benz.com", "Automotive"),
    ("Volkswagen", "vw.com", "Automotive"),
    ("SpaceX", "spacex.com", "Aerospace"),
    ("Boeing", "boeing.com", "Aerospace"),
    ("Airbus", "airbus.com", "Aerospace"),
    ("Pfizer", "pfizer.com", "Pharma"),
    ("Moderna", "modernatx.com", "Pharma / Biotech"),
    ("Johnson & Johnson", "jnj.com", "Pharma / Healthcare"),
    ("Sun Pharma", "sunpharma.com", "Pharma"),
    ("Cipla", "cipla.com", "Pharma"),
]


def get_suggestions(query, limit=8):
    """Google-style suggestion ranking: startswith matches first, then
    substring matches, both alphabetically tie-broken."""
    if not query or not query.strip():
        return []

    q = query.strip().lower()
    starts, contains = [], []

    for name, domain, category in COMPANIES:
        lname = name.lower()
        if lname.startswith(q):
            starts.append((name, domain, category))
        elif q in lname or q in domain:
            contains.append((name, domain, category))

    starts.sort(key=lambda c: c[0])
    contains.sort(key=lambda c: c[0])

    results = (starts + contains)[:limit]
    return [{"name": n, "domain": d, "category": c} for n, d, c in results]
