"""Teknik Operasyon Sistemi — premium Xenia-style Streamlit shell."""
from __future__ import annotations
import importlib
import traceback
from datetime import date
import streamlit as st

st.set_page_config(page_title="Teknik Operasyon Sistemi", layout="wide", page_icon="🏢", initial_sidebar_state="auto")

from style import inject_css, sidebar_brand, sidebar_user_card, sidebar_status, nav_section, nav_item_active, top_header
from db import gs_connected, load_data
from auth import current_user, current_role, has_access, is_logged_in, logout

inject_css()

def _load(name: str):
    try:
        return importlib.import_module(f"modules.{name}")
    except Exception as e:
        st.error(f"{name} modülü yüklenemedi: {e}")
        with st.expander("Geliştirici hata detayı"):
            st.code(traceback.format_exc())
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
duyuru = _load("duyuru")
rezervasyon = _load("rezervasyon")
ziyaretci = _load("ziyaretci")

if not is_logged_in():
    login.render()
    st.stop()

u = current_user() or {}
rol = current_role() or "Sakin"

MENU_STRUCTURE = {
    "Admin": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render), ("📑", "Raporlar", "rapor", rapor.render)]),
        ("MÜLK YÖNETİMİ", [("🏢", "Daire & Sakin", "daire", daire.render), ("📨", "Talepler", "talep", talep.render), ("💰", "Aidat", "aidat", aidat.render)]),
        ("OPERASYON", [("🛠️", "Arıza Takip", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım Planı", "bakim", bakim_plan.render), ("🔄", "Vardiya", "vardiya", vardiya.render), ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render)]),
        ("ENVANTER & TESİS", [("📦", "Ekipman & Barkod", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render), ("⚡", "Sayaç & Gider", "sayac", sayac.render), ("📍", "Lokasyonlar", "lokasyon", lokasyon.render)]),
        ("ANALİZ & DENETİM", [("💸", "Maliyet Paneli", "maliyet", maliyet.render), ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render), ("🖼️", "Medya Yönetimi", "media", media_yonetim.render)]),
        ("İLETİŞİM & GÜVENLİK", [("📢", "Duyurular", "duyuru", duyuru.render), ("📅", "Rezervasyon", "rezervasyon", rezervasyon.render), ("👥", "Ziyaretçi & Kargo", "ziyaretci", ziyaretci.render)]),
        ("YÖNETİM", [("📝", "Şablonlar", "sablon", sablon.render), ("👥", "Personel", "personel", personel.render), ("👤", "Kullanıcılar", "kullanici", kullanici.render), ("⚙️", "Ayarlar", "ayarlar", ayarlar.render)]),
    ],
    "Yonetici": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render), ("📑", "Raporlar", "rapor", rapor.render)]),
        ("MÜLK YÖNETİMİ", [("🏢", "Daire & Sakin", "daire", daire.render), ("📨", "Talepler", "talep", talep.render), ("💰", "Aidat", "aidat", aidat.render)]),
        ("OPERASYON", [("🛠️", "Arıza Takip", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım Planı", "bakim", bakim_plan.render), ("🔄", "Vardiya", "vardiya", vardiya.render), ("🔁", "Tekrarlı Görevler", "tekrar", tekrar.render)]),
        ("ENVANTER & TESİS", [("📦", "Ekipman & Barkod", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render), ("⚡", "Sayaç & Gider", "sayac", sayac.render), ("📍", "Lokasyonlar", "lokasyon", lokasyon.render)]),
        ("ANALİZ & DENETİM", [("💸", "Maliyet Paneli", "maliyet", maliyet.render), ("📋", "Aktivite Günlüğü", "aktivite_log", aktivite_log.render), ("🖼️", "Medya Yönetimi", "media", media_yonetim.render)]),
        ("İLETİŞİM & GÜVENLİK", [("📢", "Duyurular", "duyuru", duyuru.render), ("📅", "Rezervasyon", "rezervasyon", rezervasyon.render), ("👥", "Ziyaretçi & Kargo", "ziyaretci", ziyaretci.render)]),
        ("YÖNETİM", [("📝", "Şablonlar", "sablon", sablon.render), ("👥", "Personel", "personel", personel.render), ("⚙️", "Ayarlar", "ayarlar", ayarlar.render)]),
    ],
    "Teknisyen": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("İŞ EMİRLERİ", [("📨", "Talepler", "talep", talep.render), ("🛠️", "Arıza", "ariza", ariza.render), ("✅", "Kontroller", "checklist", checklist.render), ("📅", "Bakım", "bakim", bakim_plan.render), ("🔁", "Tekrarlı", "tekrar", tekrar.render)]),
        ("ENVANTER", [("📦", "Ekipman", "ekipman", ekipman.render), ("📋", "Stok", "stok", stok.render)]),
        ("VARDİYA & GÜVENLİK", [("🔄", "Vardiya Defteri", "vardiya", vardiya.render), ("👥", "Ziyaretçi & Kargo", "ziyaretci", ziyaretci.render)]),
    ],
    "Sakin": [
        (None, [("🏠", "Ana Sayfa", "ana", ana_sayfa.render)]),
        ("HİZMETLER", [
            ("📨", "Talep & Şikayet", "sakin_talep", talep.render),
            ("💰", "Aidat Borcum", "sakin_aidat", aidat.render),
            ("📢", "Duyurular", "sakin_duyuru", duyuru.render),
            ("📅", "Rezervasyon", "sakin_rezervasyon", rezervasyon.render),
            ("📦", "Kargolarım", "sakin_ziyaretci", ziyaretci.render),
        ]),
    ],
}
sections = MENU_STRUCTURE.get(rol, MENU_STRUCTURE["Sakin"])
nav_funcs = {key: func for _, items in sections for _, _, key, func in items}
nav_keys = list(nav_funcs.keys())
default_key = nav_keys[0] if nav_keys else "ana"
current_key = st.session_state.get("active_module_key", default_key)
if current_key not in nav_keys:
    current_key = default_key
