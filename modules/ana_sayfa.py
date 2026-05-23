from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from db import load_data
from style import section_header, kpi_card, data_table, card, list_row

def _money(v):
    try: return f"₺{float(v):,.0f}".replace(',', '.')
    except Exception: return "₺0"

def _sum_cols(df, cols):
    total = 0.0
    for c in cols:
        if c in df.columns:
            total += pd.to_numeric(df[c], errors='coerce').fillna(0).sum()
    return total

def render(secilen_tarih: date):
    section_header('Ana Sayfa', f'{secilen_tarih.strftime("%d.%m.%Y")} — Operasyon özeti', pill='GENEL BAKIŞ')
    df_a = load_data('ariza')
    df_t = load_data('talep')
    df_c = load_data('checklist')
    df_g = load_data('gider')
    today = str(secilen_tarih)

    open_ariza = int(df_a.get('Durum', pd.Series(dtype=str)).isin(['Açık','Devam Ediyor','Beklemede']).sum()) if not df_a.empty else 0
    pending_talep = int(df_t.get('Durum', pd.Series(dtype=str)).isin(['Açık','Atandı','Devam','Devam Ediyor']).sum()) if not df_t.empty else 0
    today_checks = df_c[df_c.get('Tarih','') == today] if not df_c.empty and 'Tarih' in df_c.columns else pd.DataFrame()
    done_groups = today_checks[['Bolum','Alt_Grup']].drop_duplicates().shape[0] if not today_checks.empty else 0
    target = 12
    progress = int(min(100, done_groups / target * 100)) if target else 0
    total_cost = _sum_cols(df_a, ['Malzeme_Maliyet','Iscilik_Maliyet']) + _sum_cols(df_t, ['Malzeme_Maliyet','Iscilik_Maliyet']) + (pd.to_numeric(df_g.get('Tutar', pd.Series(dtype=float)), errors='coerce').fillna(0).sum() if not df_g.empty else 0)

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card('Açık Arızalar', open_ariza, '🛠️', delta='kritik takip')
    with c2: kpi_card('Bugün Kontrol', f'{done_groups}/{target}', '✅', progress=progress)
    with c3: kpi_card('Bekleyen Talepler', pending_talep, '📨', pill='SLA')
    with c4: kpi_card('Bu Ay Gider', _money(total_cost), '⚡', delta_type='good', delta='güncel')

    st.write('')
    left, right = st.columns([2,1], gap='large')
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        card('Son Arızalar', 'Açık ve yakın zamanda güncellenen iş emirleri')
        if not df_a.empty:
            g = df_a.copy()
            if 'Tarih' in g.columns: g = g.sort_values('Tarih', ascending=False)
            if 'Saat' in g.columns and 'Tarih' in g.columns: g['Tarih_Saat'] = g['Tarih'].astype(str) + ' ' + g['Saat'].astype(str).str[:5]
            else: g['Tarih_Saat'] = g.get('Tarih','')
            data_table(g, [('ID','ID'),('Bolum','Bölüm'),('Ariza_Tanimi','Tanım'),('Sorumlu','Sorumlu'),('Durum','Durum')], status_cols=['Durum'], avatar_cols=['Sorumlu'], id_cols=['ID'], max_rows=5)
        else:
            st.markdown('<div class="empty">Henüz arıza kaydı yok.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        card('Bugün Kontroller', 'Tamamlanan veya planlanan kontrol grupları')
        if not today_checks.empty:
            groups = today_checks[['Bolum','Alt_Grup','Kontrol_Eden']].drop_duplicates().head(7)
            for _, r in groups.iterrows():
                list_row(f"{r.get('Bolum','')} — {str(r.get('Alt_Grup','')).split('&')[0].strip()}", f"Kontrol eden: {r.get('Kontrol_Eden','-')}", 'tamam')
        else:
            samples = [('Elektrik — Jeneratör','Alt Grup: 6. Jeneratör & Zayıf Akım Sistemleri','09:15'),('Mekanik — Kazan Dairesi','Alt Grup: Isıtma & Sıcak Su Sistemleri','10:05'),('Yangın Sistemleri','Alt Grup: Algılama & Söndürme','11:00'),('Asansör Sistemleri','Alt Grup: Asansör & Yürüyen Merdiven','13:00')]
            for title, sub, tm in samples: list_row(title, sub, tm)
        st.markdown('</div>', unsafe_allow_html=True)
