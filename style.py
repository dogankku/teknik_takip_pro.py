"""Global CSS, yardımcı HTML komponentleri, renk paleti."""
import streamlit as st

# ── Renk paleti ──────────────────────────────────────────────────────────────
C = {
    "sidebar_bg":   "#0F172A",
    "sidebar_txt":  "#CBD5E1",
    "primary":      "#3B82F6",
    "primary_dk":   "#1D4ED8",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "page_bg":      "#F1F5F9",
    "card_bg":      "#FFFFFF",
    "txt_dark":     "#1E293B",
    "txt_muted":    "#64748B",
    "border":       "#E2E8F0",
}

CSS = f"""
<style>
/* ─── Import font ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* ─── Page background ────────────────────────────────────────── */
.main {{ background-color: {C["page_bg"]}; }}
.main .block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}}

/* ─── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] > div:first-child {{
    background: {C["sidebar_bg"]};
    padding-top: 0;
}}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {{
    color: {C["sidebar_txt"]} !important;
}}
[data-testid="stSidebar"] .stRadio label {{
    color: #94A3B8 !important;
    border-radius: 8px;
    padding: 7px 10px !important;
    transition: all .15s;
    cursor: pointer;
    display: block;
    width: 100%;
    font-size: 0.875rem;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(255,255,255,.08) !important;
    color: #F8FAFC !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] label {{
    color: #94A3B8 !important;
    font-size: 0.75rem;
}}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.12); }}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,.08) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 8px !important;
    width: 100%;
    font-size: 0.85rem;
    transition: all .15s;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(239,68,68,.25) !important;
    border-color: rgba(239,68,68,.5) !important;
    color: #FCA5A5 !important;
}}

/* ─── Metric cards ──────────────────────────────────────────── */
.kpi-grid {{ display: grid; gap: 1rem; }}
.kpi-card {{
    background: {C["card_bg"]};
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
    position: relative;
    overflow: hidden;
    transition: transform .15s, box-shadow .15s;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,.12);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}}
.kpi-card.blue::before   {{ background: {C["primary"]}; }}
.kpi-card.green::before  {{ background: {C["success"]}; }}
.kpi-card.orange::before {{ background: {C["warning"]}; }}
.kpi-card.red::before    {{ background: {C["danger"]}; }}
.kpi-icon {{
    font-size: 1.6rem;
    float: right;
    line-height: 1;
    margin-top: -2px;
    opacity: .75;
}}
.kpi-label {{
    font-size: 0.72rem;
    font-weight: 600;
    color: {C["txt_muted"]};
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 2.1rem;
    font-weight: 700;
    color: {C["txt_dark"]};
    line-height: 1;
}}
.kpi-delta {{
    font-size: 0.78rem;
    color: {C["txt_muted"]};
    margin-top: 6px;
}}
.kpi-delta.ok   {{ color: {C["success"]}; }}
.kpi-delta.warn {{ color: {C["warning"]}; }}
.kpi-delta.bad  {{ color: {C["danger"]}; }}

/* ─── Section header ─────────────────────────────────────────── */
.sec-header {{
    background: linear-gradient(120deg, {C["sidebar_bg"]} 0%, #1E3A6E 100%);
    border-radius: 12px;
    padding: 20px 26px;
    margin-bottom: 24px;
    color: white;
}}
.sec-header-title {{
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
    color: #F8FAFC;
}}
.sec-header-sub {{
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 4px;
}}

/* ─── Chart card ─────────────────────────────────────────────── */
.chart-card {{
    background: {C["card_bg"]};
    border-radius: 12px;
    padding: 20px 22px 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
    margin-bottom: 1rem;
}}
.chart-card-title {{
    font-size: 0.78rem;
    font-weight: 600;
    color: {C["txt_muted"]};
    text-transform: uppercase;
    letter-spacing: .06em;
    margin-bottom: 12px;
}}

/* ─── Alert rows ─────────────────────────────────────────────── */
.alert-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: {C["txt_dark"]};
}}
.alert-row.warning {{ background: #FFFBEB; border-left: 3px solid {C["warning"]}; }}
.alert-row.danger  {{ background: #FEF2F2; border-left: 3px solid {C["danger"]}; }}
.alert-row.success {{ background: #F0FDF4; border-left: 3px solid {C["success"]}; }}
.alert-row.info    {{ background: #EFF6FF; border-left: 3px solid {C["primary"]}; }}
.alert-row b {{ font-weight: 600; }}

/* ─── Tables ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
}}

/* ─── Forms ──────────────────────────────────────────────────── */
[data-testid="stForm"] {{
    background: {C["card_bg"]};
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
    border: 1px solid {C["border"]};
}}

/* ─── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: {C["card_bg"]} !important;
    border: 1px solid {C["border"]} !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.05);
}}

/* ─── Buttons ────────────────────────────────────────────────── */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    transition: all .15s !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {C["primary"]}, {C["primary_dk"]}) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(59,130,246,.4) !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 4px 16px rgba(59,130,246,.5) !important;
    transform: translateY(-1px) !important;
}}

/* ─── Tabs ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: {C["border"]};
    border-radius: 10px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    color: {C["txt_muted"]};
}}
.stTabs [aria-selected="true"] {{
    background: {C["card_bg"]} !important;
    color: {C["primary"]} !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.1);
}}

/* ─── Metrics override ───────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {C["card_bg"]};
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
    border: 1px solid {C["border"]};
}}
[data-testid="stMetricLabel"] {{ font-size: 0.78rem !important; color: {C["txt_muted"]}; }}
[data-testid="stMetricValue"] {{ font-size: 1.8rem !important; font-weight: 700 !important; }}

/* ─── Selectbox/inputs ───────────────────────────────────────── */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {{
    border-radius: 8px !important;
    border-color: {C["border"]} !important;
}}

/* ─── Hide branding ──────────────────────────────────────────── */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
</style>
"""

