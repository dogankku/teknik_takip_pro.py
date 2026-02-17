import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR VE DOSYA YÖNETİMİ
# -----------------------------------------------------------------------------
st.set_page_config(page_title="24/7 Teknik Operasyon Merkezi", layout="wide", page_icon="🏭")

# CSV Dosya İsimleri
FILE_LOGS = "teknik_is_kayitlari.csv"
FILE_SHIFTS = "vardiya_defteri.csv"
FILE_USERS = "personel_listesi.csv"

# Veri Yükleme Fonksiyonu
def load_data(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=columns)

# Veri Kaydetme Fonksiyonu
def save_data(df, filename):
    df.to_csv(filename, index=False)

# -----------------------------------------------------------------------------
# 2. YAN MENÜ (NAVİGASYON VE FİLTRE)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🔧 Operasyon Paneli")
    
    # Menü Seçimi
    menu = st.radio(
        "Modül Seçiniz:", 
        ["📋 Günlük İş Kayıtları", "🔄 Vardiya Defteri", "👥 Personel Yönetimi"]
    )
    
    st.markdown("---")
    
    # TARİH FİLTRESİ (Sadece Günlük İşler İçin Aktif)
    secilen_tarih = date.today()
    if menu == "📋 Günlük İş Kayıtları":
        st.subheader("📅 Tarih Seçimi")
        secilen_tarih = st.date_input("Hangi günü görüntülemek istiyorsunuz?", date.today())
        st.info(f"Seçili Tarih: {secilen_tarih.strftime('%d.%m.%Y')}")

    st.markdown("---")
    st.caption("Sistem Saati: " + datetime.now().strftime("%H:%M"))

# -----------------------------------------------------------------------------
# 3. MODÜL: PERSONEL YÖNETİMİ
# -----------------------------------------------------------------------------
if menu == "👥 Personel Yönetimi":
    st.header("👥 Teknik Personel ve Sorumlular")
    
    df_users = load_data(FILE_USERS, ["Isim_Soyisim", "Gorev", "Ekip"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Yeni Personel Ekle")
        with st.form("user_form", clear_on_submit=True):
            name = st.text_input("Ad Soyad")
            role = st.selectbox("Görevi", ["Teknisyen", "Formen", "Mühendis", "Yönetici"])
            team = st.selectbox("Ekip/Vardiya", ["A Vardiyası", "B Vardiyası", "C Vardiyası", "Gündüz Ekibi"])
            submitted = st.form_submit_button("Personeli Kaydet")
            
            if submitted and name:
                new_user = {"Isim_Soyisim": name, "Gorev": role, "Ekip": team}
                df_users = pd.concat([df_users, pd.DataFrame([new_user])], ignore_index=True)
                save_data(df_users, FILE_USERS)
                st.success(f"{name} sisteme eklendi.")
                st.rerun()

    with col2:
        st.subheader("Mevcut Personel Listesi")
        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            
            st.write("---")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                del_user = st.selectbox("Silinecek Personeli Seç", df_users["Isim_Soyisim"].unique())
            with col_del2:
                if st.button("Seçili Personeli Sil"):
                    df_users = df_users[df_users["Isim_Soyisim"] != del_user]
                    save_data(df_users, FILE_USERS)
                    st.rerun()
        else:
            st.info("Henüz personel eklenmedi.")

# -----------------------------------------------------------------------------
# 4. MODÜL: GÜNLÜK İŞ KAYITLARI (GÜN GÜN TAKİP)
# -----------------------------------------------------------------------------
elif menu == "📋 Günlük İş Kayıtları":
    st.header(f"📋 Teknik Kayıt Defteri ({secilen_tarih.strftime('%d.%m.%Y')})")
    
    # Verileri Yükle
    df_logs = load_data(FILE_LOGS, ["Tarih", "Saat", "Kategori", "Lokasyon", "Detay", "Sorumlu", "Durum"])
    users_df = load_data(FILE_USERS, ["Isim_Soyisim"])
    personel_listesi = users_df["Isim_Soyisim"].tolist() if not users_df.empty else ["Tanımsız"]

    # --- KAYIT EKLEME FORMU ---
    with st.expander("➕ YENİ İŞ / ARIZA GİRİŞİ EKLEMEK İÇİN TIKLAYIN", expanded=False):
        with st.form("log_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                kategori = st.selectbox("Liste Tipi", 
                                      ["Liste 1: Rutin Kontrol", "Liste 2: Arıza/Onarım", "Liste 3: Periyodik Bakım"])
            with c2:
                lokasyon = st.text_input("Lokasyon / Ekipman")
            with c3:
                sorumlu = st.selectbox("İşi Yapan", personel_listesi)
            
            detay = st.text_area("Yapılan İşin Detayları")
            
            c4, c5 = st.columns(2)
            with c4:
                durum = st.selectbox("Durum", ["✅ Tamamlandı", "⚠️ Devam Ediyor", "🛑 Parça Bekliyor", "👀 Gözlem Altında"])
            with c5:
                # Varsayılan olarak şu anki saati getirir
                is_time = st.time_input("Saat", datetime.now().time())
            
            submit_log = st.form_submit_button("Kaydı Deftere İşle")
            
            if submit_log:
                new_log = {
                    "Tarih": secilen_tarih.strftime("%Y-%m-%d"), # Yan menüde seçilen tarihe kaydeder
                    "Saat": is_time.strftime("%H:%M"),
                    "Kategori": kategori,
                    "Lokasyon": lokasyon,
                    "Detay": detay,
                    "Sorumlu": sorumlu,
                    "Durum": durum
                }
                df_logs = pd.concat([df_logs, pd.DataFrame([new_log])], ignore_index=True)
                save_data(df_logs, FILE_LOGS)
                st.toast("Kayıt Başarıyla Eklendi!", icon="✅")
                st.rerun()

    # --- LİSTELEME VE FİLTRELEME ---
    # Sadece seçilen tarihe ait kayıtları getir
    gunluk_veriler = df_logs[df_logs["Tarih"] == secilen_tarih.strftime("%Y-%m-%d")]
    
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📝 Liste 1 (Rutin)", "🔧 Liste 2 (Arıza)", "⚙️ Liste 3 (Bakım)"])
    
    def show_table(df, category_name):
        filtered = df[df["Kategori"] == category_name]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
        else:
            st.info(f"Bu tarihte '{category_name}' kategorisinde kayıt yok.")

    with tab1: show_table(gunluk_veriler, "Liste 1: Rutin Kontrol")
    with tab2: show_table(gunluk_veriler, "Liste 2: Arıza/Onarım")
    with tab3: show_table(gunluk_veriler, "Liste 3: Periyodik Bakım")

# -----------------------------------------------------------------------------
# 5. MODÜL: VARDİYA DEFTERİ
# -----------------------------------------------------------------------------
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Teslim Tutanakları")
    
    users_df = load_data(FILE_USERS, ["Isim_Soyisim"])
    personel_listesi = users_df["Isim_Soyisim"].tolist() if not users_df.empty else ["Tanımsız"]
    df_shifts = load_data(FILE_SHIFTS, ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Ozet_Notlar", "Kritik_Notlar"])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("✍️ Vardiya Teslim Et")
        with st.form("shift_form", clear_on_submit=True):
            # Bugünün tarihi otomatik gelir
            vardiya_tarihi = st.date_input("Vardiya Tarihi", date.today())
            vardiya_saati = st.selectbox("Vardiya Aralığı", ["08:00 - 16:00", "16:00 - 00:00", "00:00 - 08:00"])
            
            c_a, c_b = st.columns(2)
            with c_a: teslim_eden = st.selectbox("Teslim Eden", personel_listesi, key="te")
            with c_b: teslim_alan = st.selectbox("Teslim Alan", personel_listesi, key="ta")
            
            ozet = st.text_area("Vardiya Özeti")
            kritik = st.text_area("❗ KRİTİK / ACİL NOTLAR", help="Bir sonraki vardiyanın dikkat etmesi gerekenler.")
            
            shift_submit = st.form_submit_button("Vardiyayı Kapat")
            
            if shift_submit:
                new_shift = {
                    "Tarih": vardiya_tarihi.strftime("%Y-%m-%d"),
                    "Vardiya": vardiya_saati,
                    "Teslim_Eden": teslim_eden,
                    "Teslim_Alan": teslim_alan,
                    "Ozet_Notlar": ozet,
                    "Kritik_Notlar": kritik
                }
                df_shifts = pd.concat([df_shifts, pd.DataFrame([new_shift])], ignore_index=True)
                save_data(df_shifts, FILE_SHIFTS)
                st.success("Vardiya kaydedildi.")
                st.rerun()

    with col2:
        st.subheader("📖 Geçmiş Vardiya Notları")
        if not df_shifts.empty:
            # En yeniden en eskiye sırala
            df_display = df_shifts.sort_values(by="Tarih", ascending=False)
            
            for index, row in df_display.iterrows():
                with st.chat_message("assistant"):
                    st.write(f"📅 **{row['Tarih']}** | 🕒 {row['Vardiya']}")
                    st.caption(f"👤 {row['Teslim_Eden']} ➡️ {row['Teslim_Alan']}")
                    st.write(f"📝 {row['Ozet_Notlar']}")
                    if pd.notna(row['Kritik_Notlar']) and row['Kritik_Notlar']:
                        st.error(f"⚠️ DİKKAT: {row['Kritik_Notlar']}")
                    st.divider()
        else:
            st.info("Henüz vardiya kaydı yok.")
