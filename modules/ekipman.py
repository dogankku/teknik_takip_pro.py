import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from barkod import make_barcode, make_qr, yeni_barkod_id, toplu_barkod_pdf
from constants import EKIPMAN_KATEGORI
from style import section_header, data_table, status_badge, avatar_chip
from media import upload_widget, render_photo_grid


DURUMLAR = ["Aktif", "Bakımda", "Arızalı", "Hurdaya Ayrıldı"]


def render(secilen_tarih: date):
    section_header("Ekipman & Barkod", "Code-128 barkod ve QR ile envanter takibi", pill="ENVANTER")
    df_e = load_data("ekipman")
    df_lok = load_data("lokasyon")

    lok_opts = ["—"]
    if not df_lok.empty:
        lok_opts += (df_lok["Ana_Lokasyon"].astype(str) + " → " +
                     df_lok["Ad"].astype(str)).tolist()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Liste", "➕ Yeni", "✏️ Düzenle", "🔍 Barkod Sorgula", "🖨️ Toplu PDF"]
    )

    with tab1:
        _liste(df_e)

    with tab2:
        _yeni(df_e, lok_opts)

    with tab3:
        _duzenle(df_e, lok_opts)

    with tab4:
        _barkod_sorgula(df_e)

    with tab5:
        _toplu_pdf(df_e)


def _liste(df_e: pd.DataFrame):
    if df_e.empty:
        st.info("Henüz ekipman eklenmemiş.")
        return

    c1, c2 = st.columns(2)
    kats = ["Tümü"] + sorted(df_e["Kategori"].dropna().unique().tolist())
    kf = c1.selectbox("Kategori", kats)
    durs = ["Tümü"] + sorted(df_e["Durum"].dropna().unique().tolist())
    df_filt = c2.selectbox("Durum", durs)

    g = df_e.copy()
    if kf != "Tümü": g = g[g["Kategori"] == kf]
    if df_filt != "Tümü": g = g[g["Durum"] == df_filt]

    arizali = len(df_e[df_e["Durum"] == "Arızalı"])
    bakimda = len(df_e[df_e["Durum"] == "Bakımda"])
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Toplam", len(df_e))
    c2m.metric("Arızalı", arizali, delta="⚠️" if arizali > 0 else None, delta_color="inverse")
    c3m.metric("Bakımda", bakimda)

    data_table(
        g,
        [("Barkod_ID", "Barkod"), ("Ekipman_Adi", "Ekipman"), ("Kategori", "Kategori"),
         ("Lokasyon", "Lokasyon"), ("Marka_Model", "Marka/Model"),
         ("Sonraki_Bakim", "Sonraki Bakım"), ("Durum", "Durum")],
        status_cols=["Durum"], id_cols=["Barkod_ID"],
    )

    # Arıza geçmişi inline
    if not df_e.empty:
        st.divider()
        st.subheader("🔗 Ekipman Arıza Geçmişi")
        sec_ad = st.selectbox("Ekipman", df_e["Ekipman_Adi"].tolist(), key="e_gecmis")
        df_a = load_data("ariza")
        if not df_a.empty:
            gecmis = df_a[df_a["Ariza_Tanimi"].str.contains(sec_ad, case=False, na=False) |
                          df_a["Lokasyon"].str.contains(sec_ad, case=False, na=False)]
            if not gecmis.empty:
                data_table(
                    gecmis,
                    [("ID", "ID"), ("Tarih", "Tarih"), ("Ariza_Tanimi", "Arıza"),
                     ("Sorumlu", "Sorumlu"), ("Durum", "Durum")],
                    status_cols=["Durum"], avatar_cols=["Sorumlu"], id_cols=["ID"],
                )
            else:
                st.caption("Bu ekipmana ait arıza kaydı yok.")

        # Fotoğraflar
        row_e = df_e[df_e["Ekipman_Adi"] == sec_ad].iloc[0]
        bid = str(row_e.get("Barkod_ID", ""))
        render_photo_grid("ekipman", bid, cols_per_row=3)


