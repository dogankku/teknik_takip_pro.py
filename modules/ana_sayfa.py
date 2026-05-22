import streamlit as st
import pandas as pd
from datetime import date, datetime
from db import load_data
from auth import current_user, current_role


def render(secilen_tarih: date):
    u = current_user() or {}
    rol = current_role() or ""

    st.header(f"👋 Hoşgeldiniz, {u.get('Ad_Soyad', '')}")
    st.caption(f"Rol: **{rol}** • Tarih: **{secilen_tarih.strftime('%d.%m.%Y')}**")
    st.divider()

    if rol == "Sakin":
        _sakin_dashboard(u, secilen_tarih)
    else:
        _yonetim_dashboard(secilen_tarih)


def _yonetim_dashboard(secilen_tarih: date):
    df_a = load_data("ariza")
    df_t = load_data("talep")
    df_b = load_data("bakim_plan")
    df_s = load_data("stok")

    bugun = str(secilen_tarih)
    acik_ariza = df_a[df_a.get("Durum", "") == "Açık"] if not df_a.empty else pd.DataFrame()
    acik_talep = df_t[~df_t.get("Durum", pd.Series()).isin(["Çözüldü", "Kapatıldı"])] if not df_t.empty else pd.DataFrame()

    geciken_bakim = pd.DataFrame()
    if not df_b.empty and "Sonraki_Tarih" in df_b.columns:
        df_b["_st"] = pd.to_datetime(df_b["Sonraki_Tarih"], errors="coerce")
        geciken_bakim = df_b[df_b["_st"] < pd.Timestamp(secilen_tarih)]

    kritik_stok = pd.DataFrame()
    if not df_s.empty and "Mevcut" in df_s.columns and "Kritik" in df_s.columns:
        df_s["_m"] = pd.to_numeric(df_s["Mevcut"], errors="coerce").fillna(0)
        df_s["_k"] = pd.to_numeric(df_s["Kritik"], errors="coerce").fillna(0)
        kritik_stok = df_s[df_s["_m"] <= df_s["_k"]]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🛠️ Açık Arıza", len(acik_ariza))
    c2.metric("📨 Açık Talep", len(acik_talep))
    c3.metric("⏰ Geciken Bakım", len(geciken_bakim))
    c4.metric("⚠️ Kritik Stok", len(kritik_stok))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⏰ Geciken / Yaklaşan Bakımlar")
        if not df_b.empty:
            df_b["_st"] = pd.to_datetime(df_b["Sonraki_Tarih"], errors="coerce")
            yaklasik = df_b.sort_values("_st").head(10)[["Baslik", "Ekipman", "Sonraki_Tarih", "Sorumlu"]]
            st.dataframe(yaklasik, use_container_width=True, hide_index=True)
        else:
            st.info("Bakım planı henüz girilmemiş.")

    with col2:
        st.subheader("📨 Bekleyen Talepler (öncelik sıralı)")
        if not acik_talep.empty:
            oncelik_sira = {"Kritik": 0, "Yuksek": 1, "Normal": 2, "Dusuk": 3}
            acik_talep = acik_talep.copy()
            acik_talep["_o"] = acik_talep.get("Oncelik", "Normal").map(oncelik_sira).fillna(2)
            acik_talep = acik_talep.sort_values("_o").head(10)
            st.dataframe(
                acik_talep[["Talep_ID", "Daire_ID", "Baslik", "Oncelik", "Durum", "Atanan"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.success("Açık talep yok!")

    if not kritik_stok.empty:
        st.subheader("⚠️ Kritik Stok Uyarıları")
        st.dataframe(
            kritik_stok[["Urun_Adi", "Kategori", "Mevcut", "Kritik", "Birim", "Depo_Yeri"]],
            use_container_width=True, hide_index=True,
        )


def _sakin_dashboard(u: dict, secilen_tarih: date):
    daire_id = u.get("Daire_ID", "")
    st.info(f"🏠 Daire: **{daire_id or 'Atanmamış'}**")

    # Borç hesabı
    df_th = load_data("tahakkuk")
    df_od = load_data("odeme")
    toplam_borc = 0.0
    toplam_odeme = 0.0
    if not df_th.empty:
        m = df_th[df_th["Daire_ID"].astype(str) == str(daire_id)]
        toplam_borc = pd.to_numeric(m.get("Tutar"), errors="coerce").fillna(0).sum()
    if not df_od.empty:
        m = df_od[df_od["Daire_ID"].astype(str) == str(daire_id)]
        toplam_odeme = pd.to_numeric(m.get("Tutar"), errors="coerce").fillna(0).sum()
    bakiye = toplam_borc - toplam_odeme

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Tahakkuk", f"{toplam_borc:,.2f} ₺")
    c2.metric("Toplam Ödeme", f"{toplam_odeme:,.2f} ₺")
    c3.metric("Bakiye (Borç)", f"{bakiye:,.2f} ₺",
              delta="Borçlu" if bakiye > 0 else "Tamam",
              delta_color="inverse" if bakiye > 0 else "normal")

    st.divider()
    st.subheader("📨 Taleplerim")
    df_t = load_data("talep")
    if not df_t.empty:
        mine = df_t[df_t["Daire_ID"].astype(str) == str(daire_id)]
        if not mine.empty:
            st.dataframe(
                mine[["Talep_ID", "Tarih", "Baslik", "Oncelik", "Durum", "Atanan"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("Henüz talebiniz yok.")
    else:
        st.info("Henüz talep kaydı yok.")
