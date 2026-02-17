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

def initialize_system():
    if not os.path.exists(FILES["sorular"]):
        # Varsayılan Sorular
        data = [
            {"Bolum": "Elektrik", "Soru": "1. Asansörler normal çalışıyor mu?"},
            {"Bolum": "Elektrik", "Soru": "2. Bahçe aydınlatmaları yanıyor mu?"},
            {"Bolum": "Mekanik", "Soru": "1. Kazan dairesi su basıncı normal mi?"},
            {"Bolum": "Mekanik", "Soru": "2. Hidrofor pompaları devrede mi?"},
            {"Bolum": "Genel", "Soru": "1. Vardiya defteri okundu mu?"}
        ]
        df = pd.DataFrame(data)
        save_data(df, "sorular")

initialize_system()

def get_questions(bolum_adi):
    df = load_data("sorular", ["Bolum", "Soru"])
    if df.empty:
        return []
    return df[df["Bolum"] == bolum_adi]["Soru"].tolist()

# -----------------------------------------------------------------------------
# 3. MENÜ YAPISI VE GÜVENLİK
# -----------------------------------------------------------------------------
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

with st.sidebar:
    st.title("🏢 Tesis Yönetimi")
    st.markdown("---")
    
    if st.session_state['admin_logged_in']:
        # Yönetici Menüsü
        secenekler = [
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
        # Personel Menüsü
        secenekler = [
            "🏠 Ana Sayfa",
            "✅ Kontrol Listeleri",
            "🛠️ Arıza Takip",
            "🔄 Vardiya Defteri",
            "🔐 Yönetici Girişi"
        ]
    
    menu = st.radio("Menü", secenekler)
    st.markdown("---")
    secilen_tarih = st.date_input("Tarih", date.today())

# -----------------------------------------------------------------------------
# 4. MODÜL: ANA SAYFA
# -----------------------------------------------------------------------------
if menu == "🏠 Ana Sayfa":
    st.header("👋 Hoşgeldiniz")
    st.write(f"**Seçili Tarih:** {secilen_tarih.strftime('%d.%m.%Y')}")
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("✅ **Kontrol Listeleri**")
        st.caption("Günlük kontrolleri girmek için.")
    with c2:
        st.warning("🛠️ **Arıza Takip**")
        st.caption("Arıza bildirmek için.")
    with c3:
        st.success("🔄 **Vardiya Defteri**")
        st.caption("Vardiya teslim notları için.")

# -----------------------------------------------------------------------------
# 5. MODÜL: GİRİŞ / ÇIKIŞ
# -----------------------------------------------------------------------------
elif menu == "🔐 Yönetici Girişi":
    st.header("🔐 Yönetici Girişi")
    with st.form("login"):
        pwd = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş"):
            if pwd == "1234":
                st.session_state['admin_logged_in'] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre")

elif menu == "🚪 Çıkış Yap":
    st.session_state['admin_logged_in'] = False
    st.rerun()

# -----------------------------------------------------------------------------
# 6. MODÜL: GÜNLÜK RAPOR (YÖNETİCİ)
# -----------------------------------------------------------------------------
elif menu == "📊 GÜNLÜK RAPOR":
    st.header(f"📊 Rapor ({secilen_tarih})")
    
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    
    tarih_str = str(secilen_tarih)
    gunluk_c = df_c[df_c["Tarih"] == tarih_str]
    gunluk_a = df_a[df_a["Tarih"] == tarih_str]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Kontrol", len(gunluk_c))
    m2.metric("Toplam Arıza", len(gunluk_a))
    sorunlu_sayisi = len(gunluk_c[gunluk_c["Durum"] == "Sorunlu"])
    m3.metric("Sorunlu Madde", sorunlu_sayisi)
    
    st.subheader("🛠️ Arızalar")
    st.dataframe(gunluk_a, use_container_width=True)
    
    st.subheader("⚠️ Sorunlu Kontroller")
    st.dataframe(gunluk_c[gunluk_c["Durum"] == "Sorunlu"], use_container_width=True)

# -----------------------------------------------------------------------------
# 7. MODÜL: PERSONEL YÖNETİMİ
# -----------------------------------------------------------------------------
elif menu == "👥 Personel Yönetimi":
    st.header("👥 Personel Listesi")
    df_p = load_data("personel", ["Isim", "Gorev"])
    
    c1, c2 = st.columns(2)
    with c1:
        with st.form("add_per"):
            ad = st.text_input("Ad Soyad")
            grv = st.text_input("Görevi")
            if st.form_submit_button("Ekle"):
                new_p = pd.DataFrame([{"Isim": ad, "Gorev": grv}])
                df_p = pd.concat([df_p, new_p], ignore_index=True)
                save_data(df_p, "personel")
                st.rerun()
    with c2:
        st.dataframe(df_p, use_container_width=True)
        if not df_p.empty:
            silinecek = st.selectbox("Sil", df_p["Isim"].unique())
            if st.button("Sil"):
                df_p = df_p[df_p["Isim"] != silinecek]
                save_data(df_p, "personel")
                st.rerun()

# -----------------------------------------------------------------------------
# 8. MODÜL: SORU DÜZENLEME
# -----------------------------------------------------------------------------
elif menu == "⚙️ Soru Düzenleme":
    st.header("⚙️ Soru Havuzu")
    df_s = load_data("sorular", ["Bolum", "Soru"])
    
    with st.form("add_q"):
        blm = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
        txt = st.text_input("Soru")
        if st.form_submit_button("Ekle"):
            new_s = pd.DataFrame([{"Bolum": blm, "Soru": txt}])
            df_s = pd.concat([df_s, new_s], ignore_index=True)
            save_data(df_s, "sorular")
            st.rerun()
            
    st.dataframe(df_s, use_container_width=True)
    
    if not df_s.empty:
        sil_q = st.selectbox("Soru Sil", df_s["Soru"].unique())
        if st.button("Sil"):
            df_s = df_s[df_s["Soru"] != sil_q]
            save_data(df_s, "sorular")
            st.rerun()

# -----------------------------------------------------------------------------
# 9. MODÜL: KONTROL LİSTELERİ
# -----------------------------------------------------------------------------
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Kontrol ({secilen_tarih})")
    
    df_check = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])
    df_pers = load_data("personel", ["Isim"])
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    t1, t2, t3 = st.tabs(["Elektrik", "Mekanik", "Genel"])

    def form_goster(bolum_kodu, key_suffix):
        sorular = get_questions(bolum_kodu)
        if not sorular:
            st.warning("Soru bulunamadı.")
            return

        # Kayıt Kontrolü
        tarih_str = str(secilen_tarih)
        mevcut_kayit = df_check[
            (df_check["Tarih"] == tarih_str) & 
            (df_check["Bolum"] == bolum_kodu)
        ]

        if not mevcut_kayit.empty:
            st.success("✅ Kayıt Tamamlandı")
            st.dataframe(mevcut_kayit[["Soru", "Durum", "Aciklama", "Kontrol_Eden"]])
        else:
            with st.form(f"frm_{key_suffix}"):
                kontrolcu = st.selectbox("Kontrol Eden", personel_listesi, key=f"usr_{key_suffix}")
                
                cevaplar = []
                for i, soru in enumerate(sorular):
                    st.write(f"**{soru}**")
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        d = st.radio("D", ["Tamam", "Sorunlu"], key=f"rad_{key_suffix}_{i}", horizontal=True)
                    with col_b:
                        n = st.text_input("Not", key=f"not_{key_suffix}_{i}")
                    
                    cevaplar.append({
                        "Tarih": tarih_str,
                        "Bolum": bolum_kodu,
                        "Soru": soru,
                        "Durum": d,
                        "Aciklama": n,
                        "Kontrol_Eden": kontrolcu
                    })
                    st.divider()
                
                if st.form_submit_button("Kaydet"):
                    yeni_veriler = pd.DataFrame(cevaplar)
                    # Hata önleyici birleştirme
                    guncel_df = pd.concat([df_check, yeni_veriler], ignore_index=True)
                    save_data(guncel_df, "checklist")
                    st.rerun()

    with t1: form_goster("Elektrik", "elek")
    with t2: form_goster("Mekanik", "mek")
    with t3: form_goster("Genel", "gen")

