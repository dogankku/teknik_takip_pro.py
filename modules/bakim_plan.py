import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db import load_data, save_data
from barkod import yeni_id
from constants import BAKIM_PERIYOT


def render(secilen_tarih: date):
    st.header("📅 Periyodik Bakım Planı")
    tab1, tab2, tab3 = st.tabs(["📋 Planlar", "➕ Yeni Plan", "📜 Bakım Geçmişi"])

    with tab1: _planlar(secilen_tarih)
    with tab2: _yeni_plan()
    with tab3: _gecmis()


def _planlar(secilen_tarih: date):
    df = load_data("bakim_plan")
    df_p = load_data("personel")
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    if df.empty:
        st.info("Henüz plan oluşturulmamış.")
        return

    # Durum hesapla
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
    st.subheader("✅ Bakım Yapıldı Kaydı")
    sec = st.selectbox("Plan", df["Plan_ID"].tolist())
    plan = df[df["Plan_ID"] == sec].iloc[0]
    st.write(f"**{plan['Baslik']}** • Ekipman: {plan.get('Ekipman','')} • "
             f"Periyot: {plan.get('Periyot_Gun','')} gün")

    with st.form("yap_form"):
        yapan = st.selectbox("Yapan", pers)
        ack = st.text_area("Bakım Açıklaması / Bulgular")
        if st.form_submit_button("✅ Bakım Yapıldı Olarak Kaydet", type="primary"):
            try:
                periyot = int(plan.get("Periyot_Gun", 30))
            except Exception:
                periyot = 30
            bugun_str = str(date.today())
            sonraki = (date.today() + timedelta(days=periyot)).strftime("%Y-%m-%d")

            # Plan güncelle
            df_orig = load_data("bakim_plan")
            df_orig.loc[df_orig["Plan_ID"] == sec, "Son_Yapilma"] = bugun_str
            df_orig.loc[df_orig["Plan_ID"] == sec, "Sonraki_Tarih"] = sonraki
            save_data(df_orig, "bakim_plan")

            # Log ekle
            df_log = load_data("bakim_log")
            log_row = {"Log_ID": yeni_id("BLG"), "Plan_ID": sec,
                       "Tarih": bugun_str, "Yapan": yapan,
                       "Aciklama": ack, "Sonraki_Tarih": sonraki}
            df_log = pd.concat([df_log, pd.DataFrame([log_row])], ignore_index=True)
            save_data(df_log, "bakim_log")
            st.success(f"Kaydedildi. Sonraki bakım: {sonraki}")
            st.rerun()


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
        ozel_gun = c5.number_input("Özel Periyot (gün, 0=şablon kullan)",
                                    min_value=0, max_value=3650, value=0)
        bas_tarih = c6.date_input("İlk Bakım Tarihi", date.today())
        c7, c8 = st.columns(2)
        sor = c7.selectbox("Sorumlu", pers)
        yasal = c8.selectbox("Yasal Zorunlu", ["Hayır", "Evet"])
        notlar = st.text_area("Notlar")

        if st.form_submit_button("💾 Plan Kaydet", type="primary"):
            if b.strip():
                periyot = ozel_gun if ozel_gun > 0 else per_gun
                row = {"Plan_ID": yeni_id("PLN"), "Baslik": b.strip(),
                       "Ekipman": "" if ek == "-" else ek, "Lokasyon": lok,
                       "Periyot_Gun": periyot, "Sorumlu": sor,
                       "Yasal_Zorunlu": yasal, "Son_Yapilma": "",
                       "Sonraki_Tarih": str(bas_tarih),
                       "Durum": "Aktif", "Notlar": notlar}
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
    st.dataframe(df.sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True)
