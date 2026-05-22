from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from auth import current_user
from barkod import yeni_id
from constants import STOK_KATEGORI


def render(secilen_tarih: date):
    section_header("Stok & Yedek Parça", "Envanter ve kritik seviye uyarıları", pill="DEPO")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📦 Stok Listesi", "➕ Yeni Ürün", "🔁 Giriş/Çıkış", "📜 Hareket Geçmişi"]
    )
    with tab1: _liste()
    with tab2: _yeni()
    with tab3: _hareket()
    with tab4: _gecmis()


def _liste():
    df = load_data("stok")
    if df.empty:
        st.info("Henüz ürün yok.")
        return

    df = df.copy()
    df["_m"] = pd.to_numeric(df["Mevcut"], errors="coerce").fillna(0)
    df["_k"] = pd.to_numeric(df["Kritik"], errors="coerce").fillna(0)
    df["Uyarı"] = df.apply(
        lambda r: "🔴 Kritik" if r["_m"] <= r["_k"] else "🟢 Normal", axis=1
    )

    c1, c2 = st.columns(2)
    sf = c1.selectbox("Filtre", ["Tümü", "Sadece Kritik", "Sadece Normal"])
    kf = c2.selectbox("Kategori", ["Tümü"] + sorted(df["Kategori"].dropna().unique().tolist()))
    g = df.copy()
    if sf == "Sadece Kritik": g = g[g["_m"] <= g["_k"]]
    elif sf == "Sadece Normal": g = g[g["_m"] > g["_k"]]
    if kf != "Tümü": g = g[g["Kategori"] == kf]

    kritik_sayi = (df["_m"] <= df["_k"]).sum()
    if kritik_sayi:
        st.warning(f"⚠️ {kritik_sayi} ürün kritik stok seviyesinde!")

    st.dataframe(
        g[["Stok_ID", "Urun_Adi", "Kategori", "Mevcut", "Kritik", "Birim",
           "Depo_Yeri", "Birim_Fiyat", "Uyarı"]],
        use_container_width=True, hide_index=True,
    )


def _yeni():
    with st.form("add_st"):
        c1, c2 = st.columns(2)
        ad = c1.text_input("Ürün Adı *")
        kat = c2.selectbox("Kategori", STOK_KATEGORI)
        c3, c4, c5 = st.columns(3)
        bir = c3.selectbox("Birim", ["adet", "metre", "litre", "kg", "kutu", "paket"])
        mev = c4.number_input("Başlangıç Stoğu", min_value=0.0, value=0.0)
        krt = c5.number_input("Kritik Seviye", min_value=0.0, value=5.0)
        c6, c7 = st.columns(2)
        depo = c6.text_input("Depo Yeri", placeholder="Depo-1 / Raf-A3")
        bf = c7.number_input("Birim Fiyat (₺)", min_value=0.0, value=0.0)
        n = st.text_area("Notlar")
        if st.form_submit_button("💾 Kaydet", type="primary"):
            if ad.strip():
                row = {"Stok_ID": yeni_id("STK"), "Urun_Adi": ad.strip(),
                       "Kategori": kat, "Birim": bir,
                       "Mevcut": mev, "Kritik": krt,
                       "Depo_Yeri": depo, "Birim_Fiyat": bf, "Notlar": n}
                df = load_data("stok")
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "stok")
                st.success("Eklendi.")
                st.rerun()


def _hareket():
    df = load_data("stok")
    if df.empty:
        st.warning("Önce stok ekleyin.")
        return

    sec = st.selectbox("Ürün",
        [f"{r['Stok_ID']} - {r['Urun_Adi']} (mevcut: {r['Mevcut']} {r['Birim']})"
         for _, r in df.iterrows()])
    sid = sec.split(" - ")[0]
    row = df[df["Stok_ID"] == sid].iloc[0]
    mevcut = float(row.get("Mevcut", 0) or 0)

    with st.form("hrk"):
        c1, c2 = st.columns(2)
        tip = c1.selectbox("Hareket Tipi", ["Giriş", "Çıkış"])
        miktar = c2.number_input("Miktar", min_value=0.0, value=1.0, step=1.0)
        ack = st.text_area("Açıklama", placeholder="İş emri / sebep")
        if st.form_submit_button("💾 İşle", type="primary"):
            u = current_user() or {}
            kim = u.get("Ad_Soyad", "")
            yeni_mevcut = mevcut + miktar if tip == "Giriş" else mevcut - miktar
            if yeni_mevcut < 0:
                st.error("Çıkış miktarı stoktan fazla olamaz.")
            else:
                df.loc[df["Stok_ID"] == sid, "Mevcut"] = yeni_mevcut
                save_data(df, "stok")
                log = load_data("stok_hrk")
                log = pd.concat([log, pd.DataFrame([{
                    "Hareket_ID": yeni_id("HRK"), "Stok_ID": sid,
                    "Tarih": str(date.today()), "Tip": tip,
                    "Miktar": miktar, "Kalan": yeni_mevcut,
                    "Aciklama": ack, "Kim": kim,
                }])], ignore_index=True)
                save_data(log, "stok_hrk")
                st.success(f"İşlendi. Yeni stok: {yeni_mevcut} {row['Birim']}")
                st.rerun()


def _gecmis():
    df = load_data("stok_hrk")
    if df.empty:
        st.info("Henüz hareket yok.")
        return
    st.dataframe(df.sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True)
