import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR VE SAYFA YAPILANDIRMASI
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

# Veri Yükleme Fonksiyonu
def load_data(key, columns=None):
    if os.path.exists(FILES[key]):
        try:
            return pd.read_csv(FILES[key])
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# Veri Kaydetme Fonksiyonu
def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# -----------------------------------------------------------------------------
# 2. BAŞLANGIÇ KURULUMU (SORULARI OLUŞTURMA)
# -----------------------------------------------------------------------------
def initialize_system():
    # Soru veritabanı yoksa varsayılanları oluştur
    if not os.path.exists(FILES["sorular"]):
        varsayilan_sorular = [
            # --- ELEKTRİK ---
            {"Bolum": "Elektrik", "Soru": "1. Asansörler normal çalışıyor mu? Arıza var mı?"},
            {"Bolum": "Elektrik", "Soru": "2. A-B Kule asansör makine dairesi klimalar çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "3. Sokak ve bahçe aydınlatmaları yanıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "4. Bina dış cephe ışıkları ve Anthill yazıları çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "5. TV ve UPS odası klimaları çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "6. Jeneratör kumanda panelleri normal konumda mı?"},
            {"Bolum": "Elektrik", "Soru": "7. Jeneratör mazot tankı seviyeleri normal mi?"},
            {"Bolum": "Elektrik", "Soru": "8. Trafo ve dağıtım odaları temiz mi?"},
            
            # --- MEKANİK ---
            {"Bolum": "Mekanik", "Soru": "1. Bir önceki vardiyadan kalan iş var mı?"},
            {"Bolum": "Mekanik", "Soru": "2. Kazan Dairesi: Arıza ışığı veya su kaçağı var mı?"},
            {"Bolum": "Mekanik", "Soru": "3. Kazan Dairesi: Su basınçları istenen seviyede mi?"},
            {"Bolum": "Mekanik", "Soru": "4. Taze hava ve egzoz santralleri çalışıyor mu?"},
            {"Bolum": "Mekanik", "Soru": "5. 25. Kat: Pompalar ve basınçlar normal mi?"},
            {"Bolum": "Mekanik", "Soru": "6. 25. Kat: Su kaçağı var mı?"},
            {"Bolum": "Mekanik", "Soru": "7. Yangın depoları dolu mu? Basınç normal mi?"},
            
            # --- GENEL ---
            {"Bolum": "Genel", "Soru": "1. Vardiya defteri incelendi mi?"},
            {"Bolum": "Genel", "Soru": "2. Çevre aydınlatma kontrolü yapıldı mı?"}
        ]
        df = pd.DataFrame(varsayilan_sorular)
        save_data(df, "sorular")

initialize_system()

# Soruları Çekme Yardımcısı
def get_questions(bolum_adi):
    df = load_data("sorular", ["Bolum", "Soru"])
    if df.empty: return []
    return df[df["Bolum"] == bolum_adi]["Soru"].tolist()

# -----------------------------------------------------------------------------
# 3. YAN MENÜ VE NAVİGASYON
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    
    menu = st.radio("Menü Seçimi", [
        "✅ Kontrol Listeleri", 
        "🛠️ Arıza Takip", 
        "🔄 Vardiya Defteri", 
        "👥 Personel",
        "⚙️ Yönetici Paneli"
    ])
    
    st.markdown("---")
    secilen_tarih = st.date_input("İşlem Tarihi", date.today())
    st.caption("v4.1 - Stable Build")

