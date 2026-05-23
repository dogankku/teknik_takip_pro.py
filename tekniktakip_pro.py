"""Teknik Operasyon Sistemi — Xenia tarzı modern arayüz."""
import sys, importlib as _il, traceback as _tb
print("STARTUP: tekniktakip_pro.py başlatılıyor", flush=True)

import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

from style import (inject_css, sidebar_brand, sidebar_user_card,
                   sidebar_status, nav_section)
inject_css()

from db import gs_connected
from auth import current_user, current_role, has_access, is_logged_in, logout


def _load(name: str):
    try:
        m = _il.import_module(f"modules.{name}")
        print(f"STARTUP: {name} yüklendi ✓", flush=True)
        return m
    except Exception as _e:
        print(f"STARTUP HATA: {name} — {_e}\n{_tb.format_exc()}", flush=True)
        raise

login         = _load("login")
ana_sayfa     = _load("ana_sayfa")
checklist     = _load("checklist")
ariza         = _load("ariza")
ekipman       = _load("ekipman")
daire         = _load("daire")
talep         = _load("talep")
bakim_plan    = _load("bakim_plan")
aidat         = _load("aidat")
stok          = _load("stok")
sayac         = _load("sayac")
rapor         = _load("rapor")
vardiya       = _load("vardiya")
personel      = _load("personel")
kullanici     = _load("kullanici")
ayarlar       = _load("ayarlar")
lokasyon      = _load("lokasyon")
sablon        = _load("sablon")
tekrar        = _load("tekrar")
aktivite_log  = _load("aktivite_log")
media_yonetim = _load("media_yonetim")
maliyet       = _load("maliyet")

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
            ("🛠️", "Arıza Takip",       "ariza",     ariza.render),
            ("✅", "Kontroller",        "checklist", checklist.render),
            ("📅", "Bakım Planı",       "bakim",     bakim_plan.render),
            ("🔄", "Vardiya",           "vardiya",   vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar",    tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman",  ekipman.render),
            ("📋", "Stok",             "stok",     stok.render),
            ("⚡", "Sayaç & Gider",    "sayac",    sayac.render),
            ("📍", "Lokasyonlar",      "lokasyon", lokasyon.render),
        ]),
        ("ANALİZ & DENETİM", [
            ("💸", "Maliyet Paneli",   "maliyet",      maliyet.render),
            ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render),
            ("🖼️", "Medya Yönetimi",   "media",        media_yonetim.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar",    "sablon",    sablon.render),
            ("👥", "Personel",     "personel",  personel.render),
            ("👤", "Kullanıcılar", "kullanici", kullanici.render),
            ("⚙️", "Ayarlar",      "ayarlar",   ayarlar.render),
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
            ("🛠️", "Arıza Takip",       "ariza",     ariza.render),
            ("✅", "Kontroller",        "checklist", checklist.render),
            ("📅", "Bakım Planı",       "bakim",     bakim_plan.render),
            ("🔄", "Vardiya",           "vardiya",   vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar",    tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman",  ekipman.render),
            ("📋", "Stok",             "stok",     stok.render),
            ("⚡", "Sayaç & Gider",    "sayac",    sayac.render),
            ("📍", "Lokasyonlar",      "lokasyon", lokasyon.render),
        ]),
        ("ANALİZ & DENETİM", [
            ("💸", "Maliyet Paneli",   "maliyet",      maliyet.render),
            ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render),
            ("🖼️", "Medya Yönetimi",   "media",        media_yonetim.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar", "sablon",   sablon.render),
            ("👥", "Personel",  "personel", personel.render),
            ("⚙️", "Ayarlar",   "ayarlar",  ayarlar.render),
        ]),
    ],
    "Teknisyen": [
        (None, [
            ("🏠", "Ana Sayfa", "ana", ana_sayfa.render),
        ]),
        ("İŞ EMİRLERİ", [
            ("📨", "Talepler",         "talep",     talep.render),
            ("🛠️", "Arıza",            "ariza",     ariza.render),
            ("✅", "Kontroller",       "checklist", checklist.render),
            ("📅", "Bakım",            "bakim",     bakim_plan.render),
            ("🔁", "Tekrarlı",         "tekrar",    tekrar.render),
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

# ── Düz nav listesi ───────────────────────────────────────────────────────────
_nav_labels: list[str]       = []
_nav_keys:   list[str]       = []
_nav_funcs:  dict            = {}

for _sec_label, _items in sections:
    for _icon, _label, _key, _func in _items:
        _nav_labels.append(f"{_icon}   {_label}")
        _nav_keys.append(_key)
        _nav_funcs[_key] = _func

default_key = _nav_keys[0] if _nav_keys else "ana"
current_key = st.session_state.get("active_module_key", default_key)
if current_key not in _nav_keys:
    current_key = default_key
    st.session_state["active_module_key"] = default_key

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad", ""), rol)
    sidebar_status(gs_connected())
    st.sidebar.markdown("---")

    # Section başlıklarını radio'nun üstüne markdown olarak ekle
    for _sec_label, _items in sections:
        if _sec_label:
            st.sidebar.markdown(
                f'<div class="nav-section-title">{_sec_label}</div>',
                unsafe_allow_html=True,
            )
        for _icon, _label, _key, _ in _items:
            # Her modül için ayrı buton — on_click ile state güncelle
            _is_active = (_key == current_key)
            if _is_active:
                st.sidebar.markdown(
                    f'<div class="nav-item-active">'
                    f'<span style="font-size:1rem">{_icon}</span>'
                    f'<span>{_label}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                def _make_cb(_k=_key):
                    def _cb():
                        st.session_state["active_module_key"] = _k
                    return _cb

                st.sidebar.button(
                    f"{_icon}   {_label}",
                    key=f"nav_{_key}",
                    use_container_width=True,
                    on_click=_make_cb(),
                )

    st.sidebar.markdown("---")
    tarih = st.sidebar.date_input("📅 Tarih", date.today())

    if st.sidebar.button("🚪   Çıkış Yap", key="logout_btn",
                          use_container_width=True):
        logout()
        st.rerun()

# ── Aktif modülü çalıştır ─────────────────────────────────────────────────────
_active_key  = st.session_state.get("active_module_key", default_key)
_active_func = _nav_funcs.get(_active_key)

if _active_func is None:
    st.error("Modül bulunamadı.")
elif has_access(_active_key) or _active_key.startswith("sakin_"):
    try:
        _active_func(tarih)
    except Exception as _ex:
        import traceback as _traceback
        st.error(f"⚠️ Modül hatası: {_ex}")
        with st.expander("Hata detayı (geliştirici)"):
            st.code(_traceback.format_exc())
else:
    st.error("Bu modüle erişim yetkiniz yok.")
