import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. SABİT SORU LİSTELERİ (DOSYALARINDAN ÇEKİLENLER)
# -----------------------------------------------------------------------------

SORULAR_ELEKTRIK = [
    "1. Asansörler normal çalışıyor mu? Arıza veya şikayet oldu mu?",
    "2. A Kule-B Kule asansör mak. dairesi klimalar çalışıyor mu? Genel mekan temiz mi?",
    "3. Sokak ve bahçe aydınlatmaları yanıyor mu?",
    "4. Bina dış cephe kayar ışıklar ve Anthill yazıları normal çalışıyor mu?",
    "5. TV odası kliması çalışıyor mu? Genel mekan temiz mi?",
    "6. UPS odası kliması çalışıyor mu? Genel mekan temiz mi?",
    "7. A-B Kule jeneratör kumanda panelleri normal konumda mı?",
    "8. Jeneratörler mazot tankları kontrolleri normal mi?",
    "9. Jeneratör ana tank mazot seviyesi kontrol edildi mi?",
    "10. Trafo koridorları, jeneratör odası, ana dağıtım odaları temiz mi?",
    "11. Restoran jeneratörü kumanda paneli normal konumda mı?"
]

SORULAR_MEKANIK = [
    "1. Bir önceki vardiyadan kalan iş var mı?",
    "2. A Blok-Kazan Dairesi: Arıza ışığı, su kaçağı veya pompa arızası var mı?",
    "3. A Blok-Kazan Dairesi: Su basınçları istenen barda mı?",
    "4. A Blok taze hava ve egzoz santralleri çalışıyor mu?",
    "5. A Blok-25. Kat: Elektrik panolarında yanan arıza ışığı var mı?",
    "6. A Blok-25. Kat: Isıtma/Soğutma pompaları çalışıyor mu? Basınçlar normal mi?",
    "7. A Blok-25. Kat: Su kaçağı var mı? Mekan temiz mi?",
    "8. A Blok-25. Kat: Su depo seviyeleri ve hidroforlar normal mi?",
    "9. A Blok-25. Kat: Yangın depoları dolu mu? Sistem basıncı normal mi?",
    "10. A Blok 1. Bodrum Kat: Panolarda arıza ışığı veya su kaçağı var mı?"
]

SORULAR_GENEL = [
    "1. Sokak ve bahçe aydınlatmaları yanıyor mu?",
    "2. Cam üstü led yanıyor mu?",
    "3. Vardiya defteri incelendi mi?",
    "4. Bir önceki vardiyadan kalan işler yapıldı mı?",
    "5. A Blok-Asansör Makine Dairesi: Klimalar çalışıyor mu?",
    "6. Kazan daireleri genel kontrolü yapıldı mı?",
    "7. Yangın sistem basınçları kontrol edildi mi?"
]

# -----------------------------------------------------------------------------
# 2. AYARLAR VE DOSYA YÖNETİMİ
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Teknik Operasyon Sistemi", layout="wide", page_icon="🏢")

FILES = {
    "checklist": "veritabani_checklist.csv",
    "ariza": "veritabani_arizalar.csv",
    "vardiya": "veritabani_vardiya.csv",
    "personel": "veritabani_personel.csv"
}

def load_data(key, columns):
    if os.path.exists(FILES[key]):
        return pd.read_csv(FILES[key])
    return pd.DataFrame(columns=columns)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# -----------------------------------------------------------------------------
# 3. YAN MENÜ
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    menu = st.radio("Menü", ["✅ Sabah Kontrol Listeleri", "🛠️ Arıza ve İş Takip", "🔄 Vardiya Defteri", "👥 Personel"])
    st.markdown("---")
    
    # Tarih seçici (Global)
    secilen_tarih = st.date_input("İşlem Tarihi", date.today())

