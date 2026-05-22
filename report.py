"""Excel ve PDF rapor üretici."""
from __future__ import annotations
import io
from datetime import datetime
import pandas as pd

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def df_to_excel(sheets: dict[str, pd.DataFrame]) -> io.BytesIO:
    """Çoklu sheet'li excel üretir. sheets = {"sheet_adi": df, ...}"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            (df if not df.empty else pd.DataFrame([{"Bilgi": "Veri yok"}])).to_excel(
                writer, sheet_name=name[:31], index=False
            )
    buf.seek(0)
    return buf


def df_to_pdf(title: str, sections: list[tuple[str, pd.DataFrame]]) -> io.BytesIO | None:
    """Çok bölümlü PDF rapor."""
    if not REPORTLAB_OK:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elems.append(Paragraph(f"Oluşturma: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Normal"]))
    elems.append(Spacer(1, 12))

    for sec_title, df in sections:
        elems.append(Paragraph(f"<b>{sec_title}</b>", styles["Heading2"]))
        if df is None or df.empty:
            elems.append(Paragraph("(Veri yok)", styles["Normal"]))
        else:
            df2 = df.fillna("").astype(str)
            data = [df2.columns.tolist()] + df2.values.tolist()
            # Sütun genişliklerini eşit dağıt
            n = len(df2.columns)
            tbl = Table(data, repeatRows=1, colWidths=[(800 / n)] * n if n else None)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F7")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elems.append(tbl)
        elems.append(Spacer(1, 16))

    doc.build(elems)
    buf.seek(0)
    return buf
