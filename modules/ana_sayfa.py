import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db import load_data
from auth import current_user, current_role
from style import (kpi_card, section_header, alert_row, chart_card_start,
                   chart_card_end, hero_banner, feature_card,
                   action_group_title, action_card)

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ── Plotly ortak theme ───────────────────────────────────────────────────────
_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444",
           "#8B5CF6", "#06B6D4", "#F97316", "#84CC16"]
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=0),
    font=dict(family="Inter, sans-serif", size=12, color="#64748B"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=220,
)


def render(secilen_tarih: date):
    u = current_user() or {}
    rol = current_role() or ""
    ad = u.get('Ad_Soyad', '').split()[0] if u.get('Ad_Soyad') else ''

    section_header(
        f"Hoşgeldiniz, {ad}",
        f"{secilen_tarih.strftime('%d %B %Y')} • Tüm sistem genel bakışı",
        pill="KONTROL MERKEZİ",
    )

    if rol == "Sakin":
        _sakin_dashboard(u)
        return

    # ── Hero banner (Xenia AI Co-Pilot tarzı) ─────────────────────────────────
    hero_banner(
        title="Akıllı Operasyon Asistanı",
        subtitle="Sistem otomatik olarak gecikmiş bakımları, kritik stokları ve acil talepleri sizin için izler.",
        badge="AKTİF",
        icon="✨",
    )

    # ── Feature Cards (Quick Actions - Xenia tarzı 2 büyük kart) ──────────────
    fc1, fc2 = st.columns(2)
    with fc1:
        feature_card(
            "Talep & Şikayet Yönetimi",
            "Sakinlerden gelen istekleri öncelik ve SLA takibi ile yönetin.",
            icon="📨", color="purple",
        )
    with fc2:
        feature_card(
            "Bakım & Operasyon",
            "Periyodik bakımları takip edin, arızaları iş emrine bağlayın.",
            icon="🔧", color="pink",
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Hızlı erişim kartları (Pre-Built Reports tarzı 3 sütun) ──────────────
    g1, g2, g3 = st.columns(3)

    with g1:
        action_group_title("🏢  Mülk Yönetimi")
        action_card("Daire & Sakin Kayıtları", "🏠", "purple")
        action_card("Aidat & Tahsilat", "💰", "amber")
        action_card("Doluluk Özeti", "📊", "indigo")

    with g2:
        action_group_title("🔧  Operasyon")
        action_card("Açık Arızalar", "🛠️", "rose")
        action_card("Bekleyen Talepler", "📨", "purple")
        action_card("Bakım Takvimi", "📅", "blue")
        action_card("Günlük Kontroller", "✅", "green")

    with g3:
        action_group_title("📦  Envanter & Mali")
        action_card("Ekipman & Barkod", "📦", "teal")
        action_card("Stok Durumu", "📋", "green")
        action_card("Sayaç & Tüketim", "⚡", "amber")
        action_card("Gider Takibi", "💸", "pink")

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── KPI metrikleri ────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:14px;">'
        '📊 Anlık Durum</div>',
        unsafe_allow_html=True,
    )
    _yonetim_dashboard(secilen_tarih)


