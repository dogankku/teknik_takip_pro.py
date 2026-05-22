from style import section_header
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db import load_data, save_data
from barkod import yeni_id
from auth import current_user
from constants import BAKIM_PERIYOT
from yorum_helper import render_yorumlar
from media import upload_widget, render_photo_grid


def render(secilen_tarih: date):
    section_header("Periyodik Bakım", "Planlama ve uyumluluk takibi", pill="ÖNLEYİCİ BAKIM")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Planlar", "➕ Yeni Plan", "📜 Bakım Geçmişi", "📊 İstatistikler"])

    with tab1: _planlar(secilen_tarih)
    with tab2: _yeni_plan()
    with tab3: _gecmis()
    with tab4: _istatistikler()


def _planlar(secilen_tarih: date):
    df = load_data("bakim_plan")
    df_p = load_data("personel")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    if df.empty:
        st.info("Henüz plan oluşturulmamış.")
        return

    df = df.copy()
    df["_st"] = pd.to_datetime(df["Sonraki_Tarih"], errors="coerce")
    bugun = pd.Timestamp(secilen_tarih)

    def _dur(t):
        if pd.isna(t): return "❓"
        d = (t - bugun).days
        if d < 0: return f"🔴 {-d} gün gecikti"
        if d == 0: return "🟡 Bugün"
        if d <= 7: return f"🟠 {d} gün"
        return f"🟢 {d} gün"
    df["Durum_İşaret"] = df["_st"].apply(_dur)

    c1, c2 = st.columns(2)
    sf = c1.selectbox("Filtre", ["Tümü", "Geciken", "Yaklaşan (7 gün)", "Yasal Zorunlu"])
    g = df.copy()
    if sf == "Geciken":
        g = g[g["_st"] < bugun]
    elif sf == "Yaklaşan (7 gün)":
        g = g[(g["_st"] >= bugun) & (g["_st"] <= bugun + pd.Timedelta(days=7))]
    elif sf == "Yasal Zorunlu":
        g = g[g["Yasal_Zorunlu"].astype(str).str.lower().isin(["evet", "true", "yes"])]

    st.dataframe(
        g[["Plan_ID", "Baslik", "Ekipman", "Lokasyon", "Periyot_Gun",
           "Son_Yapilma", "Sonraki_Tarih", "Durum_İşaret", "Sorumlu", "Yasal_Zorunlu"]],
        use_container_width=True, hide_index=True,
    )

    st.divider()
    tabs_det = st.tabs(["✅ Bakım Yaptı Kaydı", "✏️ Plan Düzenle / Sil", "💬 Yorumlar & Foto"])

    with tabs_det[0]:
        sec = st.selectbox("Plan", df["Plan_ID"].tolist(), key="bakim_sec")
        plan = df[df["Plan_ID"] == sec].iloc[0]
        st.write(f"**{plan['Baslik']}** • Ekipman: {plan.get('Ekipman','')} • "
                 f"Periyot: {plan.get('Periyot_Gun','')} gün")

        with st.form("yap_form"):
            c_y1, c_y2 = st.columns(2)
            yapan = c_y1.selectbox("Yapan", pers)
            ack = st.text_area("Bakım Açıklaması / Bulgular")
            c_m1, c_m2 = st.columns(2)
            mal_m = c_m1.number_input("Malzeme Maliyeti (₺)", min_value=0.0, step=10.0)
            isc_m = c_m2.number_input("İşçilik Maliyeti (₺)", min_value=0.0, step=10.0)

            if st.form_submit_button("✅ Bakım Yapıldı Olarak Kaydet", type="primary"):
                try:
                    periyot = int(plan.get("Periyot_Gun", 30))
                except Exception:
                    periyot = 30
                bugun_str = str(date.today())
                sonraki = (date.today() + timedelta(days=periyot)).strftime("%Y-%m-%d")

                df_orig = load_data("bakim_plan")
                df_orig.loc[df_orig["Plan_ID"] == sec, "Son_Yapilma"] = bugun_str
                df_orig.loc[df_orig["Plan_ID"] == sec, "Sonraki_Tarih"] = sonraki
                save_data(df_orig, "bakim_plan")

                df_log = load_data("bakim_log")
                log_row = {
                    "Log_ID": yeni_id("BLG"), "Plan_ID": sec,
                    "Tarih": bugun_str, "Yapan": yapan,
                    "Aciklama": ack, "Sonraki_Tarih": sonraki,
                    "Malzeme_Maliyet": mal_m, "Iscilik_Maliyet": isc_m,
                }
                df_log = pd.concat([df_log, pd.DataFrame([log_row])], ignore_index=True)
                save_data(df_log, "bakim_log")
                st.success(f"Kaydedildi. Sonraki bakım: {sonraki}")
                st.rerun()

    with tabs_det[1]:
        sec2 = st.selectbox("Plan", df["Plan_ID"].tolist(), key="bakim_edit")
        plan2 = df[df["Plan_ID"] == sec2].iloc[0]
        with st.form(f"plan_edit_{sec2}"):
            c1, c2 = st.columns(2)
            new_b = c1.text_input("Başlık", value=str(plan2.get("Baslik", "")))
            new_lok = c2.text_input("Lokasyon", value=str(plan2.get("Lokasyon", "")))
            c3, c4 = st.columns(2)
            new_per = c3.number_input("Periyot (gün)",
                                       value=int(pd.to_numeric(plan2.get("Periyot_Gun", 30), errors="coerce") or 30),
                                       min_value=1)
            sor_idx = pers.index(plan2.get("Sorumlu")) if plan2.get("Sorumlu") in pers else 0
            new_sor = c4.selectbox("Sorumlu", pers, index=sor_idx)
            try:
                st_val = pd.to_datetime(plan2.get("Sonraki_Tarih")).date()
            except Exception:
                st_val = date.today()
            new_st = st.date_input("Sonraki Tarih", value=st_val)
            new_yasal = st.selectbox("Yasal Zorunlu",
                                     ["Hayır", "Evet"],
                                     index=1 if str(plan2.get("Yasal_Zorunlu", "")).lower() in ["evet", "true"] else 0)
            new_not = st.text_area("Notlar", value=str(plan2.get("Notlar", "")))

            col_s, col_d = st.columns(2)
            if col_s.form_submit_button("💾 Güncelle", type="primary"):
                df_orig = load_data("bakim_plan")
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Baslik"] = new_b
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Lokasyon"] = new_lok
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Periyot_Gun"] = new_per
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Sorumlu"] = new_sor
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Sonraki_Tarih"] = str(new_st)
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Yasal_Zorunlu"] = new_yasal
                df_orig.loc[df_orig["Plan_ID"] == sec2, "Notlar"] = new_not
                save_data(df_orig, "bakim_plan")
                st.success("Güncellendi.")
                st.rerun()
            if col_d.form_submit_button("🗑️ Planı Sil"):
                df_orig = load_data("bakim_plan")
                df_orig = df_orig[df_orig["Plan_ID"] != sec2]
                save_data(df_orig, "bakim_plan")
                st.warning("Plan silindi.")
                st.rerun()

    with tabs_det[2]:
        sec3 = st.selectbox("Plan", df["Plan_ID"].tolist(), key="bakim_yorum")
        col_y, col_m = st.columns(2)
        with col_y:
            render_yorumlar("bakim_plan", sec3, kullanici)
        with col_m:
            upload_widget("bakim_plan", sec3, kullanici)
            render_photo_grid("bakim_plan", sec3, cols_per_row=2)


