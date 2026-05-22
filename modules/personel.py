from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data


def render(secilen_tarih: date):
    section_header("Personel", "Personel listesi ve görev bilgileri", pill="İNSAN KAYNAKLARI")
    df_p = load_data("personel")

    with st.form("add_p"):
        c1, c2, c3 = st.columns(3)
        i = c1.text_input("İsim *")
        g = c2.text_input("Görev")
        t = c3.text_input("Telefon")
        if st.form_submit_button("➕ Ekle", type="primary"):
            if i.strip():
                df_p = pd.concat([df_p, pd.DataFrame([{
                    "Isim": i.strip(), "Gorev": g, "Telefon": t
                }])], ignore_index=True)
                save_data(df_p, "personel")
                st.success("Eklendi.")
                st.rerun()
            else:
                st.error("İsim zorunlu.")

    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🗑️ Personel Sil")
        sec = st.selectbox("Sil", df_p["Isim"].tolist())
        if st.button("Sil"):
            df_p = df_p[df_p["Isim"] != sec]
            save_data(df_p, "personel")
            st.success("Silindi.")
            st.rerun()
