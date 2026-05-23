from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from constants import SORU_GRUPLARI
from db import load_data, save_data
from auth import current_user
from style import section_header, data_table, kpi_card, card
try:
    from aktivite_helper import log_ekle
except Exception:
    def log_ekle(*a, **k): pass

def render(secilen_tarih: date):
    section_header('Günlük Kontroller', f'{secilen_tarih.strftime("%d.%m.%Y")} — Kontrol formları', pill='OPERASYON')
    mode = st.radio('Görünüm', ['📋 Standart Kontroller','📝 Şablon ile Doldur','📊 Özet & Arıza'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if mode.startswith('📋'):
        _standard(secilen_tarih)
    elif mode.startswith('📝'):
        _template(secilen_tarih)
    else:
        _summary(secilen_tarih)

def _standard(secilen_tarih: date):
    df = load_data('checklist')
    df_p = load_data('personel')
    kontrol_edenler = df_p['Isim'].dropna().astype(str).tolist() if not df_p.empty and 'Isim' in df_p.columns else ['Ahmet Yılmaz','Mehmet Kaya','Hasan Demir']
    c1,c2,c3 = st.columns([1,2,1.2])
    bolum = c1.selectbox('📂 Bölüm', list(SORU_GRUPLARI.keys()))
    alt_gruplar = list(SORU_GRUPLARI.get(bolum, {}).keys())
    alt = c2.selectbox('📍 Alt Grup', alt_gruplar)
    kontrol_eden = c3.selectbox('👤 Kontrol Eden', kontrol_edenler)
    sorular = SORU_GRUPLARI.get(bolum, {}).get(alt, [])
    st.markdown(f'### {bolum} — {alt} ` {len(sorular)} soru `')
    st.caption('💡 Sorun yoksa açıklama yazmadan geçebilirsiniz. Sorunlu işaretlenenler açıklama ile arıza takibine aktarılabilir.')
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    with st.form(f'check_{bolum}_{alt}_{secilen_tarih}'):
        cevaplar = []
        for i, soru in enumerate(sorular, start=1):
            st.markdown(f'**{i}. {soru}**')
            r1,r2 = st.columns([1,2])
            durum = r1.radio('Durum', ['✅ Tamam','⚠️ Sorunlu'], key=f'durum_{i}_{alt}', horizontal=True, label_visibility='collapsed')
            aciklama = r2.text_input('Açıklama', key=f'aciklama_{i}_{alt}', placeholder='açıklama...', label_visibility='collapsed')
            cevaplar.append((soru, 'Sorunlu' if 'Sorunlu' in durum else 'Tamam', aciklama))
            st.divider()
        if st.form_submit_button(f'💾 {alt.split(".")[0]}. Grup — Kaydet ({len(sorular)} soru)', type='primary', use_container_width=True):
            rows = []
            for soru, durum, aciklama in cevaplar:
                rows.append({'Tarih':str(secilen_tarih),'Bolum':bolum,'Alt_Grup':alt,'Soru':soru,'Durum':durum,'Aciklama':aciklama,'Kontrol_Eden':kontrol_eden,'Puan':100 if durum=='Tamam' else 0,'Sablon_ID':'','Lokasyon_ID':''})
            if rows:
                df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
                save_data(df, 'checklist')
                log_ekle('checklist', f'{bolum}/{alt}', kontrol_eden, 'Kontrol kaydedildi', f'{len(rows)} soru')
                st.success('Kontrol kaydedildi.'); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def _template(secilen_tarih: date):
    df_s = load_data('sablon')
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    card('Şablon ile Kontrol', 'Tekrar kullanılabilir denetim / checklist şablonları')
    if df_s.empty:
        st.info('Henüz şablon yok. Yönetim > Şablonlar ekranından şablon oluşturabilirsiniz.')
    else:
        data_table(df_s, [('Sablon_ID','ID'),('Ad','Şablon'),('Kategori','Kategori'),('Olusturan','Oluşturan'),('Tarih','Tarih'),('Puanlama_Aktif','Puanlama')], id_cols=['Sablon_ID'], bool_cols=['Puanlama_Aktif'])
    st.markdown('</div>', unsafe_allow_html=True)

def _summary(secilen_tarih: date):
    df = load_data('checklist')
    today = df[df.get('Tarih','') == str(secilen_tarih)] if not df.empty and 'Tarih' in df.columns else pd.DataFrame()
    total = len(today); sorunlu = int((today.get('Durum',pd.Series(dtype=str))=='Sorunlu').sum()) if not today.empty else 0
    score = int(100 - (sorunlu / total * 100)) if total else 0
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card('Bugünkü Soru', total, '📋')
    with c2: kpi_card('Sorunlu', sorunlu, '⚠️')
    with c3: kpi_card('Skor', f'%{score}', '📊', progress=score)
    with c4: kpi_card('Kontrol Grubu', today[['Bolum','Alt_Grup']].drop_duplicates().shape[0] if not today.empty else 0, '✅')
    st.write('')
    data_table(today, [('Tarih','Tarih'),('Bolum','Bölüm'),('Alt_Grup','Alt Grup'),('Soru','Soru'),('Durum','Durum'),('Aciklama','Açıklama'),('Kontrol_Eden','Kontrol Eden')], status_cols=['Durum'], avatar_cols=['Kontrol_Eden'], empty_msg='Bugün kontrol kaydı yok.')