def _yeni(df_e: pd.DataFrame, lok_opts: list):
    auto = yeni_barkod_id()
    st.info(f"🏷️ Otomatik Barkod ID: **{auto}**")
    with st.form("add_ek"):
        c1, c2 = st.columns(2)
        ad = c1.text_input("Ekipman Adı *")
        kat = c2.selectbox("Kategori", EKIPMAN_KATEGORI)
        c3, c4 = st.columns(2)
        lok_sec = c3.selectbox("Lokasyon", lok_opts)
        lok_free = c4.text_input("Lokasyon (serbest)", placeholder="veya buraya yazın")
        c5, c6 = st.columns(2)
        mm = c5.text_input("Marka / Model")
        sn = c6.text_input("Seri No")
        c7, c8 = st.columns(2)
        dur = c7.selectbox("Durum", DURUMLAR)
        sa = c8.date_input("Satın Alma", date.today())
        sb = st.date_input("Sonraki Bakım", date.today())
        n = st.text_area("Notlar")
        if st.form_submit_button("💾 Kaydet", type="primary"):
            if ad.strip():
                lok_final = lok_free.strip() or (lok_sec if lok_sec != "—" else "")
                row = {
                    "Barkod_ID": auto, "Ekipman_Adi": ad.strip(), "Kategori": kat,
                    "Lokasyon": lok_final, "Marka_Model": mm, "Seri_No": sn,
                    "Satin_Alma": str(sa), "Sonraki_Bakim": str(sb),
                    "Durum": dur, "Notlar": n,
                }
                df_e = pd.concat([df_e, pd.DataFrame([row])], ignore_index=True)
                save_data(df_e, "ekipman")
                st.success(f"Kaydedildi! ID: {auto}")
                st.rerun()
            else:
                st.error("Ad zorunlu.")


def _duzenle(df_e: pd.DataFrame, lok_opts: list):
    if df_e.empty:
        st.info("Henüz ekipman yok.")
        return

    sec = st.selectbox("Ekipman seç", df_e["Ekipman_Adi"].tolist(), key="e_duzenle")
    row = df_e[df_e["Ekipman_Adi"] == sec].iloc[0]
    bid = str(row.get("Barkod_ID", ""))

    col_l, col_r = st.columns([2, 1])
    with col_l:
        with st.form(f"edit_ek_{bid}"):
            c1, c2 = st.columns(2)
            new_ad = c1.text_input("Ekipman Adı", value=str(row.get("Ekipman_Adi", "")))
            new_kat = c2.selectbox("Kategori", EKIPMAN_KATEGORI,
                                   index=EKIPMAN_KATEGORI.index(row.get("Kategori"))
                                   if row.get("Kategori") in EKIPMAN_KATEGORI else 0)
            c3, c4 = st.columns(2)
            new_lok = c3.text_input("Lokasyon", value=str(row.get("Lokasyon", "")))
            new_dur = c4.selectbox("Durum", DURUMLAR,
                                   index=DURUMLAR.index(row.get("Durum"))
                                   if row.get("Durum") in DURUMLAR else 0)
            c5, c6 = st.columns(2)
            new_mm = c5.text_input("Marka/Model", value=str(row.get("Marka_Model", "")))
            new_sn = c6.text_input("Seri No", value=str(row.get("Seri_No", "")))
            try:
                sb_val = pd.to_datetime(row.get("Sonraki_Bakim")).date()
            except Exception:
                sb_val = date.today()
            new_sb = st.date_input("Sonraki Bakım", value=sb_val)
            new_not = st.text_area("Notlar", value=str(row.get("Notlar", "")))

            col_s, col_d = st.columns(2)
            if col_s.form_submit_button("💾 Güncelle", type="primary"):
                df_e.loc[df_e["Barkod_ID"] == bid, "Ekipman_Adi"] = new_ad
                df_e.loc[df_e["Barkod_ID"] == bid, "Kategori"] = new_kat
                df_e.loc[df_e["Barkod_ID"] == bid, "Lokasyon"] = new_lok
                df_e.loc[df_e["Barkod_ID"] == bid, "Durum"] = new_dur
                df_e.loc[df_e["Barkod_ID"] == bid, "Marka_Model"] = new_mm
                df_e.loc[df_e["Barkod_ID"] == bid, "Seri_No"] = new_sn
                df_e.loc[df_e["Barkod_ID"] == bid, "Sonraki_Bakim"] = str(new_sb)
                df_e.loc[df_e["Barkod_ID"] == bid, "Notlar"] = new_not
                save_data(df_e, "ekipman")
                st.success("Güncellendi.")
                st.rerun()
            if col_d.form_submit_button("🗑️ Sil"):
                df_e = df_e[df_e["Barkod_ID"] != bid]
                save_data(df_e, "ekipman")
                st.warning("Silindi.")
                st.rerun()

    with col_r:
        st.markdown("**📸 Fotoğraf Ekle**")
        upload_widget("ekipman", bid, "Sistem")
        render_photo_grid("ekipman", bid, cols_per_row=1)

        st.markdown("---")
        st.markdown("**📊 Barkod / QR**")
        bc = make_barcode(bid)
        if bc:
            st.image(bc, caption=bid)
        qr = make_qr(f"ID:{bid}\n{row.get('Ekipman_Adi','')}\n{row.get('Lokasyon','')}")
        if qr:
            st.image(qr, width=150)


