import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR VE DOSYA YÖNETİMİ
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Teknik Operasyon Sistemi", layout="wide", page_icon="🏢")

# Dosya İsimleri
FILES = {
    "checklist": "veritabani_checklist.csv",
    "ariza": "veritabani_arizalar.csv",
    "vardiya": "veritabani_vardiya.csv",
    "personel": "veritabani_personel.csv",
    "sorular": "veritabani_sorular.csv"
}

# --- İLK KURULUM: Varsayılan Soruları Yükle ---
def initialize_questions():
    if not os.path.exists(FILES["sorular"]):
        # HATA ÇIKMAMASI İÇİN METİNLER ÜÇ TIRNAK (""") İÇİNE ALINDI
        varsayilan_sorular = [
            # --- ELEKTRİK ---
            {"Bolum": "Elektrik", "Soru": """1. Asansörler normal çalışıyor mu? Arıza veya şikayet oldu mu?"""},
            {"Bolum": "Elektrik", "Soru": """2. A-B Kule asansör makine dairesi klimalar çalışıyor mu? Genel mekan temiz mi?"""},
            {"Bolum": "Elektrik", "Soru": """3. Sokak ve bahçe aydınlatmaları yanıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """4. Bina dış cephe kayar ışıklar ve Anthill yazıları normal çalışıyor mu?"""},
            {"Bolum": "Elektrik", "Soru": """5. TV odası kliması çalışıyor mu? Genel mekan temiz mi?"""},
            {"Bolum": "Elektrik", "Soru": """6. UPS odası kliması çalışıyor mu? Genel mekan temiz mi?"""},
            {"Bolum": "Elektrik", "Soru": """7. A-B Kule jeneratör kumanda panelleri normal konumda mı?"""},
            {"Bolum": "Elektrik", "Soru": """8. Jeneratörler mazot tankları kontrolleri normal mi?"""},
            {"Bolum": "Elektrik", "Soru": """9. Jeneratör ana tank mazot seviyesi kaç santim?"""},
            {"Bolum": "Elektrik", "Soru": """10. Trafo koridorları, jeneratör odası, ana dağıtım ve sayaç odaları temiz mi?"""},
            
            # --- MEKANİK ---
            {"Bolum": "Mekanik", "Soru": """1. Bir önceki vardiyadan kalan iş var mı?"""},
            {"Bolum": "Mekanik", "Soru": """2. Bir önceki vardiyadan kalan işler yapıldı mı?"""},
            {"Bolum": "Mekanik", "Soru": """3. A Blok-Kazan Dairesi: Kazanlarda/panolarda arıza ışığı, su kaçağı var mı?"""},
            {"Bolum": "Mekanik", "Soru": """4. A Blok-Kazan Dairesi: Su basınçları istenen barda mı?"""},
            {"Bolum": "Mekanik", "Soru": """5. A Blok-Kazan Dairesi: Mekan temiz mi?"""},
            {"Bolum": "Mekanik", "Soru": """6. A Blok taze hava ve eksoz santralleri çalışıyor mu?"""},
            {"Bolum
