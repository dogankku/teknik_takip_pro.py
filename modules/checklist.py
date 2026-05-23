import json
import streamlit as st
import pandas as pd
from datetime import date, datetime
from db import load_data, save_data
from constants import SORU_GRUPLARI
from style import section_header
from auth import current_user
from barkod import yeni_id


def render(secilen_tarih: date):
    section_header(
        "Günlük Kontroller",
        f"{secilen_tarih.strftime('%d.%m.%Y')} — Kontrol formları",
        pill="OPERASYON",
    )

    # Tabs yerine radio — her zaman çalışır, click sorunu yok
    sayfa = st.radio(
        "Görünüm",
        ["📋 Standart Kontroller", "📝 Şablon ile Doldur", "📊 Özet & Arıza"],
        horizontal=True,
        label_visibility="collapsed",
        key="ck_sayfa",
    )
    st.markdown("---")

    if sayfa.startswith("📋"):
        _standart_kontroller(secilen_tarih)
    elif sayfa.startswith("📝"):
        _sablon_kontrol(secilen_tarih)
    else:
        _ozet(secilen_tarih)


# ── 1) Standart Kontroller ────────────────────────────────────────────────────
def _standart_kontroller(secilen_tarih: date):
    df_check = load_data("checklist")
    df_pers  = load_data("personel")
    pers_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    col1, col2, col3 = st.columns([2, 3, 2])
    bolum     = col1.selectbox("📂 Bölüm", list(SORU_GRUPLARI.keys()), key="ck_bolum")
    alt_gruplar = list(SORU_GRUPLARI[bolum].keys())
    alt_grup  = col2.selectbox("📍 Alt Grup", alt_gruplar, key="ck_alt_grup")
    kontrolcu = col3.selectbox("👤 Kontrol Eden", pers_listesi, key="ck_user")

    sorular   = SORU_GRUPLARI[bolum][alt_grup]
    tarih_str = str(secilen_tarih)

    st.markdown(
        f"**{bolum} — {alt_grup}** &nbsp; `{len(sorular)} soru`",
        unsafe_allow_html=True,
    )

    try:
        kayitli = df_check[
            (df_check["Tarih"].astype(str) == tarih_str) &
            (df_check["Bolum"].astype(str) == bolum) &
            (df_check["Alt_Grup"].astype(str) == alt_grup)
        ] if not df_check.empty else pd.DataFrame()
    except Exception:
        kayitli = pd.DataFrame()

    if not kayitli.empty:
        puan  = pd.to_numeric(kayitli.get("Puan", pd.Series()), errors="coerce").fillna(0).sum()
        yuzde = int(puan / len(kayitli) * 100) if len(kayitli) else 0
        st.success(f"✅ Bu grup bugün tamamlandı — Puan: **%{yuzde}** ({int(puan)}/{len(kayitli)})")
        st.dataframe(
            kayitli[["Soru", "Durum", "Aciklama"]],
            use_container_width=True, hide_index=True,
        )
        if st.button("🔄 Yeniden Doldur", key="ck_yeniden"):
            idx_sil = df_check[
                (df_check["Tarih"].astype(str) == tarih_str) &
                (df_check["Bolum"].astype(str) == bolum) &
                (df_check["Alt_Grup"].astype(str) == alt_grup)
            ].index
            df_check = df_check.drop(idx_sil)
            save_data(df_check, "checklist")
            st.rerun()
        return

    st.caption("💡 Sorun yoksa açıklama yazmadan geçebilirsiniz.")
    safe_key = f"ck_{bolum[:4]}_{alt_grup[:8]}_{tarih_str}".replace(" ", "_")

    with st.form(key=safe_key):
        cevaplar = []
        for idx, soru in enumerate(sorular):
            c1, c2, c3 = st.columns([6, 2, 3])
            c1.markdown(f"**{idx+1}.** {soru}")
            durum = c2.radio(
                "Durum", ["✅ Tamam", "⚠️ Sorunlu"],
                key=f"rd_{safe_key}_{idx}",
                horizontal=True, label_visibility="collapsed",
            )
            not_txt = c3.text_input(
                "Not", key=f"nt_{safe_key}_{idx}",
                label_visibility="collapsed", placeholder="açıklama...",
            )
            durum_temiz = "Tamam" if "Tamam" in durum else "Sorunlu"
            cevaplar.append({
                "Tarih": tarih_str, "Bolum": bolum, "Alt_Grup": alt_grup,
                "Soru": soru, "Durum": durum_temiz, "Aciklama": not_txt,
                "Kontrol_Eden": kontrolcu,
                "Puan": 1 if durum_temiz == "Tamam" else 0,
                "Sablon_ID": "", "Lokasyon_ID": "",
            })
            if idx < len(sorular) - 1:
                st.divider()

        submitted = st.form_submit_button(
            f"💾 {alt_grup[:30]} — Kaydet ({len(sorular)} soru)",
            type="primary", use_container_width=True,
        )

    if submitted:
        df_check = pd.concat([df_check, pd.DataFrame(cevaplar)], ignore_index=True)
        save_data(df_check, "checklist")
        puan = sum(1 for c in cevaplar if c["Durum"] == "Tamam")
        st.success(
            f"✅ Kaydedildi! Puan: {puan}/{len(cevaplar)} "
            f"(%{int(puan/len(cevaplar)*100) if cevaplar else 0})"
        )
        st.rerun()


# ── 2) Şablon ile Doldur ──────────────────────────────────────────────────────
def _sablon_kontrol(secilen_tarih: date):
    df_sbl   = load_data("sablon")
    df_check = load_data("checklist")
    df_pers  = load_data("personel")
    df_lok   = load_data("lokasyon")

    if df_sbl.empty:
        st.info("ℹ️ Henüz şablon oluşturulmamış. Önce **Şablonlar** modülünden şablon ekleyin.")
        return

    pers = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    lok_opts   = ["—"]
    lok_id_map = {}
    if not df_lok.empty:
        for _, r in df_lok.iterrows():
            lbl = f"{r.get('Ana_Lokasyon','')} → {r.get('Ad','')}"
            lok_opts.append(lbl)
            lok_id_map[lbl] = r.get("Lokasyon_ID", "")

    col1, col2, col3 = st.columns(3)
    sec_sbl   = col1.selectbox(
        "📋 Şablon",
        df_sbl["Sablon_ID"].tolist(),
        format_func=lambda x: (
            df_sbl[df_sbl["Sablon_ID"] == x]["Ad"].values[0]
            if x in df_sbl["Sablon_ID"].values else x
        ),
        key="sbl_sec",
    )
    kontrolcu = col2.selectbox("👤 Kontrol Eden", pers, key="sbl_pers")
    lok_sec   = col3.selectbox("📍 Lokasyon", lok_opts, key="sbl_lok")

    row_sbl     = df_sbl[df_sbl["Sablon_ID"] == sec_sbl].iloc[0]
    sorular_raw = row_sbl.get("Sorular_JSON", "[]")
    try:
        sorular = json.loads(str(sorular_raw)) if sorular_raw else []
    except Exception:
        sorular = []

    if not sorular:
        st.warning("⚠️ Bu şablonda soru yok.")
        return

    puanlama  = bool(row_sbl.get("Puanlama_Aktif", False))
    tarih_str = str(secilen_tarih)

    st.info(
        f"📋 **{row_sbl.get('Ad','')}** — {len(sorular)} soru | "
        f"Puanlama: {'✅' if puanlama else '❌'}"
    )

    try:
        zaten_var = df_check[
            (df_check["Tarih"].astype(str) == tarih_str) &
            (df_check["Sablon_ID"].astype(str) == str(sec_sbl)) &
            (df_check["Kontrol_Eden"].astype(str) == kontrolcu)
        ] if not df_check.empty else pd.DataFrame()
    except Exception:
        zaten_var = pd.DataFrame()

    if not zaten_var.empty:
        puan  = pd.to_numeric(zaten_var.get("Puan", pd.Series()), errors="coerce").fillna(0).sum()
        yuzde = int(puan / len(zaten_var) * 100) if len(zaten_var) else 0
        st.success(
            f"✅ Bu şablon bugün **{kontrolcu}** tarafından doldurulmuş — "
            f"Puan: **%{yuzde}** ({int(puan)}/{len(zaten_var)})"
        )
        st.dataframe(
            zaten_var[["Soru", "Durum", "Aciklama"]],
            use_container_width=True, hide_index=True,
        )
        return

    safe_sbl = str(sec_sbl).replace(" ", "_")[:12]
    with st.form(key=f"sbl_{safe_sbl}_{tarih_str}"):
        cevaplar = []
        for idx, soru in enumerate(sorular):
            c1, c2, c3 = st.columns([6, 2, 3])
            c1.markdown(f"**{idx+1}.** {soru}")
            durum = c2.radio(
                "Durum", ["✅ Tamam", "⚠️ Sorunlu"],
                key=f"srd_{safe_sbl}_{idx}",
                horizontal=True, label_visibility="collapsed",
            )
            not_txt = c3.text_input(
                "Not", key=f"snt_{safe_sbl}_{idx}",
                label_visibility="collapsed", placeholder="açıklama...",
            )
            lok_id      = lok_id_map.get(lok_sec, "") if lok_sec != "—" else ""
            durum_temiz = "Tamam" if "Tamam" in durum else "Sorunlu"
            cevaplar.append({
                "Tarih": tarih_str,
                "Bolum": row_sbl.get("Kategori", ""),
                "Alt_Grup": row_sbl.get("Ad", ""),
                "Soru": soru, "Durum": durum_temiz, "Aciklama": not_txt,
                "Kontrol_Eden": kontrolcu,
                "Puan": 1 if durum_temiz == "Tamam" else 0,
                "Sablon_ID": sec_sbl, "Lokasyon_ID": lok_id,
            })
            if idx < len(sorular) - 1:
                st.divider()

        submitted = st.form_submit_button(
            "💾 Kontrol Listesini Kaydet",
            type="primary", use_container_width=True,
        )

    if submitted:
        df_check = pd.concat([df_check, pd.DataFrame(cevaplar)], ignore_index=True)
        save_data(df_check, "checklist")
        puan = sum(1 for c in cevaplar if c["Durum"] == "Tamam")
        st.success(
            f"✅ Kaydedildi! Puan: {puan}/{len(cevaplar)} "
            f"(%{int(puan/len(cevaplar)*100) if cevaplar else 0})"
        )
        st.rerun()


