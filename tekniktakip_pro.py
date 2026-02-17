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
# 2. VERİTABANI VE SORU GRUPLARI (HATA ÖNLEYİCİ ÜÇLÜ TIRNAK)
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

# SORU GRUPLARI (Gruplandırılmış ve Kopyalamaya Dayanıklı)
SORU_GRUPLARI = {
    "Elektrik": {
        "Asansörler & Dış Cephe": [
            """1. ASANSÖRLER NORMAL ÇALIŞIYOR MU? ARIZA VEYA ŞİKAYET OLDU MU?""",
            """2. A KULE-B KULE ASANSÖR MAK.DAİRESİ KLİMALAR ÇALIŞIYOR MU?""",
            """3. SOKAK VE BAHÇE AYDINLATMALARI YANIYOR MU?""",
            """4. BİNA DIŞ CEPHE KAYAR IŞIKLAR VE ANTHİLL YAZILARI NORMAL Mİ?"""
        ],
        "Klima & Havalandırma (Elektrik)": [
            """5. TV ODASI KLİMASI ÇALIŞIYOR MU? MEKAN TEMİZ Mİ?""",
            """6. UPS ODASI KLİMASI ÇALIŞIYOR MU? MEKAN TEMİZ Mİ?"""
        ],
        "Jeneratörler & Trafolar": [
            """7. A-B KULE JENERATÖR KUMANDA PANELLERİ NORMAL KONUMDA MI?""",
            """8. JENERATÖRLER MAZOT TANKLARI KONTROLLERİ NORMAL Mİ?""",
            """9. JENERATÖR ANA TANK MAZOT SEVİYESİ KAÇ SANTİM?""",
            """10. TRAFO KORİDORLARI, JENERATÖR ODASI, DAĞITIM ODALARI TEMİZ Mİ?""",
            """11. RESTORAN JENERATÖRÜ KUMANDA PANELİ NORMAL Mİ?"""
        ]
    },
    "Mekanik": {
        "Devir Teslim & Genel": [
            """1. Bir önceki vardiyadan kalan iş var mı?""",
            """2. Bir önceki vardiyadan kalan işler yapıldı mı?"""
        ],
        "A Blok - Kazan Dairesi": [
            """3. Kazanlarda/panolarda arıza ışığı, su kaçağı var mı?""",
            """4. Su basınçları istenen barda mı?""",
            """5. Mekan temiz mi?""",
            """6. Taze hava ve eksoz santralleri çalışıyor mu?"""
        ],
        "A Blok - 25. Kat Teknik Oda": [
            """7. Elektrik panolarında yanan arıza ışığı var mı?""",
            """8. Isıtma sirkülasyon pompaları çalışıyor mu? Basınç normal mi?""",
            """9. Soğutma sirkülasyon pompaları çalışıyor mu? Basınç normal mi?""",
            """10. Su kaçağı var mı?""",
            """11. Su deposu ve hidroforlar normal mi?""",
            """12. Yangın depoları dolu mu? Sistem basıncı normal mi?""",
            """13. Mekan temiz mi?""",
            """14. Taze hava ve eksoz santralleri çalışıyor mu?"""
        ],
        "A Blok - 1. Bodrum": [
            """15. Elektrik panolarında yanan arıza ışığı var mı?""",
            """16. Isıtma sirkülasyon pompaları çalışıyor mu?""",
            """17. Soğutma sirkülasyon pompaları çalışıyor mu?""",
            """18. Mekan temiz mi?""",
            """19. Taze hava ve eksoz santralleri çalışıyor mu?"""
        ],
        "Su & Yangın Sistemleri (Ortak Alan)": [
            """20. Kullanma Suyu ve Arıtma: Basınç normal mi?""",
            """21. Kullanma Suyu ve Arıtma: Su kaçağı var mı?""",
            """22. Yangın Pompa Odası: Depo dolu mu? Basınç normal mi?""",
            """23. Hidrofor ve pompa daireleri temiz mi?"""
        ],
        "Sosyal Tesis & Mutfaklar": [
            """24. Sosyal Tesis: Pano arızası veya su kaçağı var mı?""",
            """25. Sosyal Tesis: Mekan temiz mi?""",
            """26. Sosyal tesis taze hava santralleri çalışıyor mu?""",
            """32. 1. Bodrum Mutfak: Su kaçağı var mı?""",
            """33. Zemin Kat Restoran: Pano arızası/su kaçağı var mı?""",
            """34. Restoran/Mutfak mekanları temiz mi?""",
            """35. Restoran/Mutfak havalandırmaları çalışıyor mu?"""
        ],
        "B Blok - 1. Bodrum": [
            """27. Elektrik panolarında arıza ışığı var mı?""",
            """28. Isıtma sirkülasyon pompaları çalışıyor mu?""",
            """29. Soğutma sirkülasyon pompaları çalışıyor mu?""",
            """30. Mekan temiz mi?""",
            """31. Taze hava ve eksoz santralleri çalışıyor mu?"""
        ],
        "B Blok - 25. Kat Teknik Oda": [
            """36. Elektrik panolarında arıza ışığı var mı?""",
            """37. Isıtma sirkülasyon pompaları çalışıyor mu?""",
            """38. Soğutma sirkülasyon pompaları çalışıyor mu?""",
            """39. Su kaçağı var mı?""",
            """40. Su deposu ve hidroforlar normal mi?""",
            """41. Yangın depoları dolu mu?""",
            """42. Mekan temiz mi?""",
            """43. Taze hava ve eksoz santralleri çalışıyor mu?"""
        ],
        "B Blok - Kazan Dairesi": [
            """44. Arıza ışığı veya su kaçağı var mı?""",
            """45. Su basınçları istenen barda mı?""",
            """46. Mekan temiz mi?"""
        ],
        "5. Bodrum & Otomasyon": [
            """47. Pompaların panolarında arıza ışığı var mı?""",
            """48. Pompalar otomatik konumda mı?""",
            """49. Otomasyon ekranında çalışmayan ekipman görünüyor mu?"""
        ]
    },
    "Engineering": {
        "Genel Denetim": [
            """1. Sokak ve bahçe aydınlatmaları yanıyor mu?""",
            """2. Cam üstü led yanıyor mu?""",
            """3. Vardiya defteri incelendi mi?""",
            """4. Önceki vardiyadan iş kaldı mı?""",
            """48. Vardiyada olumsuzluk yaşandı mı?""",
            """49. Kayar ışıklar normal mi?""",
            """50. Asansör müzikleri çalışıyor mu?"""
        ],
        "A Blok Denetimi": [
            """6. A Blok Asansör Klimaları çalışıyor mu?""",
            """7. A Blok Kazan Dairesi genel durumu normal mi?""",
            """10. A Blok 25. Kat genel durumu normal mi?""",
            """17. A Blok 1. Bodrum genel durumu normal mi?"""
        ],
        "B Blok Denetimi": [
            """27. B Blok 1. Bodrum genel durumu normal mi?""",
            """34. B Blok 25. Kat genel durumu normal mi?""",
            """41. B Blok Kazan Dairesi genel durumu normal mi?""",
            """44. B Blok Asansör Klimaları çalışıyor mu?"""
        ]
    }
}

