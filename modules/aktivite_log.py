"""Aktivite log görüntüleme — tüm kayıt değişiklikleri."""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import load_data
from style import section_header, data_table


def render(secilen_tarih: date):
    section_header("Aktivite Günlüğü", "Tüm sistem olayları ve değişiklik izleri", pill="DENETİM")

    df = load_data("aktivite")

    if df.empty:
        st.info("Henüz aktivite kaydı yok.")
        return

    # ── Filtreler ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    bas = c1.date_input("Başlangıç", date.today() - timedelta(days=7))
    bit = c2.date_input("Bitiş", date.today())

    tipler = ["Tümü"] + sorted(df["Parent_Tip"].dropna().unique().tolist()) if "Parent_Tip" in df.columns else ["Tümü"]
    tip_f = c3.selectbox("Kayıt Tipi", tipler)

    kullanici_opts = ["Tümü"] + sorted(df["Kullanici"].dropna().unique().tolist()) if "Kullanici" in df.columns else ["Tümü"]
    kul_f = c4.selectbox("Kullanıcı", kullanici_opts)

    # ── Filtrele ──────────────────────────────────────────────────────────────
    g = df.copy()
    try:
        d = pd.to_datetime(g["Tarih"], errors="coerce")
        g = g[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]
    except Exception:
        pass
    if tip_f != "Tümü":
        g = g[g["Parent_Tip"] == tip_f]
    if kul_f != "Tümü":
        g = g[g["Kullanici"] == kul_f]

    g = g.sort_values("Tarih", ascending=False).reset_index(drop=True)

    # ── Özet ──────────────────────────────────────────────────────────────────
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Toplam Olay", len(g))
    if not g.empty and "Kullanici" in g.columns:
        c2m.metric("Aktif Kullanıcı", g["Kullanici"].nunique())
    if not g.empty and "Aksiyon" in g.columns:
        c3m.metric("Farklı Aksiyon", g["Aksiyon"].nunique())

    st.markdown("---")

    # ── Timeline görünümü ─────────────────────────────────────────────────────
    if not g.empty:
        AKSIYON_RENKLER = {
            "Oluşturuldu": "#10B981",
            "Durum Değişti": "#3B82F6",
            "Güncellendi": "#F59E0B",
            "Silindi": "#EF4444",
            "Malzeme Kullanıldı": "#8B5CF6",
            "Bakım Planı Oluşturuldu": "#06B6D4",
        }
        for _, row in g.head(200).iterrows():
            aksiyon = str(row.get("Aksiyon", ""))
            renk = AKSIYON_RENKLER.get(aksiyon, "#64748B")
            tarih = str(row.get("Tarih", ""))
            saat = str(row.get("Saat", ""))
            kullanici = str(row.get("Kullanici", ""))
            tip = str(row.get("Parent_Tip", ""))
            pid = str(row.get("Parent_ID", ""))
            detay = str(row.get("Detay", ""))

            st.markdown(
                f'<div style="display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #F1F5F9;">'
                f'<div style="min-width:120px;font-size:.75rem;color:#94A3B8;">{tarih}<br>{saat}</div>'
                f'<div style="min-width:8px;background:{renk};border-radius:4px;"></div>'
                f'<div style="flex:1;">'
                f'<span style="font-size:.75rem;font-weight:600;color:{renk};background:{renk}18;'
                f'padding:2px 8px;border-radius:9999px;">{aksiyon}</span> '
                f'<span style="font-size:.8rem;color:#475569;">{tip} <b>{pid}</b></span><br>'
                f'<span style="font-size:.8rem;color:#64748B;">👤 {kullanici}'
                f'{(" — " + detay) if detay else ""}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("**Ham Tablo**")
    show_cols = [c for c in ["Tarih", "Saat", "Parent_Tip", "Parent_ID",
                              "Kullanici", "Aksiyon", "Detay"] if c in g.columns]
    col_labels = {
        "Tarih": "Tarih", "Saat": "Saat", "Parent_Tip": "Tip", "Parent_ID": "ID",
        "Kullanici": "Kullanıcı", "Aksiyon": "Aksiyon", "Detay": "Detay",
    }
    data_table(
        g[show_cols],
        [(c, col_labels.get(c, c)) for c in show_cols],
        avatar_cols=["Kullanici"] if "Kullanici" in show_cols else (),
        max_text=60,
    )
