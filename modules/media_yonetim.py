from __future__ import annotations
from datetime import date
import streamlit as st
from db import load_data
from style import section_header, data_table, kpi_card, card

def render(secilen_tarih: date):
    section_header('Medya Yönetimi', 'Fotoğraf kanıtları ve yüklenen dosyalar', pill='DENETİM')
    df = load_data('media')
    total_size = 0
    if not df.empty and 'Boyut' in df.columns:
        total_size = int(df['Boyut'].astype(str).str.extract(r'(\d+)')[0].fillna(0).astype(int).sum())
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card('Toplam Dosya', len(df), '🖼️')
    with c2: kpi_card('Görev Kanıtı', int((df.get('Parent_Tip','')=='ariza').sum()) if not df.empty else 0, '🛠️')
    with c3: kpi_card('Talep Medyası', int((df.get('Parent_Tip','')=='talep').sum()) if not df.empty else 0, '📨')
    with c4: kpi_card('Boyut', f'{total_size/1024:.1f} MB' if total_size else '0 MB', '💾')
    st.write('')
    mode = st.radio('Görünüm', ['🖼️ Galeri','📋 Liste'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if df.empty:
        st.markdown('<div class="empty">Henüz medya kaydı yok. Arıza veya talep detayında fotoğraf yükleyebilirsiniz.</div>', unsafe_allow_html=True); return
    if mode.startswith('📋'):
        data_table(df, [('Media_ID','ID'),('Parent_Tip','Tip'),('Parent_ID','Bağlı Kayıt'),('Dosya_Adi','Dosya'),('Mime','Mime'),('Boyut','Boyut'),('Yukleme_Tarihi','Yükleme'),('Yukleyen','Yükleyen')], id_cols=['Media_ID'], avatar_cols=['Yukleyen'])
    else:
        cols = st.columns(4)
        for i, (_,r) in enumerate(df.head(24).iterrows()):
            with cols[i%4]:
                st.markdown('<div class="asset-card">', unsafe_allow_html=True)
                st.markdown('🖼️')
                st.markdown(f"**{r.get('Dosya_Adi','Dosya')}**")
                st.caption(f"{r.get('Parent_Tip','')} · {r.get('Parent_ID','')}")
                st.markdown('</div>', unsafe_allow_html=True)
