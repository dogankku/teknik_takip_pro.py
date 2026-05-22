"""Media yönetim sayfası — tüm yüklü fotoğraflar."""
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from style import section_header
from media import media_bytes


def render(secilen_tarih: date):
    section_header("Fotoğraf & Medya", "Tüm yüklü görselleri görüntüle ve yönet", pill="MEDYA")

    df = load_data("media")

    if df.empty:
        st.info("Henüz fotoğraf yüklenmemiş.")
        return

    # ── Filtreler ─────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    tip_opts = ["Tümü"] + sorted(df["Parent_Tip"].dropna().unique().tolist()) if "Parent_Tip" in df.columns else ["Tümü"]
    tip_f = c1.selectbox("Kayıt Tipi", tip_opts)
    yukleyen_opts = ["Tümü"] + sorted(df["Yukleyen"].dropna().unique().tolist()) if "Yukleyen" in df.columns else ["Tümü"]
    yuk_f = c2.selectbox("Yükleyen", yukleyen_opts)
    grid_cols = c3.selectbox("Sütun Sayısı", [2, 3, 4, 5], index=1)

    g = df.copy()
    if tip_f != "Tümü":
        g = g[g["Parent_Tip"] == tip_f]
    if yuk_f != "Tümü":
        g = g[g["Yukleyen"] == yuk_f]

    g = g.sort_values("Yukleme_Tarihi", ascending=False).reset_index(drop=True)

    # ── Özet ──────────────────────────────────────────────────────────────────
    c1m, c2m, c3m, c4m = st.columns(4)
    c1m.metric("Toplam Fotoğraf", len(g))
    toplam_kb = pd.to_numeric(g.get("Boyut", 0), errors="coerce").fillna(0).sum() / 1024
    c2m.metric("Toplam Boyut", f"{toplam_kb:,.0f} KB")
    if "Parent_Tip" in g.columns:
        c3m.metric("Farklı Modül", g["Parent_Tip"].nunique())
    if "Yukleyen" in g.columns:
        c4m.metric("Farklı Kullanıcı", g["Yukleyen"].nunique())

    st.markdown("---")

    # ── Grid görünümü ─────────────────────────────────────────────────────────
    if not g.empty:
        cols = st.columns(grid_cols)
        for i, (_, row) in enumerate(g.iterrows()):
            with cols[i % grid_cols]:
                data = media_bytes(str(row.get("Base64", "")))
                if data:
                    st.image(data, use_container_width=True)
                tip = str(row.get("Parent_Tip", ""))
                pid = str(row.get("Parent_ID", ""))
                ad = str(row.get("Dosya_Adi", ""))
                tar = str(row.get("Yukleme_Tarihi", ""))[:10]
                yuk = str(row.get("Yukleyen", ""))
                boyut_kb = (pd.to_numeric(row.get("Boyut", 0), errors="coerce") or 0) / 1024
                st.caption(f"**{tip}** › {pid}\n{ad}\n📅 {tar} · 👤 {yuk}\n💾 {boyut_kb:.0f} KB")

                mid = str(row.get("Media_ID", ""))
                if mid and st.button("🗑️", key=f"del_med_{mid}", help="Sil"):
                    df_all = load_data("media")
                    df_all = df_all[df_all["Media_ID"] != mid]
                    save_data(df_all, "media")
                    st.rerun()

    st.markdown("---")
    st.markdown("**Ham Tablo**")
    show_cols = [c for c in ["Media_ID", "Parent_Tip", "Parent_ID", "Dosya_Adi",
                              "Boyut", "Yukleme_Tarihi", "Yukleyen"] if c in g.columns]
    st.dataframe(g[show_cols], use_container_width=True, hide_index=True)
