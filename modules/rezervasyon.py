"""Rezervasyon modülü — ortak alan rezervasyonları."""
import streamlit as st
import pandas as pd
from datetime import date, time, timedelta
from db import load_data, save_data
from style import section_header, data_table, status_badge
from auth import current_user, current_role
from barkod import yeni_id


ORTAK_ALANLAR = [
    "Toplantı Salonu", "Spor Salonu", "Yüzme Havuzu", "Çocuk Oyun Alanı",
    "Barbekü Alanı", "Çamaşırhane", "Misafir Odası", "Teras", "Konferans Odası", "Diğer",
]
SAAT_DILIMLERI = [
    "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
    "16:00-18:00", "18:00-20:00", "20:00-22:00",
]
REZ_DURUMLARI = ["Onay Bekliyor", "Onaylandı", "İptal", "Tamamlandı"]


def render(secilen_tarih: date):
    rol = current_role()
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")
    daire_id = u.get("Daire_ID", "")

    if rol == "Sakin":
        _sakin_view(kullanici, daire_id)
        return

    section_header("Rezervasyon", "Ortak alan rezervasyon yönetimi", pill="OPERASYON")

    tabs = st.tabs(["📅 Rezervasyonlar", "➕ Yeni Rezervasyon", "🏢 Alan Yönetimi"])

    with tabs[0]:
        _liste_yonetici()
    with tabs[1]:
        _yeni_form(kullanici, daire_id, secilen_tarih)
    with tabs[2]:
        _alan_yonetimi()


def _liste_yonetici():
    df = load_data("rezervasyon")
    if df.empty:
        st.info("Henüz rezervasyon yok.")
        return

    c1, c2, c3 = st.columns(3)
    alan_f = c1.selectbox("Alan", ["Tümü"] + ORTAK_ALANLAR)
    durum_f = c2.selectbox("Durum", ["Tümü"] + REZ_DURUMLARI)
    c3.markdown("")
    bas = c1.date_input("Başlangıç", date.today(), key="rez_bas")
    bit = c2.date_input("Bitiş", date.today() + timedelta(days=7), key="rez_bit")

    g = df.copy()
    if alan_f != "Tümü":
        g = g[g["Alan"] == alan_f]
    if durum_f != "Tümü":
        g = g[g["Durum"] == durum_f]
    try:
        d = pd.to_datetime(g["Tarih"], errors="coerce")
        g = g[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]
    except Exception:
        pass

    # Özet metrikler
    c1m, c2m, c3m, c4m = st.columns(4)
    c1m.metric("Toplam", len(g))
    c2m.metric("Onay Bekliyor", len(g[g["Durum"] == "Onay Bekliyor"]) if "Durum" in g.columns else 0)
    c3m.metric("Onaylandı", len(g[g["Durum"] == "Onaylandı"]) if "Durum" in g.columns else 0)
    c4m.metric("İptal", len(g[g["Durum"] == "İptal"]) if "Durum" in g.columns else 0)

    data_table(
        g.sort_values("Tarih", ascending=False) if not g.empty else g,
        [("Rezervasyon_ID", "ID"), ("Tarih", "Tarih"), ("Saat", "Saat"),
         ("Alan", "Alan"), ("Daire_ID", "Daire"), ("Talep_Eden", "Talep Eden"),
         ("Katilimci", "Katılımcı"), ("Durum", "Durum"), ("Notlar", "Not")],
        id_cols=["Rezervasyon_ID"], status_cols=["Durum"], avatar_cols=["Talep_Eden"],
        max_text=40,
    )

    st.divider()
    if not df.empty:
        st.subheader("⚡ Hızlı Onay / İptal")
        bekliyenler = df[df["Durum"] == "Onay Bekliyor"]
        if bekliyenler.empty:
            st.success("Bekleyen rezervasyon yok.")
        else:
            for _, row in bekliyenler.iterrows():
                rid = str(row.get("Rezervasyon_ID", ""))
                col_info, col_onay, col_iptal = st.columns([3, 1, 1])
                col_info.markdown(
                    f"**{row.get('Alan','')}** · {row.get('Tarih','')} {row.get('Saat','')} "
                    f"— Daire {row.get('Daire_ID','')} ({row.get('Talep_Eden','')})"
                )
                if col_onay.button("✅", key=f"onay_{rid}", help="Onayla"):
                    df.loc[df["Rezervasyon_ID"] == rid, "Durum"] = "Onaylandı"
                    save_data(df, "rezervasyon")
                    st.rerun()
                if col_iptal.button("❌", key=f"iptal_{rid}", help="İptal Et"):
                    df.loc[df["Rezervasyon_ID"] == rid, "Durum"] = "İptal"
                    save_data(df, "rezervasyon")
                    st.rerun()


