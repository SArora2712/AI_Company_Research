"""PDF report generation using fpdf2 (pure Python, no system deps)."""
from datetime import datetime
from io import BytesIO

from fpdf import FPDF


def _safe(text):
    """fpdf2's core fonts only support latin-1; strip anything outside that range."""
    if not text:
        return ""
    return str(text).encode("latin-1", "replace").decode("latin-1")


def generate_pdf(data: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 12, "Company Research Report", ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(2)
    pdf.set_draw_color(224, 224, 224)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Company name
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(22, 33, 62)
    pdf.cell(0, 9, _safe(data.get("companyName") or "Unknown Company"), ln=True)
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 6, f"Website: {_safe(data.get('website') or 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Phone: {_safe(data.get('phone') or 'N/A')}", ln=True)
    pdf.cell(0, 6, f"Address: {_safe(data.get('address') or 'N/A')}", ln=True)
    pdf.ln(4)

    def section_title(title):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(108, 92, 231)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(51, 51, 51)
        pdf.set_font("Helvetica", "", 10.5)

    if data.get("summary"):
        section_title("Company Summary")
        pdf.multi_cell(0, 5.5, _safe(data["summary"]))
        pdf.ln(3)

    products = data.get("products") or []
    if products:
        section_title("Products / Services")
        for p in products:
            pdf.multi_cell(0, 5.5, f"- {_safe(p)}")
        pdf.ln(3)

    pain_points = data.get("painPoints") or []
    if pain_points:
        section_title("AI-Generated Pain Points")
        for p in pain_points:
            pdf.multi_cell(0, 5.5, f"- {_safe(p)}")
        pdf.ln(3)

    competitors = data.get("competitors") or []
    if competitors:
        section_title("Competitor Analysis")
        for c in competitors:
            name = _safe(c.get("name", ""))
            website = _safe(c.get("website", "N/A"))
            pdf.multi_cell(0, 5.5, f"- {name} - {website}")

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
