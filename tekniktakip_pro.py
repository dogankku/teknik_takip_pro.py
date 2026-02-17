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
    "sorular": "veritabani_sorular.csv"  # YENİ: Soruları burada tutacağız
}

# --- İLK KURULUM: Varsayılan Soruları Yükle ---
# Eğer soru dosyası yoksa, senin gönderdiğin standart soruları oluşturur.
def initialize_questions():
    if not os.path.exists(FILES["sorular"]):
        varsayilan_sorular = [
            # Elektrik
            {"Bolum": "Elektrik", "Soru": "1. Asansörler normal çalışıyor mu? Arıza/şikayet var mı?"},
            {"Bolum": "Elektrik", "Soru": "2. A-B Kule asansör mak. dairesi klimalar çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "3. Sokak ve bahçe aydınlatmaları yanıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "4. Bina dış cephe kayar ışıklar ve Anthill yazıları çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "5. Jeneratör kumanda panelleri normal konumda mı?"},
            {"Bolum": "Elektrik", "Soru": "6. Jeneratör yakıt seviyeleri kontrol edildi mi?"},
            # Mekanik
            {"Bolum": "Mekanik", "Soru": "1. Bir önceki vardiyadan kalan iş var mı?"},
            {"Bolum": "Mekanik", "Soru": "2
