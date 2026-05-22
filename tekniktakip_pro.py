"""Teknik Operasyon Sistemi — Otel / Rezidans / Toplu Konut."""
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

# Style önce inject edilmeli
from style import inject_css, sidebar_brand, sidebar_user_card
inject_css()

from db import gs_connected
from auth import current_user, current_role, has_access, is_logged_in, logout, ensure_default_admin
from modules import (login, ana_sayfa, checklist, ariza, ekipman, daire,
                     talep, bakim_plan, aidat, stok, sayac, rapor,
                     vardiya, personel, kullanici, ayarlar)

# ── Login kontrolü ────────────────────────────────────────────────────────────
if not is_logged_in():
    login.render()
    st.stop()

u   = current_user()
rol = current_role()

# ── Menü tanımları ────────────────────────────────────────────────────────────
MENU_DEFS = {
    "Admin": [
        ("🏠  Ana Sayfa",         "ana",       ana_sayfa.render),
        ("📑  Raporlar",          "rapor",     rapor.render),
        ("─────────────────", None, None),
        ("🏢  Daire & Sakin",     "daire",     daire.render),
        ("📨  Talepler",          "talep",     talep.render),
        ("💰  Aidat & Tahsilat",  "aidat",     aidat.render),
        ("─────────────────", None, None),
        ("✅  Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️  Arıza Takip",       "ariza",     ariza.render),
        ("📅  Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦  Ekipman & Barkod",  "ekipman",   ekipman.render),
        ("📋  Stok",              "stok",      stok.render),
        ("⚡  Sayaç & Gider",     "sayac",     sayac.render),
        ("─────────────────", None, None),
        ("🔄  Vardiya Defteri",   "vardiya",   vardiya.render),
        ("👥  Personel",          "personel",  personel.render),
        ("👤  Kullanıcılar",      "kullanici", kullanici.render),
        ("⚙️  Ayarlar",           "ayarlar",   ayarlar.render),
    ],
    "Yonetici": [
        ("🏠  Ana Sayfa",         "ana",       ana_sayfa.render),
        ("📑  Raporlar",          "rapor",     rapor.render),
        ("─────────────────", None, None),
        ("🏢  Daire & Sakin",     "daire",     daire.render),
        ("📨  Talepler",          "talep",     talep.render),
        ("💰  Aidat & Tahsilat",  "aidat",     aidat.render),
        ("─────────────────", None, None),
        ("✅  Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️  Arıza Takip",       "ariza",     ariza.render),
        ("📅  Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦  Ekipman & Barkod",  "ekipman",   ekipman.render),
        ("📋  Stok",              "stok",      stok.render),
        ("⚡  Sayaç & Gider",     "sayac",     sayac.render),
        ("─────────────────", None, None),
        ("🔄  Vardiya Defteri",   "vardiya",   vardiya.render),
        ("👥  Personel",          "personel",  personel.render),
        ("⚙️  Ayarlar",           "ayarlar",   ayarlar.render),
    ],
    "Teknisyen": [
        ("🏠  Ana Sayfa",         "ana",       ana_sayfa.render),
        ("─────────────────", None, None),
        ("📨  Talepler",          "talep",     talep.render),
        ("✅  Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️  Arıza Takip",       "ariza",     ariza.render),
        ("📅  Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦  Ekipman",           "ekipman",   ekipman.render),
        ("📋  Stok",              "stok",      stok.render),
        ("─────────────────", None, None),
        ("🔄  Vardiya Defteri",   "vardiya",   vardiya.render),
    ],
    "Sakin": [
        ("🏠  Ana Sayfa",         "ana",          ana_sayfa.render),
        ("📨  Talep & Şikayet",   "sakin_talep",  talep.render),
        ("💰  Aidat Borcum",      "sakin_aidat",  aidat.render),
    ],
}

menu_items = MENU_DEFS.get(rol, MENU_DEFS["Sakin"])
# Ayırıcıları menüden çıkar (sadece navigation için)
nav_items = [(lbl, key, fn) for lbl, key, fn in menu_items if key is not None]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad", ""), rol)

    # Bağlantı durumu
    if gs_connected():
        st.markdown("""<div style="font-size:.72rem;color:#10B981;padding:4px 12px 8px;
                       display:flex;align-items:center;gap:6px;">
                       <span style="width:6px;height:6px;border-radius:50%;
                       background:#10B981;display:inline-block;"></span>
                       Google Sheets bağlı</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="font-size:.72rem;color:#F59E0B;padding:4px 12px 8px;
                       display:flex;align-items:center;gap:6px;">
                       <span style="width:6px;height:6px;border-radius:50%;
                       background:#F59E0B;display:inline-block;"></span>
                       Yerel CSV modu</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Menü listesi
    nav_labels = [m[0] for m in nav_items]
    secim = st.radio("Menü", nav_labels, label_visibility="collapsed",
                     key="menu_radio")

    st.markdown("---")
    tarih = st.date_input("📅 Tarih", date.today())
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🚪  Çıkış Yap", use_container_width=True):
        logout()
        st.rerun()

# ── Aktif modülü çalıştır ─────────────────────────────────────────────────────
secili = next((m for m in nav_items if m[0] == secim), None)
if secili:
    _, key, func = secili
    if has_access(key) or (key or "").startswith("sakin_"):
        func(tarih)
    else:
        st.error("Bu modüle erişim yetkiniz yok.")
