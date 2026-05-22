from style import section_header
import streamlit as st
import pandas as pd
from datetime import date, datetime
from db import load_data, save_data
from barkod import yeni_id


def render(secilen_tarih: date):
    section_header("Daire & Sakin", "Blok, daire ve sakin kayıtları", pill="MÜLK YÖNETİMİ")
    tab1, tab2, tab3 = st.tabs(["🏠 Daireler", "👨‍👩‍👧 Sakinler", "📊 Doluluk Özeti"])

    with tab1:
        _daire_modul()
    with tab2:
        _sakin_modul()
    with tab3:
        _doluluk_ozeti()


def _daire_modul():
    df = load_data("daire")

    with st.expander("➕ Yeni Daire Ekle"):
        with st.form("add_daire"):
            c1, c2, c3 = st.columns(3)
            blok = c1.text_input("Blok *", placeholder="A")
            kat = c2.number_input("Kat", min_value=-5, max_value=50, value=1)
            no = c3.text_input("Daire No *", placeholder="12")
            c4, c5 = st.columns(2)
            m2 = c4.number_input("m²", min_value=0, value=100)
            tip = c5.selectbox("Tip", ["1+0", "1+1", "2+1", "3+1", "4+1", "5+1", "Dubleks", "Penthouse"])
            durum = st.selectbox("Durum", ["Dolu", "Boş", "Bakımda"])
            notlar = st.text_area("Notlar")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                if blok.strip() and no.strip():
                    daire_id = f"D-{blok.strip().upper()}-{no.strip()}"
                    if not df.empty and daire_id in df["Daire_ID"].astype(str).values:
                        st.error(f"{daire_id} zaten kayıtlı.")
                    else:
                        row = {"Daire_ID": daire_id, "Blok": blok.strip().upper(),
                               "Kat": kat, "Daire_No": no.strip(), "M2": m2,
                               "Oda_Tipi": tip, "Durum": durum, "Notlar": notlar}
                        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                        save_data(df, "daire")
                        st.success(f"Kaydedildi: {daire_id}")
                        st.rerun()

    if df.empty:
        st.info("Henüz daire eklenmemiş.")
        return

    c1, c2 = st.columns(2)
    bloklar = ["Tümü"] + sorted(df["Blok"].dropna().astype(str).unique().tolist())
    bf = c1.selectbox("Blok", bloklar)
    durs = ["Tümü"] + sorted(df["Durum"].dropna().astype(str).unique().tolist())
    df_dur = c2.selectbox("Durum", durs, key="d_dur")

    g = df.copy()
    if bf != "Tümü": g = g[g["Blok"].astype(str) == bf]
    if df_dur != "Tümü": g = g[g["Durum"].astype(str) == df_dur]
    st.dataframe(g, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("✏️ Daire Sil / Düzenle")
    sec = st.selectbox("Daire", df["Daire_ID"].tolist(), key="d_sec")
    cdl1, cdl2 = st.columns(2)
    yeni_dur = cdl1.selectbox("Yeni Durum", ["Dolu", "Boş", "Bakımda"], key="d_yd")
    if cdl1.button("Durum Güncelle"):
        df.loc[df["Daire_ID"] == sec, "Durum"] = yeni_dur
        save_data(df, "daire")
        st.success("Güncellendi.")
        st.rerun()
    if cdl2.button("🗑️ Daireyi Sil", type="secondary"):
        df = df[df["Daire_ID"] != sec]
        save_data(df, "daire")
        st.success("Silindi.")
        st.rerun()


def _sakin_modul():
    df_s = load_data("sakin")
    df_d = load_data("daire")
    daire_ops = df_d["Daire_ID"].tolist() if not df_d.empty else []

    with st.expander("➕ Yeni Sakin Ekle"):
        if not daire_ops:
            st.warning("Önce daire eklemelisiniz.")
        else:
            with st.form("add_sakin"):
                c1, c2 = st.columns(2)
                ad = c1.text_input("Ad Soyad *")
                daire = c2.selectbox("Daire", daire_ops)
                c3, c4 = st.columns(2)
                tip = c3.selectbox("Tip", ["Malik", "Kiracı", "Aile Üyesi"])
                tel = c4.text_input("Telefon")
                c5, c6 = st.columns(2)
                email = c5.text_input("Email")
                giris = c6.date_input("Giriş Tarihi", date.today())
                if st.form_submit_button("💾 Kaydet", type="primary"):
                    if ad.strip():
                        sid = yeni_id("SKN")
                        row = {"Sakin_ID": sid, "Daire_ID": daire,
                               "Ad_Soyad": ad.strip(), "Tip": tip,
                               "Telefon": tel, "Email": email,
                               "Giris_Tarihi": str(giris), "Cikis_Tarihi": "",
                               "Aktif": "Evet"}
                        df_s = pd.concat([df_s, pd.DataFrame([row])], ignore_index=True)
                        save_data(df_s, "sakin")
                        # Daireyi Dolu işaretle
                        if not df_d.empty:
                            df_d.loc[df_d["Daire_ID"] == daire, "Durum"] = "Dolu"
                            save_data(df_d, "daire")
                        st.success(f"Kaydedildi: {sid}")
                        st.rerun()

    if df_s.empty:
        st.info("Henüz sakin eklenmemiş.")
        return

    aktif_filt = st.checkbox("Sadece aktif sakinler", value=True)
    g = df_s[df_s["Aktif"].astype(str).str.lower() == "evet"] if aktif_filt else df_s
    st.dataframe(g, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🚪 Çıkış İşlemi")
    aktifler = df_s[df_s["Aktif"].astype(str).str.lower() == "evet"]
    if not aktifler.empty:
        sec = st.selectbox("Sakin",
                           [f"{r['Sakin_ID']} - {r['Ad_Soyad']} ({r['Daire_ID']})"
                            for _, r in aktifler.iterrows()])
        sid = sec.split(" - ")[0]
        if st.button("🚪 Çıkış Kaydet"):
            df_s.loc[df_s["Sakin_ID"] == sid, "Aktif"] = "Hayır"
            df_s.loc[df_s["Sakin_ID"] == sid, "Cikis_Tarihi"] = str(date.today())
            save_data(df_s, "sakin")
            st.success("Çıkış kaydedildi.")
            st.rerun()


def _doluluk_ozeti():
    df_d = load_data("daire")
    df_s = load_data("sakin")
    if df_d.empty:
        st.info("Daire kaydı yok.")
        return

    toplam = len(df_d)
    dolu = len(df_d[df_d["Durum"].astype(str) == "Dolu"])
    bos = len(df_d[df_d["Durum"].astype(str) == "Boş"])
    bakim = len(df_d[df_d["Durum"].astype(str) == "Bakımda"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Daire", toplam)
    c2.metric("Dolu", dolu, f"%{(dolu/toplam*100):.1f}" if toplam else "")
    c3.metric("Boş", bos)
    c4.metric("Bakımda", bakim)

    if not df_s.empty:
        aktif = df_s[df_s["Aktif"].astype(str).str.lower() == "evet"]
        st.metric("👥 Aktif Sakin Sayısı", len(aktif))

    st.divider()
    st.subheader("Blok Bazlı Dağılım")
    blok_sayim = df_d.groupby("Blok").agg(
        Toplam=("Daire_ID", "count"),
        Dolu=("Durum", lambda x: (x == "Dolu").sum()),
        Boş=("Durum", lambda x: (x == "Boş").sum()),
    ).reset_index()
    st.dataframe(blok_sayim, use_container_width=True, hide_index=True)
