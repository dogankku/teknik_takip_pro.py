import json
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from constants import SORU_GRUPLARI
from style import section_header
from auth import current_user


def render(secilen_tarih: date):
    section_header("Günlük Kontroller",
                   f"{secilen_tarih.strftime('%d.%m.%Y')} - Kontrol formları",
                   pill="OPERASYON")

    tabs = st.tabs(["📋 Standart Kontroller", "📝 Şablon ile Doldur", "📊 Özet"])

    with tabs[0]:
        _standart_kontroller(secilen_tarih)

    with tabs[1]:
        _sablon_kontrol(secilen_tarih)

    with tabs[2]:
        _ozet(secilen_tarih)


def _standart_kontroller(secilen_tarih: date):
    df_check = load_data("checklist")
    df_pers = load_data("personel")
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    bolum_tabs = st.tabs(list(SORU_GRUPLARI.keys()))

    for i, bolum in enumerate(SORU_GRUPLARI.keys()):
        with bolum_tabs[i]:
            st.subheader(f"📋 {bolum} Kontrol Formu")
            cp, _ = st.columns([1, 3])
            kontrolcu = cp.selectbox("Kontrol Eden", personel_listesi, key=f"user_{bolum}")

            for alt_grup, sorular in SORU_GRUPLARI[bolum].items():
                with st.expander(f"📍 {alt_grup} ({len(sorular)} soru)", expanded=False):
                    tarih_str = str(secilen_tarih)
                    try:
                        kayitli = df_check[
                            (df_check["Tarih"] == tarih_str)
                            & (df_check["Bolum"] == bolum)
                            & (df_check["Alt_Grup"] == alt_grup)
                        ]
                    except KeyError:
                        kayitli = pd.DataFrame()

                    if not kayitli.empty:
                        puan_col = kayitli.get("Puan", pd.Series())
                        toplam_puan = pd.to_numeric(puan_col, errors="coerce").fillna(0).sum()
                        max_puan = len(kayitli)
                        yuzde = int(toplam_puan / max_puan * 100) if max_puan else 0
                        st.success(f"✅ Bu grup tamamlandı — Puan: {yuzde}%")
                        st.dataframe(kayitli[["Soru", "Durum", "Aciklama"]],
                                     use_container_width=True, hide_index=True)
                    else:
                        with st.form(f"form_{bolum}_{alt_grup}"):
                            st.caption("💡 Sorun yoksa açıklama yazmadan geçebilirsiniz.")
                            cevaplar = []
                            for idx, soru in enumerate(sorular):
                                c1, c2, c3 = st.columns([6, 2, 3])
                                c1.write(soru)
                                durum = c2.radio(
                                    "D", ["Tamam", "Sorunlu"],
                                    key=f"rd_{bolum}_{alt_grup}_{idx}",
                                    horizontal=True, label_visibility="collapsed",
                                )
                                not_txt = c3.text_input(
                                    "Not", key=f"nt_{bolum}_{alt_grup}_{idx}",
                                    label_visibility="collapsed",
                                )
                                cevaplar.append({
                                    "Tarih": tarih_str, "Bolum": bolum, "Alt_Grup": alt_grup,
                                    "Soru": soru, "Durum": durum, "Aciklama": not_txt,
                                    "Kontrol_Eden": kontrolcu,
                                    "Puan": 1 if durum == "Tamam" else 0,
                                    "Sablon_ID": "", "Lokasyon_ID": "",
                                })
                                st.divider()

                            if st.form_submit_button(f"💾 {alt_grup} Kaydet", type="primary"):
                                df_check = pd.concat([df_check, pd.DataFrame(cevaplar)],
                                                     ignore_index=True)
                                save_data(df_check, "checklist")
                                st.success("Kaydedildi!")
                                st.rerun()


