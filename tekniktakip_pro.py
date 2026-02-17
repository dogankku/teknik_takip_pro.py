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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("✅ **Kontrol Listeleri**")
        st.write("Günlük rutin kontrolleri girmek için kullanılır.")
    
    with col2:
        st.warning("🛠️ **Arıza Takip**")
        st.write("Arızaları kaydetmek ve durumunu güncellemek içindir.")
        
    with col3:
        st.success("🔄 **Vardiya Defteri**")
        st.write("Vardiya teslim notları içindir.")

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
    
    # HATA VEREN KISIM DÜZELTİLDİ:
    if not df_s.empty:
        dq = st.selectbox("Soru Sil", df_s["Soru"].unique())
        if st.button("Sil"):
            df_s = df_s[df_s["Soru"] != dq]
            save_data(df_s, "sorular")
            st.rerun()

# -----------------------------------------------------------------------------
# 9. MODÜL: KONTROL LİSTELERİ (HERKES)
# -----------------------------------------------------------------------------
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Kontrol Listeleri ({secilen_tarih})")
    
    df_p = load_data("personel", ["Isim"])
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]
    df_c = load_data("checklist", ["Tarih", "Bolum", "Soru", "Durum", "Aciklama", "Kontrol_Eden"])

    t1, t2, t3 = st.tabs(["Elektrik", "Mekanik", "Genel"])

    def show_check(bolum, kp):
        qs = get_questions(bolum)
        if not qs:
            st.warning("Soru yok.")
            return

        rec = df_c[(df_c["Tarih"] == str(secilen_tarih)) & (df_c["Bolum"] == bolum)]
        if not rec.empty:
            st.success("✅ Kaydedildi")
            st.dataframe(rec)
        else:
            with st.form(f"f_{kp}"):
                u = st.selectbox("Kontrol Eden", pers, key=f"u_{kp}")
                dt = []
                for i, q in enumerate(qs):
                    st.write(q)
                    c1, c2 = st.columns([1,2])
                    with c1: s = st.radio("D", ["Tamam", "Sorunlu"], key=f"r_{kp}_{i}", horizontal=True)
                    with c2: n = st.text_input("Not", key=f"n_{kp}_{i}")
                    dt.append({"Soru":q, "Durum":s, "Aciklama":n})
                    st.divider()
                if st.form_submit_button("Kaydet"):
                    rows = [{"Tarih": secilen_tarih, "Bolum": bolum, "Soru": d["Soru"], "Durum": d["Durum"], "Aciklama": d["Aciklama"], "Kontrol_Eden": u} for d in dt]
                    df_c = pd.concat([df_c, pd.DataFrame(rows)], ignore_index=True)
                    save_data(df_c, "checklist")
                    st.rerun()

    with t1: show_check("Elektrik", "e")
    with t2: show_check("Mekanik", "m")
    with t3: show_check("Genel", "g")

# -----------------------------------------------------------------------------
# 10. MODÜL: ARIZA TAKİP (HERKES)
# -----------------------------------------------------------------------------
elif menu == "🛠️ Arıza Takip":
    st.header("🛠️ Arıza Kayıtları")
    df_a = load_data("ariza", ["Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum"])
    df_p = load_data("personel", ["Isim"])
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.expander("➕ Arıza Ekle"):
        with st.form("new_a"):
            b = st.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel"])
            l = st.text_input("Lokasyon")
            s = st.selectbox("Sorumlu", pers)
            t = st.text_area("Tanım")
            d = st.selectbox("Durum", ["Açık", "Devam Ediyor", "Tamamlandı", "Parça Bekliyor"])
            if st.form_submit_button("Kaydet"):
                row = {"Tarih": secilen_tarih, "Saat": datetime.now().strftime("%H:%M"), "Bolum": b, "Lokasyon": l, "Ariza_Tanimi": t, "Sorumlu": s, "Durum": d}
                df_a = pd.concat([df_a, pd.DataFrame([row])], ignore_index=True)
                save_data(df_a, "ariza")
                st.rerun()
    st.dataframe(df_a.sort_values(by="Tarih", ascending=False), use_container_width=True)

# -----------------------------------------------------------------------------
# 11. MODÜL: VARDİYA DEFTERİ (HERKES)
# -----------------------------------------------------------------------------
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Defteri")
    df_v = load_data("vardiya", ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar", "Kritik"])
    df_p = load_data("personel", ["Isim"])
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    c1, c2 = st.columns(2)
    with c1:
        with st.form("new_v"):
            v = st.selectbox("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
            te = st.selectbox("Teslim Eden", pers, key="te")
            ta = st.selectbox("Teslim Alan", pers, key="ta")
            n = st.text_area("Notlar")
            k = st.text_area("Kritik")
            if st.form_submit_button("Kaydet"):
                row = {"Tarih": secilen_tarih, "Vardiya": v, "Teslim_Eden": te, "Teslim_Alan": ta, "Notlar": n, "Kritik": k}
                df_v = pd.concat([df_v, pd.DataFrame([row])], ignore_index=True)
                save_data(df_v, "vardiya")
                st.rerun()
    with c2:
        if not df_v.empty:
            for _, r in df_v.iloc[::-1].iterrows():
                st.info(f"{r['Tarih']} | {r['Vardiya']}\n{r['Teslim_Eden']} -> {r['Teslim_Alan']}\nNot: {r['Notlar']}")
                if pd.notna(r['Kritik']) and r['Kritik']: st.error(r['Kritik'])
