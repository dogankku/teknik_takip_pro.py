import streamlit as st
import pandas as pd
from datetime import datetime, date
from db import load_data, save_data
from style import section_header


def render(secilen_tarih: date):
    st.header("🛠️ Arıza Kayıtları")
    df_a = load_data("ariza")
    df_p = load_data("personel")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.expander("➕ Yeni Arıza Ekle"):
        with st.form("add_ariza"):
            c1, c2 = st.columns(2)
            b = c1.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel", "Bina", "Asansör"])
            stt = c2.selectbox("Durum", ["Açık", "Devam Ediyor", "Tamamlandı"])
            l = st.text_input("Lokasyon")
            s = st.selectbox("Sorumlu", pl)
            d = st.text_area("Arıza Tanımı")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                ariza_id = f"ARZ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                row = {
                    "ID": ariza_id, "Tarih": str(secilen_tarih),
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Bolum": b, "Lokasyon": l, "Ariza_Tanimi": d,
                    "Sorumlu": s, "Durum": stt,
                    "Kapanis_Tarihi": str(secilen_tarih) if stt == "Tamamlandı" else "",
                }
                df_a = pd.concat([df_a, pd.DataFrame([row])], ignore_index=True)
                save_data(df_a, "ariza")
                st.success(f"Arıza kaydedildi: {ariza_id}")
                st.rerun()

    f = st.multiselect("Durum Filtresi", ["Açık", "Devam Ediyor", "Tamamlandı"],
                       default=["Açık", "Devam Ediyor"])
    g = df_a[df_a["Durum"].isin(f)] if not df_a.empty and f else df_a
    st.dataframe(g.sort_values("Tarih", ascending=False) if not g.empty else g,
                 use_container_width=True, hide_index=True)

    if not df_a.empty:
        st.divider()
        st.subheader("✏️ Arıza Durumunu Güncelle")
        secili = st.selectbox("Arıza", df_a["ID"].tolist())
        yeni_durum = st.selectbox("Yeni Durum", ["Açık", "Devam Ediyor", "Tamamlandı"], key="yd")
        if st.button("Güncelle"):
            df_a.loc[df_a["ID"] == secili, "Durum"] = yeni_durum
            if yeni_durum == "Tamamlandı":
                df_a.loc[df_a["ID"] == secili, "Kapanis_Tarihi"] = str(date.today())
            save_data(df_a, "ariza")
            st.success("Güncellendi.")
            st.rerun()
