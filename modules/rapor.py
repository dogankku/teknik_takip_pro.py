from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data
from report import df_to_excel, df_to_pdf


def render(secilen_tarih: date):
    section_header("Raporlar", "PDF, Excel ve yedekleme", pill="ANALİZ")

    tab1, tab2, tab3 = st.tabs(["📅 Günlük Rapor", "📆 Dönem Raporu", "📦 Tüm Veri Yedek (Excel)"])

    with tab1:
        _gunluk(secilen_tarih)
    with tab2:
        _donem()
    with tab3:
        _yedek()


def _gunluk(t: date):
    ts = str(t)
    df_c = load_data("checklist")
    df_a = load_data("ariza")
    df_v = load_data("vardiya")
    df_tl = load_data("talep")

    gc = df_c[df_c["Tarih"] == ts] if not df_c.empty else pd.DataFrame()
    ga = df_a[df_a["Tarih"] == ts] if not df_a.empty else pd.DataFrame()
    gv = df_v[df_v["Tarih"] == ts] if not df_v.empty else pd.DataFrame()
    gt = df_tl[df_tl["Tarih"] == ts] if not df_tl.empty else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kontrol", len(gc))
    c2.metric("Arıza", len(ga))
    c3.metric("Talep", len(gt))
    c4.metric("Vardiya", len(gv))

    st.divider()

    c1, c2 = st.columns(2)
    if c1.button("📄 Günlük PDF Raporu Üret", use_container_width=True):
        pdf = df_to_pdf(
            f"Günlük Rapor - {t.strftime('%d.%m.%Y')}",
            [
                ("Kontrol Listesi", gc),
                ("Arızalar", ga),
                ("Talepler", gt),
                ("Vardiya", gv),
            ],
        )
        if pdf:
            st.download_button("⬇️ PDF İndir", pdf,
                f"gunluk_rapor_{ts}.pdf", "application/pdf")
        else:
            st.error("reportlab yüklü değil.")

    if c2.button("📊 Günlük Excel Raporu", use_container_width=True):
        x = df_to_excel({"Kontrol": gc, "Arizalar": ga,
                         "Talepler": gt, "Vardiya": gv})
        st.download_button("⬇️ Excel İndir", x,
            f"gunluk_rapor_{ts}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def _donem():
    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today().replace(day=1))
    bit = c2.date_input("Bitiş", date.today())

    df_a = load_data("ariza")
    df_t = load_data("talep")
    df_g = load_data("gider")
    df_o = load_data("odeme")
    df_th = load_data("tahakkuk")

    def _aralik(df, col="Tarih"):
        if df.empty or col not in df.columns: return df
        d = pd.to_datetime(df[col], errors="coerce")
        return df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]

    f_a = _aralik(df_a)
    f_t = _aralik(df_t)
    f_g = _aralik(df_g)
    f_o = _aralik(df_o)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Arıza", len(f_a))
    c2.metric("Talep", len(f_t))
    toplam_g = pd.to_numeric(f_g.get("Tutar", pd.Series()), errors="coerce").fillna(0).sum()
    toplam_od = pd.to_numeric(f_o.get("Tutar", pd.Series()), errors="coerce").fillna(0).sum()
    c3.metric("Gider", f"{toplam_g:,.0f} ₺")
    c4.metric("Tahsilat", f"{toplam_od:,.0f} ₺")

    st.divider()
    if st.button("📄 Dönem PDF Raporu Üret", type="primary"):
        pdf = df_to_pdf(
            f"Dönem Raporu {bas} - {bit}",
            [
                ("Arızalar", f_a),
                ("Talepler", f_t),
                ("Giderler", f_g),
                ("Tahsilatlar", f_o),
            ],
        )
        if pdf:
            st.download_button("⬇️ PDF İndir", pdf,
                f"donem_rapor_{bas}_{bit}.pdf", "application/pdf")


def _yedek():
    st.info("Tüm verilerin Excel yedeği (her sheet ayrı tab).")
    keys = ["daire", "sakin", "kullanici", "ekipman", "ariza", "talep",
            "bakim_plan", "bakim_log", "tahakkuk", "odeme", "stok",
            "stok_hrk", "sayac", "okuma", "gider", "checklist",
            "vardiya", "personel"]
    if st.button("📦 Tüm Veriyi Yedekle (Excel)", type="primary"):
        sheets = {k: load_data(k) for k in keys}
        x = df_to_excel(sheets)
        st.download_button(
            "⬇️ Yedek İndir", x,
            f"yedek_{date.today()}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