def _sablon_kontrol(secilen_tarih: date):
    df_sbl = load_data("sablon")
    df_check = load_data("checklist")
    df_pers = load_data("personel")
    df_lok = load_data("lokasyon")

    if df_sbl.empty:
        st.info("Henüz şablon oluşturulmamış. 'Şablon Yönetimi' menüsünden ekleyebilirsiniz.")
        return

    pers = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    lok_opts = ["—"]
    lok_id_map = {}
    if not df_lok.empty:
        for _, r in df_lok.iterrows():
            label = f"{r.get('Ana_Lokasyon','')} → {r.get('Ad','')}"
            lok_opts.append(label)
            lok_id_map[label] = r.get("Lokasyon_ID", "")

    c1, c2, c3 = st.columns(3)
    sec_sbl = c1.selectbox("Şablon seç", df_sbl["Sablon_ID"].tolist(),
                            format_func=lambda x: df_sbl[df_sbl["Sablon_ID"] == x]["Ad"].values[0]
                            if x in df_sbl["Sablon_ID"].values else x)
    kontrolcu = c2.selectbox("Kontrol Eden", pers, key="sbl_pers")
    lok_sec = c3.selectbox("Lokasyon", lok_opts, key="sbl_lok")

    row_sbl = df_sbl[df_sbl["Sablon_ID"] == sec_sbl].iloc[0]
    sorular_raw = row_sbl.get("Sorular_JSON", "[]")
    try:
        sorular = json.loads(str(sorular_raw)) if sorular_raw else []
    except Exception:
        sorular = []

    if not sorular:
        st.warning("Bu şablonda soru yok.")
        return

    puanlama = bool(row_sbl.get("Puanlama_Aktif", False))
    st.markdown(f"**{row_sbl.get('Ad','')}** — {len(sorular)} soru | Puanlama: {'✅' if puanlama else '❌'}")

    tarih_str = str(secilen_tarih)
    zaten_var = df_check[
        (df_check["Tarih"] == tarih_str) &
        (df_check["Sablon_ID"].astype(str) == str(sec_sbl)) &
        (df_check["Kontrol_Eden"].astype(str) == kontrolcu)
    ] if not df_check.empty else pd.DataFrame()

    if not zaten_var.empty:
        puan_col = zaten_var.get("Puan", pd.Series())
        toplam = pd.to_numeric(puan_col, errors="coerce").fillna(0).sum()
        yuzde = int(toplam / len(zaten_var) * 100) if len(zaten_var) else 0
        st.success(f"✅ Bu şablon bugün zaten doldurulmuş — Puan: **{yuzde}%** ({int(toplam)}/{len(zaten_var)})")
        st.dataframe(zaten_var[["Soru", "Durum", "Aciklama"]], use_container_width=True, hide_index=True)
        return

    with st.form(f"sbl_form_{sec_sbl}"):
        cevaplar = []
        for idx, soru in enumerate(sorular):
            c1, c2, c3 = st.columns([6, 2, 3])
            c1.write(f"{idx+1}. {soru}")
            durum = c2.radio("D", ["Tamam", "Sorunlu"],
                             key=f"srd_{sec_sbl}_{idx}",
                             horizontal=True, label_visibility="collapsed")
            not_txt = c3.text_input("Not", key=f"snt_{sec_sbl}_{idx}",
                                    label_visibility="collapsed")
            lok_id = lok_id_map.get(lok_sec, "") if lok_sec != "—" else ""
            cevaplar.append({
                "Tarih": tarih_str,
                "Bolum": row_sbl.get("Kategori", ""),
                "Alt_Grup": row_sbl.get("Ad", ""),
                "Soru": soru,
                "Durum": durum,
                "Aciklama": not_txt,
                "Kontrol_Eden": kontrolcu,
                "Puan": 1 if durum == "Tamam" else 0,
                "Sablon_ID": sec_sbl,
                "Lokasyon_ID": lok_id,
            })
            st.divider()

        if st.form_submit_button("💾 Kontrol Listesini Kaydet", type="primary"):
            df_check = pd.concat([df_check, pd.DataFrame(cevaplar)], ignore_index=True)
            save_data(df_check, "checklist")
            puan = sum(1 for c in cevaplar if c["Durum"] == "Tamam")
            st.success(f"Kaydedildi! Puan: {puan}/{len(cevaplar)} (%{int(puan/len(cevaplar)*100)})")
            st.rerun()


def _ozet(secilen_tarih: date):
    df = load_data("checklist")
    if df.empty:
        st.info("Henüz kayıt yok.")
        return

    tarih_str = str(secilen_tarih)
    bugun = df[df["Tarih"] == tarih_str]

    c1, c2, c3 = st.columns(3)
    c1.metric("Bugün Toplam Soru", len(bugun))
    tamam = len(bugun[bugun["Durum"] == "Tamam"]) if not bugun.empty else 0
    sorunlu = len(bugun[bugun["Durum"] == "Sorunlu"]) if not bugun.empty else 0
    c2.metric("Tamam", tamam)
    c3.metric("Sorunlu", sorunlu, delta="⚠️" if sorunlu > 0 else None, delta_color="inverse")

    if not bugun.empty and "Bolum" in bugun.columns:
        st.markdown("---")
        st.markdown("**Bölüme Göre Bugünkü Durum**")
        ozet = bugun.groupby("Bolum")["Durum"].value_counts().unstack(fill_value=0)
        st.dataframe(ozet, use_container_width=True)

    if not bugun.empty and sorunlu > 0:
        st.markdown("---")
        st.markdown("**⚠️ Sorunlu Maddeler**")
        sorunlu_df = bugun[bugun["Durum"] == "Sorunlu"][["Bolum", "Alt_Grup", "Soru", "Aciklama", "Kontrol_Eden"]]
        st.dataframe(sorunlu_df, use_container_width=True, hide_index=True)
