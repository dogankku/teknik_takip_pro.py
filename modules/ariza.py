import streamlit as st
import pandas as pd
from datetime import datetime, date
from db import load_data, save_data
from style import section_header
from auth import current_user
from barkod import yeni_id
from yorum_helper import render_yorumlar
from aktivite_helper import log_ekle
from media import upload_widget, render_photo_grid


BOLUMLER = ["Elektrik", "Mekanik", "Genel", "Bina", "Asansör", "HVAC", "Yangın", "Diğer"]
DURUMLAR = ["Açık", "Devam Ediyor", "Beklemede", "Tamamlandı", "İptal"]


def render(secilen_tarih: date):
    section_header("Arıza Takip", "Arıza kayıtları ve iş emri sistemi", pill="OPERASYON")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    df_a = load_data("ariza")
    df_p = load_data("personel")
    df_lok = load_data("lokasyon")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    lok_opts = ["—"]
    if not df_lok.empty:
        lok_opts += (df_lok["Ana_Lokasyon"].astype(str) + " → " +
                     df_lok["Ad"].astype(str)).tolist()

    tabs = st.tabs(["📋 Arıza Listesi", "➕ Yeni Arıza", "📊 İstatistikler"])

    # ── TAB 0: Liste + Detay ─────────────────────────────────────────────────
    with tabs[0]:
        if df_a.empty:
            st.info("Henüz arıza kaydı yok.")
        else:
            c1, c2, c3 = st.columns(3)
            f_dur = c1.multiselect("Durum", DURUMLAR, default=["Açık", "Devam Ediyor"])
            f_bol = c2.multiselect("Bölüm", BOLUMLER)
            f_sor = c3.selectbox("Sorumlu", ["Tümü"] + pl)

            g = df_a.copy()
            if f_dur: g = g[g["Durum"].isin(f_dur)]
            if f_bol: g = g[g["Bolum"].isin(f_bol)]
            if f_sor != "Tümü": g = g[g["Sorumlu"] == f_sor]

            g = g.sort_values("Tarih", ascending=False)
            st.dataframe(
                g[["ID", "Tarih", "Bolum", "Lokasyon", "Ariza_Tanimi",
                   "Sorumlu", "Durum", "Kapanis_Tarihi"]],
                use_container_width=True, hide_index=True,
            )

            st.divider()
            st.subheader("🔍 Arıza Detayı")
            secili_id = st.selectbox("Arıza seç", df_a["ID"].tolist())
            row = df_a[df_a["ID"] == secili_id].iloc[0]
            _ariza_detay(row, df_a, pl, kullanici)

    # ── TAB 1: Yeni Arıza ────────────────────────────────────────────────────
    with tabs[1]:
        with st.form("add_ariza"):
            c1, c2 = st.columns(2)
            b = c1.selectbox("Bölüm *", BOLUMLER)
            stt = c2.selectbox("Başlangıç Durumu", ["Açık", "Devam Ediyor"])

            c3, c4 = st.columns(2)
            lok_free = c3.text_input("Lokasyon (serbest metin)")
            lok_secim = c4.selectbox("Kayıtlı Lokasyon", lok_opts)

            s = st.selectbox("Sorumlu *", pl)
            d = st.text_area("Arıza Tanımı *")

            c5, c6, c7 = st.columns(3)
            sure = c5.number_input("Tahmini Süre (saat)", min_value=0.0, step=0.5)
            mal_m = c6.number_input("Malzeme Maliyeti (₺)", min_value=0.0, step=10.0)
            isc_m = c7.number_input("İşçilik Maliyeti (₺)", min_value=0.0, step=10.0)

            if st.form_submit_button("💾 Kaydet", type="primary"):
                if d.strip() and s != "-":
                    ariza_id = yeni_id("ARZ")
                    lok_final = lok_free or (lok_secim if lok_secim != "—" else "")
                    row_new = {
                        "ID": ariza_id, "Tarih": str(secilen_tarih),
                        "Saat": datetime.now().strftime("%H:%M"),
                        "Bolum": b, "Lokasyon": lok_final, "Lokasyon_ID": "",
                        "Ariza_Tanimi": d.strip(), "Sorumlu": s, "Durum": stt,
                        "Kapanis_Tarihi": str(secilen_tarih) if stt == "Tamamlandı" else "",
                        "Sure_Saat": sure, "Malzeme_Maliyet": mal_m,
                        "Iscilik_Maliyet": isc_m,
                    }
                    df_a = pd.concat([df_a, pd.DataFrame([row_new])], ignore_index=True)
                    save_data(df_a, "ariza")
                    log_ekle("ariza", ariza_id, kullanici, "Oluşturuldu",
                             f"Bölüm: {b}, Lokasyon: {lok_final}")
                    # ── Bildirim gönder ──
                    try:
                        tetikler = st.session_state.get("bildirim_tetikler", {})
                        if tetikler.get("ariza_yeni", True):
                            from bildirim_helper import bildirim_gonder, personel_iletisim
                            email_s, tel_s = personel_iletisim(s)
                            bildirim_gonder(
                                baslik=f"🛠️ Yeni Arıza: {ariza_id}",
                                icerik=f"Tanım: {d.strip()}\nBölüm: {b}\nLokasyon: {lok_final}\nSorumlu: {s}",
                                email_list=[email_s] if email_s else [],
                                telefon_list=[tel_s] if tel_s else [],
                            )
                    except Exception:
                        pass
                    st.success(f"Arıza kaydedildi: {ariza_id}")
                    st.rerun()
                else:
                    st.error("Arıza tanımı ve sorumlu zorunlu.")

    # ── TAB 2: İstatistikler ──────────────────────────────────────────────────
    with tabs[2]:
        _istatistikler(df_a)


