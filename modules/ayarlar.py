from style import section_header
import streamlit as st
import json, base64
from datetime import date
from db import get_worksheet, load_data, save_data
from constants import ROLLER, ALL_MODULES, YETKI


_DEFAULT_YETKI = {
    "Yonetici":  ["ana", "rapor", "checklist", "ariza", "ekipman", "daire", "talep",
                  "bakim", "aidat", "stok", "sayac", "vardiya", "personel", "ayarlar",
                  "lokasyon", "sablon", "tekrar", "maliyet", "aktivite_log", "media",
                  "duyuru", "rezervasyon", "ziyaretci"],
    "Teknisyen": ["ana", "checklist", "ariza", "ekipman", "talep", "bakim", "stok",
                  "vardiya", "tekrar", "ziyaretci"],
    "Sakin":     ["ana", "sakin_talep", "sakin_aidat",
                  "sakin_duyuru", "sakin_rezervasyon", "sakin_ziyaretci"],
}


def render(secilen_tarih: date):
    section_header("Ayarlar", "Bina bilgileri, yetki ve bildirim yönetimi", pill="YAPILANDIRMA")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Bina Bilgileri", "🔒 Yetki Yönetimi", "🔔 Bildirim Ayarları",
        "☁️ Google Sheets", "📖 Kurulum Rehberi",
    ])
    with tab1: _bina_bilgileri()
    with tab2: _yetki_yonetimi()
    with tab3: _bildirim_ayarlari()
    with tab4: _google_sheets_ayarlari()
    with tab5: _kurulum_rehberi()


# ─────────────────────────────────────────────────────────────────────────────
def _bina_bilgileri():
    st.markdown("**🏢 Bina / Site Bilgileri**")
    bina_adi   = st.session_state.get("bina_adi", "Teknik Operasyon Sistemi")
    bina_adres = st.session_state.get("bina_adres", "")
    bina_tel   = st.session_state.get("bina_tel", "")
    bina_email = st.session_state.get("bina_email", "")
    bina_vergi = st.session_state.get("bina_vergi", "")
    with st.form("bina_form"):
        ad    = st.text_input("Bina / Site Adı *", value=bina_adi)
        adres = st.text_area("Adres", value=bina_adres, height=80)
        c1, c2 = st.columns(2)
        tel = c1.text_input("Telefon", value=bina_tel)
        em  = c2.text_input("Email",   value=bina_email)
        vn  = st.text_input("Vergi No / IBAN", value=bina_vergi)
        st.markdown("**🖼️ Logo Yükle**")
        logo_file = st.file_uploader("PNG / JPG logo (max 1MB)", type=["png","jpg","jpeg"], key="logo_upload")
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
                    st.warning("Logo 1 MB'ı aşıyor.")
            st.success("Bina bilgileri kaydedildi.")
            st.rerun()
    logo_b64 = st.session_state.get("bina_logo_b64")
    if logo_b64:
        try:
            st.image(base64.b64decode(logo_b64), width=200, caption="Mevcut logo")
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
def _yetki_yonetimi():
    st.markdown(
        '<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
        'padding:12px 16px;margin-bottom:16px;">'
        '<b style="color:#1D4ED8;">ℹ️ Nasıl çalışır?</b><br>'
        '<span style="color:#1E40AF;font-size:.85rem;">'
        '1. <b>Rol Bazlı Matris</b>: Her rol hangi modüllere erişebilir.<br>'
        '2. <b>Kullanıcı Override</b>: Belirli kullanıcıya ek modül aç veya kapat.<br>'
        'Admin rolü her zaman tüm modüllere erişir.'
        '</span></div>', unsafe_allow_html=True,
    )
    subtab1, subtab2 = st.tabs(["📋 Rol Bazlı Matrix", "👤 Kullanıcı Override"])
    with subtab1: _rol_matrix()
    with subtab2: _kullanici_override()


