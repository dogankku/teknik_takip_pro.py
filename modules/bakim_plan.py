from __future__ import annotations
from datetime import date, timedelta
import pandas as pd
import streamlit as st
from db import load_data, save_data
from constants import BAKIM_PERIYOT
from barkod import yeni_id
from style import section_header, data_table, kpi_card, card, asset_card

def render(secilen_tarih: date):
    section_header('Bakım Planı', 'Periyodik bakım, yasal zorunluluk ve plan takibi', pill='OPERASYON')
    df = load_data('bakim_plan')
    df_e = load_data('ekipman')
    mode = st.radio('Görünüm', ['📅 Planlar','➕ Yeni Plan','📊 Takvim Özeti'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if mode.startswith('📅'):
        today = pd.to_datetime(date.today())
        dnext = pd.to_datetime(df.get('Sonraki_Tarih',pd.Series(dtype=str)), errors='coerce') if not df.empty else pd.Series(dtype='datetime64[ns]')
        overdue = int((dnext < today).sum()) if not df.empty else 0
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi_card('Toplam Plan', len(df), '📅')
        with c2: kpi_card('Geciken', overdue, '⚠️')
        with c3: kpi_card('Yasal Zorunlu', int(df.get('Yasal_Zorunlu',pd.Series(dtype=str)).astype(str).str.lower().isin(['evet','true','1']).sum()) if not df.empty else 0, '📌')
        with c4: kpi_card('Aktif', int((df.get('Durum',pd.Series(dtype=str))=='Aktif').sum()) if not df.empty else 0, '✅')
        st.write('')
        data_table(df, [('Plan_ID','ID'),('Baslik','Başlık'),('Ekipman','Ekipman'),('Lokasyon','Lokasyon'),('Periyot_Gun','Periyot'),('Sorumlu','Sorumlu'),('Son_Yapilma','Son Yapılma'),('Sonraki_Tarih','Sonraki'),('Durum','Durum')], status_cols=['Durum'], avatar_cols=['Sorumlu'], id_cols=['Plan_ID'])
    elif mode.startswith('➕'):
        st.markdown('<div class="form-card">', unsafe_allow_html=True); card('Yeni Bakım Planı', 'Otomatik takvimlenebilir periyodik bakım oluşturun')
        ekipmanlar = df_e['Ekipman_Adi'].dropna().astype(str).tolist() if not df_e.empty and 'Ekipman_Adi' in df_e.columns else ['Genel Ekipman']
        with st.form('new_plan'):
            c1,c2 = st.columns(2)
            baslik = c1.text_input('Plan başlığı *')
            ekipman = c2.selectbox('Ekipman', ekipmanlar)
            c3,c4,c5 = st.columns(3)
            lok = c3.text_input('Lokasyon')
            periyot_label = c4.selectbox('Periyot', list(BAKIM_PERIYOT.keys()))
            sor = c5.text_input('Sorumlu')
            yasal = st.checkbox('Yasal zorunlu bakım')
            notlar = st.text_area('Notlar')
            if st.form_submit_button('💾 Plan Kaydet', type='primary', use_container_width=True):
                if not baslik.strip(): st.error('Başlık zorunlu.'); return
                pg = BAKIM_PERIYOT[periyot_label]; sonraki = date.today() + timedelta(days=pg)
                row = {'Plan_ID':yeni_id('BKM'),'Baslik':baslik,'Ekipman':ekipman,'Lokasyon':lok,'Periyot_Gun':pg,'Sorumlu':sor,'Yasal_Zorunlu':'Evet' if yasal else 'Hayır','Son_Yapilma':'','Sonraki_Tarih':str(sonraki),'Durum':'Aktif','Notlar':notlar}
                df = pd.concat([df,pd.DataFrame([row])], ignore_index=True); save_data(df,'bakim_plan'); st.success('Bakım planı kaydedildi.'); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if df.empty: st.info('Plan kaydı yok.'); return
        st.bar_chart(df['Durum'].value_counts() if 'Durum' in df.columns else pd.Series(dtype=int))
