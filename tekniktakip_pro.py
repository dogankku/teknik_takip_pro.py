import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢"
)

# Dosya İsimleri
FILES = {
    "checklist": "veritabani_checklist.csv",
    "ariza": "veritabani_arizalar.csv",
    "vardiya": "veritabani_vardiya.csv",
    "personel": "veritabani_personel.csv",
    "sorular": "veritabani_sorular.csv"
}

# -----------------------------------------------------------------------------
# 2. VERİTABANI YÖNETİMİ
# -----------------------------------------------------------------------------
def load_data(key, columns=None):
    if os.path.exists(FILES[key]):
        try:
            return pd.read_csv(FILES[key])
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# -----------------------------------------------------------------------------
# 3. SORU GRUPLARI (DÜZELTİLMİŞ LİSTE)
# -----------------------------------------------------------------------------
# Mekanik içindeki "Pano" soruları Elektrik bölümüne taşındı.

SORU_GRUPLARI = {
    "Elektrik": {
        "Genel Aydınlatma & Sistemler": [
            """1. ASANSÖRLER NORMAL ÇALIŞIYOR MU? ARIZA/ŞİKAYET VAR MI?""",
            """2. SOKAK VE BAHÇE AYDINLATMALARI YANIYOR MU?""",
            """3. BİNA DIŞ CEPHE KAYAR IŞIKLAR VE YAZILAR ÇALIŞIYOR MU?""",
            """4. TV VE UPS ODASI KLİMALARI ÇALIŞIYOR MU?"""
        ],
        "Jeneratör & Trafo": [
            """5. JENERATÖR KUMANDA PANELLERİ NORMAL KONUMDA MI?""",
            """6. JENERATÖR MAZOT TANKI SEVİYELERİ VE KONTROLLERİ NORMAL Mİ?""",
            """7. TRAFO, JENERATÖR VE DAĞITIM ODALARI TEMİZ Mİ?""",
            """8. RESTORAN JENERATÖRÜ KUMANDA PANELİ NORMAL Mİ?"""
        ],
        "Teknik Odalar Pano Kontrolleri (Mekanik Odalar)": [
            """9. A Blok Kazan Dairesi: Elektrik panolarında arıza ışığı var mı?""",
            """10. A Blok 25. Kat: Elektrik panolarında arıza ışığı var mı?""",
            """11. A Blok 1. Bodrum: Elektrik panolarında arıza ışığı var mı?""",
            """12. Sosyal Tesis: Elektrik panolarında arıza ışığı var mı?""",
            """13. B Blok 1. Bodrum: Elektrik panolarında arıza ışığı var mı?""",
            """14. Zemin Kat Restoran: Elektrik panolarında arıza ışığı var mı?""",
            """15. B Blok 25. Kat: Elektrik panolarında arıza ışığı var mı?""",
            """16. B Blok Kazan Dairesi: Elektrik panolarında arıza ışığı var mı?""",
            """17. 5. Bodrum: Pompaların panolarında arıza ışığı var mı?""",
            """18. Otomasyon ekranında çalışmayan (kırmızı) ekipman var mı?"""
        ]
    },
    "Mekanik": {
        "Genel Kontroller": [
            """1. Bir önceki vardiyadan kalan iş var mı?""",
            """2. Bir önceki vardiyadan kalan işler yapıldı mı?"""
        ],
        "A Blok - Kazan Dairesi & Havalandırma": [
            """3. Kazanlarda su kaçağı veya basınç sorunu var mı?""",
            """4. Sirkülasyon pompaları normal çalışıyor mu?""",
            """5. Taze hava ve eksoz santralleri çalışıyor mu?""",
            """6. Mekan temiz mi?"""
        ],
        "A Blok - 25. Kat Teknik Oda": [
            """7. Isıtma/Soğutma sirkülasyon pompaları çalışıyor mu?""",
            """8. Su basınçları normal mi?""",
            """9. Su deposu, hidrofor ve yangın depoları normal mi?""",
            """10. Su kaçağı var mı?""",
            """11. Havalandırma santralleri çalışıyor mu?"""
        ],
        "A Blok - 1. Bodrum": [
            """12. Isıtma/Soğutma pompaları çalışıyor mu?""",
            """13. Su basınçları normal mi?""",
            """14. Havalandırma santralleri çalışıyor mu?""",
            """15. Mekan temiz mi?"""
        ],
        "Su & Yangın Sistemleri": [
            """16. Kullanma Suyu Hidroforları basıncı normal mi?""",
            """17. Yangın Pompa Odası: Depolar dolu ve basınç normal mi?""",
            """18. Arıtma sistemleri ve pompalar normal mi?""",
            """19. Dairelerde su kaçağı var mı?"""
        ],
        "Sosyal Tesis & Mutfaklar": [
            """20. Sosyal Tesis: Su kaçağı veya mekanik arıza var mı?""",
            """21. Sosyal Tesis: Havalandırma çalışıyor mu?""",
            """22. Mutfak ve Restoran: Su kaçağı var mı?""",
            """23. Mutfak ve Restoran: Havalandırma çalışıyor mu?"""
        ],
        "B Blok - 1. Bodrum": [
            """24. Isıtma/Soğutma pompaları çalışıyor mu?""",
            """25. Havalandırma santralleri çalışıyor mu?""",
            """26. Su kaçağı var mı?"""
        ],
        "B Blok - 25. Kat Teknik Oda": [
            """27. Isıtma/Soğutma pompaları çalışıyor mu?""",
            """28. Su deposu, hidrofor ve yangın depoları normal mi?""",
            """29. Su kaçağı var mı?""",
            """30. Havalandırma santralleri çalışıyor mu?"""
        ],
        "B Blok - Kazan Dairesi": [
            """31. Su basınçları istenen barda mı?""",
            """32. Su kaçağı var mı?""",
            """33. Mekan temiz mi?"""
        ],
        "5. Bodrum Pompalar": [
            """34. Pompalar otomatik konumda mı?""",
            """35. Herhangi bir su kaçağı veya anormal ses var mı?"""
        ]
    },
    "Engineering": {
        "Genel Denetim": [
            """1. Sokak, bahçe ve cephe aydınlatmaları kontrol edildi mi?""",
            """2. Vardiya defteri ve önceki işler kontrol edildi mi?""",
            """3. Tüm teknik hacimlerin (Kazan dairesi, 25. Kat vb.) genel temizliği uygun mu?""",
            """4. Asansör müzikleri ve klimaları çalışıyor mu?""",
            """5. Kayar ışıklar ve ledler yanıyor mu?""",
            """6. Vardiya boyunca olağandışı bir durum yaşandı mı?"""
        ]
    }
}

