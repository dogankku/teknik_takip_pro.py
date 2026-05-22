"""Modern SaaS UI: light theme, mesh gradient, glassmorphism, indigo accent."""
import streamlit as st

# ── Renk paleti ──────────────────────────────────────────────────────────────
C = {
    # Page & sidebar
    "page_bg":       "#FAFBFF",
    "sidebar_bg":    "#FFFFFF",
    "sidebar_border":"#EEF0F6",
    # Brand
    "primary":       "#6366F1",   # Indigo-500
    "primary_dk":    "#4F46E5",   # Indigo-600
    "primary_lt":    "#EEF2FF",   # Indigo-50
    "accent":        "#8B5CF6",   # Violet-500
    "accent2":       "#EC4899",   # Pink-500
    "teal":          "#06B6D4",
    # State
    "success":       "#10B981",
    "warning":       "#F59E0B",
    "danger":        "#EF4444",
    # Text
    "txt":           "#0F172A",
    "txt_2":         "#475569",
    "txt_3":         "#94A3B8",
    "border":        "#E5E7EB",
    "card_bg":       "#FFFFFF",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, sans-serif; }}

/* ═══════════════════ PAGE BACKGROUND (MESH GRADIENT) ═══════════════════ */
[data-testid="stAppViewContainer"] > .main {{
    background-color: {C["page_bg"]};
    background-image:
        radial-gradient(at 8% 12%, rgba(99,102,241,.08) 0px, transparent 50%),
        radial-gradient(at 92% 8%, rgba(236,72,153,.06) 0px, transparent 50%),
        radial-gradient(at 12% 95%, rgba(6,182,212,.07) 0px, transparent 50%),
        radial-gradient(at 88% 92%, rgba(139,92,246,.06) 0px, transparent 50%);
    background-attachment: fixed;
}}
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1320px;
}}

/* ═══════════════════ SIDEBAR (LIGHT, MODERN) ═══════════════════ */
[data-testid="stSidebar"] > div:first-child {{
    background: {C["sidebar_bg"]};
    border-right: 1px solid {C["sidebar_border"]};
    padding: 0;
    box-shadow: 4px 0 24px rgba(15,23,42,.04);
}}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {{ color: {C["txt"]} !important; }}
[data-testid="stSidebar"] hr {{ border-color: {C["border"]}; margin: .8rem 1rem; }}

/* Sidebar radio (menu) items */
[data-testid="stSidebar"] .stRadio > div {{ gap: 2px !important; }}
[data-testid="stSidebar"] .stRadio label {{
    color: {C["txt_2"]} !important;
    border-radius: 10px;
    padding: 9px 14px !important;
    margin: 0 8px;
    font-size: .88rem;
    font-weight: 500;
    transition: all .2s ease;
    display: block;
    width: calc(100% - 16px);
    cursor: pointer;
    position: relative;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: {C["primary_lt"]};
    color: {C["primary_dk"]} !important;
    transform: translateX(2px);
}}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio label[data-checked="true"],
[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["accent"]} 100%) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,.35);
    font-weight: 600;
}}

/* Date input in sidebar */
[data-testid="stSidebar"] [data-testid="stDateInput"] label {{
    color: {C["txt_3"]} !important;
    font-size: .72rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .05em;
}}

/* Sidebar logout button */
[data-testid="stSidebar"] .stButton > button {{
    background: white !important;
    color: {C["danger"]} !important;
    border: 1px solid #FECACA !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all .2s;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: #FEE2E2 !important;
    box-shadow: 0 2px 8px rgba(239,68,68,.2);
}}

/* ═══════════════════ PAGE HEADER ═══════════════════ */
.page-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid {C["border"]};
}}
.page-head-title {{
    font-size: 1.75rem;
    font-weight: 700;
    color: {C["txt"]};
    line-height: 1.1;
    margin: 0;
    letter-spacing: -.02em;
}}
.page-head-sub {{
    font-size: .9rem;
    color: {C["txt_2"]};
    margin-top: 6px;
}}
.page-head-pill {{
    display: inline-block;
    background: {C["primary_lt"]};
    color: {C["primary_dk"]};
    font-size: .72rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    letter-spacing: .04em;
    text-transform: uppercase;
    margin-bottom: 10px;
}}

/* ═══════════════════ KPI CARDS ═══════════════════ */
.kpi-card {{
    background: {C["card_bg"]};
    border: 1px solid rgba(15,23,42,.05);
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.04);
    position: relative;
    overflow: hidden;
    transition: all .25s ease;
    height: 100%;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(15,23,42,.06), 0 20px 40px rgba(15,23,42,.08);
    border-color: rgba(99,102,241,.2);
}}
.kpi-card .kpi-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}}
.kpi-label {{
    font-size: .72rem;
    font-weight: 700;
    color: {C["txt_3"]};
    text-transform: uppercase;
    letter-spacing: .08em;
}}
.kpi-icon-bg {{
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}}
.kpi-card.blue   .kpi-icon-bg {{ background: {C["primary_lt"]};   color: {C["primary_dk"]}; }}
.kpi-card.green  .kpi-icon-bg {{ background: #D1FAE5;             color: #047857; }}
.kpi-card.orange .kpi-icon-bg {{ background: #FEF3C7;             color: #B45309; }}
.kpi-card.red    .kpi-icon-bg {{ background: #FEE2E2;             color: #B91C1C; }}
.kpi-card.purple .kpi-icon-bg {{ background: #EDE9FE;             color: #6D28D9; }}
.kpi-card.teal   .kpi-icon-bg {{ background: #CFFAFE;             color: #0E7490; }}
.kpi-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {C["txt"]};
    line-height: 1;
    letter-spacing: -.03em;
}}
.kpi-delta {{
    font-size: .8rem;
    color: {C["txt_3"]};
    margin-top: 8px;
    font-weight: 500;
}}
.kpi-delta.ok   {{ color: {C["success"]}; }}
.kpi-delta.warn {{ color: {C["warning"]}; }}
.kpi-delta.bad  {{ color: {C["danger"]}; }}

/* ═══════════════════ CHART CARDS ═══════════════════ */
.chart-card {{
    background: {C["card_bg"]};
    border: 1px solid rgba(15,23,42,.05);
    border-radius: 16px;
    padding: 22px 24px 14px;
    box-shadow: 0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.04);
    margin-bottom: 16px;
}}
.chart-card-title {{
    font-size: 1rem;
    font-weight: 700;
    color: {C["txt"]};
    margin-bottom: 4px;
}}
.chart-card-sub {{
    font-size: .8rem;
    color: {C["txt_3"]};
    margin-bottom: 14px;
}}

/* ═══════════════════ ALERT ROWS ═══════════════════ */
.alert-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
    font-size: .85rem;
    color: {C["txt"]};
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
}}
.alert-row.warning {{ background: #FFFBEB; border-color: #FCD34D; }}
.alert-row.danger  {{ background: #FEF2F2; border-color: #FCA5A5; }}
.alert-row.success {{ background: #F0FDF4; border-color: #86EFAC; }}
.alert-row.info    {{ background: {C["primary_lt"]}; border-color: #C7D2FE; }}
.alert-row b {{ font-weight: 600; }}
.alert-row .alert-ico {{
    width: 28px; height: 28px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: .9rem;
}}
.alert-row.warning .alert-ico {{ background: rgba(245,158,11,.2); }}
.alert-row.danger  .alert-ico {{ background: rgba(239,68,68,.15); }}
.alert-row.success .alert-ico {{ background: rgba(16,185,129,.15); }}
.alert-row.info    .alert-ico {{ background: rgba(99,102,241,.15); }}

/* ═══════════════════ STATUS BADGES ═══════════════════ */
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .02em;
}}
.badge-blue   {{ background: {C["primary_lt"]}; color: {C["primary_dk"]}; }}
.badge-green  {{ background: #D1FAE5; color: #065F46; }}
.badge-orange {{ background: #FEF3C7; color: #92400E; }}
.badge-red    {{ background: #FEE2E2; color: #991B1B; }}
.badge-purple {{ background: #EDE9FE; color: #6D28D9; }}
.badge-gray   {{ background: #F1F5F9; color: #475569; }}

/* ═══════════════════ STREAMLIT WIDGETS OVERRIDE ═══════════════════ */
/* Forms */
[data-testid="stForm"] {{
    background: {C["card_bg"]};
    padding: 26px;
    border-radius: 16px;
    border: 1px solid rgba(15,23,42,.05);
    box-shadow: 0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.04);
}}

/* Expander */
[data-testid="stExpander"] {{
    background: {C["card_bg"]} !important;
    border: 1px solid {C["border"]} !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 2px rgba(15,23,42,.04);
    overflow: hidden;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    padding: 12px 18px !important;
}}
[data-testid="stExpander"] summary:hover {{ background: #F9FAFB; }}

/* Buttons */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: .875rem !important;
    transition: all .2s !important;
    padding: 8px 18px !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["accent"]} 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,.35) !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 8px 24px rgba(99,102,241,.45) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="secondary"] {{
    background: white !important;
    border: 1px solid {C["border"]} !important;
    color: {C["txt"]} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: white;
    border: 1px solid {C["border"]};
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 1px 2px rgba(15,23,42,.03);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 9px !important;
    font-size: .875rem !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    color: {C["txt_2"]};
    transition: all .15s;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: #F9FAFB;
    color: {C["txt"]};
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["accent"]} 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(99,102,241,.3);
}}

/* Streamlit default metrics */
[data-testid="stMetric"] {{
    background: {C["card_bg"]};
    border: 1px solid rgba(15,23,42,.05);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 2px rgba(15,23,42,.04);
}}
[data-testid="stMetricLabel"] {{
    font-size: .72rem !important;
    color: {C["txt_3"]} !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .05em;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: {C["txt"]} !important;
}}

/* Inputs */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] {{
    border-radius: 10px !important;
    border-color: {C["border"]} !important;
    transition: all .15s;
}}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"]:focus-within {{
    border-color: {C["primary"]} !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.1) !important;
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid {C["border"]};
    box-shadow: 0 1px 2px rgba(15,23,42,.04);
}}

/* Hide branding */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ═══════════════════ SIDEBAR USER & BRAND CARDS ═══════════════════ */
.sb-brand {{
    padding: 22px 18px 16px;
    border-bottom: 1px solid {C["border"]};
}}
.sb-brand-row {{
    display: flex; align-items: center; gap: 11px;
}}
.sb-brand-logo {{
    width: 38px; height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["accent"]} 100%);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.1rem;
    box-shadow: 0 4px 14px rgba(99,102,241,.35);
}}
.sb-brand-title {{
    font-size: .95rem; font-weight: 800; color: {C["txt"]};
    line-height: 1.1; letter-spacing: -.01em;
}}
.sb-brand-sub {{
    font-size: .65rem; color: {C["txt_3"]};
    letter-spacing: .08em; text-transform: uppercase;
    margin-top: 2px; font-weight: 600;
}}

.sb-user {{
    margin: 14px 12px 16px;
    padding: 14px;
    background: linear-gradient(135deg, rgba(99,102,241,.06), rgba(139,92,246,.06));
    border: 1px solid rgba(99,102,241,.12);
    border-radius: 14px;
    display: flex; align-items: center; gap: 11px;
}}
.sb-user-avatar {{
    width: 40px; height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["accent"]} 100%);
    color: white; font-weight: 700; font-size: .95rem;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(99,102,241,.35);
}}
.sb-user-name {{
    font-size: .875rem; font-weight: 700; color: {C["txt"]};
    line-height: 1.1;
}}
.sb-user-role {{
    display: inline-block;
    font-size: .65rem; font-weight: 700;
    background: white; color: {C["primary_dk"]};
    padding: 1px 8px; border-radius: 9999px;
    margin-top: 4px; letter-spacing: .04em;
}}

.sb-status {{
    margin: 0 12px 12px;
    padding: 8px 12px;
    background: white;
    border: 1px solid {C["border"]};
    border-radius: 10px;
    font-size: .72rem;
    color: {C["txt_2"]};
    display: flex; align-items: center; gap: 8px;
}}
.sb-status .dot {{
    width: 8px; height: 8px; border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(0,0,0,.05);
}}
.sb-status.online .dot {{ background: {C["success"]}; }}
.sb-status.offline .dot {{ background: {C["warning"]}; }}

/* Smooth scroll & motion */
* {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
}}
</style>
"""

# ── Role colors ──────────────────────────────────────────────────────────────
ROLE_GRADIENTS = {
    "Admin":     ("#6366F1", "#8B5CF6"),
    "Yonetici":  ("#0EA5E9", "#6366F1"),
    "Teknisyen": ("#10B981", "#06B6D4"),
    "Sakin":     ("#F59E0B", "#EC4899"),
}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ── KPI card ─────────────────────────────────────────────────────────────────
def kpi_card(label: str, value, icon: str = "", color: str = "blue",
             delta: str = "", delta_type: str = ""):
    delta_html = f'<div class="kpi-delta {delta_type}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card {color}">
        <div class="kpi-top">
            <span class="kpi-label">{label}</span>
            <div class="kpi-icon-bg">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ── Page header (replaces big gradient banner) ────────────────────────────────
def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    pill_html = f'<div class="page-head-pill">{pill}</div>' if pill else ""
    sub_html = f'<div class="page-head-sub">{subtitle}</div>' if subtitle else ""
    icon_html = f'<span style="margin-right:10px">{icon}</span>' if icon else ""
    st.markdown(f"""
    <div class="page-head">
        <div>
            {pill_html}
            <h1 class="page-head-title">{icon_html}{title}</h1>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Alert row ────────────────────────────────────────────────────────────────
def alert_row(text: str, level: str = "info"):
    icons = {"warning": "⚠", "danger": "🔴", "success": "✓", "info": "ℹ"}
    st.markdown(f"""
    <div class="alert-row {level}">
        <span class="alert-ico">{icons.get(level, "")}</span>
        <span style="flex:1">{text}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Chart card wrapper ───────────────────────────────────────────────────────
def chart_card_start(title: str, subtitle: str = ""):
    sub = f'<div class="chart-card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-card-title">{title}</div>
        {sub}
    """, unsafe_allow_html=True)


def chart_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar components ──────────────────────────────────────────────────────
def sidebar_brand():
    st.sidebar.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-row">
            <div class="sb-brand-logo">🏢</div>
            <div>
                <div class="sb-brand-title">Teknik Operasyon</div>
                <div class="sb-brand-sub">Pro Yönetim</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_user_card(ad_soyad: str, rol: str):
    initials = "".join(w[0].upper() for w in (ad_soyad or "?").split()[:2]) or "?"
    g1, g2 = ROLE_GRADIENTS.get(rol, ("#6366F1", "#8B5CF6"))
    st.sidebar.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-avatar" style="background:linear-gradient(135deg,{g1} 0%,{g2} 100%)">
            {initials}
        </div>
        <div style="flex:1;min-width:0;">
            <div class="sb-user-name">{ad_soyad}</div>
            <span class="sb-user-role">{rol}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_status(connected: bool):
    cls = "online" if connected else "offline"
    txt = "Google Sheets bağlı" if connected else "Yerel CSV modu"
    st.sidebar.markdown(f"""
    <div class="sb-status {cls}">
        <span class="dot"></span>
        <span>{txt}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Badge helper ─────────────────────────────────────────────────────────────
def badge(text: str, color: str = "blue") -> str:
    return f'<span class="badge badge-{color}">{text}</span>'
