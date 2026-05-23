from style import section_header
import streamlit as st
import json
import base64
from datetime import date
from db import get_worksheet, load_data, save_data


def render(secilen_tarih: date):
    section_header("Ayarlar", "Bina bilgileri, Google Workspace bağlantısı ve sistem ayarları", pill="YAPILANDIRMA")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Bina Bilgileri", "🔒 Yetki Yönetimi",
        "🔔 Bildirim Ayarları", "☁️ Google Sheets", "📖 Kurulum Rehberi"
    ])

    # ── TAB 0: Bina Bilgileri ─────────────────────────────────────────────────
    with tab1:
        _bina_bilgileri()

    # ── TAB 1: Yetki Yönetimi ─────────────────────────────────────────────────
    with tab2:
        _yetki_yonetimi()

    # ── TAB 2: Bildirim Ayarları ──────────────────────────────────────────────
    with tab3:
        _bildirim_ayarlari()

    # ── TAB 3: Google Sheets ──────────────────────────────────────────────────
    with tab4:
        _google_sheets_ayarlari()

    # ── TAB 4: Kurulum Rehberi ────────────────────────────────────────────────
    with tab5:
        _kurulum_rehberi()


def _yetki_yonetimi():
    st.subheader("🔒 Dinamik Yetki Yönetimi")
    try:
        from constants import ALL_MODULES, ROLLER, YETKI
    except ImportError:
        st.error("ALL_MODULES constants'ta tanımlı değil.")
        return

    sub1, sub2 = st.tabs(["📊 Rol Bazlı Matris", "👤 Kullanıcı Override"])

    with sub1:
        st.caption("Rol için hangi modüllere erişim olacağını seçin. Kaydet ile DB'ye yazılır.")
        rol_sec = st.selectbox("Rol", [r for r in ROLLER if r != "Admin"], key="ym_rol")

        # Mevcut ayarları yükle
        df_yr = load_data("yetki_rol")
        mevcut_moduller = []
        if not df_yr.empty:
            row = df_yr[df_yr["Rol"].astype(str) == rol_sec]
            if not row.empty:
                try:
                    mevcut_moduller = json.loads(str(row.iloc[0].get("Modul_JSON", "[]") or "[]"))
                except Exception:
                    pass
        if not mevcut_moduller:
            mevcut_moduller = YETKI.get(rol_sec, [])

        secilen = []
        cols = st.columns(3)
        for i, (key, label) in enumerate(ALL_MODULES.items()):
            checked = cols[i % 3].checkbox(label, value=(key in mevcut_moduller), key=f"ym_{rol_sec}_{key}")
            if checked:
                secilen.append(key)

        c1, c2 = st.columns(2)
        if c1.button("💾 Kaydet", type="primary", key="ym_kaydet"):
            df_yr = load_data("yetki_rol")
            new_row = {"Rol": rol_sec, "Modul_JSON": json.dumps(secilen, ensure_ascii=False)}
            if not df_yr.empty and (df_yr["Rol"].astype(str) == rol_sec).any():
                df_yr.loc[df_yr["Rol"].astype(str) == rol_sec, "Modul_JSON"] = new_row["Modul_JSON"]
            else:
                import pandas as pd
                df_yr = pd.concat([df_yr, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_yr, "yetki_rol")
            st.success(f"✅ {rol_sec} yetkileri kaydedildi. ({len(secilen)} modül)")
            st.rerun()
        if c2.button("🔄 Varsayılana Sıfırla", key="ym_sifirla"):
            df_yr = load_data("yetki_rol")
            if not df_yr.empty:
                df_yr = df_yr[df_yr["Rol"].astype(str) != rol_sec]
                save_data(df_yr, "yetki_rol")
            st.success(f"{rol_sec} için DB kaydı silindi — sabit varsayılan kullanılacak.")
            st.rerun()

    with sub2:
        st.caption("Belirli kullanıcıya ekstra modül ver veya mevcut modülü kapat.")
        df_k = load_data("kullanici")
        if df_k.empty:
            st.info("Kullanıcı yok.")
            return
        kullanici_adi = st.selectbox("Kullanıcı",
            df_k["Kullanici_Adi"].tolist(),
            format_func=lambda x: f"{x} ({df_k[df_k['Kullanici_Adi']==x]['Ad_Soyad'].values[0] if x in df_k['Kullanici_Adi'].values else ''})",
            key="ym_user_sec")
        mask = df_k["Kullanici_Adi"] == kullanici_adi
        u_row = df_k[mask].iloc[0]
        try:
            ekstra = json.loads(str(u_row.get("Ekstra_Modul", "") or "[]"))
        except Exception:
            ekstra = []
        try:
            kapali = json.loads(str(u_row.get("Kapali_Modul", "") or "[]"))
        except Exception:
            kapali = []
        modul_opts = list(ALL_MODULES.keys())
        modul_labels = [f"{k} — {v}" for k, v in ALL_MODULES.items()]
        new_ekstra = st.multiselect("➕ Ekstra modül izni ver", modul_opts,
            default=ekstra, format_func=lambda x: ALL_MODULES.get(x, x), key="ym_ekstra")
        new_kapali = st.multiselect("🚫 Modülü kapat (deny)", modul_opts,
            default=kapali, format_func=lambda x: ALL_MODULES.get(x, x), key="ym_kapali")
        if st.button("💾 Kullanıcı Yetkisini Güncelle", type="primary", key="ym_user_kaydet"):
            df_k.loc[mask, "Ekstra_Modul"] = json.dumps(new_ekstra, ensure_ascii=False)
            df_k.loc[mask, "Kapali_Modul"] = json.dumps(new_kapali, ensure_ascii=False)
            save_data(df_k, "kullanici")
            st.success(f"✅ {kullanici_adi} yetkileri güncellendi.")
            st.rerun()


def _bildirim_ayarlari():
    st.subheader("🔔 Çok Kanallı Bildirim Sistemi")
    st.caption("Email, Telegram ve WhatsApp bildirimlerini buradan yapılandırın.")

    # Kanalları aç/kapat
    st.markdown("##### Kanal Seçimi")
    c1, c2, c3 = st.columns(3)
    email_ak = c1.toggle("📧 Email (SMTP)", value=st.session_state.get("bildirim_email_aktif", False), key="bl_email_ak")
    tg_ak = c2.toggle("✈️ Telegram", value=st.session_state.get("bildirim_telegram_aktif", False), key="bl_tg_ak")
    wa_ak = c3.toggle("💬 WhatsApp", value=st.session_state.get("bildirim_whatsapp_aktif", False), key="bl_wa_ak")
    st.session_state["bildirim_email_aktif"] = email_ak
    st.session_state["bildirim_telegram_aktif"] = tg_ak
    st.session_state["bildirim_whatsapp_aktif"] = wa_ak

    # Email ayarları
    if email_ak:
        with st.expander("📧 Email (SMTP) Ayarları", expanded=True):
            with st.form("smtp_form"):
                c1, c2 = st.columns(2)
                smtp_sunucu = c1.text_input("SMTP Sunucu", value=st.session_state.get("bildirim_email", {}).get("smtp_sunucu", "smtp.gmail.com"))
                smtp_port = c2.number_input("Port", value=int(st.session_state.get("bildirim_email", {}).get("smtp_port", 587)), min_value=1)
                smtp_user = st.text_input("Kullanıcı Adı / Email", value=st.session_state.get("bildirim_email", {}).get("smtp_user", ""))
                smtp_pwd = st.text_input("Şifre / App Password", type="password", value=st.session_state.get("bildirim_email", {}).get("smtp_pwd", ""))
                smtp_sender = st.text_input("Gönderen Adı", value=st.session_state.get("bildirim_email", {}).get("smtp_sender", "Teknik Takip Pro"))
                test_to = st.text_input("Test gönder → Email", placeholder="test@example.com")
                c_save, c_test = st.columns(2)
                if c_save.form_submit_button("💾 Kaydet", type="primary"):
                    st.session_state["bildirim_email"] = {
                        "smtp_sunucu": smtp_sunucu, "smtp_port": smtp_port,
                        "smtp_user": smtp_user, "smtp_pwd": smtp_pwd, "smtp_sender": smtp_sender,
                        "aktif": True,
                    }
                    st.success("Email ayarları kaydedildi.")
                if c_test.form_submit_button("📤 Test Gönder"):
                    if test_to.strip():
                        try:
                            from bildirim_helper import test_email
                            ok, msg = test_email(test_to.strip())
                            st.success(msg) if ok else st.error(msg)
                        except Exception as e:
                            st.error(f"Test hatası: {e}")
                    else:
                        st.warning("Test için email adresi girin.")

    # Telegram ayarları
    if tg_ak:
        with st.expander("✈️ Telegram Bot Ayarları", expanded=True):
            with st.form("tg_form"):
                bot_token = st.text_input("Bot Token", value=st.session_state.get("bildirim_telegram", {}).get("bot_token", ""), type="password")
                chat_id = st.text_input("Chat ID (kanal/grup)", value=st.session_state.get("bildirim_telegram", {}).get("chat_id", ""))
                c_save, c_test = st.columns(2)
                if c_save.form_submit_button("💾 Kaydet", type="primary"):
                    st.session_state["bildirim_telegram"] = {"bot_token": bot_token, "chat_id": chat_id, "aktif": True}
                    st.success("Telegram ayarları kaydedildi.")
                if c_test.form_submit_button("📤 Test Gönder"):
                    try:
                        from bildirim_helper import test_telegram
                        ok, msg = test_telegram(chat_id or None)
                        st.success(msg) if ok else st.error(msg)
                    except Exception as e:
                        st.error(f"Test hatası: {e}")

    # WhatsApp ayarları
    if wa_ak:
        with st.expander("💬 WhatsApp (Twilio) Ayarları", expanded=True):
            with st.form("wa_form"):
                account_sid = st.text_input("Account SID", value=st.session_state.get("bildirim_whatsapp", {}).get("account_sid", ""), type="password")
                auth_token = st.text_input("Auth Token", value=st.session_state.get("bildirim_whatsapp", {}).get("auth_token", ""), type="password")
                from_no = st.text_input("Twilio WhatsApp Numarası", value=st.session_state.get("bildirim_whatsapp", {}).get("from_no", ""), placeholder="+14155238886")
                test_tel = st.text_input("Test gönder → Telefon", placeholder="+905001234567")
                c_save, c_test = st.columns(2)
                if c_save.form_submit_button("💾 Kaydet", type="primary"):
                    st.session_state["bildirim_whatsapp"] = {
                        "account_sid": account_sid, "auth_token": auth_token,
                        "from_no": from_no, "aktif": True,
                    }
                    st.success("WhatsApp ayarları kaydedildi.")
                if c_test.form_submit_button("📤 Test Gönder"):
                    if test_tel.strip():
                        try:
                            from bildirim_helper import test_whatsapp
                            ok, msg = test_whatsapp(test_tel.strip())
                            st.success(msg) if ok else st.error(msg)
                        except Exception as e:
                            st.error(f"Test hatası: {e}")
                    else:
                        st.warning("Test için telefon numarası girin.")

    st.divider()
    st.markdown("##### Bildirim Tetikleyicileri")
    st.caption("Hangi olaylar için bildirim gönderilsin?")
    tetikler = st.session_state.get("bildirim_tetikler", {})
    c1, c2, c3 = st.columns(3)
    tetikler["ariza_yeni"]    = c1.checkbox("🛠️ Yeni Arıza",          value=tetikler.get("ariza_yeni", True),    key="ttr_ariza")
    tetikler["talep_yeni"]    = c2.checkbox("📨 Yeni Talep",           value=tetikler.get("talep_yeni", True),    key="ttr_talep")
    tetikler["bakim_vadesi"]  = c3.checkbox("📅 Bakım Vadesi (3 gün)", value=tetikler.get("bakim_vadesi", True),  key="ttr_bakim")
    tetikler["stok_kritik"]   = c1.checkbox("⚠️ Kritik Stok",          value=tetikler.get("stok_kritik", True),   key="ttr_stok")
    tetikler["vardiya_devir"] = c2.checkbox("🔄 Vardiya Devri",        value=tetikler.get("vardiya_devir", False), key="ttr_vardiya")
    tetikler["rez_onay"]      = c3.checkbox("📅 Rezervasyon Onayı",    value=tetikler.get("rez_onay", True),      key="ttr_rez")
    st.session_state["bildirim_tetikler"] = tetikler


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
