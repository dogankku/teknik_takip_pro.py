from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from db import load_data
from style import section_header, kpi_card, data_table, card

def _num(s): return pd.to_numeric(s, errors='coerce').fillna(0)
def _money(v): return f"₺{float(v):,.0f}".replace(',', '.')

def render(secilen_tarih: date):
    section_header('Maliyet Paneli', 'Görev, talep, bakım ve genel gider maliyetleri', pill='ANALİZ')
    ariza = load_data('ariza'); talep = load_data('talep'); gider = load_data('gider'); bakim = load_data('bakim_log')
    ariza_m = (_num(ariza.get('Malzeme_Maliyet',pd.Series(dtype=float))) + _num(ariza.get('Iscilik_Maliyet',pd.Series(dtype=float)))).sum() if not ariza.empty else 0
    talep_m = (_num(talep.get('Malzeme_Maliyet',pd.Series(dtype=float))) + _num(talep.get('Iscilik_Maliyet',pd.Series(dtype=float)))).sum() if not talep.empty else 0
    gider_m = _num(gider.get('Tutar',pd.Series(dtype=float))).sum() if not gider.empty else 0
    bakim_m = (_num(bakim.get('Malzeme_Maliyet',pd.Series(dtype=float))) + _num(bakim.get('Iscilik_Maliyet',pd.Series(dtype=float)))).sum() if not bakim.empty else 0
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card('Arıza Maliyeti', _money(ariza_m), '🛠️')
    with c2: kpi_card('Talep Maliyeti', _money(talep_m), '📨')
    with c3: kpi_card('Bakım Maliyeti', _money(bakim_m), '📅')
    with c4: kpi_card('Genel Gider', _money(gider_m), '⚡')
    st.write('')
    left,right = st.columns([1,1], gap='large')
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True); card('Kategori Dağılımı')
        parts = pd.Series({'Arıza':ariza_m,'Talep':talep_m,'Bakım':bakim_m,'Genel Gider':gider_m})
        st.bar_chart(parts)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True); card('Son Giderler')
        data_table(gider, [('Gider_ID','ID'),('Tarih','Tarih'),('Kategori','Kategori'),('Aciklama','Açıklama'),('Tutar','Tutar'),('Tedarikci','Tedarikçi')], id_cols=['Gider_ID'], max_rows=8, empty_msg='Gider kaydı yok.')
        st.markdown('</div>', unsafe_allow_html=True)