def _ariza_detay(row: pd.Series, df_a: pd.DataFrame, pl: list, kullanici: str):
    ariza_id = row["ID"]

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown(f"**Tanım:** {row.get('Ariza_Tanimi', '')}")
        st.markdown(f"**Bölüm:** {row.get('Bolum', '')} | **Lokasyon:** {row.get('Lokasyon', '')}")
        st.markdown(f"**Sorumlu:** {row.get('Sorumlu', '')} | **Açılış:** {row.get('Tarih', '')} {row.get('Saat', '')}")

        sure = pd.to_numeric(row.get("Sure_Saat", 0), errors="coerce") or 0
        mal = pd.to_numeric(row.get("Malzeme_Maliyet", 0), errors="coerce") or 0
        isc = pd.to_numeric(row.get("Iscilik_Maliyet", 0), errors="coerce") or 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Süre (saat)", f"{sure:.1f}")
        c2.metric("Malzeme ₺", f"{mal:,.0f}")
        c3.metric("İşçilik ₺", f"{isc:,.0f}")

    with col_r:
        st.markdown("**✏️ Güncelle**")
        yd = st.selectbox("Yeni Durum", DURUMLAR,
                          index=DURUMLAR.index(row.get("Durum", "Açık"))
                          if row.get("Durum") in DURUMLAR else 0,
                          key=f"yd_{ariza_id}")
        ya = st.selectbox("Sorumlu", pl,
                          index=pl.index(row.get("Sorumlu")) if row.get("Sorumlu") in pl else 0,
                          key=f"ya_{ariza_id}")
        c_s, c_m, c_i = st.columns(3)
        new_sure = c_s.number_input("Süre (s)", value=float(sure), min_value=0.0, step=0.5,
                                     key=f"sure_{ariza_id}")
        new_mal = c_m.number_input("Malzeme ₺", value=float(mal), min_value=0.0,
                                    key=f"mal_{ariza_id}")
        new_isc = c_i.number_input("İşçilik ₺", value=float(isc), min_value=0.0,
                                    key=f"isc_{ariza_id}")

        if st.button("💾 Kaydet", key=f"upd_{ariza_id}", type="primary"):
            old_durum = row.get("Durum", "")
            df_a.loc[df_a["ID"] == ariza_id, "Durum"] = yd
            df_a.loc[df_a["ID"] == ariza_id, "Sorumlu"] = ya
            df_a.loc[df_a["ID"] == ariza_id, "Sure_Saat"] = new_sure
            df_a.loc[df_a["ID"] == ariza_id, "Malzeme_Maliyet"] = new_mal
            df_a.loc[df_a["ID"] == ariza_id, "Iscilik_Maliyet"] = new_isc
            if yd == "Tamamlandı":
                df_a.loc[df_a["ID"] == ariza_id, "Kapanis_Tarihi"] = str(date.today())
            save_data(df_a, "ariza")
            if old_durum != yd:
                log_ekle("ariza", ariza_id, kullanici, "Durum Değişti", f"{old_durum} → {yd}")
            st.success("Güncellendi.")
            st.rerun()

    st.divider()

    # ── Stok Malzeme Kullanımı ────────────────────────────────────────────────
    with st.expander("📦 Stoktan Malzeme Kullan"):
        df_stok = load_data("stok")
        if df_stok.empty:
            st.caption("Stok kaydı yok.")
        else:
            df_stok["_m"] = pd.to_numeric(df_stok["Mevcut"], errors="coerce").fillna(0)
            df_stok_aktif = df_stok[df_stok["_m"] > 0]
            if df_stok_aktif.empty:
                st.caption("Stokta ürün yok.")
            else:
                stok_opts = [
                    f"{r['Stok_ID']} — {r['Urun_Adi']} ({r['_m']:.1f} {r['Birim']})"
                    for _, r in df_stok_aktif.iterrows()
                ]
                col_ss1, col_ss2, col_ss3 = st.columns(3)
                sec_stok = col_ss1.selectbox("Malzeme", stok_opts, key=f"stok_sec_{ariza_id}")
                stok_id = sec_stok.split(" — ")[0]
                stok_row = df_stok[df_stok["Stok_ID"] == stok_id].iloc[0]
                max_mik = float(stok_row["_m"])
                kullan_mik = col_ss2.number_input("Miktar", min_value=0.1, max_value=max_mik,
                                                   value=1.0, step=1.0, key=f"stok_mik_{ariza_id}")
                if col_ss3.button("📤 Düş", key=f"stok_btn_{ariza_id}", type="primary"):
                    from modules.stok import stok_malzeme_kullan
                    ok = stok_malzeme_kullan(
                        stok_id, kullan_mik,
                        f"Arıza: {ariza_id} — {row.get('Ariza_Tanimi','')[:50]}",
                        kullanici,
                    )
                    if ok:
                        # Malzeme maliyetini otomatik güncelle
                        bf = float(pd.to_numeric(stok_row.get("Birim_Fiyat", 0), errors="coerce") or 0)
                        ek_maliyet = bf * kullan_mik
                        mevcut_mal = float(pd.to_numeric(
                            df_a.loc[df_a["ID"] == ariza_id, "Malzeme_Maliyet"].values[0],
                            errors="coerce") or 0)
                        df_a.loc[df_a["ID"] == ariza_id, "Malzeme_Maliyet"] = mevcut_mal + ek_maliyet
                        save_data(df_a, "ariza")
                        log_ekle("ariza", ariza_id, kullanici, "Malzeme Kullanıldı",
                                 f"{stok_row['Urun_Adi']} x{kullan_mik} = {ek_maliyet:.0f}₺")
                        st.success(f"Düşüldü: {kullan_mik} {stok_row['Birim']} {stok_row['Urun_Adi']}")
                        st.rerun()
                    else:
                        st.error("Yeterli stok yok veya hata oluştu.")

    # ── Bakım Planı Dönüştür ─────────────────────────────────────────────────
    with st.expander("📅 Periyodik Bakım Planı Oluştur"):
        st.caption("Bu arızayı tekrarlamaması için bakım planına ekleyin.")
        df_p_pers = load_data("personel")
        pers2 = df_p_pers["Isim"].tolist() if not df_p_pers.empty else ["-"]
        from constants import BAKIM_PERIYOT
        with st.form(f"bakima_donustur_{ariza_id}"):
            plan_baslik = st.text_input("Plan Başlığı",
                                         value=f"Periyodik: {row.get('Ariza_Tanimi','')[:60]}")
            c_pp1, c_pp2 = st.columns(2)
            per_sec = c_pp1.selectbox("Periyot", list(BAKIM_PERIYOT.keys()))
            plan_sor = c_pp2.selectbox("Sorumlu", pers2,
                                        index=pers2.index(row.get("Sorumlu")) if row.get("Sorumlu") in pers2 else 0)
            yasal = st.selectbox("Yasal Zorunlu", ["Hayır", "Evet"])
            if st.form_submit_button("📅 Bakım Planı Oluştur", type="primary"):
                from datetime import timedelta
                periyot = BAKIM_PERIYOT[per_sec]
                df_bp = load_data("bakim_plan")
                bp_row = {
                    "Plan_ID": yeni_id("PLN"),
                    "Baslik": plan_baslik.strip(),
                    "Ekipman": row.get("Bolum", ""),
                    "Lokasyon": row.get("Lokasyon", ""),
                    "Periyot_Gun": periyot,
                    "Sorumlu": plan_sor,
                    "Yasal_Zorunlu": yasal,
                    "Son_Yapilma": "",
                    "Sonraki_Tarih": str(date.today() + timedelta(days=periyot)),
                    "Durum": "Aktif",
                    "Notlar": f"Kaynak: Arıza {ariza_id}",
                }
                df_bp = pd.concat([df_bp, pd.DataFrame([bp_row])], ignore_index=True)
                save_data(df_bp, "bakim_plan")
                log_ekle("ariza", ariza_id, kullanici, "Bakım Planı Oluşturuldu",
                         f"Plan: {bp_row['Plan_ID']}")
                st.success(f"Bakım planı oluşturuldu: {bp_row['Plan_ID']}")
                st.rerun()

    st.divider()
    col_y, col_m = st.columns(2)
    with col_y:
        render_yorumlar("ariza", ariza_id, kullanici)
    with col_m:
        upload_widget("ariza", ariza_id, kullanici)
        render_photo_grid("ariza", ariza_id, cols_per_row=2)


def _istatistikler(df: pd.DataFrame):
    if df.empty:
        st.info("İstatistik için veri yok.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Arıza", len(df))
    acik = len(df[df["Durum"].isin(["Açık", "Devam Ediyor"])])
    c2.metric("Açık / Devam", acik)
    tam = len(df[df["Durum"] == "Tamamlandı"])
    c3.metric("Tamamlandı", tam)
    toplam_mal = pd.to_numeric(df.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum()
    toplam_isc = pd.to_numeric(df.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum()
    c4.metric("Toplam Maliyet", f"{toplam_mal + toplam_isc:,.0f} ₺")

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Bölüme Göre Dağılım**")
        if "Bolum" in df.columns:
            st.bar_chart(df["Bolum"].value_counts())
    with col_r:
        st.markdown("**Duruma Göre Dağılım**")
        if "Durum" in df.columns:
            st.bar_chart(df["Durum"].value_counts())

    st.markdown("**Sorumluya Göre Açık Arızalar**")
    acik_df = df[df["Durum"].isin(["Açık", "Devam Ediyor"])]
    if not acik_df.empty and "Sorumlu" in acik_df.columns:
        st.bar_chart(acik_df["Sorumlu"].value_counts())
