"""Ant Design Pro tarzı UI kit — Teknik Operasyon Sistemi."""
from __future__ import annotations
import html
import pandas as pd
import streamlit as st

# ── Ant Design Token Paleti ────────────────────────────────────────────────────
C = {
    # Primary — Ant Design Blue
    "primary":      "#1677FF",
    "primary_hover":"#4096FF",
    "primary_light":"#E6F4FF",
    "primary_dk":   "#0958D9",

    # Functional
    "success":      "#52C41A",
    "success_bg":   "#F6FFED",
    "success_bd":   "#B7EB8F",
    "warning":      "#FAAD14",
    "warning_bg":   "#FFFBE6",
    "warning_bd":   "#FFE58F",
    "error":        "#FF4D4F",
    "error_bg":     "#FFF2F0",
    "error_bd":     "#FFCCC7",
    "processing":   "#1677FF",

    # Neutral
    "text":         "rgba(0,0,0,0.88)",
    "text_2":       "rgba(0,0,0,0.45)",
    "text_3":       "rgba(0,0,0,0.25)",
    "border":       "#D9D9D9",
    "border_2":     "#F0F0F0",
    "bg":           "#F5F7FA",
    "bg_card":      "#FFFFFF",
    "bg_hover":     "#FAFAFA",

    # Sidebar (Ant Design Pro Dark)
    "sidebar_bg":   "#001529",
    "sidebar_item": "rgba(255,255,255,0.65)",
    "sidebar_act":  "#1677FF",
}

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  font-size: 14px !important;
}}
.stApp {{ background: {C['bg']}; }}
.block-container {{
  padding-top: 68px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  max-width: 1440px !important;
}}

/* ── Sidebar — Ant Pro Dark ───────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background: {C['sidebar_bg']} !important;
  width: 240px !important;
  border-right: none !important;
}}
section[data-testid="stSidebar"] * {{ color: {C['sidebar_item']}; }}
section[data-testid="stSidebar"] .stButton button {{
  background: transparent !important;
  color: {C['sidebar_item']} !important;
  border: none !important;
  text-align: left !important;
  justify-content: flex-start !important;
  height: 40px !important;
  border-radius: 0 !important;
  padding: 0 16px !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  width: 100% !important;
  transition: all 0.2s !important;
}}
section[data-testid="stSidebar"] .stButton button:hover {{
  background: rgba(255,255,255,0.08) !important;
  color: #fff !important;
}}
section[data-testid="stSidebar"] hr {{
  border-color: rgba(255,255,255,0.08) !important;
  margin: 6px 0 !important;
}}

/* ── Top Header ───────────────────────────────────────────────────────────── */
[data-testid="stHeader"] {{
  background: rgba(255,255,255,0.95) !important;
  backdrop-filter: blur(8px) !important;
  border-bottom: 1px solid {C['border_2']} !important;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08) !important;
}}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
button[kind="primary"], .stButton button[kind="primary"] {{
  background: {C['primary']} !important;
  border-color: {C['primary']} !important;
  border-radius: 6px !important;
  font-weight: 500 !important;
  box-shadow: 0 2px 0 rgba(5,145,255,.1) !important;
  transition: all 0.2s !important;
}}
button[kind="primary"]:hover, .stButton button[kind="primary"]:hover {{
  background: {C['primary_hover']} !important;
  border-color: {C['primary_hover']} !important;
}}

/* ── Form Inputs ──────────────────────────────────────────────────────────── */
.stTextInput input,
.stSelectbox [data-baseweb="select"],
.stDateInput input,
.stNumberInput input,
.stTextArea textarea {{
  border-radius: 6px !important;
  border-color: {C['border']} !important;
  transition: border-color 0.2s !important;
}}
.stTextInput input:focus,
.stTextArea textarea:focus {{
  border-color: {C['primary']} !important;
  box-shadow: 0 0 0 2px rgba(22,119,255,0.1) !important;
}}