def _rol_matrix():
    import pandas as pd
    df_yr = load_data("yetki_rol")
    rol_modulleri: dict = {}
    for rol in ["Yonetici", "Teknisyen", "Sakin"]:
        if not df_yr.empty:
            row = df_yr[df_yr["Rol"] == rol]
            if not row.empty:
                try:
                    rol_modulleri[rol] = json.loads(str(row.iloc[0].get("Modul_JSON","[]")))
                    continue
                except Exception:
                    pass
        rol_modulleri[rol] = _DEFAULT_YETKI.get(rol, [])

    sec_rol = st.selectbox("Rol seç", ["Yonetici", "Teknisyen", "Sakin"])
    mevcut  = rol_modulleri[sec_rol]
    st.markdown(f"**`{sec_rol}` rolü — modül erişimleri:**")
    st.caption("Admin her zaman tüm modüllere erişir.")

    cols = st.columns(3)
    sec_moduller = []
    for i, (key, label) in enumerate(ALL_MODULES.items()):
        if cols[i % 3].checkbox(label, value=(key in mevcut), key=f"yrm_{sec_rol}_{key}"):
            sec_moduller.append(key)

    col_k, col_r = st.columns(2)
    if col_k.button("💾 Kaydet", type="primary", key=f"yr_save_{sec_rol}"):
        if not df_yr.empty and sec_rol in df_yr["Rol"].values:
            df_yr.loc[df_yr["Rol"] == sec_rol, "Modul_JSON"] = json.dumps(sec_moduller, ensure_ascii=False)
        else:
            yeni = pd.DataFrame([{"Rol": sec_rol, "Modul_JSON": json.dumps(sec_moduller, ensure_ascii=False)}])
            df_yr = pd.concat([df_yr, yeni], ignore_index=True)
        save_data(df_yr, "yetki_rol")
        st.success(f"`{sec_rol}` yetkisi güncellendi ({len(sec_moduller)} modül).")
        st.rerun()

    if col_r.button("🔄 Varsayılana Sıfırla", key=f"yr_reset_{sec_rol}"):
        default_list = _DEFAULT_YETKI.get(sec_rol, [])
        if not df_yr.empty and sec_rol in df_yr["Rol"].values:
            df_yr.loc[df_yr["Rol"] == sec_rol, "Modul_JSON"] = json.dumps(default_list, ensure_ascii=False)
        else:
            yeni = pd.DataFrame([{"Rol": sec_rol, "Modul_JSON": json.dumps(default_list, ensure_ascii=False)}])
            df_yr = pd.concat([df_yr, yeni], ignore_index=True)
        save_data(df_yr, "yetki_rol")
        st.info(f"`{sec_rol}` varsayılana döndürüldü.")
        st.rerun()


