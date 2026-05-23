from style import section_header, data_table
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from barkod import yeni_id
from constants import GIDER_KATEGORI


def render(secilen_tarih: date):
    section_header("Sayaç & Gider", "Tüketim ve harcama analizi", pill="MALİ TAKİP")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Sayaç Listesi", "📖 Okuma Gir", "💸 Gider Kaydı", "📈 Tüketim Raporu"]
    )
    with tab1: _sayac_liste()
    with tab2: _okuma_gir(secilen_tarih)
    with tab3: _gider(secilen_tarih)
    with tab4: _tuketim_rapor()


def _sayac_liste():
    df = load_data("sayac")

    with st.expander("➕ Yeni Sayaç Ekle"):
        df_d = load_data("daire")
        with st.form("add_sy"):
            c1, c2 = st.columns(2)
            tip = c1.selectbox("Tip", ["Elektrik", "Su", "Doğalgaz", "Sıcak Su"])
            lok = c2.text_input("Lokasyon (Genel/Sosyal Tesis vs.)")
            c3, c4 = st.columns(2)
            daire = c3.selectbox(
                "Daire (opsiyonel)",
                ["-"] + (df_d["Daire_ID"].tolist() if not df_d.empty else []),
            )
            bf = c4.number_input("Birim Fiyat (₺)", min_value=0.0, value=2.0, step=0.1)
            if st.form_submit_button("💾 Kaydet", type="primary"):
                row = {"Sayac_ID": yeni_id("SAY"), "Tip": tip,
                       "Lokasyon": lok, "Daire_ID": "" if daire == "-" else daire,
                       "Birim_Fiyat": bf, "Aktif": "Evet"}
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "sayac")
                st.success("Eklendi.")
                st.rerun()

    if df.empty:
        st.info("Sayaç eklenmemiş.")
    else:
        data_table(
            df,
            [("Sayac_ID", "ID"), ("Tip", "Tip"), ("Lokasyon", "Lokasyon"),
             ("Daire_ID", "Daire"), ("Birim_Fiyat", "Birim Fiyat"), ("Aktif", "Durum")],
            id_cols=["Sayac_ID"], bool_cols=["Aktif"],
        )


def _okuma_gir(secilen_tarih: date):
    df_s = load_data("sayac")
    if df_s.empty:
        st.warning("Önce sayaç ekleyin.")
        return

    df_o = load_data("okuma")
    sec = st.selectbox("Sayaç",
        [f"{r['Sayac_ID']} - {r['Tip']} ({r['Lokasyon']})" for _, r in df_s.iterrows()])
    sid = sec.split(" - ")[0]
    sayac = df_s[df_s["Sayac_ID"] == sid].iloc[0]
    bf = float(sayac.get("Birim_Fiyat", 0) or 0)

    # Önceki okuma
    onceki = df_o[df_o["Sayac_ID"] == sid].sort_values("Tarih", ascending=False)
    onceki_endeks = 0.0
    if not onceki.empty:
        try:
            onceki_endeks = float(onceki.iloc[0]["Endeks"])
            st.info(f"Son okuma: **{onceki_endeks}** ({onceki.iloc[0]['Tarih']})")
        except Exception:
            pass

    with st.form("okuma_form"):
        c1, c2 = st.columns(2)
        tar = c1.date_input("Tarih", secilen_tarih)
        endeks = c2.number_input("Yeni Endeks", min_value=0.0, value=onceki_endeks)
        if st.form_submit_button("📖 Kaydet", type="primary"):
            tuketim = max(0.0, endeks - onceki_endeks)
            tutar = round(tuketim * bf, 2)
            row = {"Okuma_ID": yeni_id("OKM"), "Sayac_ID": sid,
                   "Tarih": str(tar), "Endeks": endeks,
                   "Tuketim": tuketim, "Tutar": tutar}
            df_o = pd.concat([df_o, pd.DataFrame([row])], ignore_index=True)
            save_data(df_o, "okuma")
            st.success(f"Tüketim: {tuketim} • Tutar: {tutar:,.2f} ₺")
            st.rerun()

    if not onceki.empty:
        st.subheader("📜 Okuma Geçmişi")
        data_table(
            onceki.head(20),
            [("Okuma_ID", "ID"), ("Tarih", "Tarih"), ("Endeks", "Endeks"),
             ("Tuketim", "Tüketim"), ("Tutar", "Tutar (₺)")],
            id_cols=["Okuma_ID"],
        )


