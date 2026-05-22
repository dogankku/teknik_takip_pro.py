from style import section_header
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db import load_data, save_data
from auth import current_role, current_user
from barkod import yeni_id


def render(secilen_tarih: date):
    rol = current_role()
    if rol == "Sakin":
        _sakin_view()
        return

    section_header("Aidat & Tahsilat", "Tahakkuk, ödeme ve borç takibi", pill="MALİ")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Borç Durumu", "📝 Tahakkuk", "💵 Tahsilat", "📦 Toplu Tahakkuk"]
    )
    with tab1: _borc_durumu()
    with tab2: _tahakkuk()
    with tab3: _tahsilat()
    with tab4: _toplu_tahakkuk()


def _toplam_borc(df_th: pd.DataFrame, df_od: pd.DataFrame) -> pd.DataFrame:
    """Daire bazlı toplam borç hesapla."""
    df_d = load_data("daire")
    if df_d.empty:
        return pd.DataFrame()
    result = []
    for _, d in df_d.iterrows():
        did = d["Daire_ID"]
        th = pd.to_numeric(
            df_th[df_th["Daire_ID"].astype(str) == str(did)].get("Tutar", pd.Series()),
            errors="coerce",
        ).fillna(0).sum() if not df_th.empty else 0
        od = pd.to_numeric(
            df_od[df_od["Daire_ID"].astype(str) == str(did)].get("Tutar", pd.Series()),
            errors="coerce",
        ).fillna(0).sum() if not df_od.empty else 0
        result.append({
            "Daire_ID": did, "Blok": d.get("Blok", ""), "Daire_No": d.get("Daire_No", ""),
            "Toplam_Tahakkuk": th, "Toplam_Ödeme": od, "Bakiye": th - od,
        })
    return pd.DataFrame(result)


def _borc_durumu():
    df_th = load_data("tahakkuk")
    df_od = load_data("odeme")
    bd = _toplam_borc(df_th, df_od)
    if bd.empty:
        st.info("Önce daire ve tahakkuk girişi yapın.")
        return

    toplam_th = bd["Toplam_Tahakkuk"].sum()
    toplam_od = bd["Toplam_Ödeme"].sum()
    toplam_bk = bd["Bakiye"].sum()
    borclu_say = (bd["Bakiye"] > 0).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Tahakkuk", f"{toplam_th:,.2f} ₺")
    c2.metric("Toplam Tahsilat", f"{toplam_od:,.2f} ₺")
    c3.metric("Açık Bakiye", f"{toplam_bk:,.2f} ₺")
    c4.metric("Borçlu Daire", f"{borclu_say}")

    st.divider()
    sf = st.selectbox("Filtre", ["Tümü", "Sadece Borçlu", "Sadece Ödemiş"])
    g = bd.copy()
    if sf == "Sadece Borçlu":
        g = g[g["Bakiye"] > 0]
    elif sf == "Sadece Ödemiş":
        g = g[g["Bakiye"] <= 0]
    g = g.sort_values("Bakiye", ascending=False)
    st.dataframe(
        g.style.format({"Toplam_Tahakkuk": "{:,.2f} ₺",
                        "Toplam_Ödeme": "{:,.2f} ₺",
                        "Bakiye": "{:,.2f} ₺"}),
        use_container_width=True, hide_index=True,
    )


def _tahakkuk():
    df_d = load_data("daire")
    if df_d.empty:
        st.warning("Önce daire ekleyin.")
        return
    df_th = load_data("tahakkuk")

    with st.form("add_th"):
        c1, c2 = st.columns(2)
        d = c1.selectbox("Daire", df_d["Daire_ID"].tolist())
        donem = c2.text_input("Dönem (YYYY-MM)", value=date.today().strftime("%Y-%m"))
        c3, c4 = st.columns(2)
        tutar = c3.number_input("Tutar (₺)", min_value=0.0, value=500.0, step=10.0)
        son_od = c4.date_input("Son Ödeme Tarihi",
                                date.today().replace(day=1) + timedelta(days=30))
        ack = st.text_input("Açıklama", value="Aylık aidat")
        if st.form_submit_button("💾 Tahakkuk Ekle", type="primary"):
            row = {"Tahakkuk_ID": yeni_id("THK"), "Daire_ID": d,
                   "Donem": donem, "Tutar": tutar,
                   "Son_Odeme": str(son_od), "Aciklama": ack}
            df_th = pd.concat([df_th, pd.DataFrame([row])], ignore_index=True)
            save_data(df_th, "tahakkuk")
            st.success("Eklendi.")
            st.rerun()

    if not df_th.empty:
        st.dataframe(df_th.sort_values("Donem", ascending=False),
                     use_container_width=True, hide_index=True)


