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
# 2. VERİTABANI VE SORU YAPISI (GRUPLANDIRILMIŞ)
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

# SORULARI GRUPLU HALE GETİREN YAPI
SORU_GRUPLARI = {
    "Elektrik": {
        "Asansörler & Dış Cephe": [
            "1. ASANSÖRLER NORMAL ÇALIŞIYOR MU? ARIZA VEYA ŞİKAYET OLDU MU?",
            "2. A KULE-B KULE ASANSÖR MAK.DAİRESİ KLİMALAR ÇALIŞIYOR MU?",
            "3. SOKAK VE BAHÇE AYDINLATMALARI YANIYOR MU?",
            "4. BİNA DIŞ CEPHE KAYAR IŞIKLAR VE ANTHİLL YAZILARI NORMAL Mİ?"
        ],
        "Klima & Havalandırma (Elektrik)": [
            "5. TV ODASI KLİMASI ÇALIŞIYOR MU? MEKAN TEMİZ Mİ?",
            "6. UPS ODASI KLİMASI ÇALIŞIYOR MU? MEKAN TEMİZ Mİ?"
        ],
        "Jeneratörler & Trafolar": [
            "7. A-B KULE JENERATÖR KUMANDA PANELLERİ NORMAL KONUMDA MI?",
            "8. JENERATÖRLER MAZOT TANKLARI KONTROLLERİ NORMAL Mİ?",
            "9. JENERATÖR ANA TANK MAZOT SEVİYESİ KAÇ SANTİM?",
            "10. TRAFO KORİDORLARI, JENERATÖR ODASI, DAĞITIM ODALARI TEMİZ Mİ?",
            "11. RESTORAN JENERATÖRÜ KUMANDA PANELİ NORMAL Mİ?"
        ]
    },
    "Mekanik": {
        "Devir Teslim & Genel": [
            "1. Bir önceki vardiyadan kalan iş var mı?",
            "2. Bir önceki vardiyadan kalan işler yapıldı mı?"
        ],
        "A Blok - Kazan Dairesi": [
            "3. Kazanlarda/panolarda arıza ışığı, su kaçağı var mı?",
            "4. Su basınçları istenen barda mı?",
            "5. Mekan temiz mi?",
            "6. Taze hava ve eksoz santralleri çalışıyor mu?"
        ],
        "A Blok - 25. Kat Teknik Oda": [
            "7. Elektrik panolarında yanan arıza ışığı var mı?",
            "8. Isıtma sirkülasyon pompaları çalışıyor mu? Basınç normal mi?",
            "9. Soğutma sirkülasyon pompaları çalışıyor mu? Basınç normal mi?",
            "10. Su kaçağı var mı?",
            "11. Su deposu ve hidroforlar normal mi?",
            "12. Yangın depoları dolu mu? Sistem basıncı normal mi?",
            "13. Mekan temiz mi?",
            "14. Taze hava ve eksoz santralleri çalışıyor mu?"
        ],
        "A Blok - 1. Bodrum": [
            "15. Elektrik panolarında yanan arıza ışığı var mı?",
            "16. Isıtma sirkülasyon pompaları çalışıyor mu?",
            "17. Soğutma sirkülasyon pompaları çalışıyor mu?",
            "18. Mekan temiz mi?",
            "19. Taze hava ve eksoz santralleri çalışıyor mu?"
        ],
        "Su & Yangın Sistemleri (Ortak Alan)": [
            "20. Kullanma Suyu ve Arıtma: Basınç normal mi?",
            "21. Kullanma Suyu ve Arıtma:
