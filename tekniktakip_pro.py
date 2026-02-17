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
# 2. VERİTABANI İŞLEMLERİ
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
        # Sorular alt alta yazılarak hata önlendi
        sorular = [
            {"Bolum": "Elektrik", "Soru": "1. Asansörler normal çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "2. Asansör makine dairesi klimaları çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "3. Bahçe aydınlatmaları yanıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "4. Dış cephe ışıkları çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "5. Jeneratör panelleri normal mi?"},
            {"Bolum": "Elektrik", "Soru": "6. Jeneratör yakıt seviyesi kontrolü?"},
            {"Bolum": "Mekanik", "Soru": "1. Önceki vardiyadan iş kaldı mı?"},
            {"Bolum": "Mekanik", "Soru": "2. Kazan Dairesi su kaçağı var mı?"},
            {"Bolum": "Mekanik", "Soru": "3. Su basınçları normal mi?"},
            {"Bolum": "Mekanik", "Soru": "4. Klima santralleri çalışıyor mu?"},
            {"Bolum": "Mekanik", "Soru": "5. Pompalar ve hidroforlar normal mi?"},
            {"Bolum": "Genel", "Soru": "1. Vardiya defteri okundu mu?"},
            {"Bolum": "Genel", "Soru": "2. Çevre kontrolü yapıldı mı?"}
        ]
        df = pd.DataFrame(sorular)
        save_data(df, "sorular")

initialize_system()

def get_questions(bolum_adi):
    df = load_data("sorular", ["Bolum", "Soru"])
    if df.empty: return []
    return df[df["Bolum"] == bolum_adi]["Soru"].tolist()

# -----------------------------------------------------------------------------
# 3. ANA MENÜ
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏢 Tesis Yönetimi")
    menu = st.radio("Menü", [
        "✅ Kontrol Listeleri", 
        "🛠️ Arıza Takip", 
        "🔄 Vardiya Defteri", 
        "👥 Personel",
        "⚙️ Yönetici Paneli"
    ])
    st.markdown("---")
    secilen_tarih = st.date_input("Tarih Seçimi", date.today())

# -----------------------------------------------------------------------------
# 4. MODÜL: YÖNETİCİ PANELİ
# -----------------------------------------------------------------------------
if menu == "⚙️ Yönetici Paneli":
    st.header("⚙️ Ayarlar")
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        pw = st.text_input("Yönetici Şifresi", type="password")
        if st.button("Giriş"):
            if pw == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre")
    else:
        if st.button("Çıkış"):
            st.session_state['admin_logged_in'] = False
            st.rerun()
            
        st.subheader("Soru Yönetimi")
        c1, c2 = st.columns([1, 2])
        df_q = load_data("sorular", ["Bolum", "Soru"])