# ── 3) Özet & Arıza ──────────────────────────────────────────────────────────
def _ozet(secilen_tarih: date):
    df   = load_data("checklist")
    u    = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")
    df_p = load_data("personel")
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    tarih_str = str(secilen_tarih)

    if df.empty:
        st.info("ℹ️ Henüz kontrol kaydı yok.")
        return

    bugun = df[df["Tarih"].astype(str) == tarih_str]

    if bugun.empty:
        st.info(f"📅 {secilen_tarih.strftime('%d.%m.%Y')} için kayıt bulunamadı.")
        return

    tamam   = len(bugun[bugun["Durum"] == "Tamam"])
    sorunlu = len(bugun[bugun["Durum"] == "Sorunlu"])
    yuzde   = int(tamam / len(bugun) * 100) if len(bugun) else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Soru", len(bugun))
    col2.metric("✅ Tamam", tamam)
    col3.metric("⚠️ Sorunlu", sorunlu)
    col4.metric("Puan", f"%{yuzde}")

    if "Bolum" in bugun.columns:
        st.markdown("---")
        st.markdown("**Bölüme Göre Özet**")
        ozet = bugun.groupby("Bolum")["Durum"].value_counts().unstack(fill_value=0)
        st.dataframe(ozet, use_container_width=True)

    if sorunlu > 0:
        st.markdown("---")
        st.subheader("⚠️ Sorunlu Maddeler → Arıza Kaydı Oluştur")
        sorunlu_df = bugun[bugun["Durum"] == "Sorunlu"].reset_index(drop=True)

        for i, row in sorunlu_df.iterrows():
            c_txt, c_btn = st.columns([5, 1])
            c_txt.markdown(
                f'<div style="background:#FEF2F2;border-left:3px solid #EF4444;'
                f'padding:8px 12px;border-radius:6px;margin-bottom:6px">'
                f'<b>{row.get("Bolum","")}</b> / {row.get("Alt_Grup","")}<br>'
                f'{row.get("Soru","")}'
                f'{(" — " + str(row["Aciklama"])) if row.get("Aciklama") else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )
            created_key = f"ariza_done_{tarih_str}_{i}"
            if st.session_state.get(created_key):
                c_btn.success("✅ Oluşturuldu")
            elif c_btn.button("🛠️ Arıza\nOluştur", key=f"ab_{tarih_str}_{i}"):
                _checklist_to_ariza(row, kullanici, pers)
                st.session_state[created_key] = True
                st.rerun()


def _checklist_to_ariza(row: pd.Series, kullanici: str, pers: list):
    from aktivite_helper import log_ekle
    df_a     = load_data("ariza")
    ariza_id = yeni_id("ARZ")
    tanim    = (
        f"[Checklist] {row.get('Bolum','')} / {row.get('Alt_Grup','')} "
        f"— {row.get('Soru','')}"
    )
    if row.get("Aciklama"):
        tanim += f" | Not: {row['Aciklama']}"
    sorumlu = row.get("Kontrol_Eden", pers[0] if pers else "")
    if sorumlu not in pers and pers:
        sorumlu = pers[0]

    new_row = {
        "ID": ariza_id,
        "Tarih": str(date.today()),
        "Saat": datetime.now().strftime("%H:%M"),
        "Bolum": row.get("Bolum", "Genel"),
        "Lokasyon": row.get("Alt_Grup", ""),
        "Lokasyon_ID": row.get("Lokasyon_ID", ""),
        "Ariza_Tanimi": tanim,
        "Sorumlu": sorumlu,
        "Durum": "Açık",
        "Kapanis_Tarihi": "",
        "Sure_Saat": 0, "Malzeme_Maliyet": 0, "Iscilik_Maliyet": 0,
    }
    df_a = pd.concat([df_a, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df_a, "ariza")
    log_ekle("ariza", ariza_id, kullanici, "Oluşturuldu",
             f"Checklist'ten: {row.get('Soru','')[:60]}")