# -----------------------------------------------------------------------------
# 10. MODÜL: ARIZA TAKİP
# -----------------------------------------------------------------------------
elif menu == "🛠️ Arıza Takip":
    st.header("🛠️ Arıza Kayıtları")
    df_ariza = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_pers = load_data("personel", ["Isim"])
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["-"]

    with st.expander("➕ Arıza Ekle"):
        with st.form("ariza_ekle"):
            bl = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
            lk = st.text_input("Lokasyon")
            sr = st.selectbox("Sorumlu", personel_listesi)
            tn = st.text_area("Arıza Tanımı")
            dr = st.selectbox("Durum", ["Açık", "Devam Ediyor", "Tamamlandı", "Parça Bekliyor"])
            
            if st.form_submit_button("Kaydet"):
                yeni_satir = {
                    "Tarih": str(secilen_tarih),
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Bolum": bl,
                    "Lokasyon": lk,
                    "Ariza_Tanimi": tn,
                    "Sorumlu": sr,
                    "Durum": dr
                }
                df_yeni = pd.DataFrame([yeni_satir])
                df_ariza = pd.concat([df_ariza, df_yeni], ignore_index=True)
                save_data(df_ariza, "ariza")
                st.rerun()
    
    st.dataframe(df_ariza.sort_values(by="Tarih", ascending=False), use_container_width=True)

# -----------------------------------------------------------------------------
# 11. MODÜL: VARDİYA DEFTERİ
# -----------------------------------------------------------------------------
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Defteri")
    df_vardiya = load_data("vardiya", ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar", "Kritik"])
    df_pers = load_data("personel", ["Isim"])
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["-"]

    c1, c2 = st.columns(2)
    with c1:
        with st.form("vardiya_ekle"):
            vr = st.selectbox("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
            te = st.selectbox("Teslim Eden", personel_listesi, key="te")
            ta = st.selectbox("Teslim Alan", personel_listesi, key="ta")
            nt = st.text_area("Notlar")
            kr = st.text_area("Kritik")
            
            if st.form_submit_button("Kaydet"):
                yeni_v = {
                    "Tarih": str(secilen_tarih),
                    "Vardiya": vr,
                    "Teslim_Eden": te,
                    "Teslim_Alan": ta,
                    "Notlar": nt,
                    "Kritik": kr
                }
                df_vardiya = pd.concat([df_vardiya, pd.DataFrame([yeni_v])], ignore_index=True)
                save_data(df_vardiya, "vardiya")
                st.rerun()
    
    with c2:
        if not df_vardiya.empty:
            for _, row in df_vardiya.iloc[::-1].iterrows():
                st.info(f"{row['Tarih']} | {row['Vardiya']}\n{row['Teslim_Eden']} -> {row['Teslim_Alan']}\nNot: {row['Notlar']}")
                if pd.notna(row['Kritik']) and row['Kritik']:
                    st.error(row['Kritik'])