# ─── Role badge colors ──────────────────────────────────────────────────────
ROLE_COLORS = {
    "Admin":      ("#3B82F6", "#DBEAFE"),
    "Yonetici":   ("#7C3AED", "#EDE9FE"),
    "Teknisyen":  ("#059669", "#D1FAE5"),
    "Sakin":      ("#D97706", "#FEF3C7"),
}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def kpi_card(label: str, value, icon: str = "", color: str = "blue",
             delta: str = "", delta_type: str = ""):
    delta_html = (f'<div class="kpi-delta {delta_type}">{delta}</div>' if delta else "")
    st.markdown(f"""
    <div class="kpi-card {color}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = ""):
    sub_html = (f'<div class="sec-header-sub">{subtitle}</div>' if subtitle else "")
    st.markdown(f"""
    <div class="sec-header">
        <div class="sec-header-title">{icon} {title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def alert_row(text: str, level: str = "info"):
    icons = {"warning": "⚠️", "danger": "🔴", "success": "✅", "info": "ℹ️"}
    st.markdown(f"""
    <div class="alert-row {level}">
        <span>{icons.get(level, "")}</span>
        <span>{text}</span>
    </div>
    """, unsafe_allow_html=True)


def chart_card_start(title: str):
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-card-title">{title}</div>
    """, unsafe_allow_html=True)


def chart_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def sidebar_user_card(ad_soyad: str, rol: str):
    bg, fg = ROLE_COLORS.get(rol, ("#3B82F6", "#DBEAFE"))
    initials = "".join(w[0].upper() for w in ad_soyad.split()[:2]) or "?"
    st.sidebar.markdown(f"""
    <div style="padding:16px 12px;border-bottom:1px solid rgba(255,255,255,.1);
                margin-bottom:12px;text-align:center;">
        <div style="width:48px;height:48px;border-radius:50%;
                    background:{bg};color:white;font-size:1.1rem;font-weight:700;
                    display:flex;align-items:center;justify-content:center;
                    margin:0 auto 10px;">
            {initials}
        </div>
        <div style="font-size:.9rem;font-weight:600;color:#F1F5F9;">{ad_soyad}</div>
        <div style="display:inline-block;background:{bg};color:white;
                    font-size:.65rem;font-weight:700;padding:2px 10px;
                    border-radius:9999px;margin-top:5px;letter-spacing:.06em;">
            {rol.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown("""
    <div style="padding:20px 16px 8px;border-bottom:1px solid rgba(255,255,255,.1);">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.8rem;">🏢</span>
            <div>
                <div style="font-size:.95rem;font-weight:700;color:#F8FAFC;
                            line-height:1.2;">Teknik Operasyon</div>
                <div style="font-size:.65rem;color:#64748B;letter-spacing:.04em;">
                    YÖNETİM SİSTEMİ
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
