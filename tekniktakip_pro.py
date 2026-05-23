"""Teknik Operasyon Sistemi — premium Xenia tarzı modern arayüz kabuğu."""
from __future__ import annotations

import importlib as _il
import traceback as _tb
from datetime import date

import streamlit as st

st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

from style import inject_css, sidebar_brand, sidebar_user_card, sidebar_status, nav_section, nav_item, top_header

inject_css()

from db import gs_connected, load_data
from auth import current_user, current_role, has_access, is_logged_in, logout


def _load(name: str):
    try:
        return _il.import_module(f"modules.{name}")
    except Exception as exc:
        print(f"STARTUP HATA: modules.{name} — {exc}\n{_tb.format_exc()}", flush=True)
        raise


# Modüller
login = _load("login")
ana_sayfa = _load("ana_sayfa")
checklist = _load("checklist")
ariza = _load("ariza")
ekipman = _load("ekipman")
daire = _load("daire")
talep = _load("talep")
bakim_plan = _load("bakim_plan")
aidat = _load("aidat")
stok = _load("stok")
sayac = _load("sayac")
rapor = _load("rapor")
vardiya = _load("vardiya")
personel = _load("personel")
kullanici = _load("kullanici")
ayarlar = _load("ayarlar")
lokasyon = _load("lokasyon")
sablon = _load("sablon")
tekrar = _load("tekrar")
aktivite_log = _load("aktivite_log")
media_yonetim = _load("media_yonetim")
maliyet = _load("maliyet")


# Login kontrolü
if not is_logged_in():
    login.render()
    st.stop()

u = current_user() or {}
rol = current_role() or "Sakin"


MENU_STRUCTURE = {
    "Admin": [
        (None, [
            ("🏠", "Ana Sayfa", "ana", ana_sayfa.render),
            ("📑", "Raporlar", "rapor", rapor.render),
        ]),
        ("MÜLK YÖNETİMİ", [
            ("🏢", "Daire & Sakin", "daire", daire.render),
            ("📨", "Talepler", "talep", talep.render),
            ("💰", "Aidat", "aidat", aidat.render),
        ]),
        ("OPERASYON", [
            ("🛠️", "Arıza Takip", "ariza", ariza.render),
            ("✅", "Kontroller", "checklist", checklist.render),
            ("📅", "Bakım Planı", "bakim", bakim_plan.render),
            ("🔄", "Vardiya", "vardiya", vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman", ekipman.render),
            ("📋", "Stok", "stok", stok.render),
            ("⚡", "Sayaç & Gider", "sayac", sayac.render),
            ("📍", "Lokasyonlar", "lokasyon", lokasyon.render),
        ]),
        ("ANALİZ & DENETİM", [
            ("💸", "Maliyet Paneli", "maliyet", maliyet.render),
            ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render),
            ("🖼️", "Medya Yönetimi", "media", media_yonetim.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar", "sablon", sablon.render),
            ("👥", "Personel", "personel", personel.render),
            ("👤", "Kullanıcılar", "kullanici", kullanici.render),
            ("⚙️", "Ayarlar", "ayarlar", ayarlar.render),
        ]),
    ],
    "Yonetici": [
        (None, [
            ("🏠", "Ana Sayfa", "ana", ana_sayfa.render),
            ("📑", "Raporlar", "rapor", rapor.render),
        ]),
        ("MÜLK YÖNETİMİ", [
            ("🏢", "Daire & Sakin", "daire", daire.render),
            ("📨", "Talepler", "talep", talep.render),
            ("💰", "Aidat", "aidat", aidat.render),
        ]),
        ("OPERASYON", [
            ("🛠️", "Arıza Takip", "ariza", ariza.render),
            ("✅", "Kontroller", "checklist", checklist.render),
            ("📅", "Bakım Planı", "bakim", bakim_plan.render),
            ("🔄", "Vardiya", "vardiya", vardiya.render),
            ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render),
        ]),
        ("ENVANTER & TESİS", [
            ("📦", "Ekipman & Barkod", "ekipman", ekipman.render),
            ("📋", "Stok", "stok", stok.render),
            ("⚡", "Sayaç & Gider", "sayac", sayac.render),
            ("📍", "Lokasyonlar", "lokasyon", lokasyon.render),
        ]),
        ("ANALİZ & DENETİM", [
            ("💸", "Maliyet Paneli", "maliyet", maliyet.render),
            ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render),
            ("🖼️", "Medya Yönetimi", "media", media_yonetim.render),
        ]),
        ("YÖNETİM", [
            ("📝", "Şablonlar", "sablon", sablon.render),
            ("👥", "Personel", "personel", personel.render),
            ("⚙️", "Ayarlar", "ayarlar", ayarlar.render),
        ]),
    ],
    "Teknisyen": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("İŞ EMİRLERİ", [
            ("📨", "Talepler", "talep", talep.render),
            ("🛠️", "Arıza", "ariza", ariza.render),
            ("✅", "Kontroller", "checklist", checklist.render),
            ("📅", "Bakım", "bakim", bakim_plan.render),
            ("🔁", "Tekrarlı", "tekrar", tekrar.render),
        ]),
        ("ENVANTER", [
            ("📦", "Ekipman", "ekipman", ekipman.render),
            ("📋", "Stok", "stok", stok.render),
        ]),
        ("VARDİYA", [("🔄", "Vardiya Defteri", "vardiya", vardiya.render)]),
    ],
    "Sakin": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("HİZMETLER", [
            ("📨", "Talep & Şikayet", "sakin_talep", talep.render),
            ("💰", "Aidat Borcum", "sakin_aidat", aidat.render),
        ]),
    ],
}

