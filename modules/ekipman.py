import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from barkod import make_barcode, make_qr, yeni_barkod_id, toplu_barkod_pdf
from constants import EKIPMAN_KATEGORI


def render(secilen_tarih: date):
    st.header("📦 Ekipman Takip & Barkod Sistemi")
    df_e = load_data("ekipman")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Ekipman Listesi", "➕ Yeni Ekipman", "🔍 Barkod Sorgula", "🖨️ Toplu Etiket PDF"]
    )

    with tab1:
        if df_e.empty:
            st.info("Henüz ekipman eklenmemiş.")
        else:
            c1, c2 = st.columns(2)
            kats = ["Tümü"] + sorted(df_e["Kategori"].dropna().unique().tolist())
            kf = c1.selectbox("Kategori", kats)
            durs = ["Tümü"] + sorted(df_e["Durum"].dropna().unique().tolist())
            df_filt = c2.selectbox("Durum", durs)
            g = df_e.copy()
            if kf != "Tümü": g = g[g["Kategori"] == kf]
            if df_filt != "Tümü": g = g[g["Durum"] == df_filt]
            st.dataframe(g, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🔖 Barkod & QR Görüntüle")
            sec = st.selectbox("Ekipman", df_e["Ekipman_Adi"].tolist())
            if sec:
                row = df_e[df_e["Ekipman_Adi"] == sec].iloc[0]
                bid = str(row.get("Barkod_ID", ""))
                cb, cq = st.columns(2)
                with cb:
                    st.caption("**📊 Code-128**")
                    bc = make_barcode(bid)
                    if bc:
                        st.image(bc, caption=bid)
                        st.download_button("⬇️ İndir", bc, f"{bid}_barkod.png", "image/png")
                    else:
                        st.warning("Barkod kütüphanesi yok.")
                with cq:
                    st.caption("**📱 QR Kod**")
                    qr_data = "\n".join([
                        f"ID: {row.get('Barkod_ID','')}",
                        f"Ekipman: {row.get('Ekipman_Adi','')}",
                        f"Lokasyon: {row.get('Lokasyon','')}",
                        f"Marka/Model: {row.get('Marka_Model','')}",
                        f"Seri No: {row.get('Seri_No','')}",
                    ])
                    qr = make_qr(qr_data)
                    if qr:
                        st.image(qr, width=220)
                        st.download_button("⬇️ İndir", qr, f"{bid}_qr.png", "image/png")
                    else:
                        st.warning("QR kütüphanesi yok.")
                with st.expander("Detaylar"):
                    st.json(row.to_dict())

    with tab2:
        auto = yeni_barkod_id()
        st.info(f"🏷️ Otomatik Barkod ID: **{auto}**")
        with st.form("add_ek"):
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ekipman Adı *")
            kat = c2.selectbox("Kategori", EKIPMAN_KATEGORI)
            c3, c4 = st.columns(2)
            lok = c3.text_input("Lokasyon")
            mm = c4.text_input("Marka / Model")
            c5, c6 = st.columns(2)
            sn = c5.text_input("Seri No")
            dur = c6.selectbox("Durum", ["Aktif", "Bakımda", "Arızalı", "Hurdaya Ayrıldı"])
            c7, c8 = st.columns(2)
            sa = c7.date_input("Satın Alma", date.today())
            sb = c8.date_input("Sonraki Bakım", date.today())
            n = st.text_area("Notlar")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                if ad.strip():
                    row = {
                        "Barkod_ID": auto, "Ekipman_Adi": ad.strip(), "Kategori": kat,
                        "Lokasyon": lok, "Marka_Model": mm, "Seri_No": sn,
                        "Satin_Alma": str(sa), "Sonraki_Bakim": str(sb),
                        "Durum": dur, "Notlar": n,
                    }
                    df_e = pd.concat([df_e, pd.DataFrame([row])], ignore_index=True)
                    save_data(df_e, "ekipman")
                    st.success(f"Kaydedildi! ID: {auto}")
                    st.rerun()
                else:
                    st.error("Ad zorunlu.")

    with tab3:
        q = st.text_input("Arama", placeholder="EKP-... veya pompa")
        if q and not df_e.empty:
            s = df_e[df_e.apply(
                lambda r: q.lower() in str(r.get("Barkod_ID", "")).lower()
                or q.lower() in str(r.get("Ekipman_Adi", "")).lower(), axis=1)]
            if not s.empty:
                st.success(f"{len(s)} ekipman bulundu.")
                st.dataframe(s, use_container_width=True, hide_index=True)
            else:
                st.warning("Bulunamadı.")

    with tab4:
        st.subheader("🖨️ Toplu Barkod Etiket PDF (A4, 24 etiket/sayfa)")
        if df_e.empty:
            st.info("Önce ekipman ekleyin.")
        else:
            secim = st.multiselect("Ekipmanlar (boş = hepsi)", df_e["Ekipman_Adi"].tolist())
            kullan = df_e[df_e["Ekipman_Adi"].isin(secim)] if secim else df_e
            st.write(f"**{len(kullan)}** etiket üretilecek")
            if st.button("📄 PDF Üret"):
                items = [{"id": r["Barkod_ID"], "ad": r["Ekipman_Adi"],
                          "lokasyon": r.get("Lokasyon", "")} for _, r in kullan.iterrows()]
                pdf = toplu_barkod_pdf(items)
                if pdf:
                    st.download_button("⬇️ Etiket PDF İndir", pdf,
                                       f"barkod_etiket_{date.today()}.pdf",
                                       "application/pdf")
                else:
                    st.error("reportlab yüklü değil. `pip install reportlab`")