def _gider(secilen_tarih: date):
    df = load_data("gider")

    with st.expander("➕ Yeni Gider Kaydı", expanded=True):
        with st.form("add_g"):
            c1, c2 = st.columns(2)
            tar = c1.date_input("Tarih", secilen_tarih)
            kat = c2.selectbox("Kategori", GIDER_KATEGORI)
            c3, c4 = st.columns(2)
            tut = c3.number_input("Tutar (₺)", min_value=0.0, value=0.0)
            bn = c4.text_input("Belge / Fatura No")
            ted = st.text_input("Tedarikçi / Firma")
            ack = st.text_area("Açıklama")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                row = {"Gider_ID": yeni_id("GDR"), "Tarih": str(tar),
                       "Kategori": kat, "Aciklama": ack,
                       "Tutar": tut, "Belge_No": bn, "Tedarikci": ted}
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "gider")
                st.success("Eklendi.")
                st.rerun()

    if df.empty:
        st.info("Gider kaydı yok.")
        return

    df["_t"] = pd.to_numeric(df["Tutar"], errors="coerce").fillna(0)
    df["_d"] = pd.to_datetime(df["Tarih"], errors="coerce")
    ay = st.text_input("Ay filtresi (YYYY-MM, boş=hepsi)",
                       value=date.today().strftime("%Y-%m"))
    g = df.copy()
    if ay:
        g = g[g["_d"].dt.strftime("%Y-%m") == ay]

    toplam = g["_t"].sum()
    st.metric(f"Toplam Gider ({ay or 'tüm zamanlar'})", f"{toplam:,.2f} ₺")

    st.subheader("Kategori Dağılımı")
    kat_top = g.groupby("Kategori")["_t"].sum().reset_index().sort_values("_t", ascending=False)
    kat_top.columns = ["Kategori", "Toplam (₺)"]
    data_table(kat_top, [("Kategori", "Kategori"), ("Toplam (₺)", "Toplam (₺)")])

    st.subheader("Detaylı Liste")
    gider_df = g.drop(columns=["_t", "_d"]).sort_values("Tarih", ascending=False)
    data_table(
        gider_df,
        [("Gider_ID", "ID"), ("Tarih", "Tarih"), ("Kategori", "Kategori"),
         ("Tutar", "Tutar (₺)"), ("Belge_No", "Belge No"), ("Tedarikci", "Tedarikçi"),
         ("Aciklama", "Açıklama")],
        id_cols=["Gider_ID"],
    )


def _tuketim_rapor():
    df_o = load_data("okuma")
    df_s = load_data("sayac")
    if df_o.empty:
        st.info("Henüz okuma kaydı yok.")
        return

    j = df_o.merge(df_s[["Sayac_ID", "Tip", "Lokasyon"]], on="Sayac_ID", how="left")
    j["_t"] = pd.to_numeric(j["Tuketim"], errors="coerce").fillna(0)
    j["_tu"] = pd.to_numeric(j["Tutar"], errors="coerce").fillna(0)
    j["_d"] = pd.to_datetime(j["Tarih"], errors="coerce")

    ay = st.text_input("Ay (YYYY-MM)", value=date.today().strftime("%Y-%m"), key="t_ay")
    f = j[j["_d"].dt.strftime("%Y-%m") == ay] if ay else j

    if f.empty:
        st.warning("Bu ay için kayıt yok.")
        return

    tip_sum = f.groupby("Tip").agg(
        Toplam_Tuketim=("_t", "sum"), Toplam_Tutar=("_tu", "sum")
    ).reset_index()
    st.subheader(f"📊 {ay} Tüketim Özeti")
    data_table(
        tip_sum,
        [("Tip", "Sayaç Tipi"), ("Toplam_Tuketim", "Tüketim"), ("Toplam_Tutar", "Tutar (₺)")],
    )

    st.subheader("Detay")
    det_df = f.drop(columns=["_t", "_tu", "_d"]).sort_values("Tarih", ascending=False)
    data_table(
        det_df,
        [("Okuma_ID", "ID"), ("Sayac_ID", "Sayaç"), ("Tarih", "Tarih"),
         ("Tip", "Tip"), ("Lokasyon", "Lokasyon"),
         ("Endeks", "Endeks"), ("Tuketim", "Tüketim"), ("Tutar", "Tutar (₺)")],
        id_cols=["Okuma_ID"],
    )