# ─────────────────────────────────────────────────────────────────────────────
def _yonetim_dashboard(secilen_tarih: date):
    df_a  = load_data("ariza")
    df_t  = load_data("talep")
    df_b  = load_data("bakim_plan")
    df_s  = load_data("stok")
    df_th = load_data("tahakkuk")
    df_od = load_data("odeme")
    df_g  = load_data("gider")

    today = pd.Timestamp(secilen_tarih)

    # ── KPI hesapla ───────────────────────────────────────────────────────────
    def _count(df, col, vals):
        if df.empty or col not in df.columns: return 0
        return df[col].isin(vals if isinstance(vals, list) else [vals]).sum()

    acik_ariza  = _count(df_a, "Durum", ["Açık", "Devam Ediyor"])
    acik_talep  = _count(df_t, "Durum", ["Açık", "Atandı", "Devam"])
    kritik_stok = _stok_kritik(df_s)
    geciken_bkm = _geciken_bakim(df_b, today)

    toplam_th = _para(df_th, "Tutar")
    toplam_od = _para(df_od, "Tutar")
    bu_ay_g   = _bu_ay_gider(df_g, secilen_tarih)

    # ── KPI Kartları ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Açık Arıza",      acik_ariza,  "🛠️", "red"    if acik_ariza  > 0 else "green")
    with c2: kpi_card("Açık Talep",      acik_talep,  "📨", "orange" if acik_talep  > 0 else "green")
    with c3: kpi_card("Geciken Bakım",   geciken_bkm, "⏰", "red"    if geciken_bkm > 0 else "green")
    with c4: kpi_card("Kritik Stok",     kritik_stok, "⚠️", "orange" if kritik_stok > 0 else "green")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c5, c6, c7 = st.columns(3)
    with c5: kpi_card("Toplam Tahakkuk", f"{toplam_th:,.0f} ₺", "💰", "purple")
    with c6: kpi_card("Toplam Tahsilat", f"{toplam_od:,.0f} ₺", "✅", "green")
    with c7: kpi_card("Bu Ay Gider",     f"{bu_ay_g:,.0f} ₺",   "💸", "teal")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    col_l, col_r = st.columns([1, 1])

    with col_l:
        _ariza_chart(df_a)
        _talep_oncelik_chart(df_t)

    with col_r:
        _gider_chart(df_g)
        _bakim_timeline(df_b, today)

    # ── Tekrarlı görev vade uyarıları & checklist özeti ──────────────────────
    col_tekrar, col_cl = st.columns(2)
    with col_tekrar:
        _tekrar_ozet(today)
    with col_cl:
        _checklist_ozet(secilen_tarih)

    # ── Son aktivite akışı ─────────────────────────────────────────────────────
    _aktivite_feed()

    # ── Uyarı paneli ──────────────────────────────────────────────────────────
    _uyari_paneli(df_b, today, df_s, df_t)