def _tahsilat():
    df_d = load_data("daire")
    if df_d.empty:
        st.warning("Önce daire ekleyin.")
        return
    df_od = load_data("odeme")

    with st.form("add_od"):
        c1, c2 = st.columns(2)
        d = c1.selectbox("Daire", df_d["Daire_ID"].tolist())
        tar = c2.date_input("Ödeme Tarihi", date.today())
        c3, c4 = st.columns(2)
        tut = c3.number_input("Tutar (₺)", min_value=0.0, value=500.0, step=10.0)
        yon = c4.selectbox("Yöntem", ["Nakit", "Banka EFT", "Havale", "Kredi Kartı", "Online"])
        ack = st.text_input("Açıklama", value="Aidat ödemesi")
        if st.form_submit_button("💵 Ödeme Kaydet", type="primary"):
            row = {"Odeme_ID": yeni_id("ODM"), "Daire_ID": d,
                   "Tarih": str(tar), "Tutar": tut,
                   "Yontem": yon, "Aciklama": ack}
            df_od = pd.concat([df_od, pd.DataFrame([row])], ignore_index=True)
            save_data(df_od, "odeme")
            st.success("Ödeme kaydedildi.")
            st.rerun()

    if not df_od.empty:
        st.dataframe(df_od.sort_values("Tarih", ascending=False),
                     use_container_width=True, hide_index=True)


def _toplu_tahakkuk():
    df_d = load_data("daire")
    if df_d.empty:
        st.warning("Önce daire ekleyin.")
        return

    st.info("Tüm dairelere aynı dönem için tahakkuk oluşturur.")
    with st.form("toplu_th"):
        c1, c2 = st.columns(2)
        donem = c1.text_input("Dönem (YYYY-MM)", value=date.today().strftime("%Y-%m"))
        son_od = c2.date_input("Son Ödeme", date.today() + timedelta(days=20))
        sabit = st.checkbox("Sabit tutar (tüm dairelere aynı)", value=False)
        tutar_sabit = st.number_input("Sabit Tutar", value=500.0) if sabit else 0
        if not sabit:
            st.caption("m² bazlı hesap: birim fiyat × m²")
            birim = st.number_input("m² başına fiyat (₺)", value=5.0)
        ack = st.text_input("Açıklama", value=f"Aidat - {donem}")

        if st.form_submit_button("📦 Toplu Tahakkuk Oluştur", type="primary"):
            df_th = load_data("tahakkuk")
            yeni_rows = []
            for _, d in df_d.iterrows():
                if sabit:
                    t = tutar_sabit
                else:
                    try:
                        m2 = float(d.get("M2", 0))
                    except Exception:
                        m2 = 0
                    t = round(birim * m2, 2)
                yeni_rows.append({
                    "Tahakkuk_ID": yeni_id("THK"), "Daire_ID": d["Daire_ID"],
                    "Donem": donem, "Tutar": t, "Son_Odeme": str(son_od),
                    "Aciklama": ack,
                })
            df_th = pd.concat([df_th, pd.DataFrame(yeni_rows)], ignore_index=True)
            save_data(df_th, "tahakkuk")
            st.success(f"{len(yeni_rows)} tahakkuk oluşturuldu.")
            st.rerun()


def _sakin_view():
    u = current_user() or {}
    daire_id = u.get("Daire_ID", "")
    section_header("Aidat Borç Durumu", "Mevcut bakiyeniz ve ödeme geçmişi", pill="DAİRENİZ")
    st.caption(f"Daire: **{daire_id or '(atanmamış)'}**")
    if not daire_id:
        return

    df_th = load_data("tahakkuk")
    df_od = load_data("odeme")
    m_th = df_th[df_th["Daire_ID"].astype(str) == str(daire_id)] if not df_th.empty else pd.DataFrame()
    m_od = df_od[df_od["Daire_ID"].astype(str) == str(daire_id)] if not df_od.empty else pd.DataFrame()

    th_tot = pd.to_numeric(m_th.get("Tutar", pd.Series()), errors="coerce").fillna(0).sum()
    od_tot = pd.to_numeric(m_od.get("Tutar", pd.Series()), errors="coerce").fillna(0).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Tahakkuk", f"{th_tot:,.2f} ₺")
    c2.metric("Toplam Ödeme", f"{od_tot:,.2f} ₺")
    c3.metric("Bakiye", f"{th_tot-od_tot:,.2f} ₺",
              delta="Borçlu" if th_tot - od_tot > 0 else "Tamam",
              delta_color="inverse" if th_tot - od_tot > 0 else "normal")

    st.subheader("📝 Tahakkuk Detayı")
    if not m_th.empty:
        st.dataframe(m_th.sort_values("Donem", ascending=False),
                     use_container_width=True, hide_index=True)

    st.subheader("💵 Ödeme Geçmişi")
    if not m_od.empty:
        st.dataframe(m_od.sort_values("Tarih", ascending=False),
                     use_container_width=True, hide_index=True)