# -----------------------------------------------------------------------------
# 4. YAN MENÜ
# -----------------------------------------------------------------------------
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

with st.sidebar:
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    
    if st.session_state['admin_logged_in']:
        menu = st.radio("Menü", ["🏠 Ana Sayfa", "📊 GÜNLÜK RAPOR", "👥 Personel", "✅ Kontrol Listeleri", "🛠️ Arıza Takip", "🔄 Vardiya Defteri", "🚪 Çıkış"])
        st.success("Yönetici Modu")
    else:
        menu = st.radio("Menü", ["🏠 Ana Sayfa", "✅ Kontrol Listeleri", "🛠️ Arıza Takip", "🔄 Vardiya Defteri", "🔐 Yönetici Girişi"])
    
    st.markdown("---")
    secilen_tarih = st.date_input("Tarih", date.today())

# -----------------------------------------------------------------------------
# 5. MODÜL: ANA SAYFA
# -----------------------------------------------------------------------------
if menu == "🏠 Ana Sayfa":
    st.header("👋 Hoşgeldiniz")
    st.write(f"**Tarih:** {secilen_tarih.strftime('%d.%m.%Y')}")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.info("✅ **Kontrol Listeleri**\n\nLokasyon bazlı, hızlı giriş ekranı.")
    c2.warning("🛠️ **Arıza Takip**\n\nArıza kayıt ve takip sistemi.")
    c3.success("🔄 **Vardiya Defteri**\n\nDijital vardiya teslim tutanağı.")