def _ariza_chart(df: pd.DataFrame):
    st.markdown('<div class="chart-card"><div class="chart-card-title">ARİZALAR — DURUM DAĞILIMI</div>', unsafe_allow_html=True)
    if df.empty or "Durum" not in df.columns:
        st.caption("Veri yok")
    elif PLOTLY_OK:
        g = df["Durum"].value_counts().reset_index()
        g.columns = ["Durum", "Adet"]
        color_map = {"Açık": "#EF4444", "Devam Ediyor": "#F59E0B", "Tamamlandı": "#10B981"}
        fig = px.pie(g, names="Durum", values="Adet", hole=0.55,
                     color="Durum", color_discrete_map=color_map)
        fig.update_layout(**_LAYOUT)
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          marker=dict(line=dict(color="#fff", width=2)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.dataframe(df["Durum"].value_counts(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _talep_oncelik_chart(df: pd.DataFrame):
    st.markdown('<div class="chart-card"><div class="chart-card-title">TALEPLER — ÖNCELİK DAĞILIMI</div>', unsafe_allow_html=True)
    if df.empty or "Oncelik" not in df.columns:
        st.caption("Veri yok")
    elif PLOTLY_OK:
        aktif = df[~df["Durum"].isin(["Çözüldü", "Kapatıldı"])] if "Durum" in df.columns else df
        g = aktif["Oncelik"].value_counts().reset_index()
        g.columns = ["Öncelik", "Adet"]
        order = ["Kritik", "Yuksek", "Normal", "Dusuk"]
        g["_s"] = g["Öncelik"].map({v: i for i, v in enumerate(order)})
        g = g.sort_values("_s")
        color_map = {"Kritik": "#EF4444", "Yuksek": "#F59E0B", "Normal": "#3B82F6", "Dusuk": "#10B981"}
        fig = px.bar(g, x="Öncelik", y="Adet", color="Öncelik",
                     color_discrete_map=color_map, text="Adet")
        fig.update_layout(**_LAYOUT, showlegend=False)
        fig.update_traces(textposition="outside", marker_line_width=0, cornerradius=6)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.dataframe(df["Oncelik"].value_counts(), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _gider_chart(df: pd.DataFrame):
    st.markdown('<div class="chart-card"><div class="chart-card-title">GİDERLER — KATEGORİ (Son 6 ay)</div>', unsafe_allow_html=True)
    if df.empty or "Kategori" not in df.columns:
        st.caption("Veri yok")
    elif PLOTLY_OK:
        df2 = df.copy()
        df2["_t"] = pd.to_numeric(df2["Tutar"], errors="coerce").fillna(0)
        df2["_d"] = pd.to_datetime(df2["Tarih"], errors="coerce")
        cutoff = datetime.now() - timedelta(days=180)
        df2 = df2[df2["_d"] >= cutoff]
        if df2.empty:
            st.caption("Son 6 ayda gider yok")
        else:
            g = df2.groupby("Kategori")["_t"].sum().reset_index().sort_values("_t", ascending=True).tail(8)
            fig = px.bar(g, x="_t", y="Kategori", orientation="h",
                         color="_t", color_continuous_scale=["#DBEAFE", "#1D4ED8"])
            fig.update_layout(**_LAYOUT, coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0, text=g["_t"].apply(lambda v: f"{v:,.0f}₺"),
                              textposition="outside")
            fig.update_xaxes(showgrid=False, showticklabels=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.caption("Plotly yok")
    st.markdown("</div>", unsafe_allow_html=True)


def _bakim_timeline(df: pd.DataFrame, today: pd.Timestamp):
    st.markdown('<div class="chart-card"><div class="chart-card-title">YAKLAŞAN BAKIMLAR (30 gün)</div>', unsafe_allow_html=True)
    if df.empty or "Sonraki_Tarih" not in df.columns:
        st.caption("Veri yok")
    else:
        df2 = df.copy()
        df2["_st"] = pd.to_datetime(df2["Sonraki_Tarih"], errors="coerce")
        window = df2[(df2["_st"] >= today) & (df2["_st"] <= today + pd.Timedelta(days=30))]
        geciken = df2[df2["_st"] < today]

        c1, c2 = st.columns(2)
        c1.metric("Yaklaşan (30 gün)", len(window))
        c2.metric("Gecikmiş", len(geciken), delta="⚠️ Acil" if len(geciken) > 0 else "", delta_color="inverse")

        if not window.empty:
            window = window.sort_values("_st")[["Baslik", "Sonraki_Tarih", "Sorumlu"]].head(5)
            st.dataframe(window, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _uyari_paneli(df_b, today, df_s, df_t):
    items = []

    # Geciken bakımlar
    if not df_b.empty and "Sonraki_Tarih" in df_b.columns:
        df_b2 = df_b.copy()
        df_b2["_st"] = pd.to_datetime(df_b2["Sonraki_Tarih"], errors="coerce")
        geciken = df_b2[df_b2["_st"] < today]
        for _, r in geciken.iterrows():
            items.append(("danger", f"<b>Gecikmiş bakım:</b> {r.get('Baslik','')} — {r.get('Sorumlu','')}"))

    # Kritik stok
    if not df_s.empty:
        df_s2 = df_s.copy()
        df_s2["_m"] = pd.to_numeric(df_s2.get("Mevcut", 0), errors="coerce").fillna(0)
        df_s2["_k"] = pd.to_numeric(df_s2.get("Kritik", 0), errors="coerce").fillna(0)
        for _, r in df_s2[df_s2["_m"] <= df_s2["_k"]].iterrows():
            items.append(("warning", f"<b>Kritik stok:</b> {r.get('Urun_Adi','')} ({r.get('Mevcut','')} {r.get('Birim','')})"))

    # Kritik talepler
    if not df_t.empty and "Oncelik" in df_t.columns and "Durum" in df_t.columns:
        kritik = df_t[(df_t["Oncelik"] == "Kritik") & (~df_t["Durum"].isin(["Çözüldü", "Kapatıldı"]))]
        for _, r in kritik.head(3).iterrows():
            items.append(("danger", f"<b>Kritik talep:</b> {r.get('Baslik','')} — Daire {r.get('Daire_ID','')}"))

    if items:
        st.markdown("---")
        st.markdown("#### ⚠️ Dikkat Gerektiren Konular")
        for level, text in items[:8]:
            alert_row(text, level)
    elif not all(df.empty for df in [df_b, df_s, df_t]):
        alert_row("Tüm sistemler normal. Gecikmiş bakım, kritik stok veya acil talep yok.", "success")


# ─────────────────────────────────────────────────────────────────────────────
def _sakin_dashboard(u: dict):
    daire_id = u.get("Daire_ID", "")

    st.markdown(f"""
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;
                padding:16px 20px;margin-bottom:20px;">
        <div style="font-size:.75rem;font-weight:600;color:#1D4ED8;text-transform:uppercase;
                    letter-spacing:.06em;">Daireniz</div>
        <div style="font-size:1.5rem;font-weight:700;color:#1E293B;margin-top:2px;">
            {daire_id or "Atanmamış"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_th = load_data("tahakkuk")
    df_od = load_data("odeme")
    df_t  = load_data("talep")

    th = _para_daire(df_th, daire_id)
    od = _para_daire(df_od, daire_id)
    bk = th - od

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Toplam Tahakkuk", f"{th:,.0f} ₺", "💰", "blue")
    with c2: kpi_card("Ödenen",          f"{od:,.0f} ₺", "✅", "green")
    with c3: kpi_card("Kalan Borç",      f"{bk:,.0f} ₺", "📋",
                      "red" if bk > 0 else "green",
                      delta="Lütfen ödeyin" if bk > 0 else "Hesabınız temiz",
                      delta_type="bad" if bk > 0 else "ok")

    if not df_t.empty:
        st.markdown("---")
        st.markdown("#### 📨 Taleplerim")
        mine = df_t[df_t["Daire_ID"].astype(str) == str(daire_id)]
        if not mine.empty:
            st.dataframe(
                mine[["Talep_ID", "Tarih", "Kategori", "Baslik", "Oncelik", "Durum"]
                     ].sort_values("Tarih", ascending=False).head(10),
                use_container_width=True, hide_index=True,
            )
        else:
            alert_row("Henüz talebiniz yok.", "info")


# ─────────────────────────────────────────────────────────────────────────────
def _para(df, col):
    if df.empty or col not in df.columns: return 0.0
    return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()

def _para_daire(df, did):
    if df.empty: return 0.0
    m = df[df.get("Daire_ID", pd.Series()).astype(str) == str(did)] if "Daire_ID" in df.columns else pd.DataFrame()
    return _para(m, "Tutar")

def _stok_kritik(df):
    if df.empty: return 0
    m = pd.to_numeric(df.get("Mevcut", pd.Series()), errors="coerce").fillna(0)
    k = pd.to_numeric(df.get("Kritik", pd.Series()), errors="coerce").fillna(0)
    return int((m <= k).sum())

def _geciken_bakim(df, today):
    if df.empty or "Sonraki_Tarih" not in df.columns: return 0
    t = pd.to_datetime(df["Sonraki_Tarih"], errors="coerce")
    return int((t < today).sum())

def _bu_ay_gider(df, t: date):
    if df.empty or "Tarih" not in df.columns: return 0.0
    df2 = df.copy()
    df2["_d"] = pd.to_datetime(df2["Tarih"], errors="coerce")
    m = df2[df2["_d"].dt.strftime("%Y-%m") == t.strftime("%Y-%m")]
    return pd.to_numeric(m.get("Tutar", pd.Series()), errors="coerce").fillna(0).sum()


# ─────────────────────────────────────────────────────────────────────────────
def _tekrar_ozet(today: pd.Timestamp):
    """Tekrarlı görev vade durumu özeti."""
    st.markdown('<div class="chart-card"><div class="chart-card-title">🔁 TEKRARLı GÖREVLER</div>',
                unsafe_allow_html=True)
    df = load_data("tekrar")
    if df.empty:
        st.caption("Tekrarlı görev kaydı yok.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if "Sonraki_Tarih" not in df.columns:
        st.caption("Veri yok.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    df2 = df.copy()
    df2["_st"] = pd.to_datetime(df2["Sonraki_Tarih"], errors="coerce")
    aktif = df2[df2.get("Aktif", pd.Series(dtype=str)).astype(str).str.lower().isin(
        ["evet", "true", "1"])] if "Aktif" in df2.columns else df2

    gecikti  = aktif[aktif["_st"] < today]
    bugun    = aktif[(aktif["_st"] >= today) & (aktif["_st"] < today + pd.Timedelta(days=1))]
    bu_hafta = aktif[(aktif["_st"] >= today) & (aktif["_st"] <= today + pd.Timedelta(days=7))]

    ca, cb, cc = st.columns(3)
    ca.metric("Gecikmiş",  len(gecikti),  delta="⚠️" if len(gecikti) > 0 else "",
              delta_color="inverse" if len(gecikti) > 0 else "normal")
    cb.metric("Bugün",     len(bugun))
    cc.metric("Bu Hafta",  len(bu_hafta))

    if not gecikti.empty:
        show = [c for c in ["Baslik", "Sorumlu", "Sonraki_Tarih"] if c in gecikti.columns]
        st.dataframe(gecikti[show].head(5), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _checklist_ozet(secilen_tarih: date):
    """Bugünkü checklist puan özeti."""
    st.markdown('<div class="chart-card"><div class="chart-card-title">✅ BUGÜNKÜ KONTROLLEr</div>',
                unsafe_allow_html=True)
    df = load_data("checklist")
    if df.empty or "Tarih" not in df.columns:
        st.caption("Kontrol kaydı yok.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    bugun_str = str(secilen_tarih)
    bugun_df = df[df["Tarih"].astype(str).str.startswith(bugun_str)]

    if bugun_df.empty:
        st.caption(f"{bugun_str} için kontrol kaydı yok.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    toplam = len(bugun_df)
    if "Puan" in bugun_df.columns:
        tamam   = int(pd.to_numeric(bugun_df["Puan"], errors="coerce").fillna(0).eq(1).sum())
        sorunlu = toplam - tamam
        oran = tamam / toplam * 100 if toplam else 0
    else:
        tamam   = bugun_df[bugun_df.get("Sonuc", pd.Series(dtype=str)).astype(str) == "Tamam"].shape[0] if "Sonuc" in bugun_df.columns else 0
        sorunlu = toplam - tamam
        oran = tamam / toplam * 100 if toplam else 0

    ca, cb, cc = st.columns(3)
    ca.metric("Toplam",  toplam)
    cb.metric("Tamam",   tamam)
    cc.metric("Sorunlu", sorunlu,
              delta="⚠️ İncele" if sorunlu > 0 else "",
              delta_color="inverse" if sorunlu > 0 else "normal")

    st.progress(min(int(oran), 100), text=f"Başarı: %{oran:.0f}")

    st.markdown("</div>", unsafe_allow_html=True)


def _aktivite_feed():
    """Son 10 sistem aktivitesi akışı."""
    st.markdown("---")
    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:10px;">'
        '⚡ Son Aktiviteler</div>',
        unsafe_allow_html=True,
    )
    df = load_data("aktivite")
    if df.empty:
        st.caption("Aktivite kaydı yok.")
        return

    g = df.copy()
    try:
        g = g.sort_values("Tarih", ascending=False)
    except Exception:
        pass
    g = g.head(10)

    RENK = {
        "Oluşturuldu":  "#10B981",
        "Durum Değişti":"#3B82F6",
        "Güncellendi":  "#F59E0B",
        "Silindi":      "#EF4444",
    }

    for _, row in g.iterrows():
        aksiyon  = str(row.get("Aksiyon", ""))
        renk     = RENK.get(aksiyon, "#64748B")
        tarih    = str(row.get("Tarih", ""))
        saat     = str(row.get("Saat", ""))
        kullanici= str(row.get("Kullanici", ""))
        tip      = str(row.get("Parent_Tip", ""))
        pid      = str(row.get("Parent_ID", ""))
        detay    = str(row.get("Detay", ""))

        st.markdown(
            f'<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid #F1F5F9;">'
            f'<div style="min-width:110px;font-size:.72rem;color:#94A3B8;">{tarih} {saat[:5]}</div>'
            f'<div style="min-width:6px;background:{renk};border-radius:3px;"></div>'
            f'<div style="flex:1;font-size:.8rem;color:#475569;">'
            f'<span style="font-weight:600;color:{renk};">{aksiyon}</span> '
            f'· {tip} <b>{pid}</b>'
            f'{(" — " + detay[:60]) if detay else ""}'
            f'<span style="color:#94A3B8;margin-left:8px;">👤 {kullanici}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