def _barkod_sorgula(df_e: pd.DataFrame):
    q = st.text_input("Arama (ID, ad, lokasyon)", placeholder="EKP-... veya pompa")
    if q and not df_e.empty:
        s = df_e[df_e.apply(
            lambda r: q.lower() in str(r.get("Barkod_ID", "")).lower()
            or q.lower() in str(r.get("Ekipman_Adi", "")).lower()
            or q.lower() in str(r.get("Lokasyon", "")).lower(), axis=1)]
        if not s.empty:
            st.success(f"{len(s)} ekipman bulundu.")
            st.dataframe(s, use_container_width=True, hide_index=True)
            if len(s) == 1:
                row = s.iloc[0]
                bid = str(row.get("Barkod_ID", ""))
                cb, cq = st.columns(2)
                with cb:
                    bc = make_barcode(bid)
                    if bc:
                        st.image(bc, caption=bid)
                        st.download_button("⬇️ Barkod", bc, f"{bid}.png", "image/png")
                with cq:
                    qr = make_qr(f"ID:{bid}\n{row.get('Ekipman_Adi','')}")
                    if qr:
                        st.image(qr, width=200)
                        st.download_button("⬇️ QR", qr, f"{bid}_qr.png", "image/png")
        else:
            st.warning("Bulunamadı.")


def _toplu_pdf(df_e: pd.DataFrame):
    st.subheader("🖨️ Toplu Barkod Etiket PDF (A4, 24 etiket/sayfa)")
    if df_e.empty:
        st.info("Önce ekipman ekleyin.")
        return
    secim = st.multiselect("Ekipmanlar (boş = hepsi)", df_e["Ekipman_Adi"].tolist())
    kullan = df_e[df_e["Ekipman_Adi"].isin(secim)] if secim else df_e
    st.write(f"**{len(kullan)}** etiket üretilecek")
    if st.button("📄 PDF Üret"):
        items = [{"id": r["Barkod_ID"], "ad": r["Ekipman_Adi"],
                  "lokasyon": r.get("Lokasyon", "")} for _, r in kullan.iterrows()]
        pdf = toplu_barkod_pdf(items)
        if pdf:
            st.download_button("⬇️ Etiket PDF İndir", pdf,
                               f"barkod_etiket_{date.today()}.pdf", "application/pdf")
        else:
            st.error("reportlab yüklü değil.")
