from style import section_header, data_table
import streamlit as st
import pandas as pd
from datetime import date, datetime
from db import load_data, save_data
from barkod import yeni_id
from media import upload_widget, render_photo_grid


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
    data_table(
        g,
        [("Daire_ID", "Daire"), ("Blok", "Blok"), ("Kat", "Kat"),
         ("Daire_No", "No"), ("M2", "m²"), ("Oda_Tipi", "Oda Tipi"),
         ("Durum", "Durum"), ("Notlar", "Notlar")],
        status_cols=["Durum"], id_cols=["Daire_ID"],
    )

    st.divider()
    st.subheader("🔍 Daire Detayı")
    sec = st.selectbox("Daire seç", df["Daire_ID"].tolist(), key="d_sec")
    _daire_detay(sec, df)


def _daire_detay(daire_id: str, df: pd.DataFrame):
    row = df[df["Daire_ID"] == daire_id].iloc[0]

    col_info, col_edit = st.columns([2, 1])

    with col_info:
        # Sakin bilgisi
        df_s = load_data("sakin")
        sakinler = df_s[(df_s["Daire_ID"].astype(str) == str(daire_id)) &
                        (df_s["Aktif"].astype(str).str.lower() == "evet")] if not df_s.empty else pd.DataFrame()

        st.markdown(
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;padding:14px;">'
            f'<b style="font-size:1rem">{daire_id}</b> · {row.get("Oda_Tipi","")} · {row.get("M2","")} m²<br>'
            f'Kat: {row.get("Kat","")} | Blok: {row.get("Blok","")}<br>'
            f'Durum: <b>{row.get("Durum","")}</b><br>'
            f'{"<br>".join([f"👤 " + str(s.get("Ad_Soyad","")) + " (" + str(s.get("Tip","")) + ")" for _, s in sakinler.iterrows()]) if not sakinler.empty else "Sakin yok"}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Aidat borç özeti
        st.markdown("**💰 Aidat Durumu**")
        df_th = load_data("tahakkuk")
        df_od = load_data("odeme")

        th = 0.0
        od = 0.0
        if not df_th.empty and "Daire_ID" in df_th.columns:
            m = df_th[df_th["Daire_ID"].astype(str) == str(daire_id)]
            th = pd.to_numeric(m["Tutar"], errors="coerce").fillna(0).sum()
        if not df_od.empty and "Daire_ID" in df_od.columns:
            m = df_od[df_od["Daire_ID"].astype(str) == str(daire_id)]
            od = pd.to_numeric(m["Tutar"], errors="coerce").fillna(0).sum()
        bk = th - od

        ca, cb, cc = st.columns(3)
        ca.metric("Tahakkuk", f"{th:,.0f} ₺")
        cb.metric("Ödenen", f"{od:,.0f} ₺")
        cc.metric("Kalan Borç", f"{bk:,.0f} ₺",
                  delta="Ödenmiş ✅" if bk <= 0 else "⚠️ Ödeme Gerekli",
                  delta_color="normal" if bk <= 0 else "inverse")

        # Açık talepler
        df_t = load_data("talep")
        if not df_t.empty and "Daire_ID" in df_t.columns:
            acik = df_t[(df_t["Daire_ID"].astype(str) == str(daire_id)) &
                        (~df_t["Durum"].isin(["Çözüldü", "Kapatıldı"]))]
            if not acik.empty:
                st.markdown(f"**📨 Açık Talepler ({len(acik)})**")
                data_table(
                    acik,
                    [("Talep_ID", "ID"), ("Tarih", "Tarih"), ("Baslik", "Başlık"),
                     ("Oncelik", "Öncelik"), ("Durum", "Durum")],
                    status_cols=["Durum"], priority_cols=["Oncelik"], id_cols=["Talep_ID"],
                )

    with col_edit:
        st.markdown("**✏️ Durum Güncelle**")
        yeni_dur = st.selectbox("Durum", ["Dolu", "Boş", "Bakımda"],
                                index=["Dolu", "Boş", "Bakımda"].index(row.get("Durum", "Boş"))
                                if row.get("Durum") in ["Dolu", "Boş", "Bakımda"] else 0,
                                key=f"dur_{daire_id}")
        yeni_not = st.text_area("Notlar", value=str(row.get("Notlar", "")), key=f"not_{daire_id}")

        col_gn, col_sil = st.columns(2)
        if col_gn.button("💾 Güncelle", key=f"gn_{daire_id}", type="primary"):
            df.loc[df["Daire_ID"] == daire_id, "Durum"] = yeni_dur
            df.loc[df["Daire_ID"] == daire_id, "Notlar"] = yeni_not
            save_data(df, "daire")
            st.success("Güncellendi.")
            st.rerun()
        if col_sil.button("🗑️ Sil", key=f"sil_{daire_id}"):
            df2 = df[df["Daire_ID"] != daire_id]
            save_data(df2, "daire")
            st.warning("Silindi.")
            st.rerun()

        st.markdown("---")
        st.markdown("**📎 Belgeler & Fotoğraflar**")
        upload_widget("daire", daire_id, "Sistem", label="📎 Belge / Fotoğraf ekle")
        render_photo_grid("daire", daire_id, cols_per_row=2)


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
    st.subheader("🔍 Sakin Detayı")
    aktifler = df_s[df_s["Aktif"].astype(str).str.lower() == "evet"]
    if not aktifler.empty:
        sec = st.selectbox("Sakin seç",
                           [f"{r['Sakin_ID']} - {r['Ad_Soyad']} ({r['Daire_ID']})"
                            for _, r in aktifler.iterrows()])
        sid = sec.split(" - ")[0]
        sakin_row = df_s[df_s["Sakin_ID"] == sid].iloc[0]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:14px;">'
                f'<b>{sakin_row.get("Ad_Soyad","")}</b> · {sakin_row.get("Tip","")}<br>'
                f'Daire: <b>{sakin_row.get("Daire_ID","")}</b><br>'
                f'📞 {sakin_row.get("Telefon","—")} · 📧 {sakin_row.get("Email","—")}<br>'
                f'Giriş: {sakin_row.get("Giris_Tarihi","")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Belge yükleme
            st.markdown("**📎 Belgeler**")
            upload_widget("sakin", sid, "Sistem", label="📎 Sözleşme / Belge ekle")
            render_photo_grid("sakin", sid, cols_per_row=2)

        with col_b:
            if st.button("🚪 Çıkış Kaydet", key=f"cikis_{sid}"):
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