/* ── Metrics ──────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
  background: {C['bg_card']};
  border: 1px solid {C['border_2']};
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}}

/* ── Top Bar (custom) ─────────────────────────────────────────────────────── */
.pro-topbar {{
  position: fixed; top: 0; left: 240px; right: 0;
  height: 52px; z-index: 999;
  background: #fff;
  border-bottom: 1px solid {C['border_2']};
  display: flex; align-items: center;
  justify-content: flex-end;
  padding: 0 24px; gap: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.06);
}}
.pro-icon-btn {{
  width: 32px; height: 32px;
  border-radius: 6px;
  border: 1px solid {C['border_2']};
  display: flex; align-items: center; justify-content: center;
  color: {C['text_2']}; background: #fff;
  position: relative; font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}}
.pro-icon-btn:hover {{ border-color: {C['primary']}; color: {C['primary']}; }}
.pro-badge-count {{
  position: absolute; top: -6px; right: -6px;
  min-width: 17px; height: 17px; padding: 0 4px;
  border-radius: 999px; background: {C['error']};
  color: #fff; font-size: 11px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid white;
}}

/* ── Sidebar Brand ────────────────────────────────────────────────────────── */
.brand {{
  display: flex; align-items: center; gap: 10px;
  color: white; font-weight: 700; font-size: 16px;
  padding: 16px 16px 12px; letter-spacing: -.01em;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  margin-bottom: 8px;
}}
.brand-icon {{
  width: 32px; height: 32px; border-radius: 6px;
  background: {C['primary']};
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}}
.brand-name {{ color: #fff; font-size: 15px; font-weight: 700; }}
.brand-sub {{ color: rgba(255,255,255,0.45); font-size: 11px; }}

/* ── Sidebar User Card ────────────────────────────────────────────────────── */
.side-user {{
  margin: 0 8px 8px;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  display: flex; gap: 10px; align-items: center;
}}
.side-avatar {{
  width: 34px; height: 34px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 13px;
  background: {C['primary']};
  flex-shrink: 0;
}}
.side-user-name {{ color: rgba(255,255,255,0.88); font-weight: 600; font-size: 13px; line-height: 1.3; }}
.side-role {{
  display: inline-block; margin-top: 2px;
  padding: 1px 6px; border-radius: 4px;
  background: rgba(22,119,255,0.2);
  color: {C['primary_hover']} !important;
  font-size: 10px; font-weight: 600; letter-spacing: .02em;
}}

/* ── Sidebar Status ───────────────────────────────────────────────────────── */
.side-status {{
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: rgba(255,255,255,0.35);
  padding: 4px 16px 8px;
}}
.side-status .dot {{
  width: 6px; height: 6px; border-radius: 999px;
  background: {C['success']};
  box-shadow: 0 0 0 3px rgba(82,196,26,0.15);
}}
.side-status.offline .dot {{
  background: {C['warning']};
  box-shadow: 0 0 0 3px rgba(250,173,20,0.15);
}}

/* ── Nav Section Label ────────────────────────────────────────────────────── */
.nav-section-label {{
  margin: 16px 16px 4px;
  color: rgba(255,255,255,0.25);
  font-size: 11px; font-weight: 600;
  letter-spacing: .08em; text-transform: uppercase;
}}

/* ── Nav Active Item ──────────────────────────────────────────────────────── */
.nav-active {{
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  background: {C['primary']} !important;
  color: #fff !important;
  font-weight: 600; font-size: 14px;
  position: relative;
}}

/* ── Page Header ──────────────────────────────────────────────────────────── */
.page-head {{
  display: flex; align-items: flex-start;
  justify-content: space-between;
  margin: 0 0 20px; padding-bottom: 16px;
  border-bottom: 1px solid {C['border_2']};
}}
.page-title {{
  font-size: 22px; font-weight: 700;
  color: {C['text']}; letter-spacing: -.02em; margin: 0;
}}
.page-sub {{ margin-top: 4px; color: {C['text_2']}; font-size: 13px; }}
.pill {{
  display: inline-flex; align-items: center;
  border-radius: 4px; padding: 2px 8px;
  font-size: 11px; font-weight: 600;
  background: {C['primary_light']};
  color: {C['primary']};
  margin-left: 10px;
}}

/* ── Card ─────────────────────────────────────────────────────────────────── */
.card {{
  background: {C['bg_card']};
  border: 1px solid {C['border_2']};
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: 0 4px 12px rgba(0,21,41,0.08); }}
.card-title {{
  font-size: 15px; font-weight: 600;
  color: {C['text']}; margin-bottom: 4px;
}}
.card-sub {{ color: {C['text_2']}; font-size: 13px; }}

/* ── KPI Card ─────────────────────────────────────────────────────────────── */
.kpi {{
  min-height: 120px;
  display: flex; flex-direction: column; justify-content: space-between;
}}
.kpi-top {{
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 12px;
}}
.kpi-label {{ color: {C['text_2']}; font-size: 13px; font-weight: 500; }}
.kpi-icon {{
  width: 40px; height: 40px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  background: {C['primary_light']};
}}
.kpi-value {{
  color: {C['text']}; font-size: 30px;
  font-weight: 700; letter-spacing: -.03em;
  margin-top: 8px;
}}
.progress-track {{
  width: 100%; height: 6px; border-radius: 999px;
  background: {C['border_2']}; overflow: hidden;
  margin-top: 8px;
}}
.progress-fill {{
  height: 100%; border-radius: 999px;
  background: {C['primary']};
  transition: width 0.4s ease;
}}
.delta, .small-pill {{
  display: inline-flex; align-items: center;
  border-radius: 4px; padding: 2px 6px;
  font-size: 12px; font-weight: 600;
}}
.delta.up {{ color: {C['error']}; background: {C['error_bg']}; }}
.delta.good {{ color: {C['success']}; background: {C['success_bg']}; }}

/* ── Status / Tag ─────────────────────────────────────────────────────────── */
.status {{
  display: inline-flex; align-items: center; gap: 5px;
  border-radius: 4px; padding: 2px 8px;
  font-size: 12px; font-weight: 500;
  white-space: nowrap; line-height: 20px;
  border: 1px solid transparent;
}}
/* Ant Design tag renk sistemi */
.st-acik    {{ background:{C['error_bg']};   border-color:{C['error_bd']};   color:{C['error']};   }}
.st-devam   {{ background:{C['warning_bg']}; border-color:{C['warning_bd']}; color:#D48806;        }}
.st-kapali  {{ background:{C['success_bg']}; border-color:{C['success_bd']}; color:#389E0D;        }}
.st-bekle   {{ background:{C['primary_light']}; border-color:#91CAFF;        color:{C['primary']}; }}
.st-iptal   {{ background:#FAFAFA;           border-color:{C['border']};     color:{C['text_2']};  }}

/* Status nokta (badge dot) */
.status::before {{
  content:''; width:6px; height:6px; border-radius:50%;
  display:inline-block; background:currentColor; opacity:.85;
}}

/* ── Avatar Chip ──────────────────────────────────────────────────────────── */
.avatar-chip {{
  display: inline-flex; align-items: center; gap: 6px;
  font-weight: 500; color: {C['text']};
}}
.avatar-mini {{
  width: 24px; height: 24px; border-radius: 50%;
  color: white; font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}}

/* ── Pro Table ────────────────────────────────────────────────────────────── */
.pro-table-wrap {{
  background: {C['bg_card']};
  border: 1px solid {C['border_2']};
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}}
.pro-table {{
  width: 100%; border-collapse: collapse;
  font-size: 13px; color: {C['text']};
}}
.pro-table th {{
  text-align: left; padding: 12px 16px;
  color: {C['text_2']}; font-size: 12px;
  font-weight: 600; text-transform: uppercase;
  letter-spacing: .04em;
  background: {C['bg_hover']};
  border-bottom: 1px solid {C['border_2']};
}}
.pro-table td {{
  padding: 12px 16px;
  border-bottom: 1px solid {C['border_2']};
  vertical-align: middle;
}}
.pro-table tr:last-child td {{ border-bottom: 0; }}
.pro-table tr:hover td {{ background: #E6F4FF40; }}
.id-link {{
  color: {C['primary']}; font-weight: 600;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}}

/* ── Empty State ──────────────────────────────────────────────────────────── */
.empty {{
  background: {C['bg_card']};
  border: 1px dashed {C['border']};
  border-radius: 8px; padding: 40px;
  text-align: center; color: {C['text_2']};
  font-size: 14px;
}}
.empty::before {{
  content: '📭';
  display: block; font-size: 32px; margin-bottom: 8px;
}}

/* ── List Row ─────────────────────────────────────────────────────────────── */
.list-row {{
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid {C['border_2']};
}}
.list-row:last-child {{ border-bottom: 0; }}
.list-main {{ display: flex; align-items: center; gap: 10px; }}
.check-dot {{
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: {C['success_bg']};
  color: {C['success']}; font-weight: 700; font-size: 13px;
  flex-shrink: 0;
}}
.muted {{ color: {C['text_2']}; font-size: 12px; }}

/* ── Form Card ────────────────────────────────────────────────────────────── */
.form-card {{
  background: {C['bg_card']};
  border: 1px solid {C['border_2']};
  border-radius: 8px; padding: 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}}

/* ── Asset Card ───────────────────────────────────────────────────────────── */
.asset-card {{
  background: {C['bg_card']};
  border: 1px solid {C['border_2']};
  border-radius: 8px; padding: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: all 0.2s;
}}
.asset-card:hover {{
  border-color: {C['primary']};
  box-shadow: 0 4px 12px rgba(22,119,255,0.1);
}}
.asset-head {{
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 10px;
}}
.asset-name {{ font-weight: 600; color: {C['text']}; font-size: 14px; }}
.asset-meta {{ margin-top: 3px; color: {C['text_2']}; font-size: 12px; }}
.metric-split {{
  display: grid; grid-template-columns: repeat(2,1fr);
  gap: 8px; margin-top: 12px;
}}
.mini-stat {{
  background: {C['bg']};
  border: 1px solid {C['border_2']};
  border-radius: 6px; padding: 8px 10px;
}}
.mini-stat b {{ display: block; font-size: 15px; color: {C['text']}; font-weight: 700; }}
.mini-stat span {{ color: {C['text_2']}; font-size: 11px; }}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr.soft {{ border: 0; border-top: 1px solid {C['border_2']}; margin: 16px 0; }}

/* ── Tabs Card (radio pills) ─────────────────────────────────────────────── */
.tabs-card {{
  border: 1px solid {C['border_2']};
  border-radius: 6px; background: {C['bg_card']};
  padding: 4px; display: inline-flex; gap: 4px;
}}
.tab-active, .tab-passive {{
  border-radius: 4px; padding: 6px 14px;
  font-size: 13px; font-weight: 500;
  display: inline-flex; gap: 6px; align-items: center;
  cursor: pointer;
}}
.tab-active {{ background: {C['primary']}; color: #fff; }}
.tab-passive {{ color: {C['text_2']}; }}
.tab-passive:hover {{ color: {C['primary']}; background: {C['primary_light']}; }}

/* ── collapsedControl ─────────────────────────────────────────────────────── */
[data-testid="collapsedControl"] {{
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  z-index: 1200 !important;
  background: {C['primary']} !important;
  border-radius: 0 8px 8px 0 !important;
  width: 28px !important;
  min-height: 52px !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 2px 0 8px rgba(22,119,255,.4) !important;
}}
[data-testid="collapsedControl"] svg {{ fill: white !important; stroke: white !important; }}
[data-testid="collapsedControl"] button {{
  background: transparent !important; border: none !important;
  color: white !important; width: 100% !important; height: 100% !important;
}}

/* ── Mobil Responsive ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
  .pro-topbar {{ display: none !important; }}
  [data-testid="stHeader"] {{
    background: {C['sidebar_bg']} !important;
    position: fixed !important; top: 0 !important;
    left: 0 !important; right: 0 !important;
    height: 52px !important; z-index: 999 !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
  }}
  [data-testid="stHeader"] button svg,
  [data-testid="stHeader"] button svg path {{
    fill: rgba(255,255,255,0.65) !important;
    stroke: rgba(255,255,255,0.65) !important;
  }}
  .block-container {{
    padding-top: 64px !important;
    padding-left: .75rem !important;
    padding-right: .75rem !important;
  }}
  section[data-testid="stSidebar"] {{
    width: 80vw !important; max-width: 280px !important;
  }}
  .pro-table-wrap {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch !important; }}
  .pro-table {{ font-size: 12px !important; }}
  .pro-table th, .pro-table td {{ padding: 9px 10px !important; }}
  .kpi-value {{ font-size: 24px !important; }}
  .page-title {{ font-size: 20px !important; }}
  .kpi {{ min-height: 90px !important; }}
}}
"""

ROLE_GRADIENTS = {
    "Admin":     (C["primary_dk"], C["primary"]),
    "Yonetici":  ("#0958D9", "#1677FF"),
    "Teknisyen": ("#096DD9", "#40A9FF"),
    "Sakin":     ("#D48806", "#FAAD14"),
}

# Rol → ikon renk map'i
ROLE_ICON_COLORS = {
    "Admin": C["primary"],
    "Yonetici": "#0958D9",
    "Teknisyen": "#096DD9",
    "Sakin": C["warning"],
}

def esc(x) -> str:
    return html.escape("" if x is None else str(x))

def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ── Top Bar ────────────────────────────────────────────────────────────────────
def top_header(notif: int = 0):
    b = f'<span class="pro-badge-count">{notif if notif < 100 else "99+"}</span>' if notif else ""
    st.markdown(
        f'<div class="pro-topbar">'
        f'<div class="pro-icon-btn">🔔{b}</div>'
        f'<div class="pro-icon-btn">❓</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Section Header ─────────────────────────────────────────────────────────────
def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    pill_html = f'<span class="pill">{esc(pill)}</span>' if pill else ""
    sub_html = f'<div class="page-sub">{esc(subtitle)}{pill_html}</div>' if subtitle or pill else ""
    st.markdown(
        f'<div class="page-head">'
        f'<div><h1 class="page-title">{esc(icon) + " " if icon else ""}{esc(title)}</h1>{sub_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Radio Pills ────────────────────────────────────────────────────────────────
def radio_pills(items: list[str], active: int = 0):
    html_items = "".join(
        f'<div class="{"tab-active" if i == active else "tab-passive"}">{esc(t)}</div>'
        for i, t in enumerate(items)
    )
    st.markdown(f'<div class="tabs-card">{html_items}</div><hr class="soft">', unsafe_allow_html=True)

# ── KPI Card ───────────────────────────────────────────────────────────────────
def kpi_card(label: str, value, icon: str = "", color: str = "blue",
             delta: str = "", delta_type: str = "",
             progress: int | None = None, pill: str = ""):
    extra = ""
    if progress is not None:
        p = max(0, min(int(progress), 100))
        extra = (f'<div class="progress-track">'
                 f'<div class="progress-fill" style="width:{p}%"></div></div>'
                 f'<div class="muted" style="margin-top:4px">%{p}</div>')
    elif delta:
        cls = "good" if delta_type == "good" else "up"
        extra = f'<span class="delta {cls}">{esc(delta)}</span>'
    elif pill:
        extra = f'<span class="small-pill st-bekle">{esc(pill)}</span>'

    # İkon arka plan rengini türe göre ayarla
    icon_colors = {
        "blue": (C["primary_light"], C["primary"]),
        "green": (C["success_bg"], C["success"]),
        "orange": (C["warning_bg"], C["warning"]),
        "red": (C["error_bg"], C["error"]),
    }
    bg, fg = icon_colors.get(color, (C["primary_light"], C["primary"]))
    icon_html = (f'<div class="kpi-icon" style="background:{bg}">'
                 f'<span style="filter:none">{esc(icon)}</span></div>') if icon else ""

    st.markdown(
        f'<div class="card kpi">'
        f'<div class="kpi-top"><div class="kpi-label">{esc(label)}</div>{icon_html}</div>'
        f'<div class="kpi-value">{esc(value)}</div>'
        f'{extra}</div>',
        unsafe_allow_html=True,
    )

# ── Simple Card Title ──────────────────────────────────────────────────────────
def card(title: str, subtitle: str = ""):
    sub_html = f'<div class="card-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="card-title">{esc(title)}</div>{sub_html}', unsafe_allow_html=True)

# ── Sidebar Components ─────────────────────────────────────────────────────────
def sidebar_brand():
    st.sidebar.markdown(
        '<div class="brand">'
        '<div class="brand-icon">🏢</div>'
        '<div><div class="brand-name">Teknik Takip</div>'
        '<div class="brand-sub">Pro v2.0</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

def sidebar_user_card(ad_soyad: str, rol: str):
    initials = "".join(w[0].upper() for w in (ad_soyad or "?").split()[:2]) or "?"
    color = ROLE_ICON_COLORS.get(rol, C["primary"])
    st.sidebar.markdown(
        f'<div class="side-user">'
        f'<div class="side-avatar" style="background:{color}">{esc(initials)}</div>'
        f'<div><div class="side-user-name">{esc(ad_soyad or "Kullanıcı")}</div>'
        f'<div class="side-role">{esc(rol)}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def sidebar_status(connected: bool):
    cls = "" if connected else "offline"
    txt = "Google Sheets Bağlı" if connected else "Yerel Mod (CSV)"
    st.sidebar.markdown(
        f'<div class="side-status {cls}"><span class="dot"></span>{esc(txt)}</div>',
        unsafe_allow_html=True,
    )

def nav_section(title: str):
    st.sidebar.markdown(
        f'<div class="nav-section-label">{esc(title)}</div>',
        unsafe_allow_html=True,
    )

def nav_item_active(icon: str, label: str):
    st.sidebar.markdown(
        f'<div class="nav-active"><span>{esc(icon)}</span><span>{esc(label)}</span></div>',
        unsafe_allow_html=True,
    )

# ── Badge / Status ─────────────────────────────────────────────────────────────
def badge(text: str, color: str = "blue") -> str:
    mp = {
        "red": "st-acik", "orange": "st-devam", "green": "st-kapali",
        "blue": "st-bekle", "gray": "st-iptal", "purple": "st-bekle",
    }
    return f'<span class="status {mp.get(color, "st-bekle")}">{esc(text)}</span>'

_STATUS_MAP = {
    "Açık": "st-acik", "Acik": "st-acik",
    "Devam Ediyor": "st-devam", "Devam": "st-devam",
    "Atandı": "st-bekle", "Beklemede": "st-bekle", "Onay Bekliyor": "st-bekle",
    "Tamamlandı": "st-kapali", "Kapalı": "st-kapali", "Kapali": "st-kapali",
    "Çözüldü": "st-kapali", "Onaylandı": "st-kapali", "Teslim Edildi": "st-kapali",
    "İptal": "st-iptal", "İptal Edildi": "st-iptal", "Reddedildi": "st-iptal",
    "Aktif": "st-kapali", "Pasif": "st-iptal", "Bakımda": "st-devam",
    "Arızalı": "st-acik", "Arizali": "st-acik", "Hurda": "st-iptal",
    "Kritik": "st-acik",
    "Yüksek": "st-devam", "Yuksek": "st-devam",
    "Normal": "st-bekle",
    "Düşük": "st-kapali", "Dusuk": "st-kapali",
    "Bekliyor": "st-bekle", "İade": "st-iptal",
}

def status_badge(durum: str) -> str:
    cls = _STATUS_MAP.get(str(durum), "st-bekle")
    return f'<span class="status {cls}">{esc(durum)}</span>'

def priority_badge(p: str) -> str:
    return status_badge(p)

def bool_badge(val, true_lbl: str = "Aktif", false_lbl: str = "Pasif") -> str:
    is_true = str(val).strip().lower() in {"evet", "true", "1", "aktif", "yes", "var"}
    return status_badge(true_lbl if is_true else false_lbl)

def avatar_chip(isim: str) -> str:
    if not str(isim).strip() or str(isim) in ("-", "nan", "None"):
        return "—"
    initials = "".join(w[0].upper() for w in str(isim).split()[:2]) or "?"
    colors = ["#1677FF", "#52C41A", "#FAAD14", "#FF4D4F", "#722ED1", "#13C2C2"]
    c = colors[sum(map(ord, str(isim))) % len(colors)]
    return (f'<span class="avatar-chip">'
            f'<span class="avatar-mini" style="background:{c}">{esc(initials)}</span>'
            f'{esc(isim)}</span>')

# ── Data Table ─────────────────────────────────────────────────────────────────
def data_table(
    df: pd.DataFrame,
    columns,
    status_cols=(),
    priority_cols=(),
    avatar_cols=(),
    id_cols=(),
    bool_cols=(),
    max_rows: int = 100,
    max_text: int = 60,
    empty_msg: str = "Kayıt bulunamadı",
):
    if df is None or df.empty:
        st.markdown(f'<div class="empty">{esc(empty_msg)}</div>', unsafe_allow_html=True)
        return

    safe = df.fillna("")
    head = "".join(f"<th>{esc(h)}</th>" for _, h in columns)
    body = ""

    for _, r in safe.head(max_rows).iterrows():
        cells = ""
        for col, _ in columns:
            val = r[col] if col in safe.columns else ""
            if col in status_cols:
                v = status_badge(val)
            elif col in priority_cols:
                v = priority_badge(val)
            elif col in bool_cols:
                v = bool_badge(val)
            elif col in avatar_cols:
                v = avatar_chip(val)
            elif col in id_cols:
                v = f'<span class="id-link">{esc(val)}</span>'
            else:
                s = str(val)
                v = esc(s if len(s) <= max_text else s[:max_text - 1] + "…")
            cells += f"<td>{v}</td>"
        body += f"<tr>{cells}</tr>"

    st.markdown(
        f'<div class="pro-table-wrap">'
        f'<table class="pro-table">'
        f'<thead><tr>{head}</tr></thead>'
        f'<tbody>{body}</tbody>'
        f'</table></div>',
        unsafe_allow_html=True,
    )

# ── Utility Components ─────────────────────────────────────────────────────────
def stat_pair(label: str, value: str) -> str:
    return f'<div class="mini-stat"><b>{esc(value)}</b><span>{esc(label)}</span></div>'

def asset_card(title: str, meta: str, status: str,
               left_label: str, left_val: str,
               right_label: str, right_val: str):
    st.markdown(
        f'<div class="asset-card">'
        f'<div class="asset-head">'
        f'<div><div class="asset-name">{esc(title)}</div>'
        f'<div class="asset-meta">{esc(meta)}</div></div>'
        f'{status_badge(status)}</div>'
        f'<div class="metric-split">'
        f'{stat_pair(left_label, left_val)}{stat_pair(right_label, right_val)}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

def list_row(title: str, subtitle: str, right: str = "", ok: bool = True):
    dot = "✓" if ok else "!"
    st.markdown(
        f'<div class="list-row">'
        f'<div class="list-main">'
        f'<div class="check-dot">{dot}</div>'
        f'<div><b>{esc(title)}</b><div class="muted">{esc(subtitle)}</div></div>'
        f'</div>'
        f'<div class="muted">{esc(right)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def alert_row(text: str, level: str = "info"):
    st.info(text)

def hero_banner(title: str, subtitle: str = "", badge: str = "",
                icon: str = "✨", cta_text: str = ""):
    st.markdown(
        f'<div class="card">'
        f'<div style="font-size:28px;margin-bottom:8px">{esc(icon)}</div>'
        f'<h2 style="margin:0 0 4px;color:{C["text"]};font-size:20px;font-weight:700">'
        f'{esc(title)} {badge}</h2>'
        f'<div class="muted">{esc(subtitle)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def feature_card(title: str, description: str, icon: str, color: str = "blue"):
    bg = {"blue": C["primary_light"], "green": C["success_bg"],
          "orange": C["warning_bg"], "red": C["error_bg"]}.get(color, C["primary_light"])
    st.markdown(
        f'<div class="card">'
        f'<div class="kpi-icon" style="background:{bg};margin-bottom:10px">{esc(icon)}</div>'
        f'<div class="card-title">{esc(title)}</div>'
        f'<div class="card-sub">{esc(description)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def action_group_title(text: str):
    st.markdown(f'### {text}')

def action_card(label: str, icon: str, color: str = "blue"):
    st.markdown(
        f'<div class="card">'
        f'<b style="color:{C["text"]}">{esc(icon)} {esc(label)}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

def chart_card_start(title: str, subtitle: str = ""):
    sub_html = f'<div class="card-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="card"><div class="card-title">{esc(title)}</div>{sub_html}',
        unsafe_allow_html=True,
    )

def chart_card_end():
    st.markdown('</div>', unsafe_allow_html=True)
