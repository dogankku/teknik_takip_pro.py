import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import io
import json
import uuid

# ── Opsiyonel kütüphaneler ───────────────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

try:
    import barcode as bc_lib
    from barcode.writer import ImageWriter
    BARCODE_OK = True
except ImportError:
    BARCODE_OK = False

try:
    import qrcode
    QR_OK = True
except ImportError:
    QR_OK = False

# ── Sayfa yapılandırması ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Teknik Operasyon Sistemi",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

# ── Sabitler ─────────────────────────────────────────────────────────────────
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEETS = {
    "checklist": "Checklist",
    "ariza":     "Arizalar",
    "vardiya":   "Vardiya",
    "personel":  "Personel",
    "ekipman":   "Ekipman",
}

COLS = {
    "checklist": ["Tarih", "Bolum", "Alt_Grup", "Soru", "Durum", "Aciklama", "Kontrol_Eden"],
    "ariza":     ["ID", "Tarih", "Saat", "Bolum", "Lokasyon", "Ariza_Tanimi", "Sorumlu", "Durum", "Kapanis_Tarihi"],
    "vardiya":   ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar"],
    "personel":  ["Isim", "Gorev", "Telefon"],
    "ekipman":   ["Barkod_ID", "Ekipman_Adi", "Kategori", "Lokasyon", "Marka_Model", "Seri_No", "Satin_Alma", "Sonraki_Bakim", "Durum", "Notlar"],
}

FILES = {k: f"vt_{k}.csv" for k in COLS}

# ── Session state başlatma ───────────────────────────────────────────────────
_defaults = {
    "admin_logged_in": False,
    "gs_creds": None,
    "gs_sid": "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Google Sheets bağlantısı ─────────────────────────────────────────────────
def _build_client(creds_dict: dict):
    creds = Credentials.from_service_account_info(creds_dict, scopes=GOOGLE_SCOPES)
    return gspread.authorize(creds)

def get_gs_client():
    if not GSPREAD_OK:
        return None
    if "gs_client_obj" in st.session_state:
        return st.session_state["gs_client_obj"]

    creds_dict = st.session_state.get("gs_creds")
    if creds_dict is None:
        # Streamlit secrets desteği
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            st.session_state["gs_creds"] = creds_dict
        else:
            return None

    try:
        client = _build_client(creds_dict)
        st.session_state["gs_client_obj"] = client
        return client
    except Exception as e:
        st.error(f"Google bağlantı hatası: {e}")
        return None

def _spreadsheet_id() -> str:
    sid = st.session_state.get("gs_sid", "").strip()
    if not sid and "spreadsheet_id" in st.secrets:
        sid = st.secrets["spreadsheet_id"]
        st.session_state["gs_sid"] = sid
    return sid

def get_worksheet(key: str):
    client = get_gs_client()
    sid = _spreadsheet_id()
    if client is None or not sid:
        return None
    try:
        spreadsheet = client.open_by_key(sid)
        try:
            return spreadsheet.worksheet(SHEETS[key])
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=SHEETS[key], rows=2000, cols=len(COLS[key]))
            ws.append_row(COLS[key])
            return ws
    except Exception as e:
        st.error(f"Google Sheets erişim hatası: {e}")
        return None

def load_data(key: str) -> pd.DataFrame:
    cols = COLS[key]
    ws = get_worksheet(key)
    if ws:
        try:
            records = ws.get_all_records()
            return pd.DataFrame(records) if records else pd.DataFrame(columns=cols)
        except Exception as e:
            st.warning(f"Google Sheets okuma hatası ({key}): {e}")
    if os.path.exists(FILES[key]):
        try:
            return pd.read_csv(FILES[key])
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_data(df: pd.DataFrame, key: str):
    ws = get_worksheet(key)
    if ws:
        try:
            ws.clear()
            rows = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
            ws.update(rows)
            return
        except Exception as e:
            st.warning(f"Google Sheets yazma hatası ({key}): {e}")
    df.to_csv(FILES[key], index=False)