def _yeni_form(kullanici: str, daire_id: str, secilen_tarih: date):
    df = load_data("rezervasyon")
    with st.form("yeni_rez"):
        c1, c2 = st.columns(2)
        alan = c1.selectbox("Alan *", ORTAK_ALANLAR)
        tarih = c2.date_input("Tarih *", value=secilen_tarih)
        c3, c4 = st.columns(2)
        saat = c3.selectbox("Saat Dilimi *", SAAT_DILIMLERI)
        katilimci = c4.number_input("Katılımcı Sayısı", min_value=1, value=1, step=1)
        notlar = st.text_area("Notlar / Açıklama", placeholder="Etkinlik / kullanım amacı...")

        # Çakışma kontrolü ön bilgi
        mevcut = df[(df["Alan"] == alan) & (df["Tarih"].astype(str) == str(tarih)) &
                    (df["Saat"] == saat) & df["Durum"].isin(["Onaylandı", "Onay Bekliyor"])] \
            if not df.empty else pd.DataFrame()

        if not mevcut.empty:
            st.warning(f"⚠️ Bu saat için zaten {len(mevcut)} rezervasyon var!")

        if st.form_submit_button("📅 Rezervasyon Talebi Gönder", type="primary"):
            # Çakışma yoksa veya kullanıcı yine de göndermek istiyorsa
            row = {
                "Rezervasyon_ID": yeni_id("REZ"),
                "Tarih": str(tarih),
                "Saat": saat,
                "Alan": alan,
                "Daire_ID": daire_id or "",
                "Talep_Eden": kullanici,
                "Katilimci": int(katilimci),
                "Notlar": notlar.strip(),
                "Durum": "Onay Bekliyor",
                "Olusturma": str(date.today()),
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_data(df, "rezervasyon")
            st.success(f"Rezervasyon talebi gönderildi: {alan} — {tarih} {saat}")
            st.rerun()


def _alan_yonetimi():
    st.subheader("🏢 Ortak Alan Yönetimi")
    st.info("Ortak alanların doluluk durumunu ve istatistiklerini görüntüleyin.")

    df = load_data("rezervasyon")
    if df.empty:
        st.caption("Rezervasyon verisi yok.")
        return

    alan_ozet = []
    for alan in ORTAK_ALANLAR:
        alan_df = df[df["Alan"] == alan] if not df.empty else pd.DataFrame()
        toplam = len(alan_df)
        onaylanan = len(alan_df[alan_df["Durum"] == "Onaylandı"]) if not alan_df.empty else 0
        alan_ozet.append({
            "Alan": alan, "Toplam": toplam, "Onaylanan": onaylanan,
            "Bekleyen": len(alan_df[alan_df["Durum"] == "Onay Bekliyor"]) if not alan_df.empty else 0,
            "İptal": len(alan_df[alan_df["Durum"] == "İptal"]) if not alan_df.empty else 0,
        })

    ozet_df = pd.DataFrame(alan_ozet)
    ozet_df = ozet_df[ozet_df["Toplam"] > 0].sort_values("Toplam", ascending=False)
    if not ozet_df.empty:
        data_table(
            ozet_df,
            [("Alan", "Alan"), ("Toplam", "Toplam"), ("Onaylanan", "Onaylanan"),
             ("Bekleyen", "Bekleyen"), ("İptal", "İptal")],
        )


def _sakin_view(kullanici: str, daire_id: str):
    section_header("Ortak Alan Rezervasyonu", "Ortak alan rezervasyon talepleri", pill="RESEVASYONUm")

    df = load_data("rezervasyon")
    daire_rez = df[df["Daire_ID"].astype(str) == str(daire_id)] if not df.empty and daire_id else pd.DataFrame()

    if not daire_rez.empty:
        st.subheader("📋 Rezervasyonlarım")
        data_table(
            daire_rez.sort_values("Tarih", ascending=False),
            [("Rezervasyon_ID", "ID"), ("Tarih", "Tarih"), ("Saat", "Saat"),
             ("Alan", "Alan"), ("Durum", "Durum"), ("Notlar", "Not")],
            id_cols=["Rezervasyon_ID"], status_cols=["Durum"],
        )
    else:
        st.info("Henüz rezervasyonunuz bulunmuyor.")

    st.divider()
    st.subheader("➕ Yeni Rezervasyon Talebi")
    _yeni_form(kullanici, daire_id, date.today())
