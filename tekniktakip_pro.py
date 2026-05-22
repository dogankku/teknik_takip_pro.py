"""Teknik Operasyon Sistemi - Otel / Rezidans / Toplu Konut Yönetimi."""
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

from db import gs_connected
from auth import (current_user, current_role, has_access, is_logged_in,
                  logout, ensure_default_admin)
from modules import (login, ana_sayfa, checklist, ariza, ekipman, daire,
                     talep, bakim_plan, aidat, stok, sayac, rapor,
                     vardiya, personel, kullanici, ayarlar)


# ── Login kontrolü ───────────────────────────────────────────────────────────
if not is_logged_in():
    login.render()
    st.stop()

u = current_user()
rol = current_role()

# ── Rol bazlı menü ───────────────────────────────────────────────────────────
MENU_DEFS = {
    "Admin": [
        ("🏠 Ana Sayfa",         "ana",       ana_sayfa.render),
        ("📑 Raporlar",          "rapor",     rapor.render),
        ("🏢 Daire & Sakin",     "daire",     daire.render),
        ("📨 Talepler",          "talep",     talep.render),
        ("✅ Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️ Arıza Takip",       "ariza",     ariza.render),
        ("📅 Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦 Ekipman & Barkod",  "ekipman",   ekipman.render),
        ("📋 Stok",              "stok",      stok.render),
        ("💰 Aidat & Tahsilat",  "aidat",     aidat.render),
        ("⚡ Sayaç & Gider",     "sayac",     sayac.render),
        ("🔄 Vardiya Defteri",   "vardiya",   vardiya.render),
        ("👥 Personel",          "personel",  personel.render),
        ("👤 Kullanıcılar",      "kullanici", kullanici.render),
        ("⚙️ Ayarlar",           "ayarlar",   ayarlar.render),
    ],
    "Yonetici": [
        ("🏠 Ana Sayfa",         "ana",       ana_sayfa.render),
        ("📑 Raporlar",          "rapor",     rapor.render),
        ("🏢 Daire & Sakin",     "daire",     daire.render),
        ("📨 Talepler",          "talep",     talep.render),
        ("✅ Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️ Arıza Takip",       "ariza",     ariza.render),
        ("📅 Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦 Ekipman & Barkod",  "ekipman",   ekipman.render),
        ("📋 Stok",              "stok",      stok.render),
        ("💰 Aidat & Tahsilat",  "aidat",     aidat.render),
        ("⚡ Sayaç & Gider",     "sayac",     sayac.render),
        ("🔄 Vardiya Defteri",   "vardiya",   vardiya.render),
        ("👥 Personel",          "personel",  personel.render),
        ("⚙️ Ayarlar",           "ayarlar",   ayarlar.render),
    ],
    "Teknisyen": [
        ("🏠 Ana Sayfa",         "ana",       ana_sayfa.render),
        ("📨 Talepler",          "talep",     talep.render),
        ("✅ Kontrol Listeleri", "checklist", checklist.render),
        ("🛠️ Arıza Takip",       "ariza",     ariza.render),
        ("📅 Bakım Planı",       "bakim",     bakim_plan.render),
        ("📦 Ekipman",           "ekipman",   ekipman.render),
        ("📋 Stok",              "stok",      stok.render),
        ("🔄 Vardiya Defteri",   "vardiya",   vardiya.render),
    ],
    "Sakin": [
        ("🏠 Ana Sayfa",         "ana",          ana_sayfa.render),
        ("📨 Talep & Şikayet",   "sakin_talep",  talep.render),
        ("💰 Aidat Borcum",      "sakin_aidat",  aidat.render),
    ],
}

menu_items = MENU_DEFS.get(rol, MENU_DEFS["Sakin"])

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏢 Teknik Operasyon")
    st.markdown(f"**{u.get('Ad_Soyad', '')}**  \n_{rol}_")
    st.markdown("---")

    if gs_connected():
        st.success("☁️ Google Sheets bağlı")
    else:
        st.info("💾 Yerel CSV modu")

    st.markdown("---")
    labels = [m[0] for m in menu_items]
    secim = st.radio("Menü", labels, label_visibility="collapsed", key="menu_radio")
    st.markdown("---")
    tarih = st.date_input("📅 Tarih", date.today())
    st.markdown("---")
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        logout()
        st.rerun()

# ── Modül çalıştır ───────────────────────────────────────────────────────────
secili_modul = next((m for m in menu_items if m[0] == secim), None)
if secili_modul:
    label, key, func = secili_modul
    if has_access(key) or key.startswith("sakin_"):
        func(tarih)
    else:
        st.error("Bu modüle erişim yetkiniz yok.")
