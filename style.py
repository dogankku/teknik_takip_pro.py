"""Teknik Operasyon Sistemi — Xenia benzeri modern SaaS arayüz kiti.

Bu dosya eski style.py yerine konulabilir.
Amaç: koyu lacivert sidebar, indigo aktif menü, modern kartlar,
renkli rozetler, temiz tablolar ve daha profesyonel login/dashboard görünümü.
"""
from __future__ import annotations

import html
import hashlib
import streamlit as st

C = {
    "page_bg": "#F8FAFC",
    "sidebar_bg": "#0F172A",
    "sidebar_card": "#111827",
    "sidebar_line": "rgba(148,163,184,.18)",
    "sidebar_txt": "#94A3B8",
    "sidebar_txt_hi": "#FFFFFF",
    "sidebar_label": "#64748B",
    "primary": "#6366F1",
    "primary_dk": "#4F46E5",
    "primary_lt": "#EEF2FF",
    "primary_bd": "#C7D2FE",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "txt": "#0F172A",
    "txt_2": "#475569",
    "txt_3": "#94A3B8",
    "border": "#E2E8F0",
    "border_lt": "#EEF2F7",
    "card_bg": "#FFFFFF",
}

ROLE_COLORS = {
    "Admin": ("#EEF2FF", "#4F46E5"),
    "Yonetici": ("#F3E8FF", "#7C3AED"),
    "Yönetici": ("#F3E8FF", "#7C3AED"),
    "Teknisyen": ("#CCFBF1", "#0F766E"),
    "Sakin": ("#FEF3C7", "#B45309"),
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --tos-bg: {C['page_bg']};
  --tos-sidebar: {C['sidebar_bg']};
  --tos-primary: {C['primary']};
  --tos-text: {C['txt']};
  --tos-muted: {C['txt_2']};
  --tos-border: {C['border']};
  --tos-card: {C['card_bg']};
}}

html, body, [class*="css"] {{
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

.stApp {{ background: var(--tos-bg); color: var(--tos-text); }}
.block-container {{
  padding-top: 5.25rem !important;
  padding-left: 2.9rem !important;
  padding-right: 2.9rem !important;
  max-width: 1480px !important;
}}

section[data-testid="stSidebar"] {{
  background: var(--tos-sidebar) !important;
  border-right: 1px solid rgba(148,163,184,.14);
}}
section[data-testid="stSidebar"] > div {{
  background: var(--tos-sidebar) !important;
  padding: 18px 14px 18px 14px;
}}
section[data-testid="stSidebar"] * {{ font-family: 'Inter', sans-serif !important; }}
section[data-testid="stSidebar"] hr {{
  border-color: rgba(148,163,184,.18) !important;
  margin: 14px 0 !important;
}}

.tos-brand {{
  display:flex; align-items:center; gap:11px;
  color:white; font-weight:800; font-size:17px; letter-spacing:-.02em;
  padding: 2px 10px 18px 10px;
}}
.tos-brand-logo {{
  width:34px; height:34px; border-radius:10px;
  display:grid; place-items:center;
  color:white; background: rgba(99,102,241,.18);
  border:1px solid rgba(255,255,255,.14);
  font-size:20px;
}}
.tos-user-card {{
  display:flex; align-items:center; gap:10px;
  padding: 10px; border-radius:14px;
  background: rgba(15,23,42,.62);
  border:1px solid rgba(148,163,184,.18);
}}
.tos-avatar {{
  width:38px; height:38px; border-radius:999px;
  display:grid; place-items:center;
  background: linear-gradient(135deg, #6366F1, #14B8A6);
  color:white; font-weight:800; font-size:13px;
  box-shadow: 0 8px 18px rgba(0,0,0,.18);
}}
.tos-user-name {{ color:#F8FAFC; font-weight:700; font-size:13px; line-height:1.1; }}
.tos-role {{
  display:inline-flex; align-items:center; margin-top:5px;
  padding:3px 8px; border-radius:999px;
  font-size:10px; font-weight:800;
}}
.tos-status {{
  display:flex; align-items:center; gap:7px;
  color:#CBD5E1; font-size:12px; font-weight:600;
  padding: 9px 10px 4px 10px;
}}
.tos-dot {{ width:7px; height:7px; border-radius:999px; display:inline-block; }}
.tos-dot.online {{ background:#22C55E; box-shadow:0 0 0 3px rgba(34,197,94,.14); }}
.tos-dot.offline {{ background:#F59E0B; box-shadow:0 0 0 3px rgba(245,158,11,.14); }}
.tos-nav-section {{
  color:{C['sidebar_label']};
  font-size:10px; font-weight:800; letter-spacing:.11em;
  text-transform:uppercase;
  margin: 15px 8px 6px 8px;
}}
.tos-nav-active {{
  display:flex; align-items:center; gap:10px;
  min-height:34px; padding: 8px 11px;
  border-radius:10px;
  background:{C['primary']};
  color:white !important;
  font-size:13.5px; font-weight:700;
  box-shadow:0 9px 20px rgba(99,102,241,.30);
}}
.tos-nav-icon {{ width:19px; text-align:center; font-size:15px; filter:saturate(.95); }}

section[data-testid="stSidebar"] .stButton > button {{
  background: transparent !important;
  color: {C['sidebar_txt']} !important;
  border: 0 !important;
  border-radius: 10px !important;
  min-height: 34px !important;
  padding: 8px 11px !important;
  justify-content: flex-start !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  box-shadow:none !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
  background: rgba(99,102,241,.11) !important;
  color: #F8FAFC !important;
}}
section[data-testid="stSidebar"] label {{ color:#CBD5E1 !important; font-size:12px !important; }}
section[data-testid="stSidebar"] [data-baseweb="input"] {{
  background: rgba(255,255,255,.05) !important;
  border: 1px solid rgba(148,163,184,.22) !important;
  border-radius: 10px !important;
}}

.tos-topbar {{
  position: fixed; top:0; left:0; right:0; height:56px; z-index: 999;
  background: rgba(255,255,255,.96);
  border-bottom: 1px solid rgba(226,232,240,.9);
  box-shadow: 0 1px 3px rgba(15,23,42,.08);
  display:flex; justify-content:flex-end; align-items:center;
  padding:0 24px; gap:14px;
}}
.tos-top-icon {{
  width:34px; height:34px; border-radius:999px;
  display:grid; place-items:center;
  color:#475569; border:1px solid transparent;
  font-weight:800; position:relative;
}}
.tos-top-icon:hover {{ background:#F1F5F9; border-color:#E2E8F0; }}
.tos-notif-badge {{
  position:absolute; top:-3px; right:-4px;
  min-width:17px; height:17px; padding:0 4px;
  border-radius:999px; background:#EF4444; color:white;
  display:grid; place-items:center;
  font-size:10px; font-weight:900;
  border:2px solid white;
}}

.tos-page-title {{
  display:flex; align-items:flex-start; justify-content:space-between; gap:18px;
  margin-bottom:20px;
}}
.tos-page-title h1 {{
  font-size:30px; line-height:1.05; margin:0;
  color:#0F172A; font-weight:800; letter-spacing:-.035em;
}}
.tos-page-sub {{
  margin-top:9px; color:#475569; font-size:14px; font-weight:600;
  display:flex; align-items:center; gap:10px; flex-wrap:wrap;
}}
.tos-pill {{
  display:inline-flex; align-items:center; gap:6px;
  padding:5px 10px; border-radius:999px;
  font-size:11px; font-weight:800; letter-spacing:.01em;
  background:#EEF2FF; color:#4F46E5; border:1px solid #E0E7FF;
}}

.tos-card {{
  background:#FFFFFF;
  border:1px solid #E2E8F0;
  border-radius:14px;
  box-shadow: 0 7px 24px rgba(15,23,42,.035);
  padding:18px;
}}
.tos-kpi {{
  min-height:132px; display:flex; flex-direction:column; justify-content:space-between;
}}
.tos-kpi-top {{ display:flex; align-items:center; justify-content:space-between; gap:14px; }}
.tos-kpi-label {{ color:#475569; font-size:13px; font-weight:700; }}
.tos-kpi-icon {{
  width:42px; height:42px; border-radius:12px;
  display:grid; place-items:center;
  font-size:20px; background:#EEF2FF; color:#4F46E5;
}}
.tos-kpi-value {{ font-size:32px; font-weight:850; letter-spacing:-.05em; color:#0F172A; }}
.tos-progress {{ height:8px; border-radius:999px; background:#EEF2F7; overflow:hidden; margin-top:7px; }}
.tos-progress > span {{ display:block; height:100%; border-radius:999px; background:#6366F1; }}
.tos-delta {{
  display:inline-flex; align-items:center; justify-content:center;
  padding:4px 9px; border-radius:999px;
  font-size:11px; font-weight:800;
}}
.tos-delta.up {{ background:#FEE2E2; color:#DC2626; }}
.tos-delta.down {{ background:#DCFCE7; color:#16A34A; }}

.tos-table-wrap {{
  background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
  box-shadow: 0 7px 24px rgba(15,23,42,.035); overflow:hidden;
}}
.tos-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
.tos-table th {{
  background:#F8FAFC; color:#475569; font-size:12px;
  font-weight:800; text-align:left; padding:14px 15px;
  border-bottom:1px solid #E2E8F0;
}}
.tos-table td {{
  padding:14px 15px; color:#0F172A; font-weight:500;
  border-bottom:1px solid #EEF2F7; vertical-align:middle;
}}
.tos-table tr:last-child td {{ border-bottom:0; }}
.tos-id {{ color:#4F46E5; font-weight:800; }}
.tos-empty {{
  background:#FFFFFF; border:1px dashed #CBD5E1; border-radius:14px;
  padding:30px; text-align:center; color:#64748B; font-weight:650;
}}

.status-badge {{
  display:inline-flex; align-items:center; gap:6px;
  padding:5px 10px; border-radius:999px;
  font-size:11.5px; font-weight:800; white-space:nowrap;
}}
.st-acik {{ background:#FEE2E2; color:#DC2626; }}
.st-devam {{ background:#FFEDD5; color:#EA580C; }}
.st-kapali {{ background:#DCFCE7; color:#15803D; }}
.st-bekle {{ background:#EEF2FF; color:#4F46E5; }}
.st-iptal {{ background:#F1F5F9; color:#475569; }}

.tos-avatar-chip {{ display:inline-flex; align-items:center; gap:8px; font-weight:700; }}
.tos-avatar-sm {{
  width:28px; height:28px; border-radius:999px;
  display:grid; place-items:center;
  color:white; font-size:11px; font-weight:850;
}}

.tos-hero {{
  background:#FFFFFF; border:1px solid #E2E8F0; border-radius:18px;
  padding:22px; box-shadow: 0 12px 30px rgba(15,23,42,.05);
}}
.tos-hero-icon {{
  width:48px; height:48px; border-radius:14px;
  display:grid; place-items:center; background:#EEF2FF;
  color:#4F46E5; font-size:24px; margin-bottom:14px;
}}
.tos-hero-title {{font-size:24px; font-weight:850; letter-spacing:-.03em; color:#0F172A; margin-bottom:7px;}}
.tos-hero-sub {{font-size:14px; color:#64748B; font-weight:550; line-height:1.55;}}
.tos-hero-cta {{
  display:inline-flex; margin-top:16px; padding:10px 14px;
  border-radius:10px; background:#6366F1; color:white; font-weight:800;
}}

.tos-feature {{
  background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px;
  padding:18px; min-height:135px; box-shadow: 0 7px 24px rgba(15,23,42,.035);
}}
.tos-feature-ic {{
  width:38px; height:38px; border-radius:12px;
  display:grid; place-items:center; background:#EEF2FF; color:#4F46E5;
  font-size:20px; margin-bottom:12px;
}}
.tos-feature h3 {{font-size:15px; font-weight:850; margin:0 0 6px 0; color:#0F172A;}}
.tos-feature p {{font-size:13px; color:#64748B; margin:0; line-height:1.45;}}

.tos-alert {{
  border-radius:14px; padding:13px 14px; border:1px solid #E2E8F0;
  background:#FFFFFF; color:#475569; font-weight:650;
}}
.tos-alert.info {{ background:#EFF6FF; border-color:#BFDBFE; color:#1D4ED8; }}
.tos-alert.success {{ background:#ECFDF5; border-color:#A7F3D0; color:#047857; }}
.tos-alert.warning {{ background:#FFFBEB; border-color:#FDE68A; color:#B45309; }}
.tos-alert.danger {{ background:#FEF2F2; border-color:#FECACA; color:#B91C1C; }}

div[data-testid="stTabs"] button p {{ font-weight:800 !important; }}
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTextArea textarea {{
  border-radius:11px !important;
}}
.stButton > button[kind="primary"], .stDownloadButton > button {{
  background:#6366F1 !important; border:1px solid #6366F1 !important;
  border-radius:11px !important; font-weight:850 !important;
  box-shadow:0 9px 20px rgba(99,102,241,.20) !important;
}}
</style>
"""


def _e(x) -> str:
    return html.escape(str(x or ""), quote=True)


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    pill_html = f'<span class="tos-pill">{_e(pill)}</span>' if pill else ""
    icon_html = f"{_e(icon)} " if icon else ""
    sub_html = ""
    if subtitle or pill:
        sub_html = f'<div class="tos-page-sub"><span>{_e(subtitle)}</span>{pill_html}</div>'
    st.markdown(
        f'<div class="tos-page-title"><div><h1>{icon_html}{_e(title)}</h1>{sub_html}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, icon: str = "", color: str = "blue", delta: str = "", delta_type: str = "up", progress: int | None = None, pill: str = "", pill_dir: str = "up"):
    color_map = {
        "blue": ("#EEF2FF", "#4F46E5"),
        "purple": ("#EEF2FF", "#6366F1"),
        "green": ("#DCFCE7", "#15803D"),
        "red": ("#FEE2E2", "#DC2626"),
        "orange": ("#FFEDD5", "#EA580C"),
        "teal": ("#CCFBF1", "#0F766E"),
    }
    bg, fg = color_map.get(color, color_map["blue"])
    extra = ""
    if progress is not None:
        p = max(0, min(int(progress), 100))
        extra = f'<div style="display:flex;align-items:center;gap:10px"><div class="tos-progress" style="flex:1"><span style="width:{p}%"></span></div><span style="font-size:12px;font-weight:800;color:#475569">{p}%</span></div>'
    elif pill:
        extra = f'<span class="tos-delta {pill_dir}">{_e(pill)}</span>'
    elif delta:
        extra = f'<span class="tos-delta {delta_type}">{_e(delta)}</span>'
    st.markdown(
        f'''
        <div class="tos-card tos-kpi">
          <div class="tos-kpi-top">
            <div class="tos-kpi-icon" style="background:{bg};color:{fg}">{_e(icon)}</div>
            <div class="tos-kpi-label">{_e(label)}</div>
          </div>
          <div class="tos-kpi-value">{_e(value)}</div>
          <div>{extra}</div>
        </div>
        ''', unsafe_allow_html=True,
    )


def top_header(notif: int = 0):
    badge = f'<span class="tos-notif-badge">{notif if notif < 100 else "99+"}</span>' if notif else ""
    st.markdown(
        f'<div class="tos-topbar"><div class="tos-top-icon">🔔{badge}</div><div class="tos-top-icon">?</div></div>',
        unsafe_allow_html=True,
    )

_STATUS_MAP = {
    "Açık": "st-acik", "Acik": "st-acik", "Devam Ediyor": "st-devam", "Devam": "st-devam",
    "Atandı": "st-bekle", "Beklemede": "st-bekle", "Tamamlandı": "st-kapali", "Tamamlandi": "st-kapali",
    "Kapalı": "st-kapali", "Kapali": "st-kapali", "Çözüldü": "st-kapali", "Aktif": "st-kapali",
    "Pasif": "st-iptal", "Bakımda": "st-devam", "Arızalı": "st-acik", "Arizali": "st-acik",
    "Hurdaya Ayrıldı": "st-iptal", "Hurda": "st-iptal", "Dolu": "st-kapali", "Boş": "st-bekle", "Bos": "st-bekle",
    "Kira": "st-devam", "Satılık": "st-bekle", "İptal": "st-iptal", "İptal Edildi": "st-iptal", "Kapatıldı": "st-iptal",
}

def status_badge(durum: str) -> str:
    cls = _STATUS_MAP.get(str(durum), "st-bekle")
    return f'<span class="status-badge {cls}">{_e(durum)}</span>'

_PRIORITY_MAP = {
    "Kritik": ("st-acik", "Kritik"), "Yuksek": ("st-devam", "Yüksek"), "Yüksek": ("st-devam", "Yüksek"),
    "Normal": ("st-bekle", "Normal"), "Dusuk": ("st-kapali", "Düşük"), "Düşük": ("st-kapali", "Düşük"),
}

def priority_badge(p: str) -> str:
    cls, lbl = _PRIORITY_MAP.get(str(p).strip(), ("st-bekle", str(p)))
    return f'<span class="status-badge {cls}">{_e(lbl)}</span>'

_BOOL_TRUE = {"evet", "true", "1", "aktif", "açık", "var", "yes"}
def bool_badge(val, true_lbl: str = "Aktif", false_lbl: str = "Pasif") -> str:
    s = str(val).strip().lower()
    return f'<span class="status-badge {"st-kapali" if s in _BOOL_TRUE else "st-iptal"}">{_e(true_lbl if s in _BOOL_TRUE else false_lbl)}</span>'


def avatar_chip(isim: str) -> str:
    isim = str(isim or "").strip()
    if not isim or isim in ("-", "nan"):
        return "—"
    initials = "".join(w[0].upper() for w in isim.split()[:2]) or "?"
    palette = ["#6366F1", "#0EA5E9", "#14B8A6", "#F59E0B", "#EC4899"]
    idx = int(hashlib.md5(isim.encode("utf-8")).hexdigest(), 16) % len(palette)
    return f'<span class="tos-avatar-chip"><span class="tos-avatar-sm" style="background:{palette[idx]}">{_e(initials)}</span>{_e(isim)}</span>'


def data_table(df, columns, status_cols=(), priority_cols=(), avatar_cols=(), id_cols=(), bool_cols=(), max_rows: int = 80, max_text: int = 46, empty_msg: str = "Kayıt bulunamadı"):
    if df is None or len(df) == 0:
        st.markdown(f'<div class="tos-empty">{_e(empty_msg)}</div>', unsafe_allow_html=True)
        return
    head = "".join(f"<th>{_e(h)}</th>" for _, h in columns)
    safe = df.fillna("")
    body = ""
    for _, r in safe.head(max_rows).iterrows():
        cells = ""
        for col, _ in columns:
            val = r[col] if col in safe.columns else ""
            if col in status_cols:
                cell = status_badge(val)
            elif col in priority_cols:
                cell = priority_badge(val)
            elif col in bool_cols:
                cell = bool_badge(val)
            elif col in avatar_cols:
                cell = avatar_chip(val)
            elif col in id_cols:
                cell = f'<span class="tos-id">{_e(val)}</span>'
            else:
                s = str(val)
                if len(s) > max_text:
                    s = s[: max_text - 1] + "…"
                cell = _e(s)
            cells += f"<td>{cell}</td>"
        body += f"<tr>{cells}</tr>"
    st.markdown(f'<div class="tos-table-wrap"><table class="tos-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)


def hero_banner(title: str, subtitle: str = "", badge: str = "", icon: str = "✨", cta_text: str = ""):
    badge_html = f'<span class="tos-pill">{_e(badge)}</span>' if badge else ""
    cta_html = f'<div class="tos-hero-cta">{_e(cta_text)} →</div>' if cta_text else ""
    st.markdown(
        f'<div class="tos-hero"><div class="tos-hero-icon">{_e(icon)}</div><div class="tos-hero-title">{_e(title)} {badge_html}</div><div class="tos-hero-sub">{_e(subtitle)}</div>{cta_html}</div>',
        unsafe_allow_html=True,
    )


def feature_card(title: str, description: str, icon: str, color: str = "purple"):
    st.markdown(f'<div class="tos-feature"><div class="tos-feature-ic">{_e(icon)}</div><h3>{_e(title)}</h3><p>{_e(description)}</p></div>', unsafe_allow_html=True)


def action_group_title(text: str):
    st.markdown(f'<h3 style="font-size:16px;font-weight:850;color:#0F172A;margin:18px 0 10px">{_e(text)}</h3>', unsafe_allow_html=True)


def action_card(label: str, icon: str, color: str = "purple"):
    st.markdown(f'<div class="tos-card" style="display:flex;align-items:center;gap:12px;font-weight:800"><span class="tos-kpi-icon">{_e(icon)}</span>{_e(label)}</div>', unsafe_allow_html=True)


def alert_row(text: str, level: str = "info"):
    icons = {"warning": "⚠", "danger": "⛔", "success": "✓", "info": "ℹ"}
    st.markdown(f'<div class="tos-alert {level}">{icons.get(level, "")} {_e(text)}</div>', unsafe_allow_html=True)


def chart_card_start(title: str, subtitle: str = ""):
    sub = f'<div style="color:#64748B;font-size:13px;font-weight:600;margin-top:4px">{_e(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="tos-card"><h3 style="margin:0;font-size:16px;font-weight:850">{_e(title)}</h3>{sub}<div style="margin-top:12px">', unsafe_allow_html=True)


def chart_card_end():
    st.markdown('</div></div>', unsafe_allow_html=True)


def nav_section(title: str):
    st.sidebar.markdown(f'<div class="tos-nav-section">{_e(title)}</div>', unsafe_allow_html=True)


def nav_item(icon: str, label: str, key: str, is_active: bool) -> bool:
    if is_active:
        st.sidebar.markdown(f'<div class="tos-nav-active"><span class="tos-nav-icon">{_e(icon)}</span><span>{_e(label)}</span></div>', unsafe_allow_html=True)
        return False
    return st.sidebar.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True)


def sidebar_brand():
    st.sidebar.markdown('<div class="tos-brand"><div class="tos-brand-logo">🏢</div><div>Teknik Operasyon</div></div>', unsafe_allow_html=True)


def sidebar_user_card(ad_soyad: str, rol: str):
    ad_soyad = ad_soyad or "Kullanıcı"
    initials = "".join(w[0].upper() for w in ad_soyad.split()[:2]) or "?"
    bg, fg = ROLE_COLORS.get(rol, ("#EEF2FF", "#4F46E5"))
    st.sidebar.markdown(
        f'<div class="tos-user-card"><div class="tos-avatar">{_e(initials)}</div><div><div class="tos-user-name">{_e(ad_soyad)}</div><span class="tos-role" style="background:{bg};color:{fg}">{_e(rol)}</span></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_status(connected: bool):
    cls = "online" if connected else "offline"
    txt = "Google Sheets Bağlı" if connected else "Yerel Mod (CSV)"
    st.sidebar.markdown(f'<div class="tos-status"><span class="tos-dot {cls}"></span>{_e(txt)}</div>', unsafe_allow_html=True)


def badge(text: str, color: str = "blue") -> str:
    return f'<span class="tos-pill">{_e(text)}</span>'
