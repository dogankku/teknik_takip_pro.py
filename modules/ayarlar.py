from style import section_header
import streamlit as st
import json
import base64
from datetime import date
from db import get_worksheet


def render(secilen_tarih: date):
    section_header("Ayarlar", "Bina bilgileri, Google Workspace bağlantısı ve sistem ayarları", pill="YAPILANDIRMA")

    tab1, tab2, tab3 = st.tabs(["🏢 Bina Bilgileri", "☁️ Google Sheets", "📖 Kurulum Rehberi"])

    # ── TAB 0: Bina Bilgileri ─────────────────────────────────────────────────
    with tab1:
        _bina_bilgileri()

    # ── TAB 1: Google Sheets ──────────────────────────────────────────────────
    with tab2:
        _google_sheets_ayarlari()

    # ── TAB 2: Kurulum Rehberi ────────────────────────────────────────────────
    with tab3:
        _kurulum_rehberi()


def _bina_bilgileri():
    st.markdown("**🏢 Bina / Site Bilgileri**")

    bina_adi   = st.session_state.get("bina_adi", "Teknik Operasyon Sistemi")
    bina_adres = st.session_state.get("bina_adres", "")
    bina_tel   = st.session_state.get("bina_tel", "")
    bina_email = st.session_state.get("bina_email", "")
    bina_vergi = st.session_state.get("bina_vergi", "")

    with st.form("bina_form"):
        ad = st.text_input("Bina / Site Adı *", value=bina_adi)
        adres = st.text_area("Adres", value=bina_adres, height=80)
        c1, c2 = st.columns(2)
        tel = c1.text_input("Telefon", value=bina_tel)
        em = c2.text_input("Email", value=bina_email)
        vn = st.text_input("Vergi No / IBAN", value=bina_vergi)

        st.markdown("**🖼️ Logo Yükle**")
        logo_file = st.file_uploader("PNG / JPG logo (max 1MB)", type=["png", "jpg", "jpeg"],
                                      key="logo_upload")

        if st.form_submit_button("💾 Kaydet", type="primary"):
            st.session_state["bina_adi"]   = ad.strip() or bina_adi
            st.session_state["bina_adres"] = adres.strip()
            st.session_state["bina_tel"]   = tel.strip()
            st.session_state["bina_email"] = em.strip()
            st.session_state["bina_vergi"] = vn.strip()

            if logo_file:
                raw = logo_file.read()
                if len(raw) <= 1_048_576:
                    st.session_state["bina_logo_b64"] = base64.b64encode(raw).decode()
                    st.success("Logo yüklendi.")
                else:
                    st.warning("Logo 1 MB'ı aşıyor, yüklenmedi.")

            st.success("Bina bilgileri kaydedildi.")
            st.rerun()

    # Logo önizleme
    logo_b64 = st.session_state.get("bina_logo_b64")
    if logo_b64:
        try:
            import base64 as _b64
            logo_bytes = _b64.b64decode(logo_b64)
            st.image(logo_bytes, width=200, caption="Mevcut logo")
        except Exception:
            pass


def _google_sheets_ayarlari():
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
    st.subheader("🔐 Streamlit Secrets (Önerilen)")
    st.info("""
Streamlit Community Cloud'da kalıcı bağlantı için **Secrets** kullanın:

1. Uygulama sayfanızda **Settings → Secrets** açın
2. Aşağıdaki formatı yapıştırın:

```toml
spreadsheet_id = "YOUR_SPREADSHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key_id = "key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

Secrets ayarlandığında uygulama her başlatmada otomatik bağlanır.
    """)


def _kurulum_rehberi():
    st.markdown("""
### Google Sheets Entegrasyonu — Adım Adım

1. **Google Cloud Console** → Yeni Proje oluşturun
2. **APIs & Services → Library** → "Google Sheets API" + "Google Drive API" etkinleştirin
3. **APIs & Services → Credentials** → "Create Credentials → Service Account"
4. Hesabın **Keys** sekmesinden JSON anahtar indirin
5. Google Sheet'i açın → **Paylaş** → hizmet hesabı e-postasını **Editör** olarak ekleyin
6. Sheet URL'sinden ID'yi kopyalayın:
   `docs.google.com/spreadsheets/d/**BURASI_ID**/edit`

---

### Veri Saklama

| Mod | Açıklama |
|-----|----------|
| ☁️ Google Sheets | Tüm veriler bulutta, çok kullanıcılı, kalıcı |
| 💾 CSV Yedek | Bağlantı yoksa `data/` klasörüne yerel CSV |

---

### Gerekli Python Paketleri

```
streamlit>=1.35
gspread>=6.0
google-auth>=2.28
pandas>=2.2
plotly>=5.20
python-barcode>=0.15
qrcode[pil]>=7.4
reportlab>=4.1
openpyxl>=3.1
Pillow>=10.3
```

---

### Roller ve Yetkiler

| Rol | Erişim |
|-----|--------|
| Admin | Tüm modüller + Kullanıcı Yönetimi + Ayarlar |
| Yonetici | Tüm modüller (kullanıcı yönetimi hariç) |
| Teknisyen | İş emirleri, envanter, vardiya |
| Sakin | Talep ve aidat görünümü |
    """)
