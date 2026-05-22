"""Yorum (comment) sistemi — ariza, talep vb. kayıtlara not ekleme."""
from __future__ import annotations
from datetime import datetime
import streamlit as st
import pandas as pd
from db import load_data, save_data
from barkod import yeni_id


def yorum_ekle(parent_tip: str, parent_id: str, kullanici: str, metin: str) -> bool:
    if not metin.strip():
        return False
    df = load_data("yorum")
    row = {
        "Yorum_ID": yeni_id("YRM"),
        "Parent_Tip": parent_tip,
        "Parent_ID": str(parent_id),
        "Kullanici": kullanici,
        "Tarih": datetime.now().strftime("%Y-%m-%d"),
        "Saat": datetime.now().strftime("%H:%M"),
        "Metin": metin.strip(),
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, "yorum")
    return True


def yorumlari_getir(parent_tip: str, parent_id: str) -> list[dict]:
    df = load_data("yorum")
    if df.empty:
        return []
    m = df[(df["Parent_Tip"].astype(str) == parent_tip) &
           (df["Parent_ID"].astype(str) == str(parent_id))]
    return m.sort_values("Tarih").to_dict("records") if not m.empty else []


def render_yorumlar(parent_tip: str, parent_id: str, kullanici: str):
    """Yorumlar bölümünü göster + yeni yorum formu."""
    items = yorumlari_getir(parent_tip, parent_id)
    st.markdown("**💬 Notlar & Yorumlar**")
    if items:
        for y in items:
            st.markdown(
                f'<div style="background:#F8FAFC;border-left:3px solid #3B82F6;'
                f'padding:8px 12px;border-radius:4px;margin-bottom:6px;">'
                f'<span style="font-size:.75rem;color:#64748B;">'
                f'👤 <b>{y.get("Kullanici","")}</b> · {y.get("Tarih","")[:10]} {y.get("Saat","")}</span><br>'
                f'{y.get("Metin","")}'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption("Henüz yorum yok.")

    with st.form(f"yorum_form_{parent_tip}_{parent_id}"):
        metin = st.text_area("Yeni not/yorum ekle", height=80, label_visibility="collapsed",
                              placeholder="Notunuzu yazın…")
        if st.form_submit_button("💬 Ekle"):
            if yorum_ekle(parent_tip, parent_id, kullanici, metin):
                st.success("Eklendi.")
                st.rerun()
            else:
                st.warning("Metin boş olamaz.")