# -----------------------------------------------------------------------------
# 4. MODÜL: SABAH KONTROL LİSTELERİ (CHECKLIST)
# -----------------------------------------------------------------------------
if menu == "✅ Sabah Kontrol Listeleri":
    st.header(f"✅ Günlük Kontrol Listeleri ({secilen_tarih.strftime('%d.%m.%Y')})")
    
    # Personel Yükle
    df_per = load_data("personel", ["Isim"])
    personel_list = df_per["Isim"].tolist() if not df_per.empty else ["Belirtilmedi"]
    
    # Geçmiş Kayıtları Yükle
    df_check = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    
    tab1, tab2, tab3 = st.tabs(["⚡ ELEKTRİK LİSTESİ", "🔧 MEKANİK LİSTESİ", "📋 GENEL (LOG BOOK)"])
    
    def checklist_form(bolum_adi, sorular_listesi, key_prefix):
        # O gün o bölüm için kayıt var mı kontrol et
        gunluk_kayit = df_check[
            (df_check["Tarih"] == secilen_tarih.strftime("%Y-%m-%d")) & 
            (df_check["Bolum"] == bolum_adi)
        ]
        
        if not gunluk_kayit.empty:
            st.success(f"✅ {bolum_adi} için {secilen_tarih.strftime('%d.%m.%Y')} tarihli kontroller tamamlanmış.")
            with st.expander("Kaydedilen Kontrolleri Gör"):
                st.dataframe(gunluk_kayit[["Soru", "Durum", "Aciklama", "Kontrol_Eden"]], use_container_width=True)
        else:
            st.info(f"📝 {bolum_adi} kontrolü henüz yapılmamış.")
            with st.form(f"form_{key_prefix}"):
                kontrol_eden = st.selectbox("Kontrol Eden Teknisyen", personel_list, key=f"user_{key_prefix}")
                
                cevaplar = []
                for i, soru in enumerate(sorular_listesi):
                    c1, c2, c3 = st.columns([3, 1, 2])
                    with c1: st.write(f"**{soru}**")
                    with c2: durum = st.radio("Durum", ["Tamam", "Sorunlu"], key=f"rd_{key_prefix}_{i}", horizontal=True, label_visibility="collapsed")
                    with c3: notlar = st.text_input("Varsa Not/Değer", key=f"txt_{key_prefix}_{i}", placeholder="Açıklama...")
                    cevaplar.append({"Soru": soru, "Durum": durum, "Aciklama": notlar})
                    st.divider()
                
                if st.form_submit_button(f"{bolum_adi} LİSTESİNİ KAYDET"):
                    yeni_veriler = []
                    for cvp in cevaplar:
                        yeni_veriler.append({
                            "Tarih": secilen_tarih.strftime("%Y-%m-%d"),
                            "Bolum": bolum_adi,
                            "Soru": cvp["Soru"],
                            "Durum": cvp["Durum"],
                            "Aciklama": cvp["Aciklama"],
                            "Kontrol_Eden": kontrol_eden
                        })
                    df_new = pd.DataFrame(yeni_veriler)
                    df_all = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
                    df_all = pd.concat([df_all, df_new], ignore_index=True)
                    save_data(df_all, "checklist")
                    st.success("Kontrol listesi başarıyla kaydedildi!")
                    st.rerun()

    with tab1: checklist_form("Elektrik", SORULAR_ELEKTRIK, "elek")
    with tab2: checklist_form("Mekanik", SORULAR_MEKANIK, "mek")
    with tab3: checklist_form("Genel", SORULAR_GENEL, "gen")

