"""Fotoğraf yükleme, sıkıştırma, base64 saklama."""
from __future__ import annotations
import base64
import io
from datetime import datetime
import streamlit as st
from PIL import Image
from db import load_data, save_data
from barkod import yeni_id


MAX_BASE64_SIZE = 35_000  # ~50K char limit, leave room
TARGET_WIDTH = 800
JPEG_QUALITY_START = 75


def compress_image(file_bytes: bytes) -> tuple[bytes, str, int]:
    """Görseli sıkıştır, JPEG'e çevir. (bytes, mime, byte_size) döndürür."""
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")

    # Boyut ayarla
    if img.width > TARGET_WIDTH:
        ratio = TARGET_WIDTH / img.width
        new_h = int(img.height * ratio)
        img = img.resize((TARGET_WIDTH, new_h), Image.LANCZOS)

    # Quality'yi düşürerek boyutu hedefe çek
    for q in [JPEG_QUALITY_START, 65, 55, 45, 35, 25]:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q, optimize=True)
        b64_size = len(base64.b64encode(buf.getvalue()))
        if b64_size <= MAX_BASE64_SIZE:
            buf.seek(0)
            return buf.getvalue(), "image/jpeg", b64_size

    # Hala büyükse - boyutu daha da küçült
    img = img.resize((500, int(img.height * 500 / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=40, optimize=True)
    return buf.getvalue(), "image/jpeg", len(base64.b64encode(buf.getvalue()))


def upload_media(uploaded_file, parent_tip: str, parent_id: str, yukleyen: str) -> tuple[bool, str]:
    """Streamlit file_uploader'dan gelen dosyayı kaydet."""
    if not uploaded_file:
        return False, "Dosya yok"
    try:
        raw = uploaded_file.read()
        compressed, mime, size = compress_image(raw)
        b64 = base64.b64encode(compressed).decode("ascii")

        row = {
            "Media_ID": yeni_id("MED"),
            "Parent_Tip": parent_tip,
            "Parent_ID": parent_id,
            "Dosya_Adi": uploaded_file.name,
            "Mime": mime,
            "Boyut": len(compressed),
            "Base64": b64,
            "Yukleme_Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Yukleyen": yukleyen,
        }
        df = load_data("media")
        import pandas as pd
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_data(df, "media")
        return True, "Yüklendi"
    except Exception as e:
        return False, f"Hata: {e}"


def get_media(parent_tip: str, parent_id: str):
    """Belirli bir parent'a ait fotoğrafları döndürür (dict listesi)."""
    df = load_data("media")
    if df.empty:
        return []
    m = df[(df["Parent_Tip"].astype(str) == parent_tip) &
           (df["Parent_ID"].astype(str) == str(parent_id))]
    return m.to_dict("records")


def media_bytes(b64_str: str) -> bytes:
    """Base64'ten image bytes'a çevir."""
    try:
        return base64.b64decode(b64_str)
    except Exception:
        return b""


def render_photo_grid(parent_tip: str, parent_id: str, cols_per_row: int = 4):
    """Bir görev/talep altındaki tüm fotoğrafları grid olarak göster."""
    items = get_media(parent_tip, parent_id)
    if not items:
        return
    st.markdown(f"**📸 Fotoğraflar ({len(items)})**")
    cols = st.columns(cols_per_row)
    for i, m in enumerate(items):
        with cols[i % cols_per_row]:
            data = media_bytes(m.get("Base64", ""))
            if data:
                st.image(data, caption=m.get("Dosya_Adi", ""), use_container_width=True)
                cap = f"📅 {m.get('Yukleme_Tarihi', '')[:10]} • 👤 {m.get('Yukleyen', '')}"
                st.caption(cap)


def upload_widget(parent_tip: str, parent_id: str, yukleyen: str,
                   label: str = "📸 Fotoğraf ekle"):
    """File uploader widget + upload aksiyonu."""
    files = st.file_uploader(
        label,
        type=["jpg", "jpeg", "png", "gif", "webp"],
        accept_multiple_files=True,
        key=f"upl_{parent_tip}_{parent_id}",
    )
    if files and st.button(f"⬆️ {len(files)} fotoğrafı yükle",
                            key=f"upbtn_{parent_tip}_{parent_id}",
                            use_container_width=True):
        ok_count = 0
        for f in files:
            ok, msg = upload_media(f, parent_tip, parent_id, yukleyen)
            if ok:
                ok_count += 1
            else:
                st.warning(f"{f.name}: {msg}")
        st.success(f"{ok_count}/{len(files)} fotoğraf yüklendi.")
        st.rerun()