# -----------------------------------------------------------------------------
# 3. YAN MENÜ
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
# 4. MODÜL: ANA SAYFA
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
# 5. MODÜL: KONTROL LİSTELERİ (YENİ GRUPLU YAPI)
# -----------------------------------------------------------------------------
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Günlük Kontroller ({secilen_tarih})")
    
    df_check = load_data("checklist", ["Tarih", "Bolum", "Alt_Grup", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_pers = load_data("personel", ["Isim"])
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    # Sekmeler
    tabs = st.tabs(list(SORU_GRUPLARI.keys()))

    for i, bolum in enumerate(SORU_GRUPLARI.keys()):
        with tabs[i]:
            st.subheader(f"📋 {bolum} Kontrol Formu")
            
            # Personel Seçimi
            col_p1, col_p2 = st.columns([1,3])
            with col_p1:
                kontrolcu = st.selectbox(f"Kontrol Eden ({bolum})", personel_listesi, key=f"user_{bolum}")
            
            # --- GRUPLARI DÖNGÜYE AL ---
            bolum_sorulari = SORU_GRUPLARI[bolum]
            
            for alt_grup, sorular in bolum_sorulari.items():
                with st.expander(f"📍 {alt_grup} ({len(sorular)} Soru)", expanded=False):
                    
                    # Kayıt Kontrolü
                    tarih_str = str(secilen_tarih)
                    try:
                        kayitli_grup = df_check[
                            (df_check["Tarih"] == tarih_str) & 
                            (df_check["Bolum"] == bolum) & 
                            (df_check["Alt_Grup"] == alt_grup)
                        ]
                    except KeyError:
                        kayitli_grup = pd.DataFrame() # Eski veri formatı hatasını önle

                    if not kayitli_grup.empty:
                        st.info("✅ Bu bölüm tamamlanmış.")
                        st.dataframe(kayitli_grup[["Soru", "Durum", "Aciklama"]], use_container_width=True)
                    else:
                        with st.form(f"form_{bolum}_{alt_grup}"):
                            st.caption("💡 İpucu: Sorun yoksa açıklama yazmadan geçebilirsiniz.")
                            
                            cevaplar = []
                            for idx, soru in enumerate(sorular):
                                c1, c2, c3 = st.columns([6, 2, 3])
                                c1.write(soru)
                                durum = c2.radio("D", ["Tamam", "Sorunlu"], key=f"rd_{bolum}_{alt_grup}_{idx}", horizontal=True, label_visibility="collapsed")
                                not_txt = c3.text_input("Not", key=f"nt_{bolum}_{alt_grup}_{idx}", placeholder="Varsa not...")
                                
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
                                st.success(f"{alt_grup} kaydedildi!")
                                st.rerun()

# -----------------------------------------------------------------------------
# 6. MODÜL: YÖNETİCİ GİRİŞİ / ÇIKIŞI
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
# 7. MODÜL: GÜNLÜK RAPOR
# -----------------------------------------------------------------------------
elif menu == "📊 GÜNLÜK RAPOR":
    st.header(f"📊 Rapor ({secilen_tarih})")
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama"])
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    
    t = str(secilen_tarih)
    gc = df_c[df_c["Tarih"] == t]
    ga = df_a[df_a["Tarih"] == t]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Kontrol Edilen Madde", len(gc))
    c2.metric("Arıza Sayısı", len(ga))
    sorunlu_list = gc[gc["Durum"]=="Sorunlu"] if not gc.empty else pd.DataFrame()
    c3.metric("Sorunlu Madde", len(sorunlu_list))
    
    st.subheader("⚠️ Sorunlu Kontroller")
    if not sorunlu_list.empty:
        st.dataframe(sorunlu_list, use_container_width=True)
    else:
        st.info("Sorun yok.")
    
    st.subheader("🛠️ Arızalar")
    st.dataframe(ga, use_container_width=True)

# -----------------------------------------------------------------------------
# 8. DİĞER MODÜLLER (ARIZA, VARDİYA, PERSONEL)
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