# ── Barkod & QR üretici ──────────────────────────────────────────────────────
def make_barcode(code: str) -> io.BytesIO | None:
    if not BARCODE_OK:
        return None
    try:
        CODE128 = bc_lib.get_barcode_class("code128")
        buf = io.BytesIO()
        CODE128(code, writer=ImageWriter()).write(buf)
        buf.seek(0)
        return buf
    except Exception:
        return None

def make_qr(data: str) -> io.BytesIO | None:
    if not QR_OK:
        return None
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None

def yeni_barkod_id() -> str:
    return f"EKP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

# ── Kontrol soruları ─────────────────────────────────────────────────────────
SORU_GRUPLARI = {
    "Elektrik": {
        "1. Vardiya Başlangıç & Genel": [
            "1. Vardiya defteri incelendi mi?",
            "2. Bir önceki vardiyadan kalan işler tamamlandı mı?",
            "3. Vardiya boyunca olağandışı bir elektrik arızası yaşandı mı?",
        ],
        "2. Çevre & Dış Aydınlatma": [
            "4. Sokak ve bahçe aydınlatmaları yanıyor mu?",
            "5. Bina dış cephe kayar ışıklar ve yazıları çalışıyor mu?",
            "6. Cam üstü ledler (taç ışıkları) yanıyor mu?",
            "7. Çevre aydınlatma otomasyon zaman saatleri normal mi?",
        ],
        "3. Teknik Odalar Pano Kontrolleri (A Blok)": [
            "8. A Blok Kazan Dairesi: Panolarda arıza ışığı/sigorta atığı var mı?",
            "9. A Blok 25. Kat: Panolarda arıza ışığı var mı?",
            "10. A Blok 1. Bodrum: Panolarda arıza ışığı var mı?",
            "11. A Blok Asansör Makine Dairesi: Panolar ve klimalar enerjili mi?",
        ],
        "4. Teknik Odalar Pano Kontrolleri (B Blok)": [
            "12. B Blok Kazan Dairesi: Panolarda arıza ışığı var mı?",
            "13. B Blok 25. Kat: Panolarda arıza ışığı var mı?",
            "14. B Blok 1. Bodrum: Panolarda arıza ışığı var mı?",
            "15. B Blok Asansör Makine Dairesi: Panolar ve klimalar enerjili mi?",
        ],
        "5. Ortak Alan & Sosyal Tesis Panoları": [
            "16. Zemin Kat Restoran: Panolarda arıza ışığı var mı?",
            "17. Sosyal Tesis: Panolarda arıza ışığı var mı?",
            "18. 5. Bodrum Pompalar: Panolarda arıza ışığı var mı?",
            "19. 5. Bodrum Pompalar: Şalterler otomatik konumda mı?",
        ],
        "6. Jeneratör & Zayıf Akım Sistemleri": [
            "20. Jeneratör kumanda panelleri 'Otomatik' konumda mı?",
            "21. Jeneratör ön ısıtıcıları çalışıyor mu?",
            "22. Ana dağıtım ve kompanzasyon panolarında arıza alarmı var mı?",
            "23. Asansör içi müzik yayın sistemi çalışıyor mu?",
            "24. Otomasyon bilgisayarında 'Kırmızı' (Arıza) veren cihaz var mı?",
        ],
    },
    "Mekanik": {
        "1. Vardiya Başlangıç & Genel": [
            "1. Vardiya defteri incelendi mi?",
            "2. Bir önceki vardiyadan kalan işler tamamlandı mı?",
            "3. Vardiya boyunca su kesintisi veya mekanik arıza yaşandı mı?",
        ],
        "2. A Blok - Isıtma & Soğutma": [
            "4. A Blok Kazan Dairesi: Su basınçları normal mi?",
            "5. A Blok Kazan Dairesi: Su kaçağı var mı?",
            "6. A Blok 25. Kat: Sirkülasyon pompaları çalışıyor mu?",
            "7. A Blok 25. Kat: Taze hava ve egzoz santralleri çalışıyor mu?",
            "8. A Blok 1. Bodrum: Pompalar ve eşanjörler normal mi?",
        ],
        "3. B Blok - Isıtma & Soğutma": [
            "9. B Blok Kazan Dairesi: Su basınçları normal mi?",
            "10. B Blok Kazan Dairesi: Su kaçağı var mı?",
            "11. B Blok 25. Kat: Sirkülasyon pompaları çalışıyor mu?",
            "12. B Blok 25. Kat: Taze hava ve egzoz santralleri çalışıyor mu?",
            "13. B Blok 1. Bodrum: Pompalar ve eşanjörler normal mi?",
        ],
        "4. Su Basınçlandırma & Hidroforlar": [
            "14. Kullanma suyu hidroforları basıncı normal mi?",
            "15. Su depoları seviyeleri yeterli mi?",
            "16. Arıtma sistemi (Yumuşatma) cihazları devrede mi?",
            "17. Hidrofor odalarında su kaçağı var mı?",
        ],
        "5. Yangın Söndürme Sistemleri": [
            "18. Yangın pompaları 'Otomatik' konumda bekliyor mu?",
            "19. Yangın hattı (Sprinkler/Dolap) basıncı normal mi?",
            "20. Yangın suyu deposu tam dolu mu?",
            "21. Jokey pompalar sık devreye giriyor mu? (Kaçak kontrolü)",
        ],
        "6. Sosyal Tesis & Mutfaklar": [
            "22. Havuz mekanik dairesi: Pompalar ve filtreler normal mi?",
            "23. Restoran/Mutfak: Giderlerde tıkanıklık veya koku var mı?",
            "24. Mutfak davlumbaz fanları çalışıyor mu?",
            "25. Sosyal tesis havalandırma santralleri çalışıyor mu?",
        ],
    },
}