# Yönetici/Yonetici yazım farkını tolere et
if rol == "Yönetici" and "Yonetici" in MENU_STRUCTURE:
    sections = MENU_STRUCTURE["Yonetici"]
else:
    sections = MENU_STRUCTURE.get(rol, MENU_STRUCTURE["Sakin"])

_nav_keys: list[str] = []
_nav_funcs: dict[str, object] = {}
for _sec_label, _items in sections:
    for _icon, _label, _key, _func in _items:
        _nav_keys.append(_key)
        _nav_funcs[_key] = _func

default_key = _nav_keys[0] if _nav_keys else "ana"
if "active_module_key" not in st.session_state or st.session_state["active_module_key"] not in _nav_keys:
    st.session_state["active_module_key"] = default_key
current_key = st.session_state["active_module_key"]


with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad") or u.get("Ad Soyad") or u.get("Kullanıcı") or "Admin Kullanıcı", rol)
    sidebar_status(gs_connected())
    st.sidebar.markdown("---")

    for sec_label, items in sections:
        if sec_label:
            nav_section(sec_label)
        for icon, label, key, _func in items:
            if nav_item(icon, label, key, key == current_key):
                st.session_state["active_module_key"] = key
                st.rerun()

    st.sidebar.markdown("---")
    tarih = st.sidebar.date_input("📅 Tarih", date.today())
    if st.sidebar.button("🚪 Çıkış Yap", key="logout_btn", use_container_width=True):
        logout()
        st.rerun()


def _notif_count() -> int:
    n = 0
    try:
        da = load_data("ariza")
        if not da.empty and "Durum" in da.columns:
            n += int(da["Durum"].isin(["Açık", "Devam Ediyor", "Devam"]).sum())
    except Exception:
        pass
    try:
        dt = load_data("talep")
        if not dt.empty and "Durum" in dt.columns:
            n += int(dt["Durum"].isin(["Açık", "Atandı", "Devam", "Devam Ediyor"]).sum())
    except Exception:
        pass
    return n


top_header(_notif_count() if rol != "Sakin" else 0)

_active_key = st.session_state.get("active_module_key", default_key)
_active_func = _nav_funcs.get(_active_key)

if _active_func is None:
    st.error("Modül bulunamadı.")
elif has_access(_active_key) or _active_key.startswith("sakin_"):
    try:
        _active_func(tarih)
    except Exception as exc:
        st.error(f"⚠️ Modül hatası: {exc}")
        with st.expander("Hata detayı (geliştirici)"):
            st.code(_tb.format_exc())
else:
    st.error("Bu modüle erişim yetkiniz yok.")