def _yeni_plan():
    df_p = load_data("personel")
    df_e = load_data("ekipman")
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]
    ekip_ops = ["-"] + (df_e["Ekipman_Adi"].tolist() if not df_e.empty else [])

    with st.form("add_plan"):
        c1, c2 = st.columns(2)
        b = c1.text_input("Plan Başlığı *", placeholder="Asansör aylık bakımı")
        ek = c2.selectbox("İlgili Ekipman", ekip_ops)
        c3, c4 = st.columns(2)
        lok = c3.text_input("Lokasyon", placeholder="A Blok Asansör")
        per_secim = c4.selectbox("Periyot", list(BAKIM_PERIYOT.keys()))
        per_gun = BAKIM_PERIYOT[per_secim]
        c5, c6 = st.columns(2)
        ozel_gun = c5.number_input("Özel Periyot (gün, 0=şablon)", min_value=0, max_value=3650, value=0)
        bas_tarih = c6.date_input("İlk Bakım Tarihi", date.today())
        c7, c8 = st.columns(2)
        sor = c7.selectbox("Sorumlu", pers)
        yasal = c8.selectbox("Yasal Zorunlu", ["Hayır", "Evet"])
        notlar = st.text_area("Notlar")

        if st.form_submit_button("💾 Plan Kaydet", type="primary"):
            if b.strip():
                periyot = ozel_gun if ozel_gun > 0 else per_gun
                row = {
                    "Plan_ID": yeni_id("PLN"), "Baslik": b.strip(),
                    "Ekipman": "" if ek == "-" else ek, "Lokasyon": lok,
                    "Periyot_Gun": periyot, "Sorumlu": sor,
                    "Yasal_Zorunlu": yasal, "Son_Yapilma": "",
                    "Sonraki_Tarih": str(bas_tarih),
                    "Durum": "Aktif", "Notlar": notlar,
                }
                df = load_data("bakim_plan")
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "bakim_plan")
                st.success("Plan kaydedildi.")
                st.rerun()
            else:
                st.error("Başlık zorunlu.")

    st.divider()
    st.info("""
    **💡 Yasal zorunlu bakım örnekleri (T.C.):**
    - Asansör: Aylık + Yıllık muayene
    - Yangın söndürme cihazları: 6 aylık
    - Yangın hidrant/sprinkler: Yıllık
    - Jeneratör: Aylık çalıştırma
    - Paratoner: Yıllık ölçüm
    - LPG/Doğalgaz tesisatı: 2 yıllık sızdırmazlık testi
    """)


