"""Teknik Operasyon Sistemi — premium Xenia esintili Streamlit UI kiti.

Bu dosya mevcut modüllerle geriye dönük uyumludur:
- inject_css, section_header, kpi_card, top_header
- data_table, status_badge, priority_badge, avatar_chip
- sidebar_brand, sidebar_user_card, sidebar_status, nav_section, nav_item
"""
from __future__ import annotations

import html
from typing import Iterable, Sequence

import streamlit as st

C = {
    "page_bg": "#F8FAFC",
    "sidebar_bg": "#0F172A",
    "sidebar_card": "#111C31",
    "sidebar_card_2": "#1E293B",
    "sidebar_line": "#1E293B",
    "sidebar_txt": "#94A3B8",
    "sidebar_txt_hi": "#F8FAFC",
    "sidebar_label": "#64748B",
    "primary": "#6366F1",
    "primary_dk": "#4F46E5",
    "primary_lt": "#EEF2FF",
    "primary_bd": "#C7D2FE",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "blue": "#3B82F6",
    "teal": "#14B8A6",
    "txt": "#0F172A",
    "txt_2": "#475569",
    "txt_3": "#94A3B8",
    "border": "#E2E8F0",
    "border_lt": "#EEF2F7",
    "card_bg": "#FFFFFF",
}

ROLE_GRADIENTS = {
    "Admin": ("#4F46E5", "#6366F1"),
    "Yonetici": ("#6366F1", "#8B5CF6"),
    "Yönetici": ("#6366F1", "#8B5CF6"),
    "Teknisyen": ("#14B8A6", "#06B6D4"),
    "Sakin": ("#F59E0B", "#EC4899"),
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --tos-bg: {C['page_bg']};
  --tos-sidebar: {C['sidebar_bg']};
  --tos-primary: {C['primary']};
  --tos-primary-dark: {C['primary_dk']};
  --tos-primary-light: {C['primary_lt']};
  --tos-text: {C['txt']};
  --tos-muted: {C['txt_2']};
  --tos-border: {C['border']};
  --tos-card: {C['card_bg']};
}}

html, body, [class*="css"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

.stApp {{ background: var(--tos-bg) !important; color: var(--tos-text); }}
.block-container {{
  padding-top: 78px !important;
  padding-left: 2.1rem !important;
  padding-right: 2.1rem !important;
  max-width: 1520px !important;
}}

/* Streamlit header/menu temizliği */
[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; }}
#MainMenu, footer {{ visibility: hidden; }}

/* Fixed top bar */
.tos-topbar {{
  position: fixed;
  top: 0;
  left: 240px;
  right: 0;
  height: 56px;
  background: rgba(255,255,255,.96);
  border-bottom: 1px solid rgba(226,232,240,.95);
  box-shadow: 0 1px 3px rgba(15,23,42,.08);
  backdrop-filter: blur(10px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  padding: 0 24px;
}}
.tos-topbar-search {{
  margin-right: auto;
  max-width: 420px;
  width: 38vw;
  height: 36px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
  color: #64748B;
  border-radius: 999px;
  display:flex;
  align-items:center;
  padding: 0 14px;
  font-size: 13px;
}}
.tos-topbar-icon {{
  width: 36px; height: 36px; border-radius: 999px;
  border: 1px solid #E2E8F0;
  background: white;
  display:flex; align-items:center; justify-content:center;
  color:#475569; position:relative; font-size:16px;
}}
.tos-notif-badge {{
  position:absolute; right:-4px; top:-5px;
  background:#EF4444; color:white; font-size:10px; font-weight:800;
  min-width:18px; height:18px; border-radius:999px;
  display:flex; align-items:center; justify-content:center;
  border:2px solid white;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
  min-width: 240px !important;
  max-width: 240px !important;
  width: 240px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  background: linear-gradient(180deg, #0F172A 0%, #0B1220 100%) !important;
  border-right: 1px solid #1E293B;
  padding: 14px 12px 16px !important;
}}
[data-testid="stSidebar"] * {{ font-family: 'Inter', sans-serif !important; }}
[data-testid="stSidebar"] hr {{
  border: 0; height: 1px; background: #1E293B;
  margin: 12px 0 !important;
}}

.tos-brand {{
  display:flex; align-items:center; gap:10px;
  color:white; font-weight:800; font-size:17px;
  letter-spacing:-.02em; padding: 6px 6px 14px;
}}
.tos-brand-logo {{
  width:36px; height:36px; border-radius:12px;
  background: linear-gradient(180deg,#FFFFFF,#CBD5E1);
  color:#0F172A; display:flex; align-items:center; justify-content:center;
  box-shadow: inset 0 -1px 0 rgba(15,23,42,.18);
  font-size:21px;
}}
.tos-user-card {{
  background: rgba(30,41,59,.72);
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 16px;
  padding: 12px;
  margin: 0 2px 8px;
}}
.tos-user-row {{ display:flex; align-items:center; gap:10px; }}
.tos-avatar {{
  width:42px; height:42px; border-radius:999px;
  display:flex; align-items:center; justify-content:center;
  color:white; font-weight:800; font-size:13px;
  box-shadow:0 8px 18px rgba(0,0,0,.22);
}}
.tos-user-name {{ color:#F8FAFC; font-weight:700; font-size:13px; line-height:1.15; max-width:130px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.tos-role-pill {{
  display:inline-flex; margin-top:5px; padding:3px 8px;
  border-radius:999px; color:white; font-size:10.5px; font-weight:800;
  letter-spacing:.02em;
}}
.tos-status {{
  display:flex; align-items:center; gap:7px;
  color:#CBD5E1; font-size:12px; font-weight:600;
  padding: 5px 3px 2px;
}}
.tos-dot {{ width:8px; height:8px; border-radius:999px; display:inline-block; box-shadow:0 0 0 3px rgba(16,185,129,.12); }}
.tos-dot.online {{ background:#10B981; }}
.tos-dot.offline {{ background:#F59E0B; box-shadow:0 0 0 3px rgba(245,158,11,.12); }}
.tos-nav-section {{
  color:#64748B; font-size:10px; font-weight:900;
  text-transform:uppercase; letter-spacing:.11em;
  margin: 12px 10px 5px;
}}
.tos-nav-active {{
  height: 36px;
  display:flex; align-items:center; gap:10px;
  color:white; font-weight:750; font-size:13px;
  background: #6366F1;
  border-radius: 11px;
  padding: 0 11px;
  box-shadow: 0 10px 22px rgba(99,102,241,.26);
  margin: 2px 0;
}}
.tos-nav-ico {{ width:20px; display:inline-flex; align-items:center; justify-content:center; }}

/* Sidebar native buttons as nav links */
[data-testid="stSidebar"] .stButton > button {{
  height: 36px;
  width: 100%;
  justify-content: flex-start;
  background: transparent !important;
  border: 1px solid transparent !important;
  color: #94A3B8 !important;
  border-radius: 11px !important;
  padding: 0 11px !important;
  font-size: 13px !important;
  font-weight: 650 !important;
  transition: all .15s ease;
  box-shadow:none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  color:#F8FAFC !important;
  background: rgba(148,163,184,.10) !important;
  border-color: rgba(148,163,184,.10) !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] {{
  background: rgba(30,41,59,.82);
  border:1px solid rgba(148,163,184,.22);
  border-radius: 12px;
  padding: 4px 8px 8px;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] label {{ color:#CBD5E1 !important; font-size:11px !important; }}

/* Page headings */
.tos-page-head {{ margin-bottom: 18px; }}
.tos-title-row {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
.tos-page-title {{
  font-size: 28px; font-weight: 850; line-height:1.15;
  letter-spacing:-.035em; color:#0F172A; margin:0;
}}
.tos-subline {{ display:flex; align-items:center; gap:12px; margin-top:6px; color:#475569; font-size:14px; font-weight:500; }}
.tos-pill {{
  display:inline-flex; align-items:center; gap:6px;
  padding: 4px 9px;
  border-radius:999px;
  font-size: 11px;
  font-weight: 800;
  color:#4F46E5;
  background:#EEF2FF;
  border:1px solid #E0E7FF;
  letter-spacing:.03em;
}}

/* Cards */
.tos-card {{
  background:white;
  border:1px solid #E2E8F0;
  border-radius:14px;
  box-shadow: 0 8px 28px rgba(15,23,42,.045);
}}
.tos-card-pad {{ padding:18px; }}
.tos-card-title {{
  font-size:16px; font-weight:800; color:#0F172A; letter-spacing:-.015em;
}}
.tos-muted {{ color:#64748B; font-size:13px; }}

/* KPI */
.tos-kpi {{
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 10px 28px rgba(15,23,42,.045);
  min-height: 126px;
  position: relative;
  overflow:hidden;
}}
.tos-kpi::after {{
  content:""; position:absolute; inset:auto -28px -38px auto;
  width:120px; height:120px; border-radius:999px;
  background: radial-gradient(circle, rgba(99,102,241,.08), rgba(99,102,241,0) 65%);
}}
.tos-kpi-top {{ display:flex; align-items:center; justify-content:space-between; gap:10px; }}
.tos-kpi-label {{ color:#475569; font-size:13px; font-weight:700; }}
.tos-kpi-icon {{
  width:38px; height:38px; border-radius:12px;
  display:flex; align-items:center; justify-content:center;
  font-size:18px; background:#EEF2FF; color:#4F46E5;
}}
.tos-kpi-value {{
  font-size:32px; font-weight:850; letter-spacing:-.04em;
  color:#0F172A; margin-top:14px;
}}
.tos-kpi-extra {{ margin-top:10px; }}
.tos-progress {{ height:8px; background:#EEF2F7; border-radius:999px; overflow:hidden; flex:1; }}
.tos-progress-bar {{ height:100%; background:#6366F1; border-radius:999px; }}
.tos-progress-line {{ display:flex; align-items:center; gap:10px; color:#475569; font-size:12px; font-weight:700; }}

/* Status badges */
.st-badge, .priority-badge {{
  display:inline-flex; align-items:center; justify-content:center;
  padding: 5px 10px; border-radius:999px;
  font-size:12px; font-weight:800; line-height:1;
  white-space:nowrap;
}}
.st-acik {{ background:#FEE2E2; color:#DC2626; }}
.st-devam {{ background:#FFEDD5; color:#EA580C; }}
.st-kapali {{ background:#DCFCE7; color:#15803D; }}
.st-bekle {{ background:#DBEAFE; color:#2563EB; }}
.st-iptal {{ background:#F1F5F9; color:#64748B; }}
.st-purple {{ background:#EEF2FF; color:#4F46E5; }}

/* Tables */
.tos-table-wrap {{
  background:#FFFFFF;
  border:1px solid #E2E8F0;
  border-radius:16px;
  overflow:hidden;
  box-shadow:0 8px 28px rgba(15,23,42,.045);
  margin-top: 10px;
}}
table.tos-table {{ width:100%; border-collapse:separate; border-spacing:0; }}
.tos-table thead th {{
  text-align:left; padding:14px 16px;
  background:#F8FAFC;
  border-bottom:1px solid #E2E8F0;
  color:#475569; font-size:12px; font-weight:850;
  letter-spacing:.02em;
}}
.tos-table tbody td {{
  padding:14px 16px;
  border-bottom:1px solid #EEF2F7;
  color:#0F172A; font-size:13px; vertical-align:middle;
}}
.tos-table tbody tr:hover td {{ background:#FAFBFF; }}
.tos-table tbody tr:last-child td {{ border-bottom:0; }}
.tos-id-link {{ color:#4F46E5; font-weight:850; text-decoration:none; }}
.tos-avatar-chip {{ display:inline-flex; align-items:center; gap:8px; font-weight:700; }}
.tos-avatar-mini {{
  width:28px; height:28px; border-radius:999px;
  display:inline-flex; align-items:center; justify-content:center;
  color:white; font-size:10px; font-weight:900;
}}
.tos-empty {{
  background:white; border:1px dashed #CBD5E1; color:#64748B;
  padding:26px; border-radius:16px; text-align:center; font-weight:650;
}}

/* Native widgets */
.stTabs [data-baseweb="tab-list"] {{ gap:8px; border-bottom:1px solid #E2E8F0; }}
.stTabs [data-baseweb="tab"] {{
  border:1px solid #E2E8F0; border-bottom:0;
  border-radius:12px 12px 0 0;
  padding:10px 18px; background:white;
  color:#475569; font-weight:750;
}}
.stTabs [aria-selected="true"] {{
  color:#4F46E5 !important; background:#FFFFFF !important;
  border-color:#C7D2FE !important;
}}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
  background:#6366F1 !important;
  border-color:#6366F1 !important;
  border-radius:12px !important;
  font-weight:800 !important;
  box-shadow:0 10px 24px rgba(99,102,241,.22) !important;
}}
.stButton > button:not([kind="primary"]) {{ border-radius:12px !important; font-weight:700 !important; }}
[data-baseweb="input"], [data-baseweb="select"] > div {{ border-radius:12px !important; }}

/* Login helpers */
.tos-login-shell {{ min-height: calc(100vh - 120px); display:flex; align-items:center; justify-content:center; }}
.tos-login-card {{ width: 480px; background:white; border:1px solid #E2E8F0; border-radius:18px; box-shadow:0 18px 50px rgba(15,23,42,.08); padding:34px; text-align:center; }}
.tos-login-icon {{ font-size:54px; margin-bottom:12px; }}
.tos-login-title {{ font-size:28px; font-weight:850; letter-spacing:-.035em; color:#0F172A; }}
.tos-login-sub {{ color:#64748B; margin:8px 0 24px; font-weight:550; }}
.tos-info-box {{ margin-top:14px; padding:13px 14px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; color:#475569; font-weight:650; }}

/* Responsive */
@media (max-width: 900px) {{
  .tos-topbar {{ left:0; }}
  .block-container {{ padding-left:1rem !important; padding-right:1rem !important; }}
}}
</style>
"""


def _esc(value) -> str:
    return html.escape("" if value is None else str(value))


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    pill_html = f'<span class="tos-pill">{_esc(pill)}</span>' if pill else ""
    icon_html = f"{_esc(icon)} " if icon else ""
    sub_html = ""
    if subtitle or pill:
        sub_html = f'<div class="tos-subline"><span>{_esc(subtitle)}</span>{pill_html}</div>'
    st.markdown(
        f"""
        <div class="tos-page-head">
          <div class="tos-title-row"><h1 class="tos-page-title">{icon_html}{_esc(title)}</h1></div>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, icon: str = "", color: str = "blue", delta: str = "", delta_type: str = "", progress: int | None = None, pill: str = "", pill_dir: str = "up"):
    color_map = {
        "red": ("#FEE2E2", "#DC2626"), "danger": ("#FEE2E2", "#DC2626"),
        "orange": ("#FFEDD5", "#EA580C"), "warning": ("#FFEDD5", "#EA580C"),
        "green": ("#DCFCE7", "#15803D"), "success": ("#DCFCE7", "#15803D"),
        "blue": ("#DBEAFE", "#2563EB"), "purple": ("#EEF2FF", "#4F46E5"),
        "teal": ("#CCFBF1", "#0F766E"),
    }
    bg, fg = color_map.get(color, color_map["purple"])
    extra = ""
    if progress is not None:
        p = max(0, min(int(progress), 100))
        extra = f'<div class="tos-progress-line"><div class="tos-progress"><div class="tos-progress-bar" style="width:{p}%"></div></div><span>{p}%</span></div>'
    elif pill:
        cls = "st-kapali" if pill_dir == "up" else "st-acik"
        extra = f'<span class="st-badge {cls}">{_esc(pill)}</span>'
    elif delta:
        cls = "st-kapali" if delta_type in ("positive", "up", "success") else "st-acik"
        extra = f'<span class="st-badge {cls}">{_esc(delta)}</span>'
    st.markdown(
        f"""
        <div class="tos-kpi">
          <div class="tos-kpi-top">
            <div class="tos-kpi-label">{_esc(label)}</div>
            <div class="tos-kpi-icon" style="background:{bg};color:{fg};">{_esc(icon)}</div>
          </div>
          <div class="tos-kpi-value">{_esc(value)}</div>
          <div class="tos-kpi-extra">{extra}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_header(notif: int = 0):
    badge = f'<span class="tos-notif-badge">{notif if notif < 100 else "99+"}</span>' if notif else ""
    st.markdown(
        f"""
        <div class="tos-topbar">
          <div class="tos-topbar-search">⌘ &nbsp; Modül, kayıt veya lokasyon ara...</div>
          <div class="tos-topbar-icon">🔔{badge}</div>
          <div class="tos-topbar-icon">?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_STATUS_MAP = {
    "Açık": "st-acik", "Acik": "st-acik", "Devam Ediyor": "st-devam", "Devam": "st-devam", "Atandı": "st-bekle",
    "Tamamlandı": "st-kapali", "Tamamlandi": "st-kapali", "Kapalı": "st-kapali", "Kapali": "st-kapali", "Çözüldü": "st-kapali",
    "Beklemede": "st-bekle", "İptal": "st-iptal", "İptal Edildi": "st-iptal", "Kapatıldı": "st-iptal",
    "Aktif": "st-kapali", "Pasif": "st-iptal", "Bakımda": "st-devam", "Arızalı": "st-acik", "Arizali": "st-acik", "Hurdaya Ayrıldı": "st-iptal", "Hurda": "st-iptal",
    "Dolu": "st-kapali", "Boş": "st-bekle", "Bos": "st-bekle", "Kira": "st-devam", "Satılık": "st-bekle",
    "Tamam": "st-kapali", "Sorunlu": "st-devam", "Uygun": "st-kapali", "Uygun Değil": "st-acik",
}


def status_badge(durum: str) -> str:
    cls = _STATUS_MAP.get(str(durum), "st-bekle")
    return f'<span class="st-badge {cls}">{_esc(durum)}</span>'


def avatar_chip(isim: str) -> str:
    if not str(isim).strip() or str(isim) in ("-", "nan"):
        return "—"
    initials = "".join(w[0].upper() for w in str(isim).split()[:2]) or "?"
    h = sum(ord(c) for c in str(isim)) % 5
    g = ["#4F46E5", "#0EA5E9", "#14B8A6", "#F59E0B", "#EC4899"][h]
    return f'<span class="tos-avatar-chip"><span class="tos-avatar-mini" style="background:{g};">{_esc(initials)}</span>{_esc(isim)}</span>'


_PRIORITY_MAP = {
    "Kritik": ("st-acik", "Kritik"), "Yuksek": ("st-devam", "Yüksek"), "Yüksek": ("st-devam", "Yüksek"),
    "Normal": ("st-bekle", "Normal"), "Dusuk": ("st-kapali", "Düşük"), "Düşük": ("st-kapali", "Düşük"),
}


def priority_badge(p: str) -> str:
    cls, lbl = _PRIORITY_MAP.get(str(p).strip(), ("st-bekle", str(p)))
    return f'<span class="priority-badge {cls}">{_esc(lbl)}</span>'


_BOOL_TRUE = {"evet", "true", "1", "aktif", "açık", "var", "yes"}


def bool_badge(val, true_lbl: str = "Aktif", false_lbl: str = "Pasif") -> str:
    s = str(val).strip().lower()
    if s in _BOOL_TRUE:
        return f'<span class="st-badge st-kapali">{_esc(true_lbl)}</span>'
    return f'<span class="st-badge st-iptal">{_esc(false_lbl)}</span>'


def data_table(df, columns, status_cols=(), priority_cols=(), avatar_cols=(), id_cols=(), bool_cols=(), max_rows: int = 80, max_text: int = 52, empty_msg: str = "Kayıt bulunamadı"):
    """Renkli rozetli HTML tablo. columns: [(df_col, başlık), ...]"""
    if df is None or len(df) == 0:
        st.markdown(f'<div class="tos-empty">{_esc(empty_msg)}</div>', unsafe_allow_html=True)
        return

    head = "".join(f"<th>{_esc(h)}</th>" for _, h in columns)
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
                cells += f'<td><span class="tos-id-link">{_esc(val)}</span></td>'
            else:
                s = str(val)
                if len(s) > max_text:
                    s = s[: max_text - 1] + "…"
                cells += f"<td>{_esc(s)}</td>"
        body += f"<tr>{cells}</tr>"
    st.markdown(f'<div class="tos-table-wrap"><table class="tos-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)


def hero_banner(title: str, subtitle: str = "", badge: str = "", icon: str = "✨", cta_text: str = ""):
    badge_html = f'<span class="tos-pill">{_esc(badge)}</span>' if badge else ""
    cta_html = f'<div style="margin-top:16px;"><span class="tos-pill">{_esc(cta_text)} →</span></div>' if cta_text else ""
    st.markdown(
        f"""
        <div class="tos-card tos-card-pad" style="margin-bottom:18px;">
          <div style="font-size:26px;">{_esc(icon)}</div>
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:8px;">
            <div class="tos-page-title" style="font-size:24px;">{_esc(title)}</div>{badge_html}
          </div>
          <div class="tos-muted" style="margin-top:8px;">{_esc(subtitle)}</div>
          {cta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(title: str, description: str, icon: str, color: str = "purple"):
    st.markdown(
        f"""
        <div class="tos-card tos-card-pad" style="height:100%;">
          <div class="tos-kpi-icon">{_esc(icon)}</div>
          <div class="tos-card-title" style="margin-top:12px;">{_esc(title)}</div>
          <div class="tos-muted" style="margin-top:6px;">{_esc(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_group_title(text: str):
    st.markdown(f'<div class="tos-card-title" style="margin: 12px 0 8px;">{_esc(text)}</div>', unsafe_allow_html=True)


def action_card(label: str, icon: str, color: str = "purple"):
    st.markdown(f'<div class="tos-card tos-card-pad" style="text-align:center;"><div style="font-size:24px;">{_esc(icon)}</div><div style="font-weight:800;margin-top:8px;">{_esc(label)}</div></div>', unsafe_allow_html=True)


def alert_row(text: str, level: str = "info"):
    icons = {"warning": "⚠", "danger": "⛔", "success": "✓", "info": "ℹ"}
    cls = {"warning": "st-devam", "danger": "st-acik", "success": "st-kapali", "info": "st-bekle"}.get(level, "st-bekle")
    st.markdown(f'<div class="tos-card tos-card-pad" style="padding:12px 14px;"><span class="st-badge {cls}">{icons.get(level, "ℹ")}</span> <span style="font-weight:650;color:#475569;">{_esc(text)}</span></div>', unsafe_allow_html=True)


def chart_card_start(title: str, subtitle: str = ""):
    sub = f'<div class="tos-muted">{_esc(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="tos-card tos-card-pad"><div class="tos-card-title">{_esc(title)}</div>{sub}', unsafe_allow_html=True)


def chart_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def nav_section(title: str):
    st.sidebar.markdown(f'<div class="tos-nav-section">{_esc(title)}</div>', unsafe_allow_html=True)


def nav_item(icon: str, label: str, key: str, is_active: bool) -> bool:
    if is_active:
        st.sidebar.markdown(f'<div class="tos-nav-active"><span class="tos-nav-ico">{_esc(icon)}</span><span>{_esc(label)}</span></div>', unsafe_allow_html=True)
        return False
    return st.sidebar.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True)


def sidebar_brand():
    st.sidebar.markdown('<div class="tos-brand"><div class="tos-brand-logo">🏢</div><div>Teknik Operasyon</div></div>', unsafe_allow_html=True)


def sidebar_user_card(ad_soyad: str, rol: str):
    display_name = ad_soyad or "Admin Kullanıcı"
    initials = "".join(w[0].upper() for w in display_name.split()[:2]) or "?"
    g1, g2 = ROLE_GRADIENTS.get(rol, ("#4F46E5", "#6366F1"))
    st.sidebar.markdown(
        f"""
        <div class="tos-user-card">
          <div class="tos-user-row">
            <div class="tos-avatar" style="background:linear-gradient(135deg,{g1},{g2});">{_esc(initials)}</div>
            <div>
              <div class="tos-user-name">{_esc(display_name)}</div>
              <span class="tos-role-pill" style="background:linear-gradient(135deg,{g1},{g2});">{_esc(rol)}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_status(connected: bool):
    cls = "online" if connected else "offline"
    txt = "Google Sheets Bağlı" if connected else "Yerel Mod (CSV)"
    st.sidebar.markdown(f'<div class="tos-status"><span class="tos-dot {cls}"></span><span>{_esc(txt)}</span></div>', unsafe_allow_html=True)


def badge(text: str, color: str = "blue") -> str:
    cls = {"red": "st-acik", "orange": "st-devam", "green": "st-kapali", "blue": "st-bekle", "purple": "st-purple"}.get(color, "st-bekle")
    return f'<span class="st-badge {cls}">{_esc(text)}</span>'
