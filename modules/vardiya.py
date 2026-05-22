from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data


def render(secilen_tarih: date):
    section_header("Vardiya Defteri", "Dijital teslim tutanağı", pill="OPERASYON")
    df_v = load_data("vardiya")
    df_p = load_data("personel")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.form("add_v"):
        c1, c2, c3 = st.columns(3)
        v = c1.selectbox("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
        te = c2.selectbox("Teslim Eden", pl)
        ta = c3.selectbox("Teslim Alan", pl)
        n = st.text_area("Notlar / Devir Bilgileri")
        if st.form_submit_button("💾 Kaydet", type="primary"):
            row = {"Tarih": str(secilen_tarih), "Vardiya": v,
                   "Teslim_Eden": te, "Teslim_Alan": ta, "Notlar": n}
            df_v = pd.concat([df_v, pd.DataFrame([row])], ignore_index=True)
            save_data(df_v, "vardiya")
            st.success("Kaydedildi.")
            st.rerun()

    if not df_v.empty:
        st.dataframe(df_v.sort_values("Tarih", ascending=False),
                     use_container_width=True, hide_index=True)
