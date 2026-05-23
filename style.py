"""Xenia tarzı modern SaaS UI — koyu sidebar + indigo tema."""
import streamlit as st

C = {
    "page_bg":        "#F8FAFC",
    # Sidebar (koyu lacivert)
    "sidebar_bg":     "#0F172A",
    "sidebar_card":   "#1E293B",
    "sidebar_line":   "#1E293B",
    "sidebar_txt":    "#94A3B8",   # inactive nav
    "sidebar_txt_hi": "#F1F5F9",   # hover/active
    "sidebar_label":  "#64748B",   # section başlık
    # Indigo tema
    "primary":        "#4F46E5",   # indigo-600
    "primary_dk":     "#4338CA",
    "primary_br":     "#6366F1",
    "primary_lt":     "#EEF2FF",   # indigo-50
    "primary_bd":     "#C7D2FE",   # indigo-200
    "pink":           "#EC4899",
    "indigo":         "#6366F1",
    "teal":           "#14B8A6",
    "amber":          "#F59E0B",
    "rose":           "#F43F5E",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
    "txt":            "#0F172A",
    "txt_2":          "#475569",
    "txt_3":          "#94A3B8",
    "border":         "#E2E8F0",
    "border_lt":      "#EEF1F5",
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

/* ═════════════════ SIDEBAR (KOYU) ═════════════════ */
[data-testid="stSidebar"] > div:first-child {{
    background: {C["sidebar_bg"]};
    border-right: none;
    box-shadow: none;
    padding: 0;
}}
[data-testid="stSidebar"] .stMarkdown {{ color: {C["sidebar_txt_hi"]} !important; }}
[data-testid="stSidebar"] hr {{
    border-color: {C["sidebar_line"]} !important;
    margin: 10px 16px !important;
}}

/* SECTION LABEL */
.nav-section-title {{
    font-size: .66rem;
    font-weight: 700;
    color: {C["sidebar_label"]};
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: 16px 22px 6px;
}}

/* NAV ITEM butonları (on_click callback) */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {C["sidebar_txt"]} !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 9px 16px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 500 !important;
    font-size: .88rem !important;
    transition: background .15s ease, color .15s ease !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,.06) !important;
    color: {C["sidebar_txt_hi"]} !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {{
    box-shadow: none !important;
    outline: none !important;
    color: {C["sidebar_txt_hi"]} !important;
}}

/* AKTİF NAV — solid indigo pill (HTML div) */
.nav-item-active {{
    display: flex;
    align-items: center;
    gap: 11px;
    background: {C["primary"]};
    color: #FFFFFF;
    border-radius: 9px;
    padding: 9px 16px;
    margin: 1px 0;
    font-weight: 600;
    font-size: .88rem;
    box-shadow: 0 4px 12px rgba(79,70,229,.35);
}}

