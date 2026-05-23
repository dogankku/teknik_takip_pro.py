"""Tekrarlı görev yönetimi — otomatik periyodik iş emirleri."""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import load_data, save_data
from style import section_header, data_table
from auth import current_user
from barkod import yeni_id
from constants import BAKIM_PERIYOT


HEDEF_TIPLER = ["Checklist", "Arıza", "Bakım", "Talep"]


def render(secilen_tarih: date):
    section_header("Tekrarlı Görevler", "Otomatik periyodik iş emirleri ve hatırlatıcılar", pill="OPERASYON")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    df = load_data("tekrar")
    df_p = load_data("personel")
    df_lok = load_data("lokasyon")
    df_sbl = load_data("sablon")

    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]
    lok_opts = []
    if not df_lok.empty:
        lok_opts = (df_lok["Ana_Lokasyon"].astype(str) + " → " + df_lok["Ad"].astype(str)).tolist()
    sbl_opts = df_sbl["Ad"].tolist() if not df_sbl.empty else []

    tabs = st.tabs(["📋 Aktif Görevler", "➕ Yeni Görev", "📊 Özet"])

    with tabs[0]:
        if df.empty:
            st.info("Henüz tekrarlı görev tanımlanmamış.")
        else:
            # Vadesi gelenler
            today_ts = pd.Timestamp(secilen_tarih)
            df_copy = df.copy()
            df_copy["_st"] = pd.to_datetime(df_copy["Sonraki_Tarih"], errors="coerce")

            vadesi_gecen = df_copy[
                (df_copy["_st"] <= today_ts) & (df_copy["Aktif"].astype(str).isin(["True", "1", "true"]))
            ]
            if not vadesi_gecen.empty:
                st.error(f"⚠️ **{len(vadesi_gecen)} görev** bugün veya daha önce yapılması gerekirdi!")
                data_table(
                    vadesi_gecen,
                    [("Baslik", "Başlık"), ("Hedef_Tip", "Tip"),
                     ("Periyot_Gun", "Periyot"), ("Sonraki_Tarih", "Sonraki"),
                     ("Sorumlu", "Sorumlu")],
                    avatar_cols=["Sorumlu"], max_text=60,
                )
                if st.button("✅ Vadesi Geçenleri Yenile (Sonraki Tarihe İlerlet)"):
                    for idx, r in vadesi_gecen.iterrows():
                        periyot = int(pd.to_numeric(r.get("Periyot_Gun", 7), errors="coerce") or 7)
                        yeni_tarih = str(date.today() + timedelta(days=periyot))
                        df.loc[df.index == idx, "Sonraki_Tarih"] = yeni_tarih
                        df.loc[df.index == idx, "Son_Olusturma"] = str(date.today())
                    save_data(df, "tekrar")
                    st.success("Tarihler güncellendi.")
                    st.rerun()

            st.markdown("---")
            # Tüm liste
            g = df.copy()
            aktif_f = st.radio("Filtre", ["Aktif", "Pasif", "Tümü"], horizontal=True)
            if aktif_f == "Aktif":
                g = g[g["Aktif"].astype(str).isin(["True", "1", "true"])]
            elif aktif_f == "Pasif":
                g = g[~g["Aktif"].astype(str).isin(["True", "1", "true"])]

            data_table(
                g,
                [("Baslik", "Başlık"), ("Hedef_Tip", "Tip"), ("Periyot_Gun", "Periyot"),
                 ("Sonraki_Tarih", "Sonraki"), ("Sorumlu", "Sorumlu"), ("Aktif", "Durum")],
                avatar_cols=["Sorumlu"], bool_cols=["Aktif"], max_text=60,
            )

            st.divider()
            st.subheader("✏️ Görev Düzenle")
            if not df.empty:
                sec_id = st.selectbox("Görev seç", df["Tekrar_ID"].tolist())
                row = df[df["Tekrar_ID"] == sec_id].iloc[0]
                _gorevu_duzenle(row, df, sec_id, pers, lok_opts)

    with tabs[1]:
        _yeni_gorev_form(kullanici, df, pers, lok_opts, sbl_opts)

    with tabs[2]:
        _ozet(df)


