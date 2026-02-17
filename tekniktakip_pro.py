import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# 1. AYARLAR VE VERİTABANI YÖNETİMİ
# -----------------------------------------------------------------------------
st.set_page_config(page_title="24/7 Teknik Operasyon Merkezi", layout="wide", page_icon="🏭")

# Dosya İsimleri
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
# 2. YAN MENÜ VE NAVİGASYON
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906319.png", width=100)
    st.title("Operasyon Paneli")
    
    menu = st.radio(
        "Modül Seçiniz:", 
        ["📋 Günlük İş Kayıtları", "🔄 Vardiya Defteri", "👥 Personel Yönetimi"]
    )
    
    st.markdown("---")
    st.info("📅 Tarih: " + datetime.now().strftime("%d-%m-%Y"))
    st.info("🕒 Saat: " + datetime.now().strftime("%H:%M"))

# -----------------------------------------------------------------------------
# 3. MODÜL: PERSONEL YÖNETİMİ (SORUMLU KİŞİLER)
# -----------------------------------------------------------------------------
if menu == "👥 Personel Yönetimi":
    st.header("👥 Teknik Personel ve Sorumlular")
    
    # Mevcut personeli yükle
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

    with col2:
        st.subheader("Mevcut Personel Listesi")
        st.dataframe(df_users, use_container_width=True)
        
        # Personel Silme Opsiyonu
        if not df_users.empty:
            del_user = st.selectbox("Silinecek Personeli Seç", df_users["Isim_Soyisim"].unique())
            if st.button("Personeli Sil"):
                df_users = df_users[df_users["Isim_Soyisim"] != del_user]
                save_data(df_users, FILE_USERS)
                st.rerun()

# -----------------------------------------------------------------------------
# 4. MODÜL: GÜNLÜK İŞ KAYITLARI (3 LİSTE SİSTEMİ)
# -----------------------------------------------------------------------------
elif menu == "📋 Günlük İş Kayıtları":
    st.header("📋 Teknik Kayıt Defteri (Log Book)")
    
    # Personel listesini çek (Dropdown için)
    users_df = load_data(FILE_USERS, ["Isim_Soyisim"])
    personel_listesi = users_df["Isim_Soyisim"].tolist() if not users_df.empty else ["Tanımsız"]

    # Ana Veriyi Yükle
    df_logs = load_data(FILE_LOGS, ["Tarih", "Saat", "Kategori", "Lokasyon", "Detay", "Sorumlu", "Durum"])

    # --- YENİ KAYIT FORMU ---
    with st.expander("➕ YENİ İŞ / ARIZA GİRİŞİ YAPMAK İÇİN TIKLAYIN", expanded=True):
        with st.form("log_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                kategori = st.selectbox("İş Kategorisi (Liste Tipi)", 
                                      ["Liste 1: Rutin Kontrol", "Liste 2: Arıza/Onarım", "Liste 3: Periyodik Bakım"])
            with c2:
                lokasyon = st.text_input("Lokasyon / Ekipman (Örn: Kazan Dairesi)")
            with c3:
                sorumlu = st.selectbox("İşi Yapan Teknisyen", personel_listesi)
            
            detay = st.text_area("Yapılan İşin Detayları / Arıza Tanımı")
            
            c4, c5 = st.columns(2)
            with c4:
                durum = st.selectbox("İşin Durumu", ["✅ Tamamlandı", "⚠️ Devam Ediyor", "🛑 Parça Bekliyor/Durdu", "👀 Gözlem Altında"])
            with c5:
                is_time = st.time_input("İşlem Saati", datetime.now().time())
            
            submit_log = st.form_submit_button("Kaydı Deftere İşle")
            
            if submit_log:
                new_log = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
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

    # --- LİSTE GÖRÜNÜMLERİ ---
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📝 Liste 1 (Rutin)", "🔧 Liste 2 (Arıza)", "⚙️ Liste 3 (Bakım)"])
    
    def show_table(category_name):
        # Filtreleme
        filtered_df = df_logs[df_logs["Kategori"] == category_name].sort_values(by=["Tarih", "Saat"], ascending=False)
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with tab1:
        st.caption("Günlük Rutin Kontrol Listesi")
        show_table("Liste 1: Rutin Kontrol")
        
    with tab2:
        st.caption("Arıza ve Onarım Müdahaleleri")
        show_table("Liste 2: Arıza/Onarım")
        
    with tab3:
        st.caption("Planlı Periyodik Bakımlar")
        show_table("Liste 3: Periyodik Bakım")

# -----------------------------------------------------------------------------
# 5. MODÜL: VARDİYA DEFTERİ (24 SAAT OPERASYON)
# -----------------------------------------------------------------------------
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Teslim Tutanakları")
    st.markdown("*Bu bölüm vardiya değişimlerinde ekiplerin birbirine bilgi aktarması içindir.*")

    # Personel listesini çek
    users_df = load_data(FILE_USERS, ["Isim_Soyisim"])
    personel_listesi = users_df["Isim_Soyisim"].tolist() if not users_df.empty else ["Tanımsız"]
    
    df_shifts = load_data(FILE_SHIFTS, ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Ozet_Notlar", "Kritik_Notlar"])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("✍️ Vardiya Teslim Et")
        with st.form("shift_form", clear_on_submit=True):
            vardiya_saati = st.selectbox("Vardiya Aralığı", ["08:00 - 16:00", "16:00 - 00:00", "00:00 - 08:00"])
            teslim_eden = st.selectbox("Teslim Eden Amiri", personel_listesi, key="te")
            teslim_alan = st.selectbox("Teslim Alan Amiri", personel_listesi, key="ta")
            
            ozet = st.text_area("Vardiya Özeti (Yapılan genel işler)")
            kritik = st.text_area("❗ KRİTİK NOTLAR / TAKİP EDİLMESİ GEREKENLER", 
                                  help="Sonraki vardiyanın mutlaka bilmesi gerekenler.")
            
            shift_submit = st.form_submit_button("Vardiyayı Kapat ve Teslim Et")
            
            if shift_submit:
                new_shift = {
                    "Tarih": datetime.now().strftime("%Y-%m-%d"),
                    "Vardiya": vardiya_saati,
                    "Teslim_Eden": teslim_eden,
                    "Teslim_Alan": teslim_alan,
                    "Ozet_Notlar": ozet,
                    "Kritik_Notlar": kritik
                }
                df_shifts = pd.concat([df_shifts, pd.DataFrame([new_shift])], ignore_index=True)
                save_data(df_shifts, FILE_SHIFTS)
                st.success("Vardiya kaydı başarıyla oluşturuldu.")

    with col2:
        st.subheader("📖 Geçmiş Vardiya Kayıtları")
        if not df_shifts.empty:
            # Son kayıtları en üstte göster
            df_display = df_shifts.sort_values(by="Tarih", ascending=False)
            
            for index, row in df_display.head(5).iterrows():
                with st.chat_message("assistant"):
                    st.write(f"**{row['Tarih']} | {row['Vardiya']}**")
                    st.write(f"👤 **Teslim Eden:** {row['Teslim_Eden']} ➡️ **Alan:** {row['Teslim_Alan']}")
                    st.info(f"📋 **Özet:** {row['Ozet_Notlar']}")
                    if row['Kritik_Notlar']:
                        st.error(f"❗ **KRİTİK:** {row['Kritik_Notlar']}")
                    st.divider()
        else:
            st.info("Henüz vardiya kaydı bulunmamaktadır.")

