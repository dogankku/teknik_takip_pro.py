"""Checklist şablon yönetimi."""
import json
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from style import section_header, data_table
from auth import current_user
from barkod import yeni_id


SABLON_KATEGORI = ["Elektrik", "Mekanik", "Yangın", "Asansör", "HVAC",
                    "Jeneratör", "Hidrofor", "Genel", "Diğer"]


def render(secilen_tarih: date):
    section_header("Checklist Şablonları", "Yeniden kullanılabilir kontrol listesi şablonları", pill="OPERASYON")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    df = load_data("sablon")

    tabs = st.tabs(["📋 Şablonlar", "➕ Yeni Şablon"])

    with tabs[0]:
        if df.empty:
            st.info("Henüz şablon oluşturulmamış.")
        else:
            # Kategori filtresi
            kat_list = df["Kategori"].dropna().unique().tolist() if "Kategori" in df.columns else []
            sec_kat = st.selectbox("Kategori", ["Tümü"] + sorted(kat_list))
            g = df if sec_kat == "Tümü" else df[df["Kategori"] == sec_kat]

            data_table(
                g,
                [("Sablon_ID", "ID"), ("Ad", "Şablon Adı"), ("Kategori", "Kategori"),
                 ("Aciklama", "Açıklama"), ("Olusturan", "Oluşturan"), ("Tarih", "Tarih")],
                id_cols=["Sablon_ID"], max_text=60,
            )

            st.divider()
            st.subheader("🔍 Şablon Detayı")
            sec_id = st.selectbox("Şablon seç", df["Sablon_ID"].tolist())
            row = df[df["Sablon_ID"] == sec_id].iloc[0]

            st.markdown(f"**{row.get('Ad','')}** — {row.get('Aciklama','')}")
            st.markdown(f"Kategori: `{row.get('Kategori','')}` | Puanlama: `{'Aktif' if row.get('Puanlama_Aktif') else 'Pasif'}`")

            sorular_raw = row.get("Sorular_JSON", "[]")
            try:
                sorular = json.loads(str(sorular_raw)) if sorular_raw else []
            except Exception:
                sorular = []

            if sorular:
                st.markdown(f"**Sorular ({len(sorular)})**")
                for i, s in enumerate(sorular, 1):
                    st.markdown(f"{i}. {s}")
            else:
                st.caption("Soru eklenmemiş.")

            with st.expander("✏️ Düzenle"):
                _sablon_duzenle(row, df, sec_id)

    with tabs[1]:
        _yeni_sablon_form(kullanici, df)


def _yeni_sablon_form(kullanici: str, df: pd.DataFrame):
    st.markdown("#### Yeni Şablon Oluştur")
    c1, c2 = st.columns(2)
    ad = c1.text_input("Şablon Adı *")
    kat = c2.selectbox("Kategori", SABLON_KATEGORI)
    ack = st.text_area("Açıklama")
    puan = st.checkbox("Puanlama Aktif (Tamam=1, Sorunlu=0)", value=False)

    st.markdown("**Sorular** _(her satıra bir soru)_")
    soru_metin = st.text_area("Sorular", height=200,
                               placeholder="1. Pano kontrol edildi mi?\n2. Sigorta atığı var mı?\n3. ...")

    if st.button("💾 Şablonu Kaydet", type="primary"):
        if ad.strip():
            sorular = [s.strip() for s in soru_metin.strip().splitlines() if s.strip()]
            row_new = {
                "Sablon_ID": yeni_id("SBL"),
                "Ad": ad.strip(),
                "Kategori": kat,
                "Aciklama": ack.strip(),
                "Sorular_JSON": json.dumps(sorular, ensure_ascii=False),
                "Olusturan": kullanici,
                "Tarih": str(date.today()),
                "Puanlama_Aktif": puan,
            }
            df = pd.concat([df, pd.DataFrame([row_new])], ignore_index=True)
            save_data(df, "sablon")
            st.success(f"Şablon kaydedildi: {ad} ({len(sorular)} soru)")
            st.rerun()
        else:
            st.error("Şablon adı zorunlu.")


def _sablon_duzenle(row: pd.Series, df: pd.DataFrame, sec_id: str):
    sorular_raw = row.get("Sorular_JSON", "[]")
    try:
        sorular = json.loads(str(sorular_raw)) if sorular_raw else []
    except Exception:
        sorular = []

    with st.form(f"sablon_edit_{sec_id}"):
        c1, c2 = st.columns(2)
        new_ad = c1.text_input("Ad", value=str(row.get("Ad", "")))
        new_kat = c2.selectbox("Kategori", SABLON_KATEGORI,
                                index=SABLON_KATEGORI.index(row.get("Kategori"))
                                if row.get("Kategori") in SABLON_KATEGORI else 0)
        new_ack = st.text_area("Açıklama", value=str(row.get("Aciklama", "")))
        new_puan = st.checkbox("Puanlama Aktif", value=bool(row.get("Puanlama_Aktif", False)))
        new_sorular = st.text_area("Sorular", height=150,
                                    value="\n".join(sorular))
        col_s, col_d = st.columns(2)
        if col_s.form_submit_button("💾 Kaydet", type="primary"):
            yeni_sorular = [s.strip() for s in new_sorular.splitlines() if s.strip()]
            df.loc[df["Sablon_ID"] == sec_id, "Ad"] = new_ad
            df.loc[df["Sablon_ID"] == sec_id, "Kategori"] = new_kat
            df.loc[df["Sablon_ID"] == sec_id, "Aciklama"] = new_ack
            df.loc[df["Sablon_ID"] == sec_id, "Puanlama_Aktif"] = new_puan
            df.loc[df["Sablon_ID"] == sec_id, "Sorular_JSON"] = json.dumps(yeni_sorular, ensure_ascii=False)
            save_data(df, "sablon")
            st.success("Şablon güncellendi.")
            st.rerun()
        if col_d.form_submit_button("🗑️ Sil"):
            df = df[df["Sablon_ID"] != sec_id]
            save_data(df, "sablon")
            st.warning("Şablon silindi.")
            st.rerun()


def get_sablon_sorular(sablon_id: str) -> list[str]:
    """Verilen sablon ID'sine ait soru listesini döndürür."""
    df = load_data("sablon")
    if df.empty:
        return []
    m = df[df["Sablon_ID"] == sablon_id]
    if m.empty:
        return []
    raw = m.iloc[0].get("Sorular_JSON", "[]")
    try:
        return json.loads(str(raw)) if raw else []
    except Exception:
        return []
