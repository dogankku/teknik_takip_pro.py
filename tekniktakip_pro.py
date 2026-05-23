"""Teknik Operasyon Sistemi — modern Xenia tarzı Streamlit uygulama kabuğu."""
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
from db import gs_connected, load_data
from auth import current_user, current_role, has_access, is_logged_in, logout

inject_css()


def _load(name: str):
    try:
        return _il.import_module(f"modules.{name}")
    except Exception as exc:
        print(f"STARTUP HATA: modules.{name} — {exc}\n{_tb.format_exc()}", flush=True)
        raise


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

if not is_logged_in():
    login.render()
    st.stop()

u = current_user() or {}
rol = current_role()

MENU_STRUCTURE = {
    "Admin": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render), ("📑", "Raporlar", "rapor", rapor.render)]),
        ("MÜLK YÖNETİMİ", [("🏢", "Daire & Sakin", "daire", daire.render), ("📨", "Talepler", "talep", talep.render), ("💰", "Aidat", "aidat", aidat.render)]),
        ("OPERASYON", [("🛠️", "Arıza Takip", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım Planı", "bakim", bakim_plan.render), ("🔄", "Vardiya", "vardiya", vardiya.render), ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render)]),
        ("ENVANTER & TESİS", [("📦", "Ekipman & Barkod", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render), ("⚡", "Sayaç & Gider", "sayac", sayac.render), ("📍", "Lokasyonlar", "lokasyon", lokasyon.render)]),
        ("ANALİZ & DENETİM", [("💸", "Maliyet Paneli", "maliyet", maliyet.render), ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render), ("🖼️", "Medya Yönetimi", "media", media_yonetim.render)]),
        ("YÖNETİM", [("📝", "Şablonlar", "sablon", sablon.render), ("👥", "Personel", "personel", personel.render), ("👤", "Kullanıcılar", "kullanici", kullanici.render), ("⚙️", "Ayarlar", "ayarlar", ayarlar.render)]),
    ],
    "Yonetici": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render), ("📑", "Raporlar", "rapor", rapor.render)]),
        ("MÜLK YÖNETİMİ", [("🏢", "Daire & Sakin", "daire", daire.render), ("📨", "Talepler", "talep", talep.render), ("💰", "Aidat", "aidat", aidat.render)]),
        ("OPERASYON", [("🛠️", "Arıza Takip", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım Planı", "bakim", bakim_plan.render), ("🔄", "Vardiya", "vardiya", vardiya.render), ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render)]),
        ("ENVANTER & TESİS", [("📦", "Ekipman & Barkod", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render), ("⚡", "Sayaç & Gider", "sayac", sayac.render), ("📍", "Lokasyonlar", "lokasyon", lokasyon.render)]),
        ("ANALİZ & DENETİM", [("💸", "Maliyet Paneli", "maliyet", maliyet.render), ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render), ("🖼️", "Medya Yönetimi", "media", media_yonetim.render)]),
        ("YÖNETİM", [("📝", "Şablonlar", "sablon", sablon.render), ("👥", "Personel", "personel", personel.render), ("⚙️", "Ayarlar", "ayarlar", ayarlar.render)]),
    ],
    "Teknisyen": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("İŞ EMİRLERİ", [("📨", "Talepler", "talep", talep.render), ("🛠️", "Arıza", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım", "bakim", bakim_plan.render), ("🔁", "Tekrarlı", "tekrar", tekrar.render)]),
        ("ENVANTER", [("📦", "Ekipman", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render)]),
        ("VARDİYA", [("🔄", "Vardiya Defteri", "vardiya", vardiya.render)]),
    ],
    "Sakin": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("HİZMETLER", [("📨", "Talep & Şikayet", "sakin_talep", talep.render), ("💰", "Aidat Borcum", "sakin_aidat", aidat.render)]),
    ],
}

sections = MENU_STRUCTURE.get(rol, MENU_STRUCTURE["Sakin"])

nav_keys: list[str] = []
nav_funcs: dict[str, object] = {}
for _, items in sections:
    for _, _, key, func in items:
        nav_keys.append(key)
        nav_funcs[key] = func

default_key = nav_keys[0] if nav_keys else "ana"
current_key = st.session_state.get("active_module_key", default_key)
if current_key not in nav_keys:
    current_key = default_key
# ÖNEMLİ FIX: Eski dosyada burası default_key'e set ediliyordu; menü her rerun'da Ana Sayfa'ya dönüyordu.
st.session_state["active_module_key"] = current_key

with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad", "Admin"), rol)
    sidebar_status(gs_connected())
    st.sidebar.markdown("---")

    for sec_label, items in sections:
        if sec_label:
            nav_section(sec_label)
        for icon, label, key, _ in items:
            if nav_item(icon, label, key, key == st.session_state["active_module_key"]):
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
            n += int(da["Durum"].isin(["Açık", "Devam Ediyor"]).sum())
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

active_key = st.session_state.get("active_module_key", default_key)
active_func = nav_funcs.get(active_key)
if active_func is None:
    st.error("Modül bulunamadı.")
elif has_access(active_key) or active_key.startswith("sakin_"):
    try:
        active_func(tarih)
    except Exception as ex:
        st.error(f"⚠️ Modül hatası: {ex}")
        with st.expander("Hata detayı (geliştirici)"):
            st.code(_tb.format_exc())
else:
    st.error("Bu modüle erişim yetkiniz yok.")
