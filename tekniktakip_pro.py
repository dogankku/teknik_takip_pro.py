import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR VE SAYFA YAPILANDIRMASI
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
# 2. VERİTABANI FONKSİYONLARI
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

def initialize_system():
    if not os.path.exists(FILES["sorular"]):
        varsayilan_sorular = [
            # --- ELEKTRİK ---
            {"Bolum": "Elektrik", "Soru": """1. Asansörler normal çalışıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """2. Asansör makine dairesi klimaları çalışıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """3. Bahçe aydınlatmaları yanıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """4. Dış cephe ışıkları çalışıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """5. Jeneratör panelleri normal mi?"""},
            
            # --- MEKANİK ---
            {"Bolum": "Mekanik", "Soru": """1. Önceki vardiyadan iş kaldı mı?"""},
            {"Bolum": "Mekanik", "Soru": """2. Kazan Dairesi su kaçağı var mı?"""},
            {"Bolum": "Mekanik", "Soru": """3. Su basınçları normal mi?"""},
            {"Bolum": "Mekanik", "Soru": """4. Klima santralleri çalışıyor mu?"""},
            
            # --- GENEL ---
            {"Bolum": "Genel", "Soru": """1. Vardiya defteri okundu mu?"""},
            {"Bolum": "Genel", "Soru": """2. Çevre kontrolü yapıldı mı?"""}
        ]
        df = pd.DataFrame(varsayilan_sorular)
        save_data(df, "sorular")

initialize_system()

def get_questions(bolum_adi):
    df = load_data("sorular", ["Bolum", "Soru"])
    if df.empty: return []
    return df[df["Bolum"] == bolum_adi]["Soru"].tolist()

# -----------------------------------------------------------------------------
# 3. DİNAMİK YAN MENÜ (GÜVENLİK AYARI BURADA)
# -----------------------------------------------------------------------------
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906319.png", width=80)
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    
    # KULLANICI TİPİNE GÖRE MENÜ BELİRLEME
    if st.session_state['admin_logged_in']:
        # Yönetici Giriş Yapmışsa Her Şeyi Görür
        menu_options = [
            "📊 GÜNLÜK RAPOR (YÖNETİCİ)", 
            "👥 Personel Yönetimi",
            "⚙️ Soru Düzenleme",
            "✅ Kontrol Listeleri", 
            "🛠️ Arıza Takip", 
            "🔄 Vardiya Defteri",
            "🚪 Çıkış Yap"
        ]
        st.success("Yönetici Modu Açık")
    else:
        # Personel Sadece İş Ekranlarını Görür
        menu_options = [
            "✅ Kontrol Listeleri", 
            "🛠️ Arıza Takip", 
            "🔄 Vardiya Defteri",
            "🔐 Yönetici Girişi"
        ]
    
    menu = st.radio("Menü Seçimi", menu_options)
    
    st.markdown("---")
    secilen_tarih = st.date_input("İşlem Tarihi", date.today())

# -----------------------------------------------------------------------------
# 4. GİRİŞ / ÇIKIŞ İŞLEMLERİ
# -----------------------------------------------------------------------------
if menu == "🔐 Yönetici Girişi":
    st.header("🔐 Yönetici Girişi")
    st.info("Raporları ve Personel Listesini görmek için giriş yapınız.")
    
    with st.form("login_form"):
        password = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş Yap"):
            if password == "1234":  # ŞİFRE BURADA
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")

elif menu == "🚪 Çıkış Yap":
    st.session_state['admin_logged_in'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 5. MODÜL: GÜNLÜK RAPOR (SADECE YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "📊 GÜNLÜK RAPOR (YÖNETİCİ)":
    st.header(f"📊 Günlük Operasyon Özeti ({secilen_tarih.strftime('%d.%m.%Y')})")
    
    # Verileri Çek
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_v = load_data("vardiya", ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar", "Kritik"])
    
    str_tarih = secilen_tarih.strftime("%Y-%m-%d")
    gunluk_check = df_c[df_c["Tarih"] == str_tarih]
    gunluk_ariza = df_a[df_a["Tarih"] == str_tarih]
    gunluk_vardiya = df_v[df_v["Tarih"] == str_tarih]
    
    # METRİKLER
    c1, c2, c3, c4 = st.columns(4)
    el_ok = "✅ Tamam" if not gunluk_check[gunluk_check["Bolum"]=="Elektrik"].empty else "❌ Eksik"
    mk_ok = "✅ Tamam" if not gunluk_check[gunluk_check["Bolum"]=="Mekanik"].empty else "❌ Eksik"
    
    c1.metric("Elektrik", el_ok)
    c2.metric("Mekanik", mk_ok)
    c3.metric("Arıza", f"{len(gunluk_ariza)} Adet")
    c4.metric("Vardiya", f"{len(gunluk_vardiya)} Kayıt")
    
    st.divider()
    
    # Arızalar
    st.subheader("🛠️ Günün Arızaları")
    if not gunluk_ariza.empty:
        st.dataframe(gunluk_ariza, use_container_width=True, hide_index=True)
    else:
        st.info("Arıza kaydı yok.")
        
    # Sorunlu Kontroller
    st.subheader("⚠️ Kontrol Listesi Hataları")
    errors = gunluk_check[gunluk_check["Durum"] == "Sorunlu"]
    if not errors.empty:
        st.error(f"{len(errors)} adet sorunlu madde var!")
        st.dataframe(errors[["Bolum", "Soru", "Aciklama", "Kontrol_Eden"]], use_container_width=True)
    else:
        st.success("Tüm kontroller temiz.")

# -----------------------------------------------------------------------------
# 6. MODÜL: PERSONEL YÖNETİMİ (SADECE YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Listesi Düzenleme")
    
    df_per = load_data("personel", ["Isim", "Gorev"])
    
    c1, c2 = st.columns(2)
    with c1:
        with st.form("add_per"):
            ad = st.text_input("Ad Soyad")
            grv = st.text_input("Görevi")
            if st.form_submit_button("Ekle") and ad:
                df_per = pd.concat([df_per, pd.DataFrame([{"Isim": ad, "Gorev": grv}])], ignore_index=True)
                save_data(df_per, "personel")
                st.success("Eklendi")
                st.rerun()
    with c2:
        if not df_per.empty:
            st.dataframe(df_per, use_container_width=True)
            sil = st.selectbox("Silinecek Personel", df_per["Isim"].unique())
            if st.button("Sil"):
                df_per = df_per[df_per["Isim"] != sil]
                save_data(df_per, "personel")
                st.rerun()

# -----------------------------------------------------------------------------
#
