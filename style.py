"""Xenia / Konsiyon tarzı modern SaaS UI."""
import streamlit as st

C = {
    "page_bg":        "#F9FAFB",
    "sidebar_bg":     "#FFFFFF",
    "sidebar_border": "#F1F3F7",
    "primary":        "#7C3AED",   # Violet-600 (Xenia-like purple)
    "primary_dk":     "#6D28D9",
    "primary_lt":     "#F5F3FF",   # Violet-50
    "pink":           "#EC4899",
    "indigo":         "#6366F1",
    "teal":           "#14B8A6",
    "amber":          "#F59E0B",
    "rose":           "#F43F5E",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
    "txt":            "#111827",
    "txt_2":          "#4B5563",
    "txt_3":          "#9CA3AF",
    "border":         "#E5E7EB",
    "border_lt":      "#F3F4F6",
    "card_bg":        "#FFFFFF",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, sans-serif; }}

/* ═════════════════ PAGE ═════════════════ */
[data-testid="stAppViewContainer"] > .main {{
    background: {C["page_bg"]};
}}
.main .block-container {{
    padding: 2rem 2.5rem 3rem;
    max-width: 1320px;
}}

/* ═════════════════ SIDEBAR ═════════════════ */
[data-testid="stSidebar"] > div:first-child {{
    background: {C["sidebar_bg"]};
    border-right: 1px solid {C["sidebar_border"]};
    box-shadow: none;
    padding: 0;
}}
[data-testid="stSidebar"] .stMarkdown {{ color: {C["txt"]} !important; }}
[data-testid="stSidebar"] hr {{ display: none; }}

/* SECTION LABEL */
.nav-section-title {{
    font-size: .68rem;
    font-weight: 700;
    color: {C["txt_3"]};
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: 16px 20px 6px;
}}

/* NAV ITEM - applied to all sidebar buttons (the "default" / non-active state) */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {C["txt_2"]} !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin: 1px 12px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 500 !important;
    font-size: .87rem !important;
    width: calc(100% - 24px) !important;
    transition: all .15s ease !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {C["border_lt"]} !important;
    color: {C["txt"]} !important;
}}
[data-testid="stSidebar"] .stButton > button:focus {{
    box-shadow: none !important;
    outline: none !important;
}}

/* ACTIVE NAV ITEM rendered as div (matches button style but highlighted) */
.nav-item-active {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: {C["primary_lt"]};
    color: {C["primary_dk"]};
    border-radius: 8px;
    padding: 8px 12px;
    margin: 1px 12px;
    font-weight: 600;
    font-size: .87rem;
    border-left: 3px solid {C["primary"]};
    padding-left: 9px;
}}

/* Date input in sidebar */
[data-testid="stSidebar"] [data-testid="stDateInput"] {{
    padding: 0 12px;
    margin: 8px 0;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] label {{
    color: {C["txt_3"]} !important;
    font-size: .68rem !important;
    font-weight: 700 !important;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding-left: 8px;
}}

/* LOGOUT BUTTON (override) */
[data-testid="stSidebar"] .stButton:has(button:contains("Çıkış")) > button,
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: transparent !important;
    color: {C["danger"]} !important;
}}

/* ═════════════════ PAGE HEAD ═════════════════ */
.page-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 24px;
    padding-bottom: 18px;
    border-bottom: 1px solid {C["border_lt"]};
}}
.page-head-title {{
    font-size: 1.65rem;
    font-weight: 700;
    color: {C["txt"]};
    line-height: 1.2;
    margin: 0;
    letter-spacing: -.02em;
}}
.page-head-sub {{
    font-size: .88rem;
    color: {C["txt_2"]};
    margin-top: 6px;
}}
.page-head-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {C["primary_lt"]};
    color: {C["primary_dk"]};
    font-size: .68rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 8px;
}}