def _kullanici_override():
    df_k = load_data("kullanici")
    if df_k.empty:
        st.info("Kullanıcı bulunamadı.")
        return
    kullanicilar = df_k[df_k["Rol"] != "Admin"]["Kullanici_Adi"].tolist()
    if not kullanicilar:
        st.info("Override uygulanabilecek kullanıcı yok.")
        return

    sec = st.selectbox(
        "Kullanıcı seç", kullanicilar,
        format_func=lambda x: (
            f"{df_k[df_k['Kullanici_Adi']==x]['Ad_Soyad'].values[0]} ({x})"
            if x in df_k["Kullanici_Adi"].values else x
        ),
    )
    row = df_k[df_k["Kullanici_Adi"] == sec].iloc[0]
    try:
        ekstra = json.loads(str(row.get("Ekstra_Modul","") or "[]"))
    except Exception:
        ekstra = []
    try:
        kapali = json.loads(str(row.get("Kapali_Modul","") or "[]"))
    except Exception:
        kapali = []

    st.markdown(f"**{row.get('Ad_Soyad','')} — Rol: `{row.get('Rol','')}`**")
    col_e, col_k = st.columns(2)
    with col_e:
        st.markdown("**➕ Ek Modül Aç**")
        yeni_ekstra = st.multiselect(
            "Ekstra modüller", options=list(ALL_MODULES.keys()), default=ekstra,
            format_func=lambda k: ALL_MODULES.get(k, k), key=f"ov_e_{sec}",
        )
    with col_k:
        st.markdown("**🚫 Modül Kapat**")
        yeni_kapali = st.multiselect(
            "Kapalı modüller", options=list(ALL_MODULES.keys()), default=kapali,
            format_func=lambda k: ALL_MODULES.get(k, k), key=f"ov_k_{sec}",
        )

    col_s, col_c = st.columns(2)
    if col_s.button("💾 Override Kaydet", type="primary", key=f"ov_save_{sec}"):
        df_k.loc[df_k["Kullanici_Adi"] == sec, "Ekstra_Modul"] = json.dumps(yeni_ekstra, ensure_ascii=False)
        df_k.loc[df_k["Kullanici_Adi"] == sec, "Kapali_Modul"] = json.dumps(yeni_kapali, ensure_ascii=False)
        save_data(df_k, "kullanici")
        cu = st.session_state.get("current_user", {})
        if cu.get("Kullanici_Adi") == sec:
            cu["Ekstra_Modul"] = json.dumps(yeni_ekstra, ensure_ascii=False)
            cu["Kapali_Modul"] = json.dumps(yeni_kapali, ensure_ascii=False)
            st.session_state["current_user"] = cu
        st.success("Override kaydedildi.")
        st.rerun()

    if (ekstra or kapali) and col_c.button("🔄 Temizle", key=f"ov_clear_{sec}"):
        df_k.loc[df_k["Kullanici_Adi"] == sec, "Ekstra_Modul"] = "[]"
        df_k.loc[df_k["Kullanici_Adi"] == sec, "Kapali_Modul"] = "[]"
        save_data(df_k, "kullanici")
        st.info("Override temizlendi.")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
