import streamlit as st
import json
from datetime import date
from db import get_worksheet


def render(secilen_tarih: date):
    st.header("⚙️ Google Workspace Ayarları")

    with st.expander("📖 Kurulum Rehberi"):
        st.markdown("""
1. [Google Cloud Console](https://console.cloud.google.com) → Yeni Proje oluşturun
2. **APIs & Services → Library** → "Google Sheets API" + "Google Drive API" etkinleştirin
3. **APIs & Services → Credentials** → "Create Credentials → Service Account"
4. Hesabın **Keys** sekmesinden JSON anahtar indirin
5. Google Sheet'i açın → **Paylaş** → hizmet hesabı e-postasını Editör olarak ekleyin
6. Sheet URL'sinden ID'yi kopyalayın: `docs.google.com/spreadsheets/d/**ID**/edit`
        """)

    st.subheader("1️⃣ Service Account JSON")
    if st.session_state.get("gs_creds"):
        email = st.session_state["gs_creds"].get("client_email", "")
        st.success(f"✅ Bağlı: `{email}`")
        if st.button("🗑️ Bağlantıyı Temizle"):
            st.session_state["gs_creds"] = None
            if "gs_client_obj" in st.session_state:
                del st.session_state["gs_client_obj"]
            st.rerun()
    else:
        up = st.file_uploader("Service Account JSON", type=["json"])
        if up:
            try:
                creds = json.load(up)
                st.session_state["gs_creds"] = creds
                if "gs_client_obj" in st.session_state:
                    del st.session_state["gs_client_obj"]
                st.success(f"Yüklendi: {creds.get('client_email', '')}")
                st.rerun()
            except Exception as e:
                st.error(f"JSON okunamadı: {e}")

    st.markdown("---")
    st.subheader("2️⃣ Spreadsheet ID")
    sid = st.text_input("Spreadsheet ID",
        value=st.session_state.get("gs_sid", ""),
        placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")
    if st.button("💾 Kaydet & Bağlan", type="primary"):
        st.session_state["gs_sid"] = sid.strip()
        st.rerun()

    st.markdown("---")
    st.subheader("3️⃣ Bağlantı Testi")
    if st.button("🔌 Test Et"):
        ws = get_worksheet("personel")
        if ws:
            st.success("✅ Google Sheets bağlantısı çalışıyor!")
        else:
            st.error("❌ Bağlantı kurulamadı.")

    st.markdown("---")
    st.subheader("ℹ️ Bilgi")
    st.info("""
**Veri saklama:**
- Google Sheets bağlandığında tüm veriler bulutta saklanır
- Bağlantı yoksa yerel CSV dosyalarına yedeklenir
- Streamlit Secrets ile `gcp_service_account` ve `spreadsheet_id` tanımlanabilir
    """)