/* ═════════════════ HERO BANNER (purple gradient) ═════════════════ */
.hero-banner {{
    background: linear-gradient(120deg, #7C3AED 0%, #A855F7 40%, #EC4899 100%);
    border-radius: 16px;
    padding: 22px 28px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(124,58,237,.25);
    position: relative;
    overflow: hidden;
}}
.hero-banner::before {{
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,.15) 0%, transparent 70%);
    pointer-events: none;
}}
.hero-banner::after {{
    content: '';
    position: absolute;
    bottom: -60%; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(255,255,255,.1) 0%, transparent 70%);
    pointer-events: none;
}}
.hero-icon {{
    width: 44px; height: 44px;
    background: rgba(255,255,255,.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
    backdrop-filter: blur(8px);
}}
.hero-text {{ flex: 1; z-index: 1; }}
.hero-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: white;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.hero-badge {{
    background: white;
    color: {C["primary_dk"]};
    font-size: .62rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: .06em;
}}
.hero-sub {{
    font-size: .85rem;
    color: rgba(255,255,255,.85);
    font-weight: 400;
}}
.hero-cta {{
    background: white;
    color: {C["primary_dk"]};
    padding: 8px 18px;
    border-radius: 10px;
    font-weight: 600;
    font-size: .85rem;
    flex-shrink: 0;
    z-index: 1;
    text-decoration: none;
    box-shadow: 0 4px 12px rgba(0,0,0,.1);
}}

/* ═════════════════ FEATURE CARDS (big) ═════════════════ */
.feature-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 14px;
    padding: 20px 22px;
    transition: all .2s ease;
    cursor: default;
    height: 100%;
}}
.feature-card:hover {{
    border-color: {C["primary"]};
    box-shadow: 0 8px 24px rgba(124,58,237,.1);
    transform: translateY(-2px);
}}
.feature-icon {{
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 14px;
}}
.feature-icon.purple {{ background: #F5F3FF; color: #7C3AED; }}
.feature-icon.pink   {{ background: #FCE7F3; color: #DB2777; }}
.feature-icon.blue   {{ background: #EFF6FF; color: #2563EB; }}
.feature-icon.teal   {{ background: #CCFBF1; color: #0F766E; }}
.feature-title {{
    font-size: 1rem;
    font-weight: 700;
    color: {C["txt"]};
    margin-bottom: 4px;
}}
.feature-desc {{
    font-size: .82rem;
    color: {C["txt_2"]};
    line-height: 1.5;
}}

/* ═════════════════ ACTION GROUP (pre-built reports tarzı) ═════════════════ */
.action-group-title {{
    font-size: .8rem;
    font-weight: 700;
    color: {C["txt"]};
    margin: 0 0 10px;
}}
.action-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all .15s ease;
}}
.action-card:hover {{
    border-color: {C["primary"]};
    background: {C["primary_lt"]};
    transform: translateX(2px);
}}
.action-card-icon {{
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: .95rem;
    flex-shrink: 0;
}}
.action-card-icon.purple {{ background: #F5F3FF; color: #7C3AED; }}
.action-card-icon.pink   {{ background: #FCE7F3; color: #DB2777; }}
.action-card-icon.blue   {{ background: #EFF6FF; color: #2563EB; }}
.action-card-icon.green  {{ background: #ECFDF5; color: #059669; }}
.action-card-icon.amber  {{ background: #FEF3C7; color: #B45309; }}
.action-card-icon.teal   {{ background: #CCFBF1; color: #0F766E; }}
.action-card-icon.rose   {{ background: #FFE4E6; color: #BE123C; }}
.action-card-icon.indigo {{ background: #EEF2FF; color: #4338CA; }}
.action-card-label {{
    font-size: .85rem;
    font-weight: 500;
    color: {C["txt"]};
}}

/* ═════════════════ KPI CARDS ═════════════════ */
.kpi-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 14px;
    padding: 18px 20px;
    transition: all .2s ease;
    height: 100%;
}}
.kpi-card:hover {{
    border-color: rgba(124,58,237,.3);
    box-shadow: 0 4px 16px rgba(124,58,237,.08);
}}
.kpi-top {{
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
    letter-spacing: .06em;
}}
.kpi-icon-bg {{
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem;
}}
.kpi-card.blue   .kpi-icon-bg {{ background: #EFF6FF; color: #2563EB; }}
.kpi-card.green  .kpi-icon-bg {{ background: #ECFDF5; color: #059669; }}
.kpi-card.orange .kpi-icon-bg {{ background: #FEF3C7; color: #B45309; }}
.kpi-card.red    .kpi-icon-bg {{ background: #FEE2E2; color: #B91C1C; }}
.kpi-card.purple .kpi-icon-bg {{ background: #F5F3FF; color: #7C3AED; }}
.kpi-card.teal   .kpi-icon-bg {{ background: #CCFBF1; color: #0F766E; }}
.kpi-card.pink   .kpi-icon-bg {{ background: #FCE7F3; color: #DB2777; }}
.kpi-value {{
    font-size: 1.85rem;
    font-weight: 800;
    color: {C["txt"]};
    line-height: 1;
    letter-spacing: -.03em;
}}
.kpi-delta {{
    font-size: .78rem;
    color: {C["txt_3"]};
    margin-top: 8px;
    font-weight: 500;
}}
.kpi-delta.ok   {{ color: {C["success"]}; }}
.kpi-delta.warn {{ color: {C["warning"]}; }}
.kpi-delta.bad  {{ color: {C["danger"]}; }}

/* ═════════════════ CHART CARDS ═════════════════ */
.chart-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 14px;
    padding: 20px 22px 12px;
    margin-bottom: 14px;
}}
.chart-card-title {{
    font-size: .95rem;
    font-weight: 700;
    color: {C["txt"]};
    margin-bottom: 4px;
}}
.chart-card-sub {{
    font-size: .78rem;
    color: {C["txt_3"]};
    margin-bottom: 14px;
}}

/* ═════════════════ ALERT ROWS ═════════════════ */
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
    border: 1px solid {C["border_lt"]};
}}
.alert-row.warning {{ background: #FFFBEB; border-color: #FCD34D; }}
.alert-row.danger  {{ background: #FEF2F2; border-color: #FCA5A5; }}
.alert-row.success {{ background: #F0FDF4; border-color: #86EFAC; }}
.alert-row.info    {{ background: {C["primary_lt"]}; border-color: #DDD6FE; }}
.alert-row b {{ font-weight: 600; }}
.alert-ico {{
    width: 28px; height: 28px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: .9rem;
    flex-shrink: 0;
}}
.alert-row.warning .alert-ico {{ background: rgba(245,158,11,.2); }}
.alert-row.danger  .alert-ico {{ background: rgba(239,68,68,.15); }}
.alert-row.success .alert-ico {{ background: rgba(16,185,129,.15); }}
.alert-row.info    .alert-ico {{ background: rgba(124,58,237,.15); }}

/* ═════════════════ BADGES ═════════════════ */
.badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: .72rem;
    font-weight: 700;
}}
.badge-blue   {{ background: #DBEAFE; color: #1E40AF; }}
.badge-green  {{ background: #D1FAE5; color: #065F46; }}
.badge-orange {{ background: #FEF3C7; color: #92400E; }}
.badge-red    {{ background: #FEE2E2; color: #991B1B; }}
.badge-purple {{ background: #EDE9FE; color: #6D28D9; }}
.badge-gray   {{ background: #F1F5F9; color: #475569; }}

/* ═════════════════ FORMS / EXPANDER / TABS ═════════════════ */
[data-testid="stForm"] {{
    background: {C["card_bg"]};
    padding: 24px;
    border-radius: 14px;
    border: 1px solid {C["border_lt"]};
    box-shadow: none;
}}
[data-testid="stExpander"] {{
    background: {C["card_bg"]} !important;
    border: 1px solid {C["border_lt"]} !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    overflow: hidden;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    padding: 12px 18px !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background: transparent;
    border-bottom: 1px solid {C["border_lt"]};
    border-radius: 0;
    padding: 0;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    font-size: .88rem !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    color: {C["txt_2"]};
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    border-bottom-color: {C["primary"]} !important;
    color: {C["primary_dk"]} !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}}

/* ═════════════════ BUTTONS (main area) ═════════════════ */
.main .stButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: .875rem !important;
    transition: all .15s !important;
    padding: 8px 18px !important;
}}
.main .stButton > button[kind="primary"] {{
    background: linear-gradient(120deg, {C["primary"]} 0%, {C["pink"]} 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(124,58,237,.3) !important;
}}
.main .stButton > button[kind="primary"]:hover {{
    box-shadow: 0 6px 20px rgba(124,58,237,.4) !important;
    transform: translateY(-1px) !important;
}}

/* Metric override */
[data-testid="stMetric"] {{
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 12px;
    padding: 16px 18px;
}}
[data-testid="stMetricLabel"] {{
    font-size: .72rem !important;
    color: {C["txt_3"]} !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 1.65rem !important;
    font-weight: 800 !important;
}}

/* Inputs */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] {{
    border-radius: 8px !important;
    border-color: {C["border"]} !important;
}}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"]:focus-within {{
    border-color: {C["primary"]} !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.1) !important;
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
    border: 1px solid {C["border_lt"]};
    overflow: hidden;
}}

/* ═════════════════ SIDEBAR HEADER (BRAND + USER) ═════════════════ */
.sb-brand {{
    padding: 20px 20px 16px;
    border-bottom: 1px solid {C["border_lt"]};
}}
.sb-brand-row {{ display: flex; align-items: center; gap: 11px; }}
.sb-brand-logo {{
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, {C["primary"]} 0%, {C["pink"]} 100%);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 1.05rem;
    box-shadow: 0 6px 14px rgba(124,58,237,.3);
}}
.sb-brand-title {{
    font-size: .92rem; font-weight: 700; color: {C["txt"]};
    line-height: 1.1;
}}
.sb-brand-sub {{
    font-size: .68rem; color: {C["txt_3"]};
    letter-spacing: .08em; text-transform: uppercase;
    font-weight: 600;
    margin-top: 2px;
}}
.sb-user {{
    margin: 14px 16px 10px;
    padding: 10px 12px;
    background: {C["border_lt"]};
    border-radius: 10px;
    display: flex; align-items: center; gap: 10px;
}}
.sb-user-avatar {{
    width: 34px; height: 34px;
    border-radius: 50%;
    color: white; font-weight: 700; font-size: .82rem;
    display: flex; align-items: center; justify-content: center;
}}
.sb-user-name {{
    font-size: .82rem; font-weight: 600; color: {C["txt"]};
    line-height: 1.1;
}}
.sb-user-role {{
    font-size: .65rem; color: {C["txt_3"]};
    margin-top: 1px;
    font-weight: 500;
}}
.sb-status {{
    margin: 0 16px 12px;
    padding: 6px 10px;
    background: {C["card_bg"]};
    border: 1px solid {C["border_lt"]};
    border-radius: 8px;
    font-size: .68rem;
    color: {C["txt_2"]};
    display: flex; align-items: center; gap: 6px;
}}
.sb-status .dot {{
    width: 6px; height: 6px; border-radius: 50%;
}}
.sb-status.online .dot {{ background: {C["success"]}; }}
.sb-status.offline .dot {{ background: {C["warning"]}; }}

/* Hide branding */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
</style>
"""

ROLE_GRADIENTS = {
    "Admin":     ("#7C3AED", "#EC4899"),
    "Yonetici":  ("#6366F1", "#7C3AED"),
    "Teknisyen": ("#14B8A6", "#06B6D4"),
    "Sakin":     ("#F59E0B", "#EC4899"),
}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


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


def hero_banner(title: str, subtitle: str = "", badge: str = "", icon: str = "✨",
                cta_text: str = ""):
    badge_html = f'<span class="hero-badge">{badge}</span>' if badge else ""
    cta_html = f'<div class="hero-cta">{cta_text} →</div>' if cta_text else ""
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-icon">{icon}</div>
        <div class="hero-text">
            <div class="hero-title">{title} {badge_html}</div>
            <div class="hero-sub">{subtitle}</div>
        </div>
        {cta_html}
    </div>
    """, unsafe_allow_html=True)


def feature_card(title: str, description: str, icon: str, color: str = "purple"):
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon {color}">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def action_group_title(text: str):
    st.markdown(f'<div class="action-group-title">{text}</div>', unsafe_allow_html=True)


def action_card(label: str, icon: str, color: str = "purple"):
    st.markdown(f"""
    <div class="action-card">
        <div class="action-card-icon {color}">{icon}</div>
        <div class="action-card-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def alert_row(text: str, level: str = "info"):
    icons = {"warning": "⚠", "danger": "🔴", "success": "✓", "info": "ℹ"}
    st.markdown(f"""
    <div class="alert-row {level}">
        <span class="alert-ico">{icons.get(level, "")}</span>
        <span style="flex:1">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def chart_card_start(title: str, subtitle: str = ""):
    sub = f'<div class="chart-card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-card-title">{title}</div>
        {sub}
    """, unsafe_allow_html=True)


def chart_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar navigation helpers ───────────────────────────────────────────────
def nav_section(title: str):
    st.sidebar.markdown(f'<div class="nav-section-title">{title}</div>',
                        unsafe_allow_html=True)


def nav_item(icon: str, label: str, key: str, is_active: bool) -> bool:
    """Sidebar nav item. Returns True if clicked (not active)."""
    if is_active:
        st.sidebar.markdown(
            f'<div class="nav-item-active"><span style="font-size:1rem">{icon}</span>'
            f'<span>{label}</span></div>',
            unsafe_allow_html=True,
        )
        return False
    return st.sidebar.button(
        f"{icon}   {label}",
        key=f"nav_{key}",
        use_container_width=True,
    )


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
    g1, g2 = ROLE_GRADIENTS.get(rol, ("#7C3AED", "#EC4899"))
    st.sidebar.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-avatar" style="background:linear-gradient(135deg,{g1} 0%,{g2} 100%)">
            {initials}
        </div>
        <div style="flex:1;min-width:0;">
            <div class="sb-user-name">{ad_soyad}</div>
            <div class="sb-user-role">{rol}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_status(connected: bool):
    cls = "online" if connected else "offline"
    txt = "Bulut bağlı" if connected else "Yerel mod"
    st.sidebar.markdown(f"""
    <div class="sb-status {cls}">
        <span class="dot"></span>
        <span>{txt}</span>
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "blue") -> str:
    return f'<span class="badge badge-{color}">{text}</span>'
