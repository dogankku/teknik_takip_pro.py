"""Lokasyon (alan/bölge) yönetimi modülü."""
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from style import section_header, data_table
from barkod import yeni_id


LOK_TIPLER = ["Kazan Dairesi", "Elektrik Odası", "Tesisat", "Ortak Alan",
               "Asansör", "Otopark", "Bahçe", "Daire", "Çatı", "Bodrum", "Diğer"]


def render(secilen_tarih: date):
    section_header("Lokasyon Yönetimi", "Bina alanları ve teknik bölgeler", pill="TESİS")
    df = load_data("lokasyon")

    tabs = st.tabs(["🏢 Lokasyonlar", "➕ Yeni Ekle"])

    with tabs[0]:
        if df.empty:
            st.info("Henüz lokasyon eklenmemiş.")
        else:
            # Özet kartlar
            ana_loks = df["Ana_Lokasyon"].dropna().unique().tolist() if "Ana_Lokasyon" in df.columns else []
            c_cols = st.columns(min(len(ana_loks), 4)) if ana_loks else [st.container()]
            for i, ana in enumerate(ana_loks[:4]):
                with c_cols[i]:
                    alt_count = len(df[df["Ana_Lokasyon"] == ana])
                    st.markdown(
                        f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;'
                        f'border-radius:10px;padding:12px;text-align:center;">'
                        f'<div style="font-size:.75rem;font-weight:600;color:#1D4ED8;">{ana}</div>'
                        f'<div style="font-size:1.5rem;font-weight:700;color:#1E293B;">{alt_count}</div>'
                        f'<div style="font-size:.7rem;color:#64748B;">alan</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            # Filtre
            ana_sec = st.selectbox("Ana Lokasyon Filtrele",
                                   ["Tümü"] + sorted(ana_loks))
            g = df if ana_sec == "Tümü" else df[df["Ana_Lokasyon"] == ana_sec]
            data_table(
                g,
                [("Lokasyon_ID", "ID"), ("Ana_Lokasyon", "Ana Lokasyon"),
                 ("Ad", "Ad"), ("Tip", "Tip"), ("Notlar", "Notlar")],
                id_cols=["Lokasyon_ID"], max_text=50,
            )

            st.divider()
            st.subheader("✏️ Düzenle / Sil")
            sec_id = st.selectbox("Lokasyon seç", df["Lokasyon_ID"].tolist())
            row = df[df["Lokasyon_ID"] == sec_id].iloc[0]

            with st.form(f"lok_edit_{sec_id}"):
                c1, c2 = st.columns(2)
                new_ana = c1.text_input("Ana Lokasyon", value=str(row.get("Ana_Lokasyon", "")))
                new_ad = c2.text_input("Alan Adı", value=str(row.get("Ad", "")))
                new_tip = st.selectbox("Tip", LOK_TIPLER,
                                       index=LOK_TIPLER.index(row.get("Tip")) if row.get("Tip") in LOK_TIPLER else 0)
                new_not = st.text_area("Notlar", value=str(row.get("Notlar", "")))
                col_s, col_d = st.columns(2)
                if col_s.form_submit_button("💾 Güncelle", type="primary"):
                    df.loc[df["Lokasyon_ID"] == sec_id, "Ana_Lokasyon"] = new_ana
                    df.loc[df["Lokasyon_ID"] == sec_id, "Ad"] = new_ad
                    df.loc[df["Lokasyon_ID"] == sec_id, "Tip"] = new_tip
                    df.loc[df["Lokasyon_ID"] == sec_id, "Notlar"] = new_not
                    save_data(df, "lokasyon")
                    st.success("Güncellendi.")
                    st.rerun()
                if col_d.form_submit_button("🗑️ Sil"):
                    df = df[df["Lokasyon_ID"] != sec_id]
                    save_data(df, "lokasyon")
                    st.warning("Silindi.")
                    st.rerun()

    with tabs[1]:
        with st.form("yeni_lok"):
            c1, c2 = st.columns(2)
            ana = c1.text_input("Ana Lokasyon *", placeholder="örn: A Blok, Bodrum")
            ad = c2.text_input("Alan Adı *", placeholder="örn: Kazan Dairesi")
            tip = st.selectbox("Tip", LOK_TIPLER)
            notlar = st.text_area("Notlar")
            if st.form_submit_button("➕ Ekle", type="primary"):
                if ana.strip() and ad.strip():
                    row_new = {
                        "Lokasyon_ID": yeni_id("LOK"),
                        "Ana_Lokasyon": ana.strip(),
                        "Ad": ad.strip(),
                        "Tip": tip,
                        "Adres": "",
                        "Notlar": notlar.strip(),
                    }
                    df = pd.concat([df, pd.DataFrame([row_new])], ignore_index=True)
                    save_data(df, "lokasyon")
                    st.success(f"Lokasyon eklendi: {ana} → {ad}")
                    st.rerun()
                else:
                    st.error("Ana lokasyon ve alan adı zorunlu.")