# ── Yardımcı: bağlantı durumu ────────────────────────────────────────────────
def gs_connected() -> bool:
    return bool(get_gs_client() and _spreadsheet_id())

# ── Yan menü ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏢 Teknik Operasyon")
    st.markdown("---")

    if gs_connected():
        st.success("☁️ Google Sheets bağlı")
    else:
        st.info("💾 Yerel CSV modu")

    st.markdown("---")

    if st.session_state["admin_logged_in"]:
        MENU_ITEMS = [
            "🏠 Ana Sayfa",
            "📊 Günlük Rapor",
            "✅ Kontrol Listeleri",
            "🛠️ Arıza Takip",
            "📦 Ekipman & Barkod",
            "🔄 Vardiya Defteri",
            "👥 Personel",
            "⚙️ Ayarlar",
            "🚪 Çıkış",
        ]
    else:
        MENU_ITEMS = [
            "🏠 Ana Sayfa",
            "✅ Kontrol Listeleri",
            "🛠️ Arıza Takip",
            "📦 Ekipman & Barkod",
            "🔄 Vardiya Defteri",
            "🔐 Yönetici Girişi",
        ]

    menu = st.radio("Menü", MENU_ITEMS, label_visibility="collapsed")
    st.markdown("---")
    secilen_tarih = st.date_input("📅 Tarih", date.today())

# ═════════════════════════════════════════════════════════════════════════════
# MODÜLLER
# ═════════════════════════════════════════════════════════════════════════════

# ── ANA SAYFA ────────────────────────────────────────────────────────────────
if menu == "🏠 Ana Sayfa":
    st.header("👋 Teknik Operasyon Sistemi")
    st.write(f"**Tarih:** {secilen_tarih.strftime('%d.%m.%Y')}")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.info("**✅ Kontrol Listeleri**\n\nElektrik ve Mekanik saha kontrolleri.")
    c2.warning("**🛠️ Arıza Takip**\n\nArıza kayıt ve iş emri sistemi.")
    c3.success("**🔄 Vardiya Defteri**\n\nDijital vardiya teslim tutanağı.")
    c4.info("**📦 Ekipman & Barkod**\n\nCode-128 ve QR kodlu ekipman takibi.")