def _gecmis():
    df = load_data("bakim_log")
    if df.empty:
        st.info("Henüz bakım kaydı yok.")
        return

    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today().replace(day=1))
    bit = c2.date_input("Bitiş", date.today())

    try:
        d = pd.to_datetime(df["Tarih"], errors="coerce")
        df_f = df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]
    except Exception:
        df_f = df

    mal = pd.to_numeric(df_f.get("Malzeme_Maliyet", pd.Series()), errors="coerce").fillna(0).sum()
    isc = pd.to_numeric(df_f.get("Iscilik_Maliyet", pd.Series()), errors="coerce").fillna(0).sum()
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Bakım Sayısı", len(df_f))
    c2m.metric("Malzeme ₺", f"{mal:,.0f}")
    c3m.metric("İşçilik ₺", f"{isc:,.0f}")

    st.dataframe(df_f.sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True)


def _istatistikler():
    df_plan = load_data("bakim_plan")
    df_log = load_data("bakim_log")

    if df_plan.empty:
        st.info("Veri yok.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Plan", len(df_plan))
    yasal = len(df_plan[df_plan["Yasal_Zorunlu"].astype(str).str.lower().isin(["evet", "true"])])
    c2.metric("Yasal Zorunlu", yasal)
    toplam_log = len(df_log)
    c3.metric("Toplam Bakım Yapıldı", toplam_log)

    if not df_log.empty:
        st.markdown("---")
        toplam_mal = pd.to_numeric(df_log.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum()
        toplam_isc = pd.to_numeric(df_log.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum()
        c4, c5, c6 = st.columns(3)
        c4.metric("Toplam Maliyet", f"{toplam_mal + toplam_isc:,.0f} ₺")
        c5.metric("Malzeme ₺", f"{toplam_mal:,.0f}")
        c6.metric("İşçilik ₺", f"{toplam_isc:,.0f}")
