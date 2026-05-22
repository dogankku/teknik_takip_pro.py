"""Barkod, QR ve PDF üretici yardımcıları."""
from __future__ import annotations
import io
import uuid
from datetime import datetime

try:
    import barcode as bc_lib
    from barcode.writer import ImageWriter
    BARCODE_OK = True
except ImportError:
    BARCODE_OK = False

try:
    import qrcode
    QR_OK = True
except ImportError:
    QR_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def make_barcode(code: str) -> io.BytesIO | None:
    if not BARCODE_OK or not code:
        return None
    try:
        CODE128 = bc_lib.get_barcode_class("code128")
        buf = io.BytesIO()
        CODE128(str(code), writer=ImageWriter()).write(buf)
        buf.seek(0)
        return buf
    except Exception:
        return None


def make_qr(data: str) -> io.BytesIO | None:
    if not QR_OK or not data:
        return None
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None


def yeni_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"


def yeni_barkod_id() -> str:
    return yeni_id("EKP")


def toplu_barkod_pdf(items: list[dict]) -> io.BytesIO | None:
    """A4 sayfada toplu barkod etiket PDF (3x8 grid = 24 etiket/sayfa).

    items: [{"id": "...", "ad": "...", "lokasyon": "..."}]
    """
    if not REPORTLAB_OK or not BARCODE_OK or not items:
        return None
    try:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        page_w, page_h = A4
        cols, rows = 3, 8
        margin_x, margin_y = 8 * mm, 10 * mm
        cell_w = (page_w - 2 * margin_x) / cols
        cell_h = (page_h - 2 * margin_y) / rows
        per_page = cols * rows

        CODE128 = bc_lib.get_barcode_class("code128")

        for i, it in enumerate(items):
            if i and i % per_page == 0:
                c.showPage()
            idx = i % per_page
            col = idx % cols
            row = idx // cols
            x = margin_x + col * cell_w
            y = page_h - margin_y - (row + 1) * cell_h

            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.rect(x + 1, y + 1, cell_w - 2, cell_h - 2)

            # Barkod
            bc_buf = io.BytesIO()
            CODE128(str(it.get("id", "")), writer=ImageWriter()).write(bc_buf)
            bc_buf.seek(0)
            img = ImageReader(bc_buf)
            c.drawImage(img, x + 4, y + cell_h * 0.35,
                        width=cell_w - 8, height=cell_h * 0.45, preserveAspectRatio=True)

            # Ad + lokasyon
            c.setFont("Helvetica-Bold", 8)
            ad = str(it.get("ad", ""))[:30]
            c.drawString(x + 4, y + cell_h - 12, ad)
            c.setFont("Helvetica", 7)
            lok = str(it.get("lokasyon", ""))[:30]
            c.drawString(x + 4, y + cell_h - 22, lok)

        c.save()
        buf.seek(0)
        return buf
    except Exception:
        return None