# ── KONTROL LİSTELERİ ────────────────────────────────────────────────────────
elif menu == "✅ Kontrol Listeleri":
    st.header(f"✅ Günlük Kontroller ({secilen_tarih})")

    df_check = load_data("checklist")
    df_pers = load_data("personel")
    personel_listesi = df_pers["Isim"].tolist() if not df_pers.empty else ["Personel Yok"]

    tabs = st.tabs(list(SORU_GRUPLARI.keys()))

    for i, bolum in enumerate(SORU_GRUPLARI.keys()):
        with tabs[i]:
            st.subheader(f"📋 {bolum} Kontrol Formu")
            cp, _ = st.columns([1, 3])
            with cp:
                kontrolcu = st.selectbox("Kontrol Eden", personel_listesi, key=f"user_{bolum}")

            for alt_grup, sorular in SORU_GRUPLARI[bolum].items():
                with st.expander(f"📍 {alt_grup} ({len(sorular)} soru)", expanded=False):
                    tarih_str = str(secilen_tarih)
                    try:
                        kayitli = df_check[
                            (df_check["Tarih"] == tarih_str)
                            & (df_check["Bolum"] == bolum)
                            & (df_check["Alt_Grup"] == alt_grup)
                        ]
                    except KeyError:
                        kayitli = pd.DataFrame()

                    if not kayitli.empty:
                        st.success("✅ Bu grup tamamlandı")
                        st.dataframe(kayitli[["Soru", "Durum", "Aciklama"]], use_container_width=True)
                    else:
                        with st.form(f"form_{bolum}_{alt_grup}"):
                            st.caption("💡 Sorun yoksa açıklama yazmadan geçebilirsiniz.")
                            cevaplar = []
                            for idx, soru in enumerate(sorular):
                                c1, c2, c3 = st.columns([6, 2, 3])
                                c1.write(soru)
                                durum = c2.radio(
                                    "D",
                                    ["Tamam", "Sorunlu"],
                                    key=f"rd_{bolum}_{alt_grup}_{idx}",
                                    horizontal=True,
                                    label_visibility="collapsed",
                                )
                                not_txt = c3.text_input(
                                    "Not",
                                    key=f"nt_{bolum}_{alt_grup}_{idx}",
                                    label_visibility="collapsed",
                                )
                                cevaplar.append({
                                    "Tarih": tarih_str,
                                    "Bolum": bolum,
                                    "Alt_Grup": alt_grup,
                                    "Soru": soru,
                                    "Durum": durum,
                                    "Aciklama": not_txt,
                                    "Kontrol_Eden": kontrolcu,
                                })
                                st.divider()

                            if st.form_submit_button(f"💾 {alt_grup} Kaydet", type="primary"):
                                df_check = pd.concat([df_check, pd.DataFrame(cevaplar)], ignore_index=True)
                                save_data(df_check, "checklist")
                                st.success("Kaydedildi!")
                                st.rerun()