# -----------------------------------------------------------------------------
# 5. MODÜL: ARIZA VE İŞ TAKİP
# -----------------------------------------------------------------------------
elif menu == "🛠️ Arıza ve İş Takip":
    st.header("🛠️ Arıza ve İş Kayıtları")
    
    df_ariza = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_per = load_data("personel", ["Isim"])
    personel_list = df_per["Isim"].tolist() if not df_per.empty else ["Belirtilmedi"]

    # Yeni Arıza Ekleme
    with st.expander("➕ YENİ ARIZA / İŞ GİRİŞİ", expanded=False):
        with st.form("ariza_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: bolum = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "İnşaat/Genel"])
            with c2: lokasyon = st.text_input("Lokasyon (Örn: Kazan Dairesi)")
            with c3: sorumlu = st.selectbox("Sorumlu Teknisyen", personel_list)
            
            detay = st.text_area("Arıza veya İşin Tanımı")
            durum = st.selectbox("Durum", ["🛑 Açık (Bekliyor)", "⚠️ Devam Ediyor", "✅ Tamamlandı", "📦 Parça Bekliyor"])
            
            if st.form_submit_button("Kaydet"):
                new_row = {
                    "Tarih": secilen_tarih.strftime("%Y-%m-%d"),
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Bolum": bolum,
                    "Lokasyon": lokasyon,
                    "Ariza_Tanimi": detay,
                    "Sorumlu": sorumlu,
                    "Durum": durum
                }
                df_ariza = pd.concat([df_ariza, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_ariza, "ariza")
                st.success("Kayıt eklendi.")
                st.rerun()

    # Arıza Listesi (Filtreli)
    st.divider()
    filtre_durum = st.multiselect("Duruma Göre Filtrele", df_ariza["Durum"].unique(), default=df_ariza["Durum"].unique())
    
    gosterilecek_veri = df_ariza[df_ariza["Durum"].isin(filtre_durum)]
    # Tarih filtresi sadece o günü görmek istersek (İsteğe bağlı, genelde açık işler hep görünmeli)
    # gosterilecek_veri = gosterilecek_veri[gosterilecek_veri["Tarih"] == secilen_tarih.strftime("%Y-%m-%d")]
    
    if not gosterilecek_veri.empty:
        st.dataframe(gosterilecek_veri.sort_values(by="Tarih", ascending=False), use_container_width=True)
    else:
        st.info("Kriterlere uygun kayıt bulunamadı.")

# -----------------------------------------------------------------------------
# 6. MODÜL: VARDİYA DEFTERİ
# -----------------------------------------------------------------------------
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Teslim Tutanakları")
    
    df_vardiya = load_data("vardiya", ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar", "Kritik"])
    df_per = load_data("personel", ["Isim"])
    personel_list = df_per["Isim"].tolist() if not df_per.empty else ["Belirtilmedi"]

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("✍️ Teslim Et")
        with st.form("vardiya_form"):
            vardiya_saati = st.selectbox("Vardiya", ["08:00 - 16:00", "16:00 - 00:00", "00:00 - 08:00"])
            t_eden = st.selectbox("Teslim Eden", personel_list, key="v_eden")
            t_alan = st.selectbox("Teslim Alan", personel_list, key="v_alan")
            notlar = st.text_area("Vardiya Notları")
            kritik = st.text_area("❗ ACİL / KRİTİK DURUMLAR")
            
            if st.form_submit_button("Vardiyayı Kaydet"):
                new_v = {
                    "Tarih": secilen_tarih.strftime("%Y-%m-%d"),
                    "Vardiya": vardiya_saati,
                    "Teslim_Eden": t_eden,
                    "Teslim_Alan": t_alan,
                    "Notlar": notlar,
                    "Kritik": kritik
                }
                df_vardiya = pd.concat([df_vardiya, pd.DataFrame([new_v])], ignore_index=True)
                save_data(df_vardiya, "vardiya")
                st.success("Vardiya kaydedildi.")
                st.rerun()

    with c2:
        st.subheader("📖 Geçmiş Kayıtlar")
        if not df_vardiya.empty:
            for _, row in df_vardiya.sort_values(by="Tarih", ascending=False).iterrows():
                with st.chat_message("assistant"):
                    st.write(f"**{row['Tarih']} | {row['Vardiya']}**")
                    st.caption(f"{row['Teslim_Eden']} ➡️ {row['Teslim_Alan']}")
                    st.write(row['Notlar'])
                    if row['Kritik']: st.error(f"DİKKAT: {row['Kritik']}")
        else:
            st.info("Kayıt yok.")

# -----------------------------------------------------------------------------
# 7. MODÜL: PERSONEL YÖNETİMİ
# -----------------------------------------------------------------------------
elif menu == "👥 Personel":
    st.header("👥 Personel Listesi")
    df_per = load_data("personel", ["Isim", "Gorev"])
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("pers_ekle"):
            ad = st.text_input("Ad Soyad")
            gorev = st.text_input("Görevi (Örn: Elektrik Teknisyeni)")
            if st.form_submit_button("Ekle") and ad:
                df_per = pd.concat([df_per, pd.DataFrame([{"Isim": ad, "Gorev": gorev}])], ignore_index=True)
                save_data(df_per, "personel")
                st.rerun()
    
    with col2:
        if not df_per.empty:
            st.dataframe(df_per, use_container_width=True)
            sil = st.selectbox("Silinecek Kişi", df_per["Isim"].unique())
            if st.button("Sil"):
                df_per = df_per[df_per["Isim"] != sil]
                save_data(df_per, "personel")
                st.rerun()