/* Date input (koyu) */
[data-testid="stSidebar"] [data-testid="stDateInput"] {{
    padding: 0 16px;
    margin: 6px 0;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] label {{
    color: {C["sidebar_label"]} !important;
    font-size: .66rem !important;
    font-weight: 700 !important;
    letter-spacing: .1em;
    text-transform: uppercase;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {{
    background: {C["sidebar_card"]} !important;
    border-color: #334155 !important;
    border-radius: 9px !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
    color: {C["sidebar_txt_hi"]} !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] svg {{
    fill: {C["sidebar_txt"]} !important;
}}

/* ÇIKIŞ butonu (key=logout_btn) */
.st-key-logout_btn button {{
    background: {C["sidebar_card"]} !important;
    border: 1px solid #334155 !important;
    color: {C["sidebar_txt_hi"]} !important;
    border-radius: 9px !important;
    margin: 4px 16px !important;
    width: calc(100% - 32px) !important;
    justify-content: center !important;
    text-align: center !important;
}}
.st-key-logout_btn button:hover {{
    background: #334155 !important;
    color: #FFFFFF !important;
}}

/* ═════════════════ SIDEBAR HEADER (BRAND + USER) ═════════════════ */
.sb-brand {{
    padding: 22px 22px 16px;
    border-bottom: 1px solid {C["sidebar_line"]};
}}
.sb-brand-row {{ display: flex; align-items: center; gap: 11px; }}
.sb-brand-logo {{
    width: 38px; height: 38px;
    border-radius: 10px;
    background: rgba(99,102,241,.18);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 1.15rem;
}}
.sb-brand-title {{
    font-size: 1.05rem; font-weight: 800; color: #FFFFFF;
    line-height: 1.15; letter-spacing: -.01em;
}}
.sb-user {{
    margin: 16px 18px 8px;
    display: flex; align-items: center; gap: 11px;
}}
.sb-user-avatar {{
    width: 40px; height: 40px;
    border-radius: 50%;
    color: white; font-weight: 700; font-size: .9rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
}}
.sb-user-name {{
    font-size: .82rem; font-weight: 600; color: {C["sidebar_txt_hi"]};
    line-height: 1.2; margin-bottom: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.sb-role-badge {{
    display: inline-block;
    background: {C["primary"]};
    color: #fff;
    font-size: .6rem; font-weight: 700;
    padding: 2px 10px;
    border-radius: 9999px;
    letter-spacing: .02em;
}}
.sb-status {{
    margin: 2px 18px 14px;
    font-size: .7rem;
    color: {C["sidebar_txt"]};
    display: flex; align-items: center; gap: 7px;
}}
.sb-status .dot {{
    width: 7px; height: 7px; border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(16,185,129,.18);
}}
.sb-status.online .dot {{ background: {C["success"]}; }}
.sb-status.offline .dot {{
    background: {C["warning"]};
    box-shadow: 0 0 0 3px rgba(245,158,11,.18);
}}

/* ═════════════════ PAGE HEAD ═════════════════ */
.page-head {{
    margin-bottom: 22px;
    padding-bottom: 18px;
    border-bottom: 1px solid {C["border_lt"]};
}}
.page-head-title {{
    font-size: 1.9rem;
    font-weight: 800;
    color: {C["txt"]};
    line-height: 1.15;
    margin: 0;
    letter-spacing: -.025em;
}}
.page-head-sub {{
    font-size: .9rem;
    color: {C["txt_2"]};
    margin-top: 8px;
    display: flex; align-items: center; gap: 12px;
}}
.page-head-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {C["primary_lt"]};
    color: {C["primary_dk"]};
    font-size: .66rem;
    font-weight: 700;
    padding: 4px 11px;
    border-radius: 7px;
    letter-spacing: .06em;
    text-transform: uppercase;
}}

/* ═════════════════ HERO BANNER ═════════════════ */
.hero-banner {{
    background: linear-gradient(120deg, {C["primary"]} 0%, {C["primary_br"]} 50%, {C["indigo"]} 100%);
    border-radius: 16px;
    padding: 22px 28px;
    color: white;
    display: flex; align-items: center; justify-content: space-between;
    gap: 20px; margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(79,70,229,.25);
    position: relative; overflow: hidden;
}}
.hero-banner::before {{
    content: ''; position: absolute; top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,.15) 0%, transparent 70%);
    pointer-events: none;
}}
.hero-icon {{
    width: 44px; height: 44px;
    background: rgba(255,255,255,.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
}}
.hero-text {{ flex: 1; z-index: 1; }}
.hero-title {{
    font-size: 1.15rem; font-weight: 700; color: white;
    margin-bottom: 4px; display: flex; align-items: center; gap: 10px;
}}
.hero-badge {{
    background: white; color: {C["primary_dk"]};
    font-size: .62rem; font-weight: 800;
    padding: 2px 8px; border-radius: 4px; letter-spacing: .06em;
}}
.hero-sub {{ font-size: .85rem; color: rgba(255,255,255,.85); }}
.hero-cta {{
    background: white; color: {C["primary_dk"]};
    padding: 8px 18px; border-radius: 10px;
    font-weight: 600; font-size: .85rem;
    flex-shrink: 0; z-index: 1; text-decoration: none;
    box-shadow: 0 4px 12px rgba(0,0,0,.1);
}}

/* ═════════════════ FEATURE CARDS ═════════════════ */
.feature-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 14px;
    padding: 20px 22px;
    transition: all .2s ease; height: 100%;
}}
.feature-card:hover {{
    border-color: {C["primary_bd"]};
    box-shadow: 0 8px 24px rgba(79,70,229,.1);
    transform: translateY(-2px);
}}
.feature-icon {{
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem; margin-bottom: 14px;
}}
.feature-icon.purple {{ background: #EEF2FF; color: #4F46E5; }}
.feature-icon.pink   {{ background: #FCE7F3; color: #DB2777; }}
.feature-icon.blue   {{ background: #EFF6FF; color: #2563EB; }}
.feature-icon.teal   {{ background: #CCFBF1; color: #0F766E; }}
.feature-title {{ font-size: 1rem; font-weight: 700; color: {C["txt"]}; margin-bottom: 4px; }}
.feature-desc {{ font-size: .82rem; color: {C["txt_2"]}; line-height: 1.5; }}

/* ═════════════════ ACTION GROUP ═════════════════ */
.action-group-title {{ font-size: .8rem; font-weight: 700; color: {C["txt"]}; margin: 0 0 10px; }}
.action-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 10px 14px; margin-bottom: 6px;
    display: flex; align-items: center; gap: 10px;
    transition: all .15s ease;
}}
.action-card:hover {{
    border-color: {C["primary_bd"]};
    background: {C["primary_lt"]};
    transform: translateX(2px);
}}
.action-card-icon {{
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: .95rem; flex-shrink: 0;
}}
.action-card-icon.purple {{ background: #EEF2FF; color: #4F46E5; }}
.action-card-icon.pink   {{ background: #FCE7F3; color: #DB2777; }}
.action-card-icon.blue   {{ background: #EFF6FF; color: #2563EB; }}
.action-card-icon.green  {{ background: #ECFDF5; color: #059669; }}
.action-card-icon.amber  {{ background: #FEF3C7; color: #B45309; }}
.action-card-icon.teal   {{ background: #CCFBF1; color: #0F766E; }}
.action-card-icon.rose   {{ background: #FFE4E6; color: #BE123C; }}
.action-card-icon.indigo {{ background: #EEF2FF; color: #4338CA; }}
.action-card-label {{ font-size: .85rem; font-weight: 500; color: {C["txt"]}; }}

/* ═════════════════ KPI CARDS ═════════════════ */
.kpi-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 14px;
    padding: 18px 20px;
    transition: all .2s ease; height: 100%;
}}
.kpi-card:hover {{
    border-color: {C["primary_bd"]};
    box-shadow: 0 4px 16px rgba(79,70,229,.08);
}}
.kpi-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }}
.kpi-label {{ font-size: .8rem; font-weight: 600; color: {C["txt_2"]}; }}
.kpi-icon-bg {{
    width: 40px; height: 40px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}}
.kpi-card.blue   .kpi-icon-bg {{ background: #EFF6FF; color: #2563EB; }}
.kpi-card.green  .kpi-icon-bg {{ background: #ECFDF5; color: #059669; }}
.kpi-card.orange .kpi-icon-bg {{ background: #FEF3C7; color: #B45309; }}
.kpi-card.red    .kpi-icon-bg {{ background: #FEE2E2; color: #DC2626; }}
.kpi-card.purple .kpi-icon-bg {{ background: #EEF2FF; color: #4F46E5; }}
.kpi-card.teal   .kpi-icon-bg {{ background: #CCFBF1; color: #0F766E; }}
.kpi-card.pink   .kpi-icon-bg {{ background: #FCE7F3; color: #DB2777; }}
.kpi-value {{ font-size: 2rem; font-weight: 800; color: {C["txt"]}; line-height: 1; letter-spacing: -.03em; }}
.kpi-delta {{ font-size: .78rem; color: {C["txt_3"]}; margin-top: 10px; font-weight: 600; }}
.kpi-delta.ok   {{ color: {C["success"]}; }}
.kpi-delta.warn {{ color: {C["warning"]}; }}
.kpi-delta.bad  {{ color: {C["danger"]}; }}

/* ═════════════════ CHART CARDS ═════════════════ */
.chart-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 14px;
    padding: 20px 22px 12px; margin-bottom: 14px;
}}
.chart-card-title {{ font-size: 1.05rem; font-weight: 700; color: {C["txt"]}; margin-bottom: 4px; }}
.chart-card-sub {{ font-size: .78rem; color: {C["txt_3"]}; margin-bottom: 14px; }}

/* ═════════════════ ALERT ROWS ═════════════════ */
.alert-row {{
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 12px; margin-bottom: 8px;
    font-size: .85rem; color: {C["txt"]};
    background: {C["card_bg"]}; border: 1px solid {C["border"]};
}}
.alert-row.warning {{ background: #FFFBEB; border-color: #FCD34D; }}
.alert-row.danger  {{ background: #FEF2F2; border-color: #FCA5A5; }}
.alert-row.success {{ background: #F0FDF4; border-color: #86EFAC; }}
.alert-row.info    {{ background: {C["primary_lt"]}; border-color: {C["primary_bd"]}; }}
.alert-row b {{ font-weight: 600; }}
.alert-ico {{
    width: 28px; height: 28px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: .9rem; flex-shrink: 0;
}}
.alert-row.warning .alert-ico {{ background: rgba(245,158,11,.2); }}
.alert-row.danger  .alert-ico {{ background: rgba(239,68,68,.15); }}
.alert-row.success .alert-ico {{ background: rgba(16,185,129,.15); }}
.alert-row.info    .alert-ico {{ background: rgba(79,70,229,.15); }}

/* ═════════════════ BADGES ═════════════════ */
.badge {{
    display: inline-block; padding: 3px 12px;
    border-radius: 9999px; font-size: .72rem; font-weight: 700;
}}
.badge-blue   {{ background: #DBEAFE; color: #1E40AF; }}
.badge-green  {{ background: #D1FAE5; color: #065F46; }}
.badge-orange {{ background: #FEF3C7; color: #92400E; }}
.badge-red    {{ background: #FEE2E2; color: #991B1B; }}
.badge-purple {{ background: #EDE9FE; color: #6D28D9; }}
.badge-gray   {{ background: #F1F5F9; color: #475569; }}

/* ═════════════════ FORMS / TABS ═════════════════ */
[data-testid="stForm"] {{
    background: {C["card_bg"]};
    padding: 24px; border-radius: 16px;
    border: 1px solid {C["border"]};
    box-shadow: 0 1px 3px rgba(15,23,42,.04);
}}
[data-testid="stExpander"] {{
    background: {C["card_bg"]} !important;
    border: 1px solid {C["border"]} !important;
    border-radius: 12px !important;
    box-shadow: none !important; overflow: hidden;
}}
[data-testid="stExpander"] summary {{ font-weight: 600 !important; padding: 12px 18px !important; }}

/* Tabs → segment kart görünümü (mockup) */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px; background: transparent;
    border-bottom: none; padding: 0; margin-bottom: 6px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px !important;
    border: 1.5px solid {C["border"]} !important;
    background: {C["card_bg"]} !important;
    font-size: .9rem !important; font-weight: 600 !important;
    padding: 10px 20px !important;
    color: {C["txt_2"]} !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    border-color: {C["primary_bd"]} !important;
    color: {C["primary"]} !important;
}}
.stTabs [aria-selected="true"] {{
    border-color: {C["primary"]} !important;
    color: {C["primary"]} !important;
    background: {C["primary_lt"]} !important;
    box-shadow: 0 1px 3px rgba(79,70,229,.12) !important;
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ═════════════════ RADIO → segment kontrol (sayfa anahtarı) ═════════════════ */
.main [data-testid="stRadio"] > div[role="radiogroup"] {{
    flex-direction: row; gap: 8px; flex-wrap: wrap;
}}
.main [data-testid="stRadio"] label {{
    border: 1.5px solid {C["border"]} !important;
    border-radius: 10px !important;
    padding: 9px 18px !important;
    background: {C["card_bg"]} !important;
    margin: 0 !important;
    cursor: pointer; transition: all .15s;
}}
.main [data-testid="stRadio"] label:hover {{
    border-color: {C["primary_bd"]} !important;
}}
.main [data-testid="stRadio"] label > div:first-child {{ display: none !important; }}
.main [data-testid="stRadio"] label:has(input:checked) {{
    border-color: {C["primary"]} !important;
    background: {C["primary_lt"]} !important;
}}
.main [data-testid="stRadio"] label:has(input:checked) p {{
    color: {C["primary"]} !important; font-weight: 600 !important;
}}
/* Form içi radio (Tamam/Sorunlu) → daire geri gelsin */
[data-testid="stForm"] [data-testid="stRadio"] label {{
    border: none !important; background: transparent !important;
    padding: 2px 10px 2px 0 !important;
}}
[data-testid="stForm"] [data-testid="stRadio"] label > div:first-child {{ display: flex !important; }}
[data-testid="stForm"] [data-testid="stRadio"] label:has(input:checked) {{
    background: transparent !important;
}}
[data-testid="stForm"] [data-testid="stRadio"] label:has(input:checked) p {{
    color: {C["txt"]} !important; font-weight: 500 !important;
}}

/* ═════════════════ BUTTONS (main) — solid indigo ═════════════════ */
.main .stButton > button,
[data-testid="stForm"] button {{
    border-radius: 10px !important;
    font-weight: 600 !important; font-size: .875rem !important;
    transition: all .15s !important; padding: 9px 18px !important;
}}
.main .stButton > button[kind="primary"],
[data-testid="stForm"] button[kind="primary"],
[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
    background: {C["primary"]} !important;
    border: none !important; color: white !important;
    box-shadow: 0 4px 12px rgba(79,70,229,.28) !important;
}}
.main .stButton > button[kind="primary"]:hover,
[data-testid="stForm"] button[kind="primary"]:hover,
[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {{
    background: {C["primary_dk"]} !important;
    box-shadow: 0 6px 20px rgba(79,70,229,.4) !important;
    transform: translateY(-1px) !important;
}}
.main .stButton > button[kind="secondary"] {{
    background: {C["card_bg"]} !important;
    border: 1px solid {C["border"]} !important;
    color: {C["txt_2"]} !important;
}}
.main .stButton > button[kind="secondary"]:hover {{
    border-color: {C["primary_bd"]} !important;
    color: {C["primary"]} !important;
}}

/* Metric */
[data-testid="stMetric"] {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 14px; padding: 16px 18px;
}}
[data-testid="stMetricLabel"] {{
    font-size: .8rem !important; color: {C["txt_2"]} !important; font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{ font-size: 1.85rem !important; font-weight: 800 !important; }}

/* Inputs */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] {{
    border-radius: 10px !important;
    border-color: {C["border"]} !important;
}}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"]:focus-within {{
    border-color: {C["primary"]} !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.1) !important;
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    border: 1px solid {C["border"]};
    overflow: hidden;
}}

/* ═════════════════ TOP-RIGHT HEADER (🔔 + ?) ═════════════════ */
.top-header {{
    position: fixed; top: 14px; right: 30px; z-index: 1000;
    display: flex; gap: 12px; align-items: center;
}}
.th-icon {{
    width: 40px; height: 40px; border-radius: 11px;
    background: #FFFFFF; border: 1px solid {C["border"]};
    display: flex; align-items: center; justify-content: center;
    font-size: 1.05rem; color: {C["txt_2"]};
    position: relative; cursor: pointer;
    box-shadow: 0 1px 3px rgba(15,23,42,.06);
    transition: all .15s;
}}
.th-icon:hover {{ border-color: {C["primary_bd"]}; color: {C["primary"]}; }}
.th-badge {{
    position: absolute; top: -6px; right: -6px;
    background: {C["danger"]}; color: #fff;
    font-size: .6rem; font-weight: 800;
    min-width: 17px; height: 17px; border-radius: 9999px;
    display: flex; align-items: center; justify-content: center;
    padding: 0 4px; border: 2px solid #fff;
}}

/* ═════════════════ DATA TABLE (renkli rozetli) ═════════════════ */
.panel-card {{
    background: {C["card_bg"]};
    border: 1px solid {C["border"]};
    border-radius: 16px;
    padding: 18px 22px 14px;
    box-shadow: 0 1px 3px rgba(15,23,42,.04);
    height: 100%;
}}
.panel-head {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px;
}}
.panel-title {{ font-size: 1.1rem; font-weight: 700; color: {C["txt"]}; }}
.panel-link {{ font-size: .78rem; font-weight: 600; color: {C["primary"]};
    background: {C["primary_lt"]}; padding: 5px 12px; border-radius: 8px; }}
.panel-foot {{
    text-align: center; padding: 12px 0 2px;
    font-size: .82rem; font-weight: 600; color: {C["primary"]};
}}

.data-table {{ width: 100%; border-collapse: collapse; font-size: .83rem; }}
.data-table thead th {{
    text-align: left; padding: 9px 12px;
    font-size: .66rem; font-weight: 700; color: {C["txt_3"]};
    text-transform: uppercase; letter-spacing: .04em;
    border-bottom: 1px solid {C["border"]};
}}
.data-table tbody td {{
    padding: 13px 12px; border-bottom: 1px solid {C["border_lt"]};
    color: {C["txt_2"]}; vertical-align: middle;
}}
.data-table tbody tr:last-child td {{ border-bottom: none; }}
.data-table tbody tr:hover {{ background: {C["page_bg"]}; }}
.id-cell {{ color: {C["primary"]}; font-weight: 600; white-space: nowrap; }}
.row-avatar {{
    width: 28px; height: 28px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    color: #fff; font-size: .62rem; font-weight: 700;
    margin-right: 8px; vertical-align: middle;
}}

/* Status badge (tablo) */
.st-badge {{ display: inline-block; padding: 4px 13px; border-radius: 9999px;
    font-size: .72rem; font-weight: 700; white-space: nowrap; }}
.st-acik   {{ background: #FEE2E2; color: #DC2626; }}
.st-devam  {{ background: #FEF3C7; color: #D97706; }}
.st-kapali {{ background: #D1FAE5; color: #059669; }}
.st-bekle  {{ background: #E0E7FF; color: #4338CA; }}
.st-iptal  {{ background: #F1F5F9; color: #64748B; }}

/* ═════════════════ LIST CARD (Bugün Kontroller) ═════════════════ */
.list-row {{
    display: flex; align-items: center; gap: 13px;
    padding: 12px 0; border-bottom: 1px solid {C["border_lt"]};
}}
.list-row:last-child {{ border-bottom: none; }}
.list-check {{
    width: 30px; height: 30px; border-radius: 50%;
    background: #D1FAE5; color: #059669;
    display: flex; align-items: center; justify-content: center;
    font-size: .85rem; flex-shrink: 0;
}}
.list-check.warn {{ background: #FEF3C7; color: #D97706; }}
.list-main {{ flex: 1; min-width: 0; }}
.list-title {{ font-size: .87rem; font-weight: 600; color: {C["txt"]}; }}
.list-sub {{ font-size: .74rem; color: {C["txt_3"]}; margin-top: 1px; }}
.list-time {{ font-size: .76rem; color: {C["txt_3"]}; font-weight: 500; white-space: nowrap; }}

/* KPI progress bar */
.kpi-progress {{
    height: 7px; background: {C["primary_lt"]};
    border-radius: 9999px; margin-top: 13px; overflow: hidden;
}}
.kpi-progress > span {{ display: block; height: 100%;
    background: {C["primary"]}; border-radius: 9999px; }}
.kpi-pill {{
    display: inline-block; margin-top: 10px;
    background: #FEE2E2; color: #DC2626;
    font-size: .72rem; font-weight: 700;
    padding: 2px 9px; border-radius: 7px;
}}
.kpi-pill.up {{ background: #FEE2E2; color: #DC2626; }}
.kpi-pill.down {{ background: #D1FAE5; color: #059669; }}

/* Hide Streamlit branding */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
</style>
"""

ROLE_GRADIENTS = {
    "Admin":     ("#4F46E5", "#6366F1"),
    "Yonetici":  ("#6366F1", "#8B5CF6"),
    "Teknisyen": ("#14B8A6", "#06B6D4"),
    "Sakin":     ("#F59E0B", "#EC4899"),
}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    pill_html = f'<span class="page-head-pill">{pill}</span>' if pill else ""
    icon_html = f'<span style="margin-right:10px">{icon}</span>' if icon else ""
    sub_html = ""
    if subtitle or pill:
        sub_html = f'<div class="page-head-sub"><span>{subtitle}</span>{pill_html}</div>'
    st.markdown(f"""
    <div class="page-head">
        <h1 class="page-head-title">{icon_html}{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label: str, value, icon: str = "", color: str = "blue",
             delta: str = "", delta_type: str = "", progress: int = None,
             pill: str = "", pill_dir: str = "up"):
    extra = ""
    if progress is not None:
        p = max(0, min(int(progress), 100))
        extra = (f'<div class="kpi-progress"><span style="width:{p}%"></span></div>'
                 f'<div class="kpi-delta" style="margin-top:6px">%{p}</div>')
    elif pill:
        extra = f'<div class="kpi-pill {pill_dir}">{pill}</div>'
    elif delta:
        extra = f'<div class="kpi-delta {delta_type}">{delta}</div>'
    st.markdown(f"""
    <div class="kpi-card {color}">
        <div class="kpi-top">
            <span class="kpi-label">{label}</span>
            <div class="kpi-icon-bg">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        {extra}
    </div>
    """, unsafe_allow_html=True)


def top_header(notif: int = 0):
    badge = f'<span class="th-badge">{notif if notif < 100 else "99+"}</span>' if notif else ""
    st.markdown(f"""
    <div class="top-header">
        <div class="th-icon" title="Bildirimler">🔔{badge}</div>
        <div class="th-icon" title="Yardım">?</div>
    </div>
    """, unsafe_allow_html=True)


_STATUS_MAP = {
    # Arıza / Talep
    "Açık": "st-acik", "Acik": "st-acik",
    "Devam Ediyor": "st-devam", "Devam": "st-devam",
    "Tamamlandı": "st-kapali", "Tamamlandi": "st-kapali",
    "Kapalı": "st-kapali", "Kapali": "st-kapali", "Çözüldü": "st-kapali",
    "Beklemede": "st-bekle", "Atandı": "st-bekle",
    "İptal": "st-iptal", "İptal Edildi": "st-iptal", "Kapatıldı": "st-iptal",
    # Ekipman / genel
    "Aktif": "st-kapali", "Pasif": "st-iptal",
    "Bakımda": "st-devam", "Arızalı": "st-acik", "Arizali": "st-acik",
    "Hurdaya Ayrıldı": "st-iptal", "Hurda": "st-iptal",
    # Daire
    "Dolu": "st-kapali", "Boş": "st-bekle", "Bos": "st-bekle",
    "Kira": "st-devam", "Satılık": "st-bekle",
}


def status_badge(durum: str) -> str:
    cls = _STATUS_MAP.get(str(durum), "st-bekle")
    return f'<span class="st-badge {cls}">{durum}</span>'


def avatar_chip(isim: str) -> str:
    if not str(isim).strip() or str(isim) in ("-", "nan"):
        return '<span style="color:#94A3B8">—</span>'
    initials = "".join(w[0].upper() for w in str(isim).split()[:2]) or "?"
    h = sum(ord(c) for c in str(isim)) % 5
    g = ["#4F46E5", "#0EA5E9", "#14B8A6", "#F59E0B", "#EC4899"][h]
    return (f'<span class="row-avatar" style="background:{g}">{initials}</span>'
            f'<span>{isim}</span>')


_PRIORITY_MAP = {
    "Kritik": ("st-acik", "Kritik"),
    "Yuksek": ("st-devam", "Yüksek"), "Yüksek": ("st-devam", "Yüksek"),
    "Normal": ("st-bekle", "Normal"),
    "Dusuk": ("st-kapali", "Düşük"), "Düşük": ("st-kapali", "Düşük"),
}


def priority_badge(p: str) -> str:
    cls, lbl = _PRIORITY_MAP.get(str(p).strip(), ("st-bekle", str(p)))
    return f'<span class="st-badge {cls}">{lbl}</span>'


_BOOL_TRUE = {"evet", "true", "1", "aktif", "açık", "var", "yes"}


def bool_badge(val, true_lbl: str = "Aktif", false_lbl: str = "Pasif") -> str:
    s = str(val).strip().lower()
    if s in _BOOL_TRUE:
        return f'<span class="st-badge st-kapali">{true_lbl}</span>'
    return f'<span class="st-badge st-iptal">{false_lbl}</span>'


def data_table(df, columns, status_cols=(), priority_cols=(), avatar_cols=(),
               id_cols=(), bool_cols=(), max_rows: int = 80, max_text: int = 46,
               empty_msg: str = "Kayıt bulunamadı"):
    """Renkli rozetli HTML tablo. columns: [(df_col, başlık), ...]"""
    if df is None or len(df) == 0:
        st.markdown(
            f'<div class="panel-card"><div style="text-align:center;'
            f'color:#94A3B8;padding:28px;font-size:.9rem">{empty_msg}</div></div>',
            unsafe_allow_html=True,
        )
        return
    head = "".join(f"<th>{h}</th>" for _, h in columns)
    safe = df.fillna("")
    body = ""
    for _, r in safe.head(max_rows).iterrows():
        cells = ""
        for col, _ in columns:
            val = r[col] if col in safe.columns else ""
            if col in status_cols:
                cells += f"<td>{status_badge(val)}</td>"
            elif col in priority_cols:
                cells += f"<td>{priority_badge(val)}</td>"
            elif col in bool_cols:
                cells += f"<td>{bool_badge(val)}</td>"
            elif col in avatar_cols:
                cells += f"<td>{avatar_chip(val)}</td>"
            elif col in id_cols:
                cells += f"<td class='id-cell'>{val}</td>"
            else:
                s = str(val)
                if len(s) > max_text:
                    s = s[:max_text - 1] + "…"
                cells += f"<td>{s}</td>"
        body += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div class="panel-card"><table class="data-table">'
        f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
        unsafe_allow_html=True,
    )


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
            <div class="sb-brand-title">Teknik Operasyon</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_user_card(ad_soyad: str, rol: str):
    initials = "".join(w[0].upper() for w in (ad_soyad or "?").split()[:2]) or "?"
    g1, g2 = ROLE_GRADIENTS.get(rol, ("#4F46E5", "#6366F1"))
    st.sidebar.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-avatar" style="background:linear-gradient(135deg,{g1} 0%,{g2} 100%)">
            {initials}
        </div>
        <div style="flex:1;min-width:0;">
            <div class="sb-user-name">{ad_soyad}</div>
            <span class="sb-role-badge">{rol}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_status(connected: bool):
    cls = "online" if connected else "offline"
    txt = "Google Sheets Bağlı" if connected else "Yerel Mod (CSV)"
    st.sidebar.markdown(f"""
    <div class="sb-status {cls}">
        <span class="dot"></span>
        <span>{txt}</span>
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "blue") -> str:
    return f'<span class="badge badge-{color}">{text}</span>'