st.session_state["active_module_key"] = current_key

with st.sidebar:
    sidebar_brand()
    sidebar_user_card(u.get("Ad_Soyad", "Kullanıcı"), rol)
    sidebar_status(gs_connected())
    st.markdown("---")
    for section_label, items in sections:
        if section_label:
            nav_section(section_label)
        for icon, label, key, _ in items:
            if key == st.session_state["active_module_key"]:
                nav_item_active(icon, label)
            else:
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state["active_module_key"] = key
                    st.rerun()
    st.markdown("---")
    tarih = st.date_input("📅 Tarih", date.today())
    if st.button("🚪 Çıkış Yap", key="logout_btn", use_container_width=True):
        logout()
        st.rerun()

def _notif_count() -> int:
    n = 0
    try:
        d = load_data("ariza")
        if not d.empty and "Durum" in d.columns:
            n += int(d["Durum"].isin(["Açık", "Devam Ediyor", "Beklemede"]).sum())
    except Exception: pass
    try:
        d = load_data("talep")
        if not d.empty and "Durum" in d.columns:
            n += int(d["Durum"].isin(["Açık", "Atandı", "Devam", "Devam Ediyor"]).sum())
    except Exception: pass
    return n

top_header(_notif_count() if rol != "Sakin" else 0)
active_key = st.session_state.get("active_module_key", default_key)
func = nav_funcs.get(active_key)
if func is None:
    st.error("Modül bulunamadı.")
elif has_access(active_key) or active_key.startswith("sakin_"):
    try:
        func(tarih)
    except Exception as ex:
        st.error(f"⚠️ Modül hatası: {ex}")
        with st.expander("Hata detayı (geliştirici)"):
            st.code(traceback.format_exc())
else:
    st.error("Bu modüle erişim yetkiniz yok.")
