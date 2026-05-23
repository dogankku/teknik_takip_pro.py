from __future__ import annotations
from datetime import datetime, date
import pandas as pd
import streamlit as st
from db import load_data, save_data
from constants import TALEP_KATEGORI, ONCELIK_SLA
from barkod import yeni_id
from style import section_header, data_table, kpi_card, card
try:
    from aktivite_helper import log_ekle
except Exception:
    def log_ekle(*a, **k): pass

DURUMLAR = ['Açık','Atandı','Devam','Tamamlandı','İptal']

def render(secilen_tarih: date):
    section_header('Talepler', f'{secilen_tarih.strftime("%d.%m.%Y")} — sakin ve operasyon talepleri', pill='MÜLK YÖNETİMİ')
    df = load_data('talep')
    df_p = load_data('personel')
    pl = df_p['Isim'].dropna().astype(str).tolist() if not df_p.empty and 'Isim' in df_p.columns else ['Ahmet Yılmaz','Mehmet Kaya','Hasan Demir']
    mode = st.radio('Görünüm', ['📨 Talep Listesi','➕ Yeni Talep','📊 SLA Özeti'], horizontal=True, label_visibility='collapsed')
    st.divider()
    if mode.startswith('📨'):
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi_card('Toplam', len(df), '📨')
        with c2: kpi_card('Açık', int(df.get('Durum',pd.Series(dtype=str)).isin(['Açık','Atandı','Devam']).sum()) if not df.empty else 0, '🔥')
        with c3: kpi_card('Tamamlanan', int((df.get('Durum',pd.Series(dtype=str))=='Tamamlandı').sum()) if not df.empty else 0, '✅')
        with c4: kpi_card('Kritik', int((df.get('Oncelik',pd.Series(dtype=str))=='Kritik').sum()) if not df.empty else 0, '⚠️')
        st.write('')
        f1,f2,f3,f4 = st.columns([1,1,1,1.6])
        durum = f1.multiselect('Durum', DURUMLAR, default=['Açık','Atandı','Devam'])
        kategori = f2.multiselect('Kategori', TALEP_KATEGORI)
        atanan = f3.selectbox('Atanan', ['Tümü']+pl)
        q = f4.text_input('Ara', placeholder='🔍 daire, sakin, başlık...')
        g = df.copy()
        if durum and 'Durum' in g.columns: g = g[g['Durum'].isin(durum)]
        if kategori and 'Kategori' in g.columns: g = g[g['Kategori'].isin(kategori)]
        if atanan != 'Tümü' and 'Atanan' in g.columns: g = g[g['Atanan']==atanan]
        if q and not g.empty: g = g[g.astype(str).agg(' '.join, axis=1).str.lower().str.contains(q.lower(), na=False)]
        if {'Tarih','Saat'}.issubset(g.columns): g['Tarih_Saat'] = g['Tarih'].astype(str)+' '+g['Saat'].astype(str).str[:5]
        data_table(g, [('Talep_ID','ID'),('Tarih_Saat','Tarih'),('Daire_ID','Daire'),('Sakin','Sakin'),('Kategori','Kategori'),('Baslik','Başlık'),('Oncelik','Öncelik'),('Atanan','Atanan'),('Durum','Durum')], status_cols=['Durum'], priority_cols=['Oncelik'], avatar_cols=['Atanan'], id_cols=['Talep_ID'])
    elif mode.startswith('➕'):
        st.markdown('<div class="form-card">', unsafe_allow_html=True); card('Yeni Talep', 'Sakin, personel veya yönetim adına talep oluşturun')
        with st.form('new_talep_pro'):
            c1,c2,c3 = st.columns(3)
            daire = c1.text_input('Daire ID')
            sakin = c2.text_input('Sakin / bildiren')
            kat = c3.selectbox('Kategori', TALEP_KATEGORI)
            baslik = st.text_input('Başlık *')
            aciklama = st.text_area('Açıklama *')
            c4,c5,c6 = st.columns(3)
            oncelik = c4.selectbox('Öncelik', ['Normal','Yüksek','Kritik','Düşük'])
            atanan = c5.selectbox('Atanan', pl)
            durum = c6.selectbox('Durum', ['Açık','Atandı'])
            if st.form_submit_button('➕ Talep Kaydet', type='primary', use_container_width=True):
                if not baslik.strip() or not aciklama.strip(): st.error('Başlık ve açıklama zorunlu.'); return
                tid = yeni_id('TLP')
                row = {'Talep_ID':tid,'Tarih':str(secilen_tarih),'Saat':datetime.now().strftime('%H:%M'),'Daire_ID':daire,'Sakin':sakin,'Kategori':kat,'Baslik':baslik,'Aciklama':aciklama,'Oncelik':oncelik,'Durum':durum,'Atanan':atanan,'SLA_Saat':ONCELIK_SLA.get(oncelik,72),'Cozum_Tarihi':'','Cozum_Notu':'','Lokasyon_ID':'','Sure_Saat':0,'Malzeme_Maliyet':0,'Iscilik_Maliyet':0}
                df = pd.concat([df,pd.DataFrame([row])], ignore_index=True); save_data(df,'talep'); log_ekle('talep',tid,atanan,'Oluşturuldu',baslik)
                # ── Bildirim ──
                try:
                    tetikler = st.session_state.get("bildirim_tetikler", {})
                    if tetikler.get("talep_yeni", True):
                        from bildirim_helper import bildirim_gonder, personel_iletisim
                        email_s, tel_s = personel_iletisim(atanan) if atanan else ("", "")
                        bildirim_gonder(
                            baslik=f"📨 Yeni Talep: {tid}",
                            icerik=f"Başlık: {baslik}\nÖncelik: {oncelik}\nDaire: {daire}\nAtanan: {atanan or 'Atanmadı'}",
                            email_list=[email_s] if email_s else [],
                            telefon_list=[tel_s] if tel_s else [],
                        )
                except Exception:
                    pass
                st.success(f'Talep oluşturuldu: {tid}'); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if df.empty: st.info('SLA analizi için kayıt yok.'); return
        st.bar_chart(df['Oncelik'].value_counts() if 'Oncelik' in df.columns else pd.Series(dtype=int))
