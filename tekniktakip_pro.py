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
            {"Bolum": "Elektrik", "Soru": "1. Asansörler normal çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "2. Dış cephe ve bahçe aydınlatmaları yanıyor mu?"},
            {"Bolum": "Mekanik", "Soru": "1. Kazan dairesi su basınçları normal mi?"},
            {"Bolum": "Mekanik", "Soru": "2. Hidrofor ve pompalar çalışıyor mu?"},
            {"Bolum": "Genel", "Soru": "1. Vardiya defteri okundu mu?"}
        ]
        df = pd.DataFrame(varsayilan_sorular)
        save_data(df, "sorular")

initialize_system()

def get_questions(bolum_adi):
    df = load_data("sorular", ["Bolum", "Soru"])
    if df.empty: return []
    return df[df["Bolum"] == bolum_adi]["Soru"].tolist()

# -----------------------------------------------------------------------------
# 3. YAN MENÜ VE GÜVENLİK
# -----------------------------------------------------------------------------
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906319.png", width=80)
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    
    # MENÜ SEÇENEKLERİ
    if st.session_state['admin_logged_in']:
        # --- YÖNETİCİ MENÜSÜ ---
        menu_options = [
            "🏠 Ana Sayfa",
            "📊 GÜNLÜK RAPOR", 
            "👥 Personel Yönetimi",
            "⚙️ Soru Düzenleme",
            "✅ Kontrol Listeleri", 
            "🛠️ Arıza Takip", 
            "🔄 Vardiya Defteri",
            "🚪 Çıkış Yap"
        ]
        st.success("Yönetici Modu")
    else:
        # --- PERSONEL MENÜSÜ ---
        menu_options = [
            "🏠 Ana Sayfa",
            "✅ Kontrol Listeleri", 
            "🛠️ Arıza Takip", 
            "🔄 Vardiya Defteri",
            "🔐 Yönetici Girişi"
        ]
    
    menu = st.radio("Menü", menu_options)
    
    st.markdown("---")
    secilen_tarih = st.date_input("Tarih", date.today())

# -----------------------------------------------------------------------------
# 4. MODÜL: ANA SAYFA (HERKES GÖRÜR)
# -----------------------------------------------------------------------------
if menu == "🏠 Ana Sayfa":
    st.header("👋 Hoşgeldiniz")
    st.markdown(f"**Tarih:** {secilen_tarih.strftime('%d.%m.%Y')}")
    st.divider()
    
    # Bilgilendirme Kartları
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("✅ **Kontrol Listeleri**")
        st.write("Günlük rutin kontrolleri (Elektrik, Mekanik) girmek için kullanılır.")
    
    with col2:
        st.warning("🛠️ **Arıza Takip**")
        st.write("Binada oluşan arızaları kaydetmek ve durumunu güncellemek içindir.")
        
    with col3:
        st.success("🔄 **Vardiya Defteri**")
        st.write("Vardiya değişimlerinde not bırakmak ve teslim yapmak içindir.")

    st.divider()
    if not st.session_state['admin_logged_in']:
        st.caption("ℹ️ Yönetici paneline erişmek için sol menüden 'Yönetici Girişi' yapınız.")

# -----------------------------------------------------------------------------
# 5. MODÜL: YÖNETİCİ GİRİŞİ / ÇIKIŞI
# -----------------------------------------------------------------------------
elif menu == "🔐 Yönetici Girişi":
    st.header("🔐 Yönetici Girişi")
    with st.form("login_form"):
        password = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş Yap"):
            if password == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")

elif menu == "🚪 Çıkış Yap":
    st.session_state['admin_logged_in'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 6. MODÜL: GÜNLÜK RAPOR (SADECE YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "📊 GÜNLÜK RAPOR":
    st.header(f"📊 Özet Rapor ({secilen_tarih})")
    
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    
    str_t = secilen_tarih.strftime("%Y-%m-%d")
    gunluk_c = df_c[df_c["Tarih"] == str_t]
    gunluk_a = df_a[df_a["Tarih"] == str_t]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Kontrol", len(gunluk_c))
    c2.metric("Toplam Arıza", len(gunluk_a))
    sorunlu = gunluk_c[gunluk_c["Durum"] == "Sorunlu"]
    c3.metric("Sorunlu Madde", len(sorunlu))
    
    st.subheader("🛠️ Arızalar")
    st.dataframe(gunluk_a, use_container_width=True)
    
    st.subheader("⚠️ Sorunlu Kontroller")
    st.dataframe(sorunlu, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. MODÜL: PERSONEL YÖNETİMİ (SADECE YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Listesi")
    df_p = load_data("personel", ["Isim", "Gorev"])
    
    c1, c2 = st.columns(2)
    with c1:
        with st.form("add_p"):
            nm = st.text_input("Ad Soyad")
            gr = st.text_input("Görevi")
            if st.form_submit_button("Ekle") and nm:
                df_p = pd.concat([df_p, pd.DataFrame([{"Isim": nm, "Gorev": gr}])], ignore_index=True)
                save_data(df_p, "personel")
                st.rerun()
    with c2:
        st.dataframe(df_p, use_container_width=True)
        if not df_p.empty:
            dl = st.selectbox("Sil", df_p["Isim"].unique())
            if st.button("Sil"):
                df_p = df_p[df_p["Isim"] != dl]
                save_data(df_p, "personel")
                st.rerun()

# -----------------------------------------------------------------------------
# 8. MODÜL: SORU DÜZENLEME (SADECE YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "⚙️ Soru Düzenleme":
    st.header("⚙️ Soru Havuzu")
    df_s = load_data("sorular", ["Bolum", "Soru"])
    
    with st.form("add_q"):
        b = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
        q = st.text_input("Soru")
        if st.form_submit_button("Ekle") and q:
            df_s = pd.concat([df_s, pd.DataFrame([{"Bolum": b, "Soru": q}])], ignore_index=True)
            save_data(df_s, "sorular")
            st.rerun()
            
    st.dataframe(df_s, use_container_width=True)
    if not df_s.empty:
