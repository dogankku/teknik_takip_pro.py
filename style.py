"""Premium Xenia-style UI kit for Teknik Operasyon Sistemi (Streamlit)."""
from __future__ import annotations
import html
import pandas as pd
import streamlit as st

C = {
    "page_bg": "#F8FAFC", "sidebar_bg": "#0F172A", "sidebar_card": "#111C31",
    "primary": "#6366F1", "primary_dk": "#4F46E5", "primary_lt": "#EEF2FF",
    "success": "#10B981", "warning": "#F59E0B", "danger": "#EF4444", "info": "#0EA5E9",
    "txt": "#0F172A", "txt_2": "#475569", "txt_3": "#94A3B8",
    "border": "#E2E8F0", "card_bg": "#FFFFFF",
}

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {{ --primary:{C['primary']}; --navy:{C['sidebar_bg']}; --border:{C['border']}; --bg:{C['page_bg']}; }}
html, body, [class*="css"] {{ font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }}
.stApp {{ background:{C['page_bg']}; }}
.block-container {{ padding-top: 72px !important; padding-left: 2.35rem !important; padding-right: 2.35rem !important; max-width: 1480px !important; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg,#0F172A 0%,#101827 100%) !important; width: 260px !important; }}
section[data-testid="stSidebar"] * {{ color:#CBD5E1; }}
section[data-testid="stSidebar"] .stButton button {{
  background:transparent !important; color:#CBD5E1 !important; border:0 !important; text-align:left !important;
  justify-content:flex-start !important; height:34px !important; border-radius:10px !important; padding:0 12px !important; font-weight:600 !important;
}}
section[data-testid="stSidebar"] .stButton button:hover {{ background:#1E293B !important; color:#fff !important; }}
section[data-testid="stSidebar"] hr {{ border-color:#1E293B !important; margin:.65rem 0 !important; }}
[data-testid="stHeader"] {{ background: rgba(255,255,255,.88) !important; backdrop-filter: blur(12px); box-shadow:0 1px 3px rgba(15,23,42,.08); }}
button[kind="primary"], .stButton button[kind="primary"] {{ background:{C['primary']} !important; border-color:{C['primary']} !important; border-radius:12px !important; font-weight:700 !important; }}
.stTextInput input, .stSelectbox [data-baseweb="select"], .stDateInput input, .stNumberInput input, .stTextArea textarea {{ border-radius:12px !important; border-color:#CBD5E1 !important; }}
[data-testid="stMetric"] {{ background:white; border:1px solid {C['border']}; border-radius:14px; padding:18px; box-shadow:0 10px 25px rgba(15,23,42,.04); }}
.pro-topbar {{ position:fixed; top:0; left:260px; right:0; height:56px; z-index:999; background:rgba(255,255,255,.92); border-bottom:1px solid #E2E8F0; display:flex; align-items:center; justify-content:flex-end; padding:0 24px; gap:12px; box-shadow:0 1px 3px rgba(15,23,42,.08); backdrop-filter:blur(10px); }}
.pro-icon-btn {{ width:34px; height:34px; border-radius:999px; border:1px solid #E2E8F0; display:flex; align-items:center; justify-content:center; color:#475569; background:white; position:relative; font-weight:700; }}
.pro-badge-count {{ position:absolute; top:-8px; right:-6px; min-width:19px; height:19px; padding:0 5px; border-radius:999px; background:#EF4444; color:#fff; font-size:11px; display:flex; align-items:center; justify-content:center; border:2px solid white; }}
.brand {{ display:flex; align-items:center; gap:10px; color:white; font-weight:800; font-size:18px; padding:14px 6px 10px 6px; letter-spacing:-.02em; }}
.brand-icon {{ width:36px; height:36px; border-radius:12px; background:linear-gradient(135deg,#6366F1,#14B8A6); display:flex; align-items:center; justify-content:center; color:white; box-shadow:0 12px 28px rgba(99,102,241,.28); }}
.side-user {{ margin:10px 0 8px; padding:12px; border:1px solid rgba(148,163,184,.18); border-radius:16px; background:rgba(30,41,59,.72); display:flex; gap:10px; align-items:center; }}
.side-avatar {{ width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:800;background:linear-gradient(135deg,#6366F1,#8B5CF6); }}
.side-user-name {{ color:#fff;font-weight:800;font-size:13px;line-height:1.2; }}
.side-role {{ display:inline-flex;margin-top:4px;padding:2px 8px;border-radius:999px;background:#EEF2FF;color:#4F46E5!important;font-size:10px;font-weight:800; }}
.side-status {{ display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:#CBD5E1;margin:4px 4px 10px; }}
.side-status .dot {{ width:8px;height:8px;border-radius:999px;background:#10B981;box-shadow:0 0 0 4px rgba(16,185,129,.12); }}
.side-status.offline .dot {{ background:#F59E0B;box-shadow:0 0 0 4px rgba(245,158,11,.12); }}
.nav-section-label {{ margin:13px 4px 6px; color:#64748B; font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }}
.nav-active {{ display:flex; align-items:center; gap:9px; padding:8px 12px; border-radius:11px; background:#6366F1; color:#fff!important; font-weight:800; box-shadow:0 10px 22px rgba(99,102,241,.28); margin:2px 0; }}
.page-head {{ display:flex; align-items:flex-start; justify-content:space-between; margin:6px 0 22px; }}
.page-title {{ font-size:30px; line-height:1.12; font-weight:800; color:#0F172A; letter-spacing:-.035em; margin:0; }}
.page-sub {{ margin-top:7px; color:#475569; font-weight:600; font-size:14px; }}
.pill {{ display:inline-flex; align-items:center; gap:6px; border-radius:999px; padding:4px 10px; font-size:11px; font-weight:800; background:#EEF2FF; color:#4F46E5; margin-left:10px; }}
.tabs-card {{ border:1px solid #E2E8F0; border-radius:14px; background:#fff; padding:6px; display:inline-flex; gap:6px; box-shadow:0 10px 28px rgba(15,23,42,.04); }}
.tab-active, .tab-passive {{ border-radius:11px; padding:10px 16px; font-size:13px; font-weight:800; display:inline-flex; gap:8px; align-items:center; }}
.tab-active {{ background:#EEF2FF; color:#4F46E5; }} .tab-passive {{ color:#64748B; }}
.card {{ background:white; border:1px solid #E2E8F0; border-radius:16px; padding:18px; box-shadow:0 10px 28px rgba(15,23,42,.045); }}
.card-title {{ font-size:16px; color:#0F172A; font-weight:800; margin-bottom:4px; }} .card-sub {{ color:#64748B; font-size:12px; font-weight:600; }}
.kpi {{ min-height:130px; display:flex; flex-direction:column; justify-content:space-between; }}
.kpi-top {{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }} .kpi-label {{ color:#475569; font-size:13px; font-weight:700; }}
.kpi-icon {{ width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;background:#EEF2FF;color:#4F46E5; }}
.kpi-value {{ color:#0F172A; font-size:34px; font-weight:800; letter-spacing:-.04em; }}
.progress-track {{ width:100%; height:8px; border-radius:999px; background:#E2E8F0; overflow:hidden; }} .progress-fill {{ height:100%; border-radius:999px; background:#6366F1; }}
.delta, .small-pill {{ display:inline-flex; align-items:center; justify-content:center; border-radius:999px; padding:4px 9px; font-size:11px; font-weight:800; }}
.delta.up {{ color:#DC2626; background:#FEE2E2; }} .delta.good {{ color:#047857; background:#D1FAE5; }}
.status {{ display:inline-flex; align-items:center; gap:6px; border-radius:999px; padding:5px 10px; font-size:12px; font-weight:800; white-space:nowrap; }}
.st-acik {{ background:#FEE2E2; color:#DC2626; }} .st-devam {{ background:#FFEDD5; color:#EA580C; }} .st-kapali {{ background:#DCFCE7; color:#15803D; }} .st-bekle {{ background:#E0F2FE; color:#0369A1; }} .st-iptal {{ background:#F1F5F9; color:#64748B; }}
.avatar-chip {{ display:inline-flex; align-items:center; gap:8px; font-weight:700; color:#334155; }} .avatar-mini {{ width:26px;height:26px;border-radius:999px;color:white;font-size:10px;font-weight:800;display:flex;align-items:center;justify-content:center; }}
.pro-table-wrap {{ background:#fff;border:1px solid #E2E8F0;border-radius:16px;overflow:hidden;box-shadow:0 10px 28px rgba(15,23,42,.045); }}
.pro-table {{ width:100%; border-collapse:collapse; font-size:13px; }} .pro-table th {{ text-align:left; padding:13px 16px; color:#64748B; font-size:11px; text-transform:uppercase; letter-spacing:.04em; background:#F8FAFC; border-bottom:1px solid #E2E8F0; }}
.pro-table td {{ padding:13px 16px; border-bottom:1px solid #EEF2F7; color:#0F172A; vertical-align:middle; }} .pro-table tr:last-child td {{ border-bottom:0; }} .pro-table tr:hover td {{ background:#FAFBFF; }}
.id-link {{ color:#4F46E5; font-weight:800; text-decoration:none; }}
.empty {{ background:white;border:1px dashed #CBD5E1;border-radius:16px;padding:28px;text-align:center;color:#64748B;font-weight:700; }}
.list-row {{ display:flex; align-items:center; justify-content:space-between; padding:13px 0; border-bottom:1px solid #EEF2F7; }} .list-row:last-child {{ border-bottom:0; }}
.list-main {{ display:flex; align-items:center; gap:12px; }} .check-dot {{ width:28px;height:28px;border-radius:999px;display:flex;align-items:center;justify-content:center;background:#DCFCE7;color:#15803D;font-weight:900; }}
.muted {{ color:#64748B; font-size:12px; font-weight:600; }}
.form-card {{ background:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:18px;box-shadow:0 10px 28px rgba(15,23,42,.045); }}
.asset-card {{ background:white;border:1px solid #E2E8F0;border-radius:16px;padding:16px;box-shadow:0 10px 24px rgba(15,23,42,.04);min-height:150px; }}
.asset-head {{ display:flex;align-items:start;justify-content:space-between;gap:10px; }} .asset-name {{ font-weight:800;color:#0F172A;font-size:15px; }} .asset-meta {{ margin-top:4px;color:#64748B;font-size:12px;font-weight:600; }}
.metric-split {{ display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px; }} .mini-stat {{ background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:10px; }} .mini-stat b {{ display:block;font-size:16px;color:#0F172A; }} .mini-stat span {{ color:#64748B;font-size:11px;font-weight:700; }}
hr.soft {{ border:0;border-top:1px solid #E2E8F0;margin:18px 0; }}

/* ── Mobil hamburger butonu — Streamlit sidebar toggle'ı her zaman göster ── */
[data-testid="collapsedControl"] {{
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  z-index: 1100 !important;
}}
button[data-testid="stSidebarNavCollapseIcon"],
button[kind="header"] {{
  display: flex !important;
  visibility: visible !important;
}}

/* ── Mobil responsive (≤768px) ────────────────────────────────────────────── */
@media (max-width: 768px) {{
  /* Pro topbar'ı mobilde gizle — stHeader hamburger kullanılsın */
  .pro-topbar {{ display: none !important; }}

  /* Streamlit header'ı mobilde göster */
  [data-testid="stHeader"] {{
    display: flex !important;
    visibility: visible !important;
    height: 52px !important;
    z-index: 1050 !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
  }}

  /* İçerik alanı padding'i mobile uyarla */
  .block-container {{
    padding-top: 64px !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }}

  /* Sidebar tam genişlik üstte overlay olsun */
  section[data-testid="stSidebar"] {{
    width: 100vw !important;
    max-width: 300px !important;
  }}

  /* Tablo mobilde scroll edilebilir */
  .pro-table-wrap {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
  }}

  /* KPI kartlar mobilde daha küçük */
  .kpi-value {{ font-size: 26px !important; }}
  .page-title {{ font-size: 22px !important; }}
}}
"""

ROLE_GRADIENTS = {"Admin": ("#4F46E5", "#6366F1"), "Yonetici": ("#6366F1", "#8B5CF6"), "Teknisyen": ("#14B8A6", "#06B6D4"), "Sakin": ("#F59E0B", "#EC4899")}

def esc(x) -> str: return html.escape("" if x is None else str(x))
def inject_css(): st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

def top_header(notif: int = 0):
    b = f'<span class="pro-badge-count">{notif if notif < 100 else "99+"}</span>' if notif else ""
    st.markdown(f'<div class="pro-topbar"><div class="pro-icon-btn">🔔{b}</div><div class="pro-icon-btn">?</div></div>', unsafe_allow_html=True)
    # Mobil: sidebar açma butonu (küçük ekranlarda görünür, büyükte gizli)
    st.markdown("""
    <style>
    .mob-menu-bar {
      display: none;
      position: fixed; top: 0; left: 0; right: 0; z-index: 1050;
      height: 52px; background: #0F172A;
      align-items: center; padding: 0 16px; gap: 12px;
    }
    .mob-menu-bar span { color: #fff; font-weight: 800; font-size: 15px; flex: 1; }
    .mob-ham { font-size: 22px; cursor: pointer; background: none; border: none;
               color: #fff; padding: 6px; border-radius: 8px; }
    @media (max-width: 768px) {
      .mob-menu-bar { display: flex !important; }
    }
    </style>
    <div class="mob-menu-bar">
      <button class="mob-ham" onclick="
        var sb = window.parent.document.querySelector('[data-testid=stSidebar]');
        var cc = window.parent.document.querySelector('[data-testid=collapsedControl]');
        if(cc){ cc.click(); } else if(sb){ sb.style.display = sb.style.display==='none' ? '' : 'none'; }
      ">☰</button>
      <span>🏢 Teknik Operasyon</span>
    </div>
    """, unsafe_allow_html=True)

def section_header(title: str, subtitle: str = "", icon: str = "", pill: str = ""):
    st.markdown(f'''<div class="page-head"><div><h1 class="page-title">{esc(icon)} {esc(title)}</h1><div class="page-sub">{esc(subtitle)}{f'<span class="pill">{esc(pill)}</span>' if pill else ''}</div></div></div>''', unsafe_allow_html=True)

def radio_pills(items: list[str], active: int = 0):
    html_items = "".join(f'<div class="{"tab-active" if i==active else "tab-passive"}">{esc(t)}</div>' for i,t in enumerate(items))
    st.markdown(f'<div class="tabs-card">{html_items}</div><hr class="soft">', unsafe_allow_html=True)

def kpi_card(label: str, value, icon: str = "", color: str = "blue", delta: str = "", delta_type: str = "", progress: int | None = None, pill: str = ""):
    extra = ""
    if progress is not None:
        p = max(0, min(int(progress), 100)); extra = f'<div><div class="progress-track"><div class="progress-fill" style="width:{p}%"></div></div><div class="muted" style="margin-top:6px">%{p}</div></div>'
    elif delta:
        extra = f'<span class="delta {"good" if delta_type=="good" else "up"}">{esc(delta)}</span>'
    elif pill:
        extra = f'<span class="small-pill st-bekle">{esc(pill)}</span>'
    st.markdown(f'<div class="card kpi"><div class="kpi-top"><div class="kpi-label">{esc(label)}</div><div class="kpi-icon">{esc(icon)}</div></div><div class="kpi-value">{esc(value)}</div>{extra}</div>', unsafe_allow_html=True)

def card(title: str, subtitle: str = ""):
    sub_html = f'<div class="card-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="card-title">{esc(title)}</div>{sub_html}', unsafe_allow_html=True)

def sidebar_brand(): st.sidebar.markdown('<div class="brand"><div class="brand-icon">🏢</div><div>Teknik Operasyon</div></div>', unsafe_allow_html=True)
def sidebar_user_card(ad_soyad: str, rol: str):
    initials = "".join(w[0].upper() for w in (ad_soyad or "?").split()[:2]) or "?"
    st.sidebar.markdown(f'<div class="side-user"><div class="side-avatar">{esc(initials)}</div><div><div class="side-user-name">{esc(ad_soyad or "Kullanıcı")}</div><div class="side-role">{esc(rol)}</div></div></div>', unsafe_allow_html=True)
def sidebar_status(connected: bool):
    cls = "" if connected else "offline"; txt = "Google Sheets Bağlı" if connected else "Yerel Mod (CSV)"
    st.sidebar.markdown(f'<div class="side-status {cls}"><span class="dot"></span>{esc(txt)}</div>', unsafe_allow_html=True)
def nav_section(title: str): st.sidebar.markdown(f'<div class="nav-section-label">{esc(title)}</div>', unsafe_allow_html=True)
def nav_item_active(icon: str, label: str): st.sidebar.markdown(f'<div class="nav-active"><span>{esc(icon)}</span><span>{esc(label)}</span></div>', unsafe_allow_html=True)

def badge(text: str, color: str = "blue") -> str:
    mp = {"red":"st-acik","orange":"st-devam","green":"st-kapali","blue":"st-bekle","gray":"st-iptal","purple":"st-bekle"}
    return f'<span class="status {mp.get(color,"st-bekle")}">{esc(text)}</span>'
_STATUS_MAP = {"Açık":"st-acik","Acik":"st-acik","Devam Ediyor":"st-devam","Devam":"st-devam","Atandı":"st-bekle","Beklemede":"st-bekle","Tamamlandı":"st-kapali","Kapalı":"st-kapali","Kapali":"st-kapali","Çözüldü":"st-kapali","İptal":"st-iptal","İptal Edildi":"st-iptal","Aktif":"st-kapali","Pasif":"st-iptal","Bakımda":"st-devam","Arızalı":"st-acik","Arizali":"st-acik","Hurda":"st-iptal","Kritik":"st-acik","Yüksek":"st-devam","Yuksek":"st-devam","Normal":"st-bekle","Düşük":"st-kapali","Dusuk":"st-kapali"}
def status_badge(durum: str) -> str: return f'<span class="status {_STATUS_MAP.get(str(durum),"st-bekle")}">{esc(durum)}</span>'
def priority_badge(p: str) -> str: return status_badge(p)
def bool_badge(val, true_lbl="Aktif", false_lbl="Pasif") -> str: return status_badge(true_lbl if str(val).strip().lower() in {"evet","true","1","aktif","yes","var"} else false_lbl)
def avatar_chip(isim: str) -> str:
    if not str(isim).strip() or str(isim) in ("-", "nan"): return "—"
    initials = "".join(w[0].upper() for w in str(isim).split()[:2]) or "?"; colors=["#4F46E5","#0EA5E9","#14B8A6","#F59E0B","#EC4899"]; c=colors[sum(map(ord,str(isim)))%len(colors)]
    return f'<span class="avatar-chip"><span class="avatar-mini" style="background:{c}">{esc(initials)}</span>{esc(isim)}</span>'

def data_table(df: pd.DataFrame, columns, status_cols=(), priority_cols=(), avatar_cols=(), id_cols=(), bool_cols=(), max_rows: int = 80, max_text: int = 54, empty_msg: str = "Kayıt bulunamadı"):
    if df is None or df.empty:
        st.markdown(f'<div class="empty">{esc(empty_msg)}</div>', unsafe_allow_html=True); return
    safe = df.fillna(""); head = "".join(f"<th>{esc(h)}</th>" for _,h in columns); body=""
    for _, r in safe.head(max_rows).iterrows():
        cells=""
        for col,_ in columns:
            val = r[col] if col in safe.columns else ""
            if col in status_cols: v=status_badge(val)
            elif col in priority_cols: v=priority_badge(val)
            elif col in bool_cols: v=bool_badge(val)
            elif col in avatar_cols: v=avatar_chip(val)
            elif col in id_cols: v=f'<span class="id-link">{esc(val)}</span>'
            else:
                s=str(val); v=esc(s if len(s)<=max_text else s[:max_text-1]+"…")
            cells += f"<td>{v}</td>"
        body += f"<tr>{cells}</tr>"
    st.markdown(f'<div class="pro-table-wrap"><table class="pro-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)

def stat_pair(label: str, value: str): return f'<div class="mini-stat"><b>{esc(value)}</b><span>{esc(label)}</span></div>'
def asset_card(title: str, meta: str, status: str, left_label: str, left_val: str, right_label: str, right_val: str):
    st.markdown(f'<div class="asset-card"><div class="asset-head"><div><div class="asset-name">{esc(title)}</div><div class="asset-meta">{esc(meta)}</div></div>{status_badge(status)}</div><div class="metric-split">{stat_pair(left_label,left_val)}{stat_pair(right_label,right_val)}</div></div>', unsafe_allow_html=True)

def list_row(title: str, subtitle: str, right: str = "", ok: bool = True):
    dot = "✓" if ok else "!"; cls = "check-dot" if ok else "check-dot st-devam"
    st.markdown(f'<div class="list-row"><div class="list-main"><div class="{cls}">{dot}</div><div><b>{esc(title)}</b><div class="muted">{esc(subtitle)}</div></div></div><div class="muted">{esc(right)}</div></div>', unsafe_allow_html=True)

def alert_row(text: str, level: str = "info"): st.info(text)
def hero_banner(title: str, subtitle: str = "", badge: str = "", icon: str = "✨", cta_text: str = ""):
    st.markdown(f'<div class="card"><div style="font-size:28px">{esc(icon)}</div><h2 style="margin:.2rem 0;color:#0F172A">{esc(title)} {badge and badge}</h2><div class="muted">{esc(subtitle)}</div></div>', unsafe_allow_html=True)
def feature_card(title: str, description: str, icon: str, color: str = "purple"): st.markdown(f'<div class="card"><div class="kpi-icon">{esc(icon)}</div><div class="card-title">{esc(title)}</div><div class="card-sub">{esc(description)}</div></div>', unsafe_allow_html=True)
def action_group_title(text: str): st.markdown(f'### {text}')
def action_card(label: str, icon: str, color: str = "purple"): st.markdown(f'<div class="card"><b>{esc(icon)} {esc(label)}</b></div>', unsafe_allow_html=True)
def chart_card_start(title: str, subtitle: str = ""): st.markdown(f'<div class="card"><div class="card-title">{esc(title)}</div><div class="card-sub">{esc(subtitle)}</div>', unsafe_allow_html=True)
def chart_card_end(): st.markdown('</div>', unsafe_allow_html=True)
