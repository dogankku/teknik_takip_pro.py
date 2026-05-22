"""Teknik Operasyon Sistemi — Xenia tarzı modern arayüz."""
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

from style import (inject_css, sidebar_brand, sidebar_user_card,
                   sidebar_status, nav_section, nav_item)
inject_css()

from db import gs_connected
from auth import current_user, current_role, has_access, is_logged_in, logout
from modules import (login, ana_sayfa, checklist, ariza, ekipman, daire,
                     talep, bakim_plan, aidat, stok, sayac, rapor,
                     vardiya, personel, kullanici, ayarlar,
                     lokasyon, sablon, tekrar)

# ── Login kontrolü ────────────────────────────────────────────────────────────
if not is_logged_in():
    login.render()
    st.stop()

u   = current_user()
rol = current_role()

# ── Menü yapısı ──────────────────────────────────────────────────────────────
MENU_STRUCTURE = {
    "Admin": [
        (None, [
            ("🏠", "Ana Sayfa",  "ana",   ana_sayfa.render),
            ("📑", "Raporlar",   "rapor", rapor.render),
        ]),
        ("MÜLK YÖNETİMİ", [
            ("🏢", "Daire & Sakin", "daire", daire.render),
            ("📨", "Talepler",      "talep", talep.render),
            ("💰", "Aidat",         "aidat", aidat.render),
        ]),
        ("OPERASYON", [
            ("🛠️", "Arıza Takip",   "ariza",     ariza.render),
            ("✅", "Kontroller",    "checklist", checklist.render),
            ("📅", "Bakım Planı",   "bakim",     bakim_plan.render),
            ("🔄", "Vardiya",       "vardiya",   vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman",  ekipman.render),
            ("📋", "Stok",             "stok",     stok.render),
            ("⚡", "Sayaç & Gider",    "sayac",    sayac.render),
            ("📍", "Lokasyonlar",      "lokasyon", lokasyon.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar",     "sablon",    sablon.render),
            ("👥", "Personel",      "personel",  personel.render),
            ("👤", "Kullanıcılar",  "kullanici", kullanici.render),
            ("⚙️", "Ayarlar",       "ayarlar",   ayarlar.render),
        ]),
    ],
    "Yonetici": [
        (None, [
            ("🏠", "Ana Sayfa",  "ana",   ana_sayfa.render),
            ("📑", "Raporlar",   "rapor", rapor.render),
        ]),
        ("MÜLK YÖNETİMİ", [
            ("🏢", "Daire & Sakin", "daire", daire.render),
            ("📨", "Talepler",      "talep", talep.render),
            ("💰", "Aidat",         "aidat", aidat.render),
        ]),
        ("OPERASYON", [
            ("🛠️", "Arıza Takip",   "ariza",     ariza.render),
            ("✅", "Kontroller",    "checklist", checklist.render),
            ("📅", "Bakım Planı",   "bakim",     bakim_plan.render),
            ("🔄", "Vardiya",       "vardiya",   vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman",  ekipman.render),
            ("📋", "Stok",             "stok",     stok.render),
            ("⚡", "Sayaç & Gider",    "sayac",    sayac.render),
            ("📍", "Lokasyonlar",      "lokasyon", lokasyon.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar",  "sablon",   sablon.render),
            ("👥", "Personel",   "personel", personel.render),
            ("⚙️", "Ayarlar",    "ayarlar",  ayarlar.render),
        ]),
    ],
    "Teknisyen": [
        (None, [
            ("🏠", "Ana Sayfa", "ana", ana_sayfa.render),
        ]),
        ("İŞ EMİRLERİ", [
            ("📨", "Talepler",     "talep",     talep.render),
            ("🛠️", "Arıza",        "ariza",     ariza.render),
            ("✅", "Kontroller",   "checklist", checklist.render),
            ("📅", "Bakım",        "bakim",     bakim_plan.render),
            ("🔁", "Tekrarlı",     "tekrar",    tekrar.render),
        ]),
        ("ENVANTER", [
            ("📦", "Ekipman", "ekipman", ekipman.render),
            ("📋", "Stok",    "stok",    stok.render),
        ]),
        ("VARDİYA", [
            ("🔄", "Vardiya Defteri", "vardiya", vardiya.render),
        ]),
    ],
    "Sakin": [
        (None, [
            ("🏠", "Ana Sayfa", "ana", ana_sayfa.render),
        ]),
        ("HİZMETLER", [
            ("📨", "Talep & Şikayet", "sakin_talep", talep.render),
            ("💰", "Aidat Borcum",    "sakin_aidat", aidat.render),
        ]),
    ],
}

sections = MENU_STRUCTURE.get(rol, MENU_STRUCTURE["Sakin"])

all_items = [item for _, items in sections for item in items]
default_key = all_items[0][2] if all_items else "ana"
current_key = st.session_state.get("active_module_key", default_key)
if current_key not in [i[2] for i in all_items]:
    current_key = default_key
    st.session_state["active_module_key"] = default_key

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad", ""), rol)
    sidebar_status(gs_connected())

    for section_label, items in sections:
        if section_label:
            nav_section(section_label)
        for icon, label, key, _ in items:
            if nav_item(icon, label, key, is_active=(key == current_key)):
                st.session_state["active_module_key"] = key
                st.rerun()

    st.sidebar.markdown('<div class="nav-section-title">&nbsp;</div>',
                        unsafe_allow_html=True)
    tarih = st.date_input("📅 Tarih", date.today())
    st.sidebar.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    if st.sidebar.button("🚪   Çıkış Yap", key="logout_btn",
                          use_container_width=True):
        logout()
        st.rerun()

# ── Aktif modülü çalıştır ─────────────────────────────────────────────────────
active = next((it for it in all_items if it[2] == current_key), all_items[0])
_, _, key, func = active
if has_access(key) or key.startswith("sakin_"):
    func(tarih)
else:
    st.error("Bu modüle erişim yetkiniz yok.")
