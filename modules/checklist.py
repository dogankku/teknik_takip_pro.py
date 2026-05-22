import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from constants import SORU_GRUPLARI
from style import section_header


def render(secilen_tarih: date):
    section_header("Günlük Kontroller", secilen_tarih.strftime("%d.%m.%Y"), "✅")
    # st.header(f"✅ Günlük Kontroller ({secilen_tarih.strftime('%d.%m.%Y')})")

    df_check = load_data("checklist")
    df_pers = load_data("personel")
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    tabs = st.tabs(list(SORU_GRUPLARI.keys()))

    for i, bolum in enumerate(SORU_GRUPLARI.keys()):
        with tabs[i]:
            st.subheader(f"📋 {bolum} Kontrol Formu")
            cp, _ = st.columns([1, 3])
            kontrolcu = cp.selectbox("Kontrol Eden", personel_listesi, key=f"user_{bolum}")

            for alt_grup, sorular in SORU_GRUPLARI[bolum].items():
                with st.expander(f"📍 {alt_grup} ({len(sorular)} soru)", expanded=False):
                    tarih_str = str(secilen_tarih)
                    try:
                        kayitli = df_check[
                            (df_check["Tarih"] == tarih_str)
                            & (df_check["Bolum"] == bolum)
                            & (df_check["Alt_Grup"] == alt_grup)
                        ]
                    except KeyError:
                        kayitli = pd.DataFrame()

                    if not kayitli.empty:
                        st.success("✅ Bu grup tamamlandı")
                        st.dataframe(kayitli[["Soru", "Durum", "Aciklama"]],
                                     use_container_width=True, hide_index=True)
                    else:
                        with st.form(f"form_{bolum}_{alt_grup}"):
                            st.caption("💡 Sorun yoksa açıklama yazmadan geçebilirsiniz.")
                            cevaplar = []
                            for idx, soru in enumerate(sorular):
                                c1, c2, c3 = st.columns([6, 2, 3])
                                c1.write(soru)
                                durum = c2.radio(
                                    "D", ["Tamam", "Sorunlu"],
                                    key=f"rd_{bolum}_{alt_grup}_{idx}",
                                    horizontal=True, label_visibility="collapsed",
                                )
                                not_txt = c3.text_input(
                                    "Not", key=f"nt_{bolum}_{alt_grup}_{idx}",
                                    label_visibility="collapsed",
                                )
                                cevaplar.append({
                                    "Tarih": tarih_str, "Bolum": bolum, "Alt_Grup": alt_grup,
                                    "Soru": soru, "Durum": durum, "Aciklama": not_txt,
                                    "Kontrol_Eden": kontrolcu,
                                })
                                st.divider()

                            if st.form_submit_button(f"💾 {alt_grup} Kaydet", type="primary"):
                                df_check = pd.concat([df_check, pd.DataFrame(cevaplar)],
                                                     ignore_index=True)
                                save_data(df_check, "checklist")
                                st.success("Kaydedildi!")
                                st.rerun()