def _bildirim_ayarlari():
    st.markdown("Bildirim kanallarını yapılandırın.")
    st.caption("💡 Kalıcı yapılandırma için Streamlit Secrets kullanın (📖 Kurulum sekmesi).")

    st.subheader("⚙️ Kanal Aktivasyonları")
    g = st.session_state.get("bildirim_genel", {})
    c1, c2, c3 = st.columns(3)
    email_ak = c1.toggle("📧 E-posta", value=bool(g.get("email_aktif")),    key="tog_email")
    tg_ak    = c2.toggle("✈️ Telegram", value=bool(g.get("telegram_aktif")), key="tog_tg")
    wa_ak    = c3.toggle("📱 WhatsApp",  value=bool(g.get("whatsapp_aktif")), key="tog_wa")
    st.session_state["bildirim_genel"] = {"email_aktif": email_ak, "telegram_aktif": tg_ak, "whatsapp_aktif": wa_ak}

    st.divider()

    # ── E-posta ──
    with st.expander("📧 E-posta (SMTP) Ayarları", expanded=email_ak):
        cfg_e = st.session_state.get("bildirim_email", {})
        with st.form("form_email"):
            c1, c2 = st.columns(2)
            smtp_s  = c1.text_input("SMTP Sunucu",   value=str(cfg_e.get("smtp_sunucu","")), placeholder="smtp.gmail.com")
            smtp_p  = c2.number_input("Port",         value=int(cfg_e.get("smtp_port",587) or 587), min_value=1, max_value=65535)
            c3, c4  = st.columns(2)
            smtp_u  = c3.text_input("Kullanıcı Adı", value=str(cfg_e.get("smtp_user","")))
            smtp_pw = c4.text_input("Şifre",          type="password", value=str(cfg_e.get("smtp_pwd","")))
            smtp_sn = st.text_input("Gönderici",      value=str(cfg_e.get("smtp_sender","")), placeholder="noreply@site.com")
            col_s, col_t = st.columns(2)
            if col_s.form_submit_button("💾 Kaydet"):
                st.session_state["bildirim_email"] = {
                    "smtp_sunucu": smtp_s.strip(), "smtp_port": smtp_p,
                    "smtp_user": smtp_u.strip(), "smtp_pwd": smtp_pw, "smtp_sender": smtp_sn.strip(),
                }
                st.success("E-posta ayarları kaydedildi.")
            if col_t.form_submit_button("🧪 Test"):
                st.session_state["bildirim_email"] = {
                    "smtp_sunucu": smtp_s.strip(), "smtp_port": smtp_p,
                    "smtp_user": smtp_u.strip(), "smtp_pwd": smtp_pw, "smtp_sender": smtp_sn.strip(),
                }
                from bildirim_helper import test_email
                ok, err = test_email(smtp_u.strip())
                st.success("✅ Test maili gönderildi.") if ok else st.error(f"❌ {err}")
        st.caption("Gmail: Hesap → Güvenlik → Uygulama şifreleri → 'Diğer' → şifreyi kopyala")

    # ── Telegram ──
    with st.expander("✈️ Telegram Bot Ayarları", expanded=tg_ak):
        cfg_t = st.session_state.get("bildirim_telegram", {})
        with st.form("form_telegram"):
            tok = st.text_input("Bot Token",       value=str(cfg_t.get("bot_token","")), placeholder="1234567890:AAF...")
            cid = st.text_input("Grup Chat ID",    value=str(cfg_t.get("chat_id","")),   placeholder="-1001234567890")
            col_s, col_t = st.columns(2)
            if col_s.form_submit_button("💾 Kaydet"):
                st.session_state["bildirim_telegram"] = {"bot_token": tok.strip(), "chat_id": cid.strip()}
                st.success("Telegram ayarları kaydedildi.")
            if col_t.form_submit_button("🧪 Test"):
                st.session_state["bildirim_telegram"] = {"bot_token": tok.strip(), "chat_id": cid.strip()}
                from bildirim_helper import test_telegram
                ok, err = test_telegram()
                st.success("✅ Test mesajı gönderildi.") if ok else st.error(f"❌ {err}")
        st.caption("@BotFather → /newbot → token al → gruba ekle → getUpdates ile chat_id bul")

    # ── WhatsApp ──
    with st.expander("📱 WhatsApp (Twilio) Ayarları", expanded=wa_ak):
        cfg_w = st.session_state.get("bildirim_whatsapp", {})
        with st.form("form_whatsapp"):
            sid  = st.text_input("Account SID",    value=str(cfg_w.get("account_sid","")), placeholder="ACxxxxx")
            auth = st.text_input("Auth Token",      type="password", value=str(cfg_w.get("auth_token","")))
            frm  = st.text_input("From (WhatsApp)", value=str(cfg_w.get("from_number","whatsapp:+14155238886")))
            c1, _ = st.columns(2)
            test_tel = c1.text_input("Test Numarası", placeholder="+905001234567")
            col_s, col_t = st.columns(2)
            if col_s.form_submit_button("💾 Kaydet"):
                st.session_state["bildirim_whatsapp"] = {"account_sid": sid.strip(), "auth_token": auth, "from_number": frm.strip()}
                st.success("WhatsApp ayarları kaydedildi.")
            if col_t.form_submit_button("🧪 Test"):
                st.session_state["bildirim_whatsapp"] = {"account_sid": sid.strip(), "auth_token": auth, "from_number": frm.strip()}
                if test_tel.strip():
                    from bildirim_helper import test_whatsapp
                    ok, err = test_whatsapp(test_tel.strip())
                    st.success("✅ WhatsApp test gönderildi.") if ok else st.error(f"❌ {err}")
                else:
                    st.warning("Test numarası girin.")
        st.caption("twilio.com/console → Account SID + Auth Token | Sandbox: +14155238886'ye 'join <kelime>' yazın")

    # ── Tetikleyiciler ──
    st.divider()
    st.subheader("🎯 Bildirim Tetikleyiciler")
    t = st.session_state.get("bildirim_tetikler", {})
    c1, c2 = st.columns(2)
    with c1:
        t["ariza_yeni"]    = st.checkbox("🛠️ Yeni Arıza oluşturuldu",          value=t.get("ariza_yeni", True))
        t["talep_yeni"]    = st.checkbox("📨 Yeni Talep oluşturuldu",           value=t.get("talep_yeni", True))
        t["bakim_vadesi"]  = st.checkbox("📅 Bakım vadesi yaklaştı (7 gün)",    value=t.get("bakim_vadesi", True))
    with c2:
        t["stok_kritik"]   = st.checkbox("📦 Stok kritik seviyeye düştü",       value=t.get("stok_kritik", True))
        t["vardiya_devir"] = st.checkbox("🔄 Vardiya devri yapıldı",            value=t.get("vardiya_devir", False))
        t["rez_onay"]      = st.checkbox("📅 Rezervasyon onay/ret bildirim",    value=t.get("rez_onay", True))
    st.session_state["bildirim_tetikler"] = t
    if st.button("💾 Tetikleyicileri Kaydet"):
        st.success("Bildirim tercihleri güncellendi.")


