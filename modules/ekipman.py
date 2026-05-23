from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from db import load_data, save_data
from constants import EKIPMAN_KATEGORI
from barkod import yeni_barkod_id, make_qr, make_barcode, toplu_barkod_pdf
from style import section_header, data_table, kpi_card, asset_card, card

def render(secilen_tarih: date):
    section_header('Ekipman & Barkod', 'Varlık envanteri, QR ve bakım takibi', pill='ENVANTER')
    df = load_data('ekipman')
    mode = st.radio('Görünüm', ['📦 Ekipmanlar','➕ Yeni Ekipman','🏷️ Barkod / QR'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if mode.startswith('📦'): _list(df)
    elif mode.startswith('➕'): _new(df)
    else: _labels(df)

def _list(df):
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card('Toplam Ekipman', len(df), '📦')
    with c2: kpi_card('Aktif', int((df.get('Durum',pd.Series(dtype=str))=='Aktif').sum()) if not df.empty else 0, '✅')
    with c3: kpi_card('Bakımda', int((df.get('Durum',pd.Series(dtype=str))=='Bakımda').sum()) if not df.empty else 0, '🛠️')
    with c4: kpi_card('Arızalı', int((df.get('Durum',pd.Series(dtype=str))=='Arızalı').sum()) if not df.empty else 0, '⚠️')
    st.write('')
    f1,f2,f3 = st.columns([1.2,1.2,2])
    kategori = f1.multiselect('Kategori', EKIPMAN_KATEGORI)
    durum = f2.multiselect('Durum', ['Aktif','Bakımda','Arızalı','Pasif','Hurda'])
    q = f3.text_input('Ara', placeholder='🔍 ekipman, lokasyon, barkod...')
    g = df.copy()
    if kategori and 'Kategori' in g.columns: g = g[g['Kategori'].isin(kategori)]
    if durum and 'Durum' in g.columns: g = g[g['Durum'].isin(durum)]
    if q and not g.empty:
        hay = g.astype(str).agg(' '.join, axis=1).str.lower(); g = g[hay.str.contains(q.lower(), na=False)]
    view = st.toggle('Kart görünümü', value=True)
    if view:
        cols = st.columns(3)
        for i, (_, r) in enumerate(g.head(12).iterrows()):
            with cols[i % 3]:
                asset_card(r.get('Ekipman_Adi','-'), f"{r.get('Kategori','-')} · {r.get('Lokasyon','-')}", r.get('Durum','Aktif'), 'Barkod', r.get('Barkod_ID','-'), 'Sonraki Bakım', r.get('Sonraki_Bakim','-'))
        if g.empty: st.markdown('<div class="empty">Ekipman kaydı bulunamadı.</div>', unsafe_allow_html=True)
    else:
        data_table(g, [('Barkod_ID','Barkod'),('Ekipman_Adi','Ekipman'),('Kategori','Kategori'),('Lokasyon','Lokasyon'),('Marka_Model','Marka/Model'),('Seri_No','Seri No'),('Sonraki_Bakim','Sonraki Bakım'),('Durum','Durum')], status_cols=['Durum'], id_cols=['Barkod_ID'])

def _new(df):
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    card('Yeni Ekipman', 'QR ve Code-128 barkodlu varlık kaydı oluşturun')
    with st.form('add_ekipman_pro'):
        c1,c2,c3 = st.columns(3)
        ad = c1.text_input('Ekipman adı *')
        kat = c2.selectbox('Kategori', EKIPMAN_KATEGORI)
        durum = c3.selectbox('Durum', ['Aktif','Bakımda','Arızalı','Pasif','Hurda'])
        c4,c5,c6 = st.columns(3)
        lok = c4.text_input('Lokasyon')
        marka = c5.text_input('Marka / Model')
        seri = c6.text_input('Seri No')
        c7,c8 = st.columns(2)
        satin = c7.date_input('Satın alma tarihi', value=date.today())
        sonraki = c8.date_input('Sonraki bakım', value=date.today())
        notlar = st.text_area('Notlar')
        if st.form_submit_button('➕ Ekipman Kaydet', type='primary', use_container_width=True):
            if not ad.strip(): st.error('Ekipman adı zorunlu.'); return
            row = {'Barkod_ID':yeni_barkod_id(),'Ekipman_Adi':ad.strip(),'Kategori':kat,'Lokasyon':lok,'Marka_Model':marka,'Seri_No':seri,'Satin_Alma':str(satin),'Sonraki_Bakim':str(sonraki),'Durum':durum,'Notlar':notlar}
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True); save_data(df,'ekipman')
            st.success(f'Ekipman kaydedildi: {row["Barkod_ID"]}'); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def _labels(df):
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    card('Barkod / QR Etiketleri', 'Tekil veya toplu etiket üretimi')
    if df.empty:
        st.info('Önce ekipman ekleyin.'); st.markdown('</div>', unsafe_allow_html=True); return
    sec = st.selectbox('Ekipman seç', df['Barkod_ID'].astype(str).tolist())
    row = df[df['Barkod_ID'].astype(str)==sec].iloc[0]
    c1,c2 = st.columns(2)
    qr = make_qr(f"{row.get('Barkod_ID')} | {row.get('Ekipman_Adi')} | {row.get('Lokasyon')}")
    bc = make_barcode(str(row.get('Barkod_ID')))
    if qr: c1.image(qr, caption='QR Kod')
    if bc: c2.image(bc, caption='Code-128 Barkod')
    items = [{'id':r.get('Barkod_ID',''),'ad':r.get('Ekipman_Adi',''),'lokasyon':r.get('Lokasyon','')} for _,r in df.iterrows()]
    pdf = toplu_barkod_pdf(items)
    if pdf: st.download_button('📄 Toplu Barkod PDF İndir', pdf, 'ekipman_barkodlari.pdf', 'application/pdf', use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