# ── ARIZA TAKİP ──────────────────────────────────────────────────────────────
elif menu == "🛠️ Arıza Takip":
    st.header("🛠️ Arıza Kayıtları")

    df_a = load_data("ariza")
    df_p = load_data("personel")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.expander("➕ Yeni Arıza Ekle", expanded=False):
        with st.form("add_ariza"):
            c1, c2 = st.columns(2)
            b = c1.selectbox("Bölüm", ["Elektrik", "Mekanik", "Genel", "Bina", "Asansör"])
            stt = c2.selectbox("Durum", ["Açık", "Devam Ediyor", "Tamamlandı"])
            l = st.text_input("Lokasyon")
            s = st.selectbox("Sorumlu", pl)
            d = st.text_area("Arıza Tanımı")
            if st.form_submit_button("💾 Kaydet", type="primary"):
                ariza_id = f"ARZ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                row = {
                    "ID": ariza_id,
                    "Tarih": str(secilen_tarih),
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Bolum": b,
                    "Lokasyon": l,
                    "Ariza_Tanimi": d,
                    "Sorumlu": s,
                    "Durum": stt,
                    "Kapanis_Tarihi": str(secilen_tarih) if stt == "Tamamlandı" else "",
                }
                df_a = pd.concat([df_a, pd.DataFrame([row])], ignore_index=True)
                save_data(df_a, "ariza")
                st.success(f"Arıza kaydedildi: {ariza_id}")
                st.rerun()

    col1, col2 = st.columns(2)
    filtre_durum = col1.multiselect(
        "Durum Filtresi",
        ["Açık", "Devam Ediyor", "Tamamlandı"],
        default=["Açık", "Devam Ediyor"],
    )

    if not df_a.empty and "Durum" in df_a.columns and filtre_durum:
        gosterilen = df_a[df_a["Durum"].isin(filtre_durum)]
    else:
        gosterilen = df_a

    st.dataframe(
        gosterilen.sort_values(by="Tarih", ascending=False) if not gosterilen.empty else gosterilen,
        use_container_width=True,
    )

# ── EKİPMAN & BARKOD ─────────────────────────────────────────────────────────
elif menu == "📦 Ekipman & Barkod":
    st.header("📦 Ekipman Takip & Barkod Sistemi")

    df_e = load_data("ekipman")

    tab1, tab2, tab3 = st.tabs(["📋 Ekipman Listesi", "➕ Yeni Ekipman", "🔍 Barkod Sorgula"])

    # ── Ekipman Listesi ──────────────────────────────────────────────────────
    with tab1:
        if df_e.empty:
            st.info("Henüz ekipman eklenmemiş. 'Yeni Ekipman' sekmesinden ekleyebilirsiniz.")
        else:
            col1, col2 = st.columns(2)
            kategoriler = ["Tümü"] + sorted(df_e["Kategori"].dropna().unique().tolist()) if "Kategori" in df_e.columns else ["Tümü"]
            filtre_kat = col1.selectbox("Kategori Filtresi", kategoriler)
            durumlar = ["Tümü"] + sorted(df_e["Durum"].dropna().unique().tolist()) if "Durum" in df_e.columns else ["Tümü"]
            filtre_dur = col2.selectbox("Durum Filtresi", durumlar)

            gost = df_e.copy()
            if filtre_kat != "Tümü":
                gost = gost[gost["Kategori"] == filtre_kat]
            if filtre_dur != "Tümü":
                gost = gost[gost["Durum"] == filtre_dur]

            st.dataframe(gost, use_container_width=True)

            st.markdown("---")
            st.subheader("🔖 Barkod & QR Kodu Görüntüle")

            ekipman_isimleri = df_e["Ekipman_Adi"].tolist() if "Ekipman_Adi" in df_e.columns else []
            if ekipman_isimleri:
                secili = st.selectbox("Ekipman seçin", ekipman_isimleri)
                row = df_e[df_e["Ekipman_Adi"] == secili].iloc[0]
                barkod_id = str(row.get("Barkod_ID", ""))

                col_bc, col_qr = st.columns(2)

                with col_bc:
                    st.caption("**📊 Code-128 Barkod**")
                    bc_img = make_barcode(barkod_id)
                    if bc_img:
                        st.image(bc_img, caption=barkod_id)
                        st.download_button(
                            "⬇️ Barkod İndir (PNG)",
                            bc_img,
                            file_name=f"{barkod_id}_barkod.png",
                            mime="image/png",
                        )
                    else:
                        st.warning("Barkod kütüphanesi yüklü değil.")
                        st.code("pip install python-barcode[images]")

                with col_qr:
                    st.caption("**📱 QR Kod**")
                    qr_data = "\n".join([
                        f"ID: {row.get('Barkod_ID', '')}",
                        f"Ekipman: {row.get('Ekipman_Adi', '')}",
                        f"Kategori: {row.get('Kategori', '')}",
                        f"Lokasyon: {row.get('Lokasyon', '')}",
                        f"Marka/Model: {row.get('Marka_Model', '')}",
                        f"Seri No: {row.get('Seri_No', '')}",
                        f"Durum: {row.get('Durum', '')}",
                        f"Bakım: {row.get('Sonraki_Bakim', '')}",
                    ])
                    qr_img = make_qr(qr_data)
                    if qr_img:
                        st.image(qr_img, caption="QR Kod", width=220)
                        st.download_button(
                            "⬇️ QR İndir (PNG)",
                            qr_img,
                            file_name=f"{barkod_id}_qr.png",
                            mime="image/png",
                        )
                    else:
                        st.warning("QR kütüphanesi yüklü değil.")
                        st.code("pip install qrcode[pil]")

                with st.expander("📋 Ekipman Detayları"):
                    st.json(row.to_dict())

    # ── Yeni Ekipman ─────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Yeni Ekipman Kayıt")
        auto_id = yeni_barkod_id()
        st.info(f"🏷️ Otomatik Barkod ID: **{auto_id}**")

        with st.form("add_ekipman"):
            c1, c2 = st.columns(2)
            ekipman_adi = c1.text_input("Ekipman Adı *")
            kategori = c2.selectbox(
                "Kategori",
                ["Elektrik", "Mekanik", "HVAC", "Yangın", "Asansör", "Jeneratör", "Otomasyon", "Diğer"],
            )

            c3, c4 = st.columns(2)
            lokasyon = c3.text_input("Lokasyon")
            marka_model = c4.text_input("Marka / Model")

            c5, c6 = st.columns(2)
            seri_no = c5.text_input("Seri Numarası")
            durum = c6.selectbox("Durum", ["Aktif", "Bakımda", "Arızalı", "Hurdaya Ayrıldı"])

            c7, c8 = st.columns(2)
            satin_alma = c7.date_input("Satın Alma Tarihi", date.today())
            sonraki_bakim = c8.date_input("Sonraki Bakım Tarihi", date.today())

            notlar = st.text_area("Notlar")

            if st.form_submit_button("💾 Ekipman Kaydet & Barkod Oluştur", type="primary"):
                if ekipman_adi.strip():
                    row = {
                        "Barkod_ID": auto_id,
                        "Ekipman_Adi": ekipman_adi.strip(),
                        "Kategori": kategori,
                        "Lokasyon": lokasyon,
                        "Marka_Model": marka_model,
                        "Seri_No": seri_no,
                        "Satin_Alma": str(satin_alma),
                        "Sonraki_Bakim": str(sonraki_bakim),
                        "Durum": durum,
                        "Notlar": notlar,
                    }
                    df_e = pd.concat([df_e, pd.DataFrame([row])], ignore_index=True)
                    save_data(df_e, "ekipman")
                    st.success(f"✅ Ekipman kaydedildi! Barkod ID: **{auto_id}**")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Ekipman adı zorunludur.")

    # ── Barkod Sorgula ────────────────────────────────────────────────────────
    with tab3:
        st.subheader("🔍 Barkod ID veya İsim ile Sorgula")
        query = st.text_input("Arama", placeholder="EKP-20240101-XXXX  veya  pompa")

        if query and not df_e.empty:
            sonuc = df_e[
                df_e.apply(
                    lambda r: query.lower() in str(r.get("Barkod_ID", "")).lower()
                    or query.lower() in str(r.get("Ekipman_Adi", "")).lower(),
                    axis=1,
                )
            ]
            if not sonuc.empty:
                st.success(f"{len(sonuc)} ekipman bulundu.")
                st.dataframe(sonuc, use_container_width=True)

                if len(sonuc) == 1:
                    row = sonuc.iloc[0]
                    bid = str(row.get("Barkod_ID", ""))
                    col_bc, col_qr = st.columns(2)
                    with col_bc:
                        bc_img = make_barcode(bid)
                        if bc_img:
                            st.image(bc_img, caption=bid)
                            st.download_button("⬇️ Barkod İndir", bc_img, f"{bid}_barkod.png", "image/png")
                    with col_qr:
                        qr_img = make_qr(f"ID:{bid}\n{row.get('Ekipman_Adi','')}\n{row.get('Lokasyon','')}")
                        if qr_img:
                            st.image(qr_img, width=200)
                            st.download_button("⬇️ QR İndir", qr_img, f"{bid}_qr.png", "image/png")
            else:
                st.warning("Eşleşen ekipman bulunamadı.")

# ── GÜNLÜK RAPOR ─────────────────────────────────────────────────────────────
elif menu == "📊 Günlük Rapor":
    st.header(f"📊 Günlük Rapor ({secilen_tarih})")

    df_c = load_data("checklist")
    df_a = load_data("ariza")

    t = str(secilen_tarih)
    gc = df_c[df_c["Tarih"] == t] if not df_c.empty and "Tarih" in df_c.columns else pd.DataFrame()
    ga = df_a[df_a["Tarih"] == t] if not df_a.empty and "Tarih" in df_a.columns else pd.DataFrame()

    sorunlu = gc[gc["Durum"] == "Sorunlu"] if not gc.empty and "Durum" in gc.columns else pd.DataFrame()
    acik = ga[ga["Durum"] == "Açık"] if not ga.empty and "Durum" in ga.columns else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kontrol Sayısı", len(gc))
    col2.metric("Arıza Sayısı", len(ga))
    col3.metric("Sorunlu Kontrol", len(sorunlu))
    col4.metric("Açık Arıza", len(acik))

    st.divider()

    st.subheader("⚠️ Sorunlu Kontroller")
    if not sorunlu.empty:
        st.dataframe(sorunlu, use_container_width=True)
    else:
        st.info("Bugün sorunlu kontrol yok.")

    st.subheader("🛠️ Bugünkü Arızalar")
    if not ga.empty:
        st.dataframe(ga, use_container_width=True)
    else:
        st.info("Bugün arıza kaydı yok.")

# ── VARDİYA DEFTERİ ──────────────────────────────────────────────────────────
elif menu == "🔄 Vardiya Defteri":
    st.header("🔄 Vardiya Defteri")

    df_v = load_data("vardiya")
    df_p = load_data("personel")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.form("add_vardiya"):
        c1, c2, c3 = st.columns(3)
        v = c1.selectbox("Vardiya", ["08:00-16:00", "16:00-00:00", "00:00-08:00"])
        te = c2.selectbox("Teslim Eden", pl)
        ta = c3.selectbox("Teslim Alan", pl)
        n = st.text_area("Notlar / Devir Bilgileri")
        if st.form_submit_button("💾 Kaydet", type="primary"):
            row = {"Tarih": str(secilen_tarih), "Vardiya": v, "Teslim_Eden": te, "Teslim_Alan": ta, "Notlar": n}
            df_v = pd.concat([df_v, pd.DataFrame([row])], ignore_index=True)
            save_data(df_v, "vardiya")
            st.success("Vardiya kaydedildi.")
            st.rerun()

    st.dataframe(
        df_v.sort_values(by="Tarih", ascending=False) if not df_v.empty else df_v,
        use_container_width=True,
    )

# ── PERSONEL ─────────────────────────────────────────────────────────────────
elif menu == "👥 Personel":
    st.header("👥 Personel Yönetimi")

    df_p = load_data("personel")

    with st.form("add_personel"):
        c1, c2, c3 = st.columns(3)
        i = c1.text_input("İsim *")
        g = c2.text_input("Görev")
        t = c3.text_input("Telefon")
        if st.form_submit_button("➕ Ekle", type="primary"):
            if i.strip():
                df_p = pd.concat([df_p, pd.DataFrame([{"Isim": i.strip(), "Gorev": g, "Telefon": t}])], ignore_index=True)
                save_data(df_p, "personel")
                st.success("Personel eklendi.")
                st.rerun()
            else:
                st.error("İsim zorunludur.")

    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True)

# ── AYARLAR ──────────────────────────────────────────────────────────────────
elif menu == "⚙️ Ayarlar":
    st.header("⚙️ Google Workspace Ayarları")

    with st.expander("📖 Kurulum Rehberi", expanded=False):
        st.markdown("""
**Google Sheets entegrasyonu için adımlar:**

1. [Google Cloud Console](https://console.cloud.google.com) → Yeni Proje oluşturun
2. **APIs & Services → Library** → "Google Sheets API" ve "Google Drive API" etkinleştirin
3. **APIs & Services → Credentials** → "Create Credentials → Service Account" seçin
4. Oluşturulan hesabın **Keys** sekmesinden JSON anahtar indirin
5. Google Sheet'i açın ve sağ üstten **Paylaş** → hizmet hesabı e-postasını ekleyin (Düzenleyici)
6. Sheet URL'sinden ID'yi kopyalayın: `docs.google.com/spreadsheets/d/**ID**/edit`
        """)

    st.subheader("1️⃣ Service Account JSON")

    if st.session_state.get("gs_creds"):
        email = st.session_state["gs_creds"].get("client_email", "")
        st.success(f"✅ Bağlı hesap: `{email}`")
        if st.button("🗑️ Kimlik Bilgilerini Temizle"):
            st.session_state["gs_creds"] = None
            if "gs_client_obj" in st.session_state:
                del st.session_state["gs_client_obj"]
            st.rerun()
    else:
        uploaded = st.file_uploader("Service Account JSON dosyasını yükleyin", type=["json"])
        if uploaded:
            try:
                creds_dict = json.load(uploaded)
                st.session_state["gs_creds"] = creds_dict
                if "gs_client_obj" in st.session_state:
                    del st.session_state["gs_client_obj"]
                st.success(f"✅ Yüklendi: `{creds_dict.get('client_email', '')}`")
                st.rerun()
            except Exception as e:
                st.error(f"JSON okunamadı: {e}")

    st.markdown("---")
    st.subheader("2️⃣ Spreadsheet ID")
    sid = st.text_input(
        "Google Sheets ID",
        value=st.session_state.get("gs_sid", ""),
        placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
    )
    if st.button("💾 Kaydet & Bağlan", type="primary"):
        st.session_state["gs_sid"] = sid.strip()
        st.rerun()

    st.markdown("---")
    st.subheader("3️⃣ Bağlantı Testi")
    if st.button("🔌 Bağlantıyı Test Et"):
        ws = get_worksheet("personel")
        if ws:
            st.success("✅ Google Sheets bağlantısı başarılı!")
        else:
            st.error("❌ Bağlantı kurulamadı. Kimlik bilgilerini ve ID'yi kontrol edin.")

    st.markdown("---")
    st.subheader("4️⃣ Yönetici Şifresi")
    st.info("Şifre değiştirmek için kaynak kodundaki `'1234'` değerini güncelleyin.")

# ── YÖNETİCİ GİRİŞİ ──────────────────────────────────────────────────────────
elif menu == "🔐 Yönetici Girişi":
    st.header("🔐 Yönetici Girişi")
    with st.form("login_form"):
        p = st.text_input("Şifre", type="password")
        if st.form_submit_button("Giriş Yap"):
            if p == "1234":
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("Hatalı şifre.")

# ── ÇIKIŞ ────────────────────────────────────────────────────────────────────
elif menu == "🚪 Çıkış":
    st.session_state["admin_logged_in"] = False
    st.rerun()