# -----------------------------------------------------------------------------
# 4. MODÜL: YÖNETİCİ PANELİ
# -----------------------------------------------------------------------------
if menu == "⚙️ Yönetici Paneli":
    st.header("⚙️ Sistem Ayarları")
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False

    if not st.session_state['admin_logged_in']:
        with st.form("admin_login"):
            password = st.text_input("Yönetici Şifresi", type="password")
            if st.form_submit_button("Giriş"):
                if password == "1234":
                    st.session_state['admin_logged_in'] = True
                    st.success("Giriş Başarılı!")
                    st.rerun()
                else:
                    st.error("Hatalı Şifre!")
    else:
        if st.button("Çıkış Yap"):
            st.session_state['admin_logged_in'] = False
            st.rerun()

        st.divider()
        st.subheader("📝 Kontrol Listesi Düzenleme")
        
        col1, col2 = st.columns([1, 2])
        df_sorular = load_data("sorular", ["Bolum", "Soru"])

        with col1:
            with st.form("soru_ekle_form"):
                st.write("**Yeni Soru Ekle**")
                bolum = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
                soru = st.text_input("Soru Metni")
                if st.form_submit_button("Ekle"):
                    if soru:
                        new_row = {"Bolum": bolum, "Soru": soru}
                        df_sorular = pd.concat([df_sorular, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df_sorular, "sorular")
                        st.success("Eklendi!")
                        st.rerun()

        with col2:
            st.write("**Mevcut Sorular**")
            tab_e, tab_m, tab_g = st.tabs(["Elektrik", "Mekanik", "Genel"])
            
            def list_q(bolum_filter):
                subset = df_sorular[df_sorular["Bolum"] == bolum_filter]
                if not subset.empty:
                    for idx, row in subset.iterrows():
                        c_text, c_del = st.columns([4, 1])
                        c_text.text(f"• {row['Soru']}")
                        if c_del.button("Sil", key=f"del_{idx}"):
                            df_sorular.drop(idx, inplace=True)
                            save_data(df_sorular, "sorular")
                            st.rerun()
                else:
                    st.info("Soru yok.")

            with tab_e: list_q("Elektrik")
            with tab_m: list_q("Mekanik")
            with tab_g: list_q("Genel")

# -----------------------------------------------------------------------------
# 5. MODÜL: KONTROL LİSTELERİ
# -----------------------------------------------------------------------------
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Günlük Kontrol ({secilen_tarih.strftime('%d.%m.%Y')})")
    
    df_per = load_data("personel", ["Isim"])
    personel = df_per["Isim"].tolist() if not df_per.empty else ["Belirtilmedi"]
    df_check = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])

    tab1, tab2, tab3 = st.tabs(["⚡ ELEKTRİK", "🔧 MEKANİK", "📋 GENEL"])

    def render_checklist(bolum, prefix):
        questions = get_questions(bolum)
        if not questions:
            st.warning("Bu bölümde soru yok. Yönetici panelinden ekleyin.")
            return

        # O günkü kayıtları kontrol et
        daily_records = df_check[
            (df_check["Tarih"] == secilen_tarih.strftime("%Y-%m-%d")) & 
            (df_check["Bolum"] == bolum)
        ]

        if not daily_records.empty:
            st.success("✅ Kontroller tamamlanmış.")
            st.dataframe(daily_records[["Soru", "Durum", "Aciklama", "Kontrol_Eden"]], use_container_width=True)
        else:
            with st.form(f"form_{prefix}"):
                user = st.selectbox("Kontrol Eden", personel, key=f"u_{prefix}")
                answers = []
                
                for i, q in enumerate(questions):
                    st.write(f"**{q}**")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        status = st.radio("Durum", ["Tamam", "Sorunlu"], key=f"rad_{prefix}_{i}", horizontal=True, label_visibility="collapsed")
                    with c2:
                        note = st.text_input("Not", key=f"txt_{prefix}_{i}", placeholder="Açıklama...")
                    answers.append({"Soru": q, "Durum": status, "Aciklama": note})
                    st.divider()
                
                if st.form_submit_button("KAYDET"):
                    new_data = []
                    for ans in answers:
                        new_data.append({
                            "Tarih": secilen_tarih.strftime("%Y-%m-%d"),
                            "Bolum": bolum,
                            "Soru": ans["Soru"],
                            "Durum": ans["Durum"],
                            "Aciklama": ans["Aciklama"],
                            "Kontrol_Eden": user
                        })
                    df_check_new = pd.concat([df_check, pd.DataFrame(new_data)], ignore_index=True)
                    save_data(df_check_new, "checklist")
                    st.success("Kaydedildi!")
                    st.rerun()

    with tab1: render_checklist("Elektrik", "elek")
    with tab2: render_checklist("Mekanik", "mek")
    with tab3: render_checklist("Genel", "gen")

# -----------------------------------------------------------------------------
# 6. MODÜL: ARIZA TAKİP
# -----------------------------------------------------------------------------
elif menu == "🛠️ Arıza Takip":
    st.header("🛠️ Arıza ve İş Kayıtları")
    
    df_ariza = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_per = load_data("personel", ["Isim"])
    personel = df_per["Isim"].tolist() if not df_per.empty else ["Belirtilmedi"]

    with st.expander("➕ Yeni Kayıt Ekle", expanded=False):
        with st.form("ariza_form"):
            c1, c2, c3 = st.columns(3)
            with c1: bolum = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
            with c2: yer = st.text_input("Lokasyon")
            with c3: kisi = st.selectbox("Sorumlu", personel)
            
            detay = st.text_area("İş / Arıza Tanımı")
            durum = st.selectbox("Durum", ["🛑 Açık", "⚠️ Devam Ediyor", "✅ Tamamlandı", "📦 Par