def _yeni_gorev_form(kullanici: str, df: pd.DataFrame, pers, lok_opts, sbl_opts):
    with st.form("yeni_tekrar"):
        baslik = st.text_input("Görev Başlığı *")
        ack = st.text_area("Açıklama")
        c1, c2 = st.columns(2)
        hedef = c1.selectbox("Hedef Tip", HEDEF_TIPLER)
        periyot_label = c2.selectbox("Periyot", list(BAKIM_PERIYOT.keys()))
        periyot_gun = BAKIM_PERIYOT[periyot_label]

        c3, c4 = st.columns(2)
        sorumlu = c3.selectbox("Sorumlu", pers)
        sonraki = c4.date_input("İlk Yapılma Tarihi", value=date.today())

        if lok_opts:
            lok_sec = st.selectbox("Lokasyon", ["—"] + lok_opts)
        else:
            lok_sec = "—"

        if sbl_opts:
            sbl_sec = st.selectbox("Şablon (Checklist için)", ["—"] + sbl_opts)
        else:
            sbl_sec = "—"

        aktif = st.checkbox("Aktif", value=True)

        if st.form_submit_button("💾 Kaydet", type="primary"):
            if baslik.strip():
                row_new = {
                    "Tekrar_ID": yeni_id("TKR"),
                    "Baslik": baslik.strip(),
                    "Aciklama": ack.strip(),
                    "Hedef_Tip": hedef,
                    "Periyot_Gun": periyot_gun,
                    "Sonraki_Tarih": str(sonraki),
                    "Sorumlu": sorumlu,
                    "Lokasyon_ID": lok_sec if lok_sec != "—" else "",
                    "Sablon_ID": sbl_sec if sbl_sec != "—" else "",
                    "Aktif": aktif,
                    "Son_Olusturma": str(date.today()),
                }
                df = pd.concat([df, pd.DataFrame([row_new])], ignore_index=True)
                save_data(df, "tekrar")
                st.success(f"Tekrarlı görev oluşturuldu: {baslik} (her {periyot_gun} günde bir)")
                st.rerun()
            else:
                st.error("Başlık zorunlu.")


def _gorevu_duzenle(row: pd.Series, df: pd.DataFrame, sec_id: str, pers, lok_opts):
    with st.form(f"tekrar_edit_{sec_id}"):
        baslik = st.text_input("Başlık", value=str(row.get("Baslik", "")))
        c1, c2 = st.columns(2)
        periyot = c1.number_input("Periyot (gün)", value=int(
            pd.to_numeric(row.get("Periyot_Gun", 7), errors="coerce") or 7), min_value=1)
        sorumlu_idx = pers.index(row.get("Sorumlu")) if row.get("Sorumlu") in pers else 0
        sorumlu = c2.selectbox("Sorumlu", pers, index=sorumlu_idx)
        try:
            sonraki_val = pd.to_datetime(row.get("Sonraki_Tarih")).date()
        except Exception:
            sonraki_val = date.today()
        sonraki = st.date_input("Sonraki Tarih", value=sonraki_val)
        aktif = st.checkbox("Aktif", value=bool(row.get("Aktif", True)))

        col_s, col_d = st.columns(2)
        if col_s.form_submit_button("💾 Güncelle", type="primary"):
            df.loc[df["Tekrar_ID"] == sec_id, "Baslik"] = baslik
            df.loc[df["Tekrar_ID"] == sec_id, "Periyot_Gun"] = periyot
            df.loc[df["Tekrar_ID"] == sec_id, "Sorumlu"] = sorumlu
            df.loc[df["Tekrar_ID"] == sec_id, "Sonraki_Tarih"] = str(sonraki)
            df.loc[df["Tekrar_ID"] == sec_id, "Aktif"] = aktif
            save_data(df, "tekrar")
            st.success("Güncellendi.")
            st.rerun()
        if col_d.form_submit_button("🗑️ Sil"):
            df = df[df["Tekrar_ID"] != sec_id]
            save_data(df, "tekrar")
            st.warning("Silindi.")
            st.rerun()


def _ozet(df: pd.DataFrame):
    if df.empty:
        st.info("Henüz görev yok.")
        return
    aktif = len(df[df["Aktif"].astype(str).isin(["True", "1", "true"])])
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Görev", len(df))
    c2.metric("Aktif", aktif)
    c3.metric("Pasif", len(df) - aktif)

    st.markdown("---")
    st.markdown("**Hedef Tipe Göre Dağılım**")
    if "Hedef_Tip" in df.columns:
        st.bar_chart(df["Hedef_Tip"].value_counts())
