from __future__ import annotations
from datetime import datetime, date
import pandas as pd
import streamlit as st
from db import load_data, save_data
from style import section_header, radio_pills, data_table, kpi_card, card, asset_card
from auth import current_user
from barkod import yeni_id
try:
    from aktivite_helper import log_ekle
except Exception:
    def log_ekle(*a, **k): pass
try:
    from yorum_helper import render_yorumlar
except Exception:
    def render_yorumlar(*a, **k): pass
try:
    from media import upload_widget, render_photo_grid
except Exception:
    def upload_widget(*a, **k): pass
    def render_photo_grid(*a, **k): pass

BOLUMLER = ['Elektrik','Mekanik','Genel','Bina','Asansör','HVAC','Yangın','Peyzaj','Diğer']
DURUMLAR = ['Açık','Devam Ediyor','Beklemede','Tamamlandı','İptal']

def render(secilen_tarih: date):
    section_header('Arıza Takip', f'{secilen_tarih.strftime("%d.%m.%Y")} — Açık ve geçmiş arızalar', pill='OPERASYON')
    df = load_data('ariza')
    df_p = load_data('personel')
    df_lok = load_data('lokasyon')
    pl = df_p['Isim'].dropna().astype(str).tolist() if not df_p.empty and 'Isim' in df_p.columns else ['Ahmet Yılmaz','Mehmet Kaya','Hasan Demir']
    lok_opts = ['—']
    if not df_lok.empty and {'Ana_Lokasyon','Ad'}.issubset(df_lok.columns):
        lok_opts += (df_lok['Ana_Lokasyon'].astype(str)+' → '+df_lok['Ad'].astype(str)).tolist()

    mode = st.radio('Görünüm', ['📋 Tüm Arızalar','➕ Yeni Arıza','📊 İstatistik'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if mode.startswith('📋'):
        _list(df, pl)
    elif mode.startswith('➕'):
        _new(df, pl, lok_opts, secilen_tarih)
    else:
        _stats(df)

def _list(df: pd.DataFrame, pl: list[str]):
    if df.empty:
        st.markdown('<div class="empty">Henüz arıza kaydı yok. Yeni arıza sekmesinden ilk kaydı oluşturabilirsiniz.</div>', unsafe_allow_html=True)
        return
    f1,f2,f3,f4 = st.columns([1.1,1.1,1.1,1.7])
    durum = f1.multiselect('Durum', DURUMLAR, default=['Açık','Devam Ediyor'])
    bol = f2.multiselect('Bölüm', BOLUMLER)
    sor = f3.selectbox('Sorumlu', ['Tümü']+pl)
    q = f4.text_input('Ara', placeholder='🔍 ID, lokasyon veya arıza tanımı...')
    g = df.copy()
    if durum and 'Durum' in g.columns: g = g[g['Durum'].isin(durum)]
    if bol and 'Bolum' in g.columns: g = g[g['Bolum'].isin(bol)]
    if sor != 'Tümü' and 'Sorumlu' in g.columns: g = g[g['Sorumlu']==sor]
    if q:
        hay = g.astype(str).agg(' '.join, axis=1).str.lower()
        g = g[hay.str.contains(q.lower(), na=False)]
    if {'Tarih','Saat'}.issubset(g.columns): g['Tarih_Saat'] = g['Tarih'].astype(str)+' '+g['Saat'].astype(str).str[:5]
    elif 'Tarih' in g.columns: g['Tarih_Saat'] = g['Tarih'].astype(str)
    if 'Tarih' in g.columns: g = g.sort_values('Tarih', ascending=False)
    st.caption(f'{len(g)} kayıt gösteriliyor')
    data_table(g, [('ID','ID'),('Tarih_Saat','Tarih'),('Bolum','Bölüm'),('Lokasyon','Lokasyon'),('Ariza_Tanimi','Arıza Tanımı'),('Sorumlu','Sorumlu'),('Durum','Durum')], status_cols=['Durum'], avatar_cols=['Sorumlu'], id_cols=['ID'])
    st.write('')
    with st.expander('Seçili arızayı düzenle / detay gör', expanded=False):
        secili = st.selectbox('Arıza seç', g['ID'].astype(str).tolist() if 'ID' in g.columns else [])
        if secili:
            _detail(secili, df, pl)

def _detail(secili_id: str, df: pd.DataFrame, pl: list[str]):
    row = df[df['ID'].astype(str)==secili_id].iloc[0]
    c1,c2,c3 = st.columns(3)
    c1.metric('Bölüm', row.get('Bolum','-')); c2.metric('Lokasyon', row.get('Lokasyon','-')); c3.metric('Durum', row.get('Durum','-'))
    with st.form(f'edit_{secili_id}'):
        durum = st.selectbox('Durum', DURUMLAR, index=DURUMLAR.index(row.get('Durum','Açık')) if row.get('Durum','Açık') in DURUMLAR else 0)
        sor = st.selectbox('Sorumlu', pl, index=pl.index(row.get('Sorumlu')) if row.get('Sorumlu') in pl else 0)
        tanim = st.text_area('Arıza tanımı', value=str(row.get('Ariza_Tanimi','')))
        c1,c2,c3 = st.columns(3)
        sure = c1.number_input('Süre (saat)', value=float(row.get('Sure_Saat') or 0), min_value=0.0, step=.5)
        malz = c2.number_input('Malzeme maliyeti', value=float(row.get('Malzeme_Maliyet') or 0), min_value=0.0, step=10.0)
        isc = c3.number_input('İşçilik maliyeti', value=float(row.get('Iscilik_Maliyet') or 0), min_value=0.0, step=10.0)
        if st.form_submit_button('💾 Güncelle', type='primary'):
            mask = df['ID'].astype(str)==secili_id
            df.loc[mask, ['Durum','Sorumlu','Ariza_Tanimi','Sure_Saat','Malzeme_Maliyet','Iscilik_Maliyet']] = [durum,sor,tanim,sure,malz,isc]
            if durum in ['Tamamlandı','İptal']: df.loc[mask,'Kapanis_Tarihi'] = str(date.today())
            save_data(df, 'ariza'); log_ekle('ariza', secili_id, (current_user() or {}).get('Ad_Soyad','Sistem'), 'Güncellendi', f'Durum: {durum}')
            st.success('Arıza güncellendi.'); st.rerun()
    upload_widget('ariza', secili_id); render_photo_grid('ariza', secili_id); render_yorumlar('ariza', secili_id)

def _new(df: pd.DataFrame, pl: list[str], lok_opts: list[str], secilen_tarih: date):
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    card('Yeni Arıza Kaydı', 'Saha ekiplerine atanacak yeni iş emri oluşturun')
    with st.form('add_ariza_pro'):
        c1,c2,c3 = st.columns(3)
        bol = c1.selectbox('Bölüm *', BOLUMLER)
        durum = c2.selectbox('Başlangıç durumu', ['Açık','Devam Ediyor'])
        sor = c3.selectbox('Sorumlu *', pl)
        c4,c5 = st.columns(2)
        lok_free = c4.text_input('Lokasyon', placeholder='Örn: B Blok - Çatı')
        lok_sec = c5.selectbox('Kayıtlı lokasyon', lok_opts)
        tanim = st.text_area('Arıza tanımı *', placeholder='Sorunu kısa ve net açıklayın...')
        c6,c7,c8 = st.columns(3)
        sure = c6.number_input('Tahmini süre (saat)', min_value=0.0, step=.5)
        malz = c7.number_input('Malzeme maliyeti (₺)', min_value=0.0, step=10.0)
        isc = c8.number_input('İşçilik maliyeti (₺)', min_value=0.0, step=10.0)
        if st.form_submit_button('➕ Arıza Kaydet', type='primary', use_container_width=True):
            if not tanim.strip(): st.error('Arıza tanımı zorunlu.'); return
            ariza_id = yeni_id('ARZ'); lok = lok_free or (lok_sec if lok_sec!='—' else '')
            row = {'ID':ariza_id,'Tarih':str(secilen_tarih),'Saat':datetime.now().strftime('%H:%M'),'Bolum':bol,'Lokasyon':lok,'Lokasyon_ID':'','Ariza_Tanimi':tanim.strip(),'Sorumlu':sor,'Durum':durum,'Kapanis_Tarihi':'','Sure_Saat':sure,'Malzeme_Maliyet':malz,'Iscilik_Maliyet':isc}
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            save_data(df,'ariza'); log_ekle('ariza', ariza_id, (current_user() or {}).get('Ad_Soyad','Sistem'), 'Oluşturuldu', f'Bölüm: {bol}')
            st.success(f'Arıza kaydedildi: {ariza_id}'); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def _stats(df: pd.DataFrame):
    c1,c2,c3,c4 = st.columns(4)
    total = len(df); open_n = int(df.get('Durum',pd.Series(dtype=str)).isin(['Açık','Devam Ediyor']).sum()) if not df.empty else 0
    kapali = int(df.get('Durum',pd.Series(dtype=str)).isin(['Tamamlandı','Kapalı']).sum()) if not df.empty else 0
    maliyet = 0
    for c in ['Malzeme_Maliyet','Iscilik_Maliyet']:
        if c in df.columns: maliyet += pd.to_numeric(df[c], errors='coerce').fillna(0).sum()
    with c1: kpi_card('Toplam Kayıt', total, '📋')
    with c2: kpi_card('Açık İş', open_n, '🔥')
    with c3: kpi_card('Kapanan', kapali, '✅')
    with c4: kpi_card('Maliyet', f'₺{maliyet:,.0f}'.replace(',','.'), '💸')
    if not df.empty and 'Bolum' in df.columns:
        st.bar_chart(df['Bolum'].value_counts())