# -----------------------------------------------------------------------------
# 6. MODÜL: KONTROL LİSTELERİ
# -----------------------------------------------------------------------------
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Günlük Kontroller ({secilen_tarih})")
    
    df_check = load_data("checklist", ["Tarih", "Bolum", "Alt_Grup", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_pers = load_data("personel", ["Isim"])
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    tabs = st.tabs(list(SORU_GRUPLARI.keys()))

    for i, bolum in enumerate(SORU_GRUPLARI.keys()):
        with tabs[i]:
            st.subheader(f"📋 {bolum} Kontrol Formu")
            
            c_p1, c_p2 = st.columns([1,3])
            with c_p1:
                kontrolcu = st.selectbox(f"Kontrol Eden ({bolum})", personel_listesi, key=f"user_{bolum}")
            
            bolum_sorulari = SORU_GRUPLARI[bolum]
            
            for alt_grup, sorular in bolum_sorulari.items():
                with st.expander(f"📍 {alt_grup} ({len(sorular)} Soru)", expanded=False):
                    
                    tarih_str = str(secilen_tarih)
                    try:
                        kayitli_grup = df_check[
                            (df_check["Tarih"] == tarih_str) & 
                            (df_check["Bolum"] == bolum) & 
                            (df_check["Alt_Grup"] == alt_grup)
                        ]
                    except KeyError:
                        kayitli_grup = pd.DataFrame()

                    if not kayitli_grup.empty:
                        st.success("✅ Tamamlandı")
                        st.dataframe(kayitli_grup[["Soru", "Durum", "Aciklama"]], use_container_width=True)
                    else:
                        with st.form(f"form_{bolum}_{alt_grup}"):
                            st.caption("💡 İpucu: Sorun yoksa açıklama yazmadan geçebilirsiniz.")
                            cevaplar = []
                            for idx, soru in enumerate(sorular):
                                c1, c2, c3 = st.columns([6, 2, 3])
                                c1.write(soru)
                                durum = c2.radio("D", ["Tamam", "Sorunlu"], key=f"rd_{bolum}_{alt_grup}_{idx}", horizontal=True, label_visibility="collapsed")
                                not_txt = c3.text_input("Not", key=f"nt_{bolum}_{alt_grup}_{idx}")
                                
                                cevaplar.append({
                                    "Tarih": tarih_str,
                                    "Bolum": bolum,
                                    "Alt_Grup": alt_grup,
                                    "Soru": soru,
                                    "Durum": durum,
                                    "Aciklama": not_txt,
                                    "Kontrol_Eden": kontrolcu
                                })
                                st.divider()
                            
                            if st.form_submit_button(f"💾 {alt_grup} KAYDET"):
                                yeni_df = pd.DataFrame(cevaplar)
                                df_check = pd.concat([df_check, yeni_df], ignore_index=True)
                                save_data(df_check, "checklist")
                                st.rerun()

# -----------------------------------------------------------------------------
# 7. MODÜL: YÖNETİCİ GİRİŞİ / ÇIKIŞI
# -----------------------------------------------------------------------------
elif menu == "🔐 Yönetici Girişi":
    st.header("🔐 Yönetici Girişi")
    with st.form("login"):
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş"):
            if p == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else: st.error("Hatalı")
elif menu == "🚪 Çıkış":
    st.session_state['admin_logged_in'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 8. MODÜL: GÜNLÜK RAPOR
# -----------------------------------------------------------------------------
elif menu == "📊 GÜNLÜK RAPOR":
    st.header(f"📊 Rapor ({secilen_tarih})")
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama"])
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    
    t = str(secilen_tarih)
    gc = df_c[df_c["Tarih"] == t]
    ga = df_a[df_a["Tarih"] == t]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Kontrol", len(gc))
    c2.metric("Arıza", len(ga))
    sorunlu = gc[gc["Durum"]=="Sorunlu"] if not gc.empty else pd.DataFrame()
    c3.metric("Sorunlu", len(sorunlu))
    
    st.subheader("⚠️ Sorunlar")
    if not sorunlu.empty: st.dataframe(sorunlu, use_container_width=True)
    else: st.info("Sorun yok.")
    
    st.subheader("🛠️ Arızalar")
    st.dataframe(ga, use_container_width=True)

# -----------------------------------------------------------------------------
# 9. DİĞER MODÜLLER
# -----------------------------------------------------------------------------
elif menu == "🛠️ Arıza Takip":
    st.header("🛠️ Arıza Kayıtları")
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_p = load_data("personel", ["Isim"])
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.expander("➕ Arıza Ekle"):
        with st.form("add_a"):
            b = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
            l = st.text_input("Lokasyon")
            s = st.selectbox("Sorumlu", pl)
            d = st.text_area("Tanım")
            stt = st.selectbox("Durum", ["Açık", "Devam Ediyor", "Tamamlandı"])
            if st.form_submit_button("Kaydet"):
                row = {"Tarih": str(secilen_tarih), "Saat": datetime.now().strftime("%H:%M"), "Bolum":b, "Lokasyon":l, "Ariza_Tanimi":d, "Sorumlu":s, "Durum":stt}
                df_a = pd.concat([df_a, pd.DataFrame([row])], ignore_index=True)
                save_data(df_a, "ariza")
                st.rerun()
    st.dataframe(df_a.sort_values(by="Tarih", ascending=False), use_container_width=True)

elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Defteri")
    df_v = load_data("vardiya", ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar"])
    df_p = load_data("personel", ["Isim"])
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]
    
    with st.form("add_v"):
        v = st.selectbox("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
        te = st.selectbox("Teslim Eden", pl, key="te")
        ta = st.selectbox("Teslim Alan", pl, key="ta")
        n = st.text_area("Notlar")
        if st.form_submit_button("Kaydet"):
            row = {"Tarih": str(secilen_tarih), "Vardiya":v, "Teslim_Eden":te, "Teslim_Alan":ta, "Notlar":n}
            df_v = pd.concat([df_v, pd.DataFrame([row])], ignore_index=True)
            save_data(df_v, "vardiya")
            st.rerun()
    st.dataframe(df_v.sort_values(by="Tarih", ascending=False), use_container_width=True)

elif menu == "👥 Personel":
    st.header("👥 Personel")
    df_p = load_data("personel", ["Isim", "Gorev"])
    with st.form("add_p"):
        i = st.text_input("İsim")
        g = st.text_input("Görev")
        if st.form_submit_button("Ekle"):
            df_p = pd.concat([df_p, pd.DataFrame([{"Isim":i, "Gorev":g}])], ignore_index=True)
            save_data(df_p, "personel")
            st.rerun()
    st.dataframe(df_p, use_container_width=True)