# ─────────────────────────────────────────────────────────────────────────────
def _google_sheets_ayarlari():
    import json as _json
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
                creds = _json.load(up)
                st.session_state["gs_creds"] = creds
                if "gs_client_obj" in st.session_state:
                    del st.session_state["gs_client_obj"]
                st.success(f"Yüklendi: {creds.get('client_email','')}")
                st.rerun()
            except Exception as e:
                st.error(f"JSON okunamadı: {e}")
    st.markdown("---")
    st.subheader("2️⃣ Spreadsheet ID")
    sid = st.text_input("Spreadsheet ID", value=st.session_state.get("gs_sid",""),
                         placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")
    if st.button("💾 Kaydet & Bağlan", type="primary"):
        st.session_state["gs_sid"] = sid.strip()
        st.rerun()
    st.markdown("---")
    st.subheader("3️⃣ Bağlantı Testi")
    if st.button("🔌 Test Et"):
        ws = get_worksheet("personel")
        st.success("✅ Bağlantı çalışıyor!") if ws else st.error("❌ Bağlantı kurulamadı.")
    st.markdown("---")
    st.subheader("🔐 Streamlit Secrets (Önerilen)")
    st.info("""
Streamlit Community Cloud'da kalıcı bağlantı için **Secrets** kullanın:

```toml
spreadsheet_id = "YOUR_SPREADSHEET_ID_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project"
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"

[bildirim_email]
smtp_sunucu = "smtp.gmail.com"
smtp_port = 587
smtp_user = "noreply@site.com"
smtp_pwd = "uygulama-sifresi"

[bildirim_telegram]
bot_token = "1234567890:AAFxxx"
chat_id = "-1001234567890"

[bildirim_whatsapp]
account_sid = "ACxxx"
auth_token = "xxx"
from_number = "whatsapp:+14155238886"
```
    """)


# ─────────────────────────────────────────────────────────────────────────────
def _kurulum_rehberi():
    st.markdown("""
### Google Sheets Entegrasyonu

1. **Google Cloud Console** → Yeni Proje
2. **APIs** → Google Sheets API + Google Drive API etkinleştir
3. **Credentials** → Service Account → JSON anahtar indir
4. Google Sheet → **Paylaş** → service account e-postasını Editör yap
5. Sheet URL'den ID kopyala

---

### Gerekli Paketler

```
streamlit>=1.35    gspread>=6.0       google-auth>=2.28
pandas>=2.2        plotly>=5.20       openpyxl>=3.1
requests>=2.31     twilio>=8.0        reportlab>=4.1
python-barcode>=0.15   qrcode[pil]>=7.4   Pillow>=10.3
```

---

### Roller ve Yetkiler

| Rol | Erişim |
|-----|--------|
| Admin | Tüm modüller — değiştirilemez |
| Yonetici / Teknisyen / Sakin | Ayarlar → Yetki Yönetimi'nden yapılandırılır |
    """)
