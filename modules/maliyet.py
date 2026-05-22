"""Maliyet & Gider Özet Paneli."""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import load_data
from style import section_header

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=0),
    font=dict(family="Inter, sans-serif", size=12, color="#64748B"),
    height=260,
)


def render(secilen_tarih: date):
    section_header("Maliyet & Gider Paneli",
                   "Arıza, talep, bakım ve işletme giderlerinin birleşik analizi",
                   pill="MALİ")

    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today().replace(day=1))
    bit = c2.date_input("Bitiş", date.today())

    def aralik(df, col="Tarih"):
        if df.empty or col not in df.columns:
            return df
        d = pd.to_datetime(df[col], errors="coerce")
        return df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))].copy()

    df_a = aralik(load_data("ariza"))
    df_t = aralik(load_data("talep"))
    df_b = aralik(load_data("bakim_log"))
    df_g = aralik(load_data("gider"))
    df_s = aralik(load_data("stok_hrk"))

    def _sum(df, col):
        if df.empty or col not in df.columns:
            return 0.0
        return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()

    a_mal = _sum(df_a, "Malzeme_Maliyet")
    a_isc = _sum(df_a, "Iscilik_Maliyet")
    t_mal = _sum(df_t, "Malzeme_Maliyet")
    t_isc = _sum(df_t, "Iscilik_Maliyet")
    b_mal = _sum(df_b, "Malzeme_Maliyet")
    b_isc = _sum(df_b, "Iscilik_Maliyet")
    gider = _sum(df_g, "Tutar")

    # Stok çıkış değeri
    stok_cikis = 0.0
    if not df_s.empty:
        cikislar = df_s[df_s.get("Tip", pd.Series()) == "Çıkış"] if "Tip" in df_s.columns else pd.DataFrame()
        if not cikislar.empty:
            stok_cikis = _sum(cikislar, "Miktar")  # miktar × birim fiyat yok ama miktar göster

    toplam = a_mal + a_isc + t_mal + t_isc + b_mal + b_isc + gider

    # ── KPI Kartları ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Arıza Maliyeti", f"{a_mal + a_isc:,.0f} ₺",
              delta=f"Malz: {a_mal:,.0f} / İşç: {a_isc:,.0f}")
    c2.metric("Talep Maliyeti", f"{t_mal + t_isc:,.0f} ₺",
              delta=f"Malz: {t_mal:,.0f} / İşç: {t_isc:,.0f}")
    c3.metric("Bakım Maliyeti", f"{b_mal + b_isc:,.0f} ₺",
              delta=f"Malz: {b_mal:,.0f} / İşç: {b_isc:,.0f}")
    c4.metric("İşletme Gideri", f"{gider:,.0f} ₺")
    c5.metric("TOPLAM", f"{toplam:,.0f} ₺")

    st.markdown("---")

    # ── Özet Tablo ────────────────────────────────────────────────────────────
    ozet = pd.DataFrame([
        {"Kaynak": "🛠️ Arıza", "Malzeme (₺)": a_mal, "İşçilik (₺)": a_isc, "Toplam (₺)": a_mal + a_isc},
        {"Kaynak": "📨 Talep", "Malzeme (₺)": t_mal, "İşçilik (₺)": t_isc, "Toplam (₺)": t_mal + t_isc},
        {"Kaynak": "🔧 Bakım", "Malzeme (₺)": b_mal, "İşçilik (₺)": b_isc, "Toplam (₺)": b_mal + b_isc},
        {"Kaynak": "💸 Genel Gider", "Malzeme (₺)": gider, "İşçilik (₺)": 0.0, "Toplam (₺)": gider},
        {"Kaynak": "━ TOPLAM", "Malzeme (₺)": a_mal + t_mal + b_mal + gider,
         "İşçilik (₺)": a_isc + t_isc + b_isc,
         "Toplam (₺)": toplam},
    ])
    for col in ["Malzeme (₺)", "İşçilik (₺)", "Toplam (₺)"]:
        ozet[col] = ozet[col].apply(lambda v: f"{v:,.0f}")
    st.dataframe(ozet, use_container_width=True, hide_index=True)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # ── Pasta Grafiği ─────────────────────────────────────────────────────────
    with col_l:
        st.markdown("**Toplam Maliyet Dağılımı**")
        pie_data = {
            "Arıza": a_mal + a_isc,
            "Talep": t_mal + t_isc,
            "Bakım": b_mal + b_isc,
            "Genel Gider": gider,
        }
        pie_data = {k: v for k, v in pie_data.items() if v > 0}
        if pie_data and PLOTLY_OK:
            fig = px.pie(
                values=list(pie_data.values()),
                names=list(pie_data.keys()),
                hole=0.5,
                color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B", "#EF4444"],
            )
            fig.update_layout(**_LAYOUT)
            fig.update_traces(textposition="inside", textinfo="percent+label",
                              marker=dict(line=dict(color="#fff", width=2)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        elif pie_data:
            st.bar_chart(pd.Series(pie_data))
        else:
            st.caption("Bu dönemde maliyet kaydı yok.")

    # ── Gider Kategorileri ────────────────────────────────────────────────────
    with col_r:
        st.markdown("**Genel Gider Kategorileri**")
        if not df_g.empty and "Kategori" in df_g.columns:
            kat_g = (
                df_g.groupby("Kategori")["Tutar"]
                .apply(lambda s: pd.to_numeric(s, errors="coerce").fillna(0).sum())
                .sort_values(ascending=False)
                .reset_index()
            )
            kat_g.columns = ["Kategori", "Tutar (₺)"]
            if PLOTLY_OK:
                fig2 = px.bar(kat_g, x="Tutar (₺)", y="Kategori", orientation="h",
                              color="Tutar (₺)", color_continuous_scale=["#DBEAFE", "#1D4ED8"],
                              text=kat_g["Tutar (₺)"].apply(lambda v: f"{v:,.0f}₺"))
                fig2.update_layout(**_LAYOUT, coloraxis_showscale=False, showlegend=False)
                fig2.update_traces(textposition="outside", marker_line_width=0)
                fig2.update_xaxes(showgrid=False, showticklabels=False)
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.dataframe(kat_g, use_container_width=True, hide_index=True)
        else:
            st.caption("Bu dönemde gider kaydı yok.")

    # ── Aylık Trend ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Aylık Gider Trendi**")
    df_g_all = load_data("gider")
    if not df_g_all.empty and "Tarih" in df_g_all.columns:
        df_g_all["_d"] = pd.to_datetime(df_g_all["Tarih"], errors="coerce")
        df_g_all["_ay"] = df_g_all["_d"].dt.strftime("%Y-%m")
        df_g_all["_tutar"] = pd.to_numeric(df_g_all["Tutar"], errors="coerce").fillna(0)
        aylik = df_g_all.groupby("_ay")["_tutar"].sum().reset_index()
        aylik.columns = ["Ay", "Tutar (₺)"]
        aylik = aylik.sort_values("Ay").tail(12)
        if PLOTLY_OK:
            fig3 = px.bar(aylik, x="Ay", y="Tutar (₺)", text="Tutar (₺)",
                          color_discrete_sequence=["#3B82F6"])
            fig3.update_layout(**_LAYOUT, height=220)
            fig3.update_traces(texttemplate="%{text:,.0f}₺", textposition="outside",
                               marker_line_width=0, cornerradius=4)
            fig3.update_xaxes(showgrid=False)
            fig3.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        else:
            st.line_chart(aylik.set_index("Ay")["Tutar (₺)"])
    else:
        st.caption("Gider kaydı yok.")
