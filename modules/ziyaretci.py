"""Ziyaretçi & Kargo takip modülü."""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from db import load_data, save_data
from style import section_header, data_table, status_badge
from auth import current_user, current_role
from barkod import yeni_id


KARGO_FIRMALAR = ["PTT", "Yurtiçi Kargo", "Aras Kargo", "MNG Kargo", "Sürat Kargo",
                   "UPS", "DHL", "FedEx", "Hepsi Express", "Diğer"]
ZIYARET_TIPLER = ["Aile", "Arkadaş", "Hizmet", "Teslimat", "Resmi", "Diğer"]
TESLIM_DURUM = ["Bekliyor", "Teslim Edildi", "İade"]


def render(secilen_tarih: date):
    rol = current_role()
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")
    daire_id = u.get("Daire_ID", "")

    if rol == "Sakin":
        _sakin_view(daire_id)
        return

    section_header("Ziyaretçi & Kargo", "Ziyaretçi kayıtları ve kargo takibi", pill="GÜVENLİK")

    tabs = st.tabs(["👥 Ziyaretçiler", "📦 Kargolar", "➕ Ziyaretçi Ekle", "📦 Kargo Ekle", "📊 Özet"])

    with tabs[0]:
        _ziyaretci_liste()
    with tabs[1]:
        _kargo_liste()
    with tabs[2]:
        _yeni_ziyaretci(kullanici, secilen_tarih)
    with tabs[3]:
        _yeni_kargo(kullanici, secilen_tarih)
    with tabs[4]:
        _ozet()


def _ziyaretci_liste():
    df = load_data("ziyaretci")
    if df.empty:
        st.info("Henüz ziyaretçi kaydı yok.")
        return

    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today(), key="ziy_bas")
    bit = c2.date_input("Bitiş", date.today(), key="ziy_bit")

    g = df.copy()
    try:
        d = pd.to_datetime(g["Tarih"], errors="coerce")
        g = g[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]
    except Exception:
        pass

    c1m, c2m = st.columns(2)
    c1m.metric("Bugün Ziyaretçi", len(df[df["Tarih"].astype(str) == str(date.today())]) if "Tarih" in df.columns else 0)
    c2m.metric("Dönem Toplam", len(g))

    data_table(
        g.sort_values("Tarih", ascending=False) if not g.empty else g,
        [("Ziyaretci_ID", "ID"), ("Tarih", "Tarih"), ("Giris_Saati", "Giriş"),
         ("Cikis_Saati", "Çıkış"), ("Isim", "Ziyaretçi"), ("Tip", "Tip"),
         ("Daire_ID", "Ziyaret Dairesi"), ("Plaka", "Araç Plakası"), ("Kaydeden", "Kaydeden")],
        id_cols=["Ziyaretci_ID"], avatar_cols=["Isim"], max_text=40,
    )

    st.divider()
    st.subheader("📝 Çıkış Kaydı")
    aktif = df[df["Cikis_Saati"].astype(str).isin(["", "nan", "None"])] if not df.empty else pd.DataFrame()
    if aktif.empty:
        st.success("Şu an içeride ziyaretçi yok.")
    else:
        sec = st.selectbox("Çıkış yapan", aktif["Ziyaretci_ID"].tolist(),
                           format_func=lambda x: f"{aktif[aktif['Ziyaretci_ID']==x]['Isim'].values[0]} - Daire {aktif[aktif['Ziyaretci_ID']==x]['Daire_ID'].values[0]}" if x in aktif["Ziyaretci_ID"].values else x)
        if st.button("🚪 Çıkış Kaydet", type="primary"):
            saat = datetime.now().strftime("%H:%M")
            df.loc[df["Ziyaretci_ID"] == sec, "Cikis_Saati"] = saat
            save_data(df, "ziyaretci")
            st.success(f"Çıkış kaydedildi: {saat}")
            st.rerun()


def _kargo_liste():
    df = load_data("kargo")
    if df.empty:
        st.info("Henüz kargo kaydı yok.")
        return

    c1, c2 = st.columns(2)
    durum_f = c1.selectbox("Durum", ["Tümü"] + TESLIM_DURUM)
    firma_f = c2.selectbox("Firma", ["Tümü"] + KARGO_FIRMALAR)

    g = df.copy()
    if durum_f != "Tümü":
        g = g[g["Durum"] == durum_f]
    if firma_f != "Tümü":
        g = g[g["Firma"] == firma_f]

    bekleyen = len(df[df["Durum"] == "Bekliyor"]) if "Durum" in df.columns else 0
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Bekleyen", bekleyen, delta="⚠️ Teslim Edilecek" if bekleyen > 0 else None, delta_color="inverse")
    c2m.metric("Teslim Edildi", len(df[df["Durum"] == "Teslim Edildi"]) if "Durum" in df.columns else 0)
    c3m.metric("Toplam", len(df))

    data_table(
        g.sort_values("Gelis_Tarihi", ascending=False) if not g.empty else g,
        [("Kargo_ID", "ID"), ("Gelis_Tarihi", "Geliş"), ("Firma", "Firma"),
         ("Alici_Daire", "Daire"), ("Alici_Isim", "Alıcı"), ("Takip_No", "Takip No"),
         ("Durum", "Durum"), ("Teslim_Tarihi", "Teslim"), ("Kaydeden", "Kaydeden")],
        id_cols=["Kargo_ID"], status_cols=["Durum"], avatar_cols=["Alici_Isim"],
        max_text=40,
    )

    st.divider()
    st.subheader("✅ Kargo Teslim Et")
    bekleyenler = df[df["Durum"] == "Bekliyor"] if not df.empty else pd.DataFrame()
    if bekleyenler.empty:
        st.success("Teslim bekleyen kargo yok.")
    else:
        sec = st.selectbox("Kargo seç", bekleyenler["Kargo_ID"].tolist(),
                           format_func=lambda x: f"Daire {bekleyenler[bekleyenler['Kargo_ID']==x]['Alici_Daire'].values[0]} — {bekleyenler[bekleyenler['Kargo_ID']==x]['Firma'].values[0]}" if x in bekleyenler["Kargo_ID"].values else x)
        teslim_alan = st.text_input("Teslim Alan Kişi")
        if st.button("📦 Teslim Kaydet", type="primary"):
            df.loc[df["Kargo_ID"] == sec, "Durum"] = "Teslim Edildi"
            df.loc[df["Kargo_ID"] == sec, "Teslim_Tarihi"] = str(date.today())
            df.loc[df["Kargo_ID"] == sec, "Teslim_Alan"] = teslim_alan
            save_data(df, "kargo")
            st.success("Teslim kaydedildi.")
            st.rerun()


def _yeni_ziyaretci(kullanici: str, secilen_tarih: date):
    df_d = load_data("daire")
    daire_opts = df_d["Daire_ID"].tolist() if not df_d.empty else []

    df = load_data("ziyaretci")
    with st.form("yeni_ziyaretci"):
        c1, c2 = st.columns(2)
        isim = c1.text_input("Ziyaretçi Adı Soyadı *")
        tip = c2.selectbox("Ziyaret Tipi", ZIYARET_TIPLER)
        c3, c4 = st.columns(2)
        daire = c3.selectbox("Ziyaret Edilen Daire", [""] + daire_opts)
        plaka = c4.text_input("Araç Plakası (opsiyonel)")
        giris = st.text_input("Giriş Saati", value=datetime.now().strftime("%H:%M"))
        notlar = st.text_area("Notlar")

        if st.form_submit_button("✅ Ziyaretçi Kaydı Oluştur", type="primary"):
            if isim.strip():
                row = {
                    "Ziyaretci_ID": yeni_id("ZIY"),
                    "Tarih": str(secilen_tarih),
                    "Giris_Saati": giris,
                    "Cikis_Saati": "",
                    "Isim": isim.strip(),
                    "Tip": tip,
                    "Daire_ID": daire,
                    "Plaka": plaka.strip(),
                    "Notlar": notlar.strip(),
                    "Kaydeden": kullanici,
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "ziyaretci")
                st.success(f"Ziyaretçi kaydı oluşturuldu: {isim}")
                st.rerun()
            else:
                st.error("Ziyaretçi adı zorunlu.")


def _yeni_kargo(kullanici: str, secilen_tarih: date):
    df_d = load_data("daire")
    daire_opts = df_d["Daire_ID"].tolist() if not df_d.empty else []

    df = load_data("kargo")
    with st.form("yeni_kargo"):
        c1, c2 = st.columns(2)
        firma = c1.selectbox("Kargo Firması *", KARGO_FIRMALAR)
        daire = c2.selectbox("Alıcı Daire *", [""] + daire_opts)
        c3, c4 = st.columns(2)
        alici = c3.text_input("Alıcı Adı")
        takip = c4.text_input("Takip No (opsiyonel)")
        notlar = st.text_area("Notlar")

        if st.form_submit_button("📦 Kargo Kaydı Oluştur", type="primary"):
            if firma and daire:
                row = {
                    "Kargo_ID": yeni_id("KRG"),
                    "Gelis_Tarihi": str(secilen_tarih),
                    "Firma": firma,
                    "Alici_Daire": daire,
                    "Alici_Isim": alici.strip(),
                    "Takip_No": takip.strip(),
                    "Notlar": notlar.strip(),
                    "Durum": "Bekliyor",
                    "Teslim_Tarihi": "",
                    "Teslim_Alan": "",
                    "Kaydeden": kullanici,
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "kargo")
                st.success(f"Kargo kaydedildi: {firma} → Daire {daire}")
                st.rerun()
            else:
                st.error("Firma ve daire zorunlu.")


def _ozet():
    df_z = load_data("ziyaretci")
    df_k = load_data("kargo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Bu Ay Ziyaretçi",
              len(df_z[pd.to_datetime(df_z["Tarih"], errors="coerce").dt.month == date.today().month]) if not df_z.empty else 0)
    c2.metric("Bekleyen Kargo", len(df_k[df_k["Durum"] == "Bekliyor"]) if not df_k.empty and "Durum" in df_k.columns else 0)
    c3.metric("Bu Ay Kargo", len(df_k[pd.to_datetime(df_k["Gelis_Tarihi"], errors="coerce").dt.month == date.today().month]) if not df_k.empty else 0)

    if not df_k.empty and "Firma" in df_k.columns:
        st.markdown("---")
        st.markdown("**Kargo Firmalarına Göre Dağılım**")
        st.bar_chart(df_k["Firma"].value_counts().head(8))


def _sakin_view(daire_id: str):
    section_header("Ziyaretçi & Kargolarım", "Bekleyen kargolarınız ve ziyaretçi kayıtları", pill="BİLGİ")

    if not daire_id:
        st.warning("Daire bilginiz tanımlı değil.")
        return

    # Bekleyen kargolar
    df_k = load_data("kargo")
    if not df_k.empty:
        bekleyen = df_k[(df_k["Alici_Daire"].astype(str) == str(daire_id)) &
                        (df_k["Durum"] == "Bekliyor")]
        if not bekleyen.empty:
            st.error(f"📦 **{len(bekleyen)} bekleyen kargonuz var!**")
            data_table(
                bekleyen,
                [("Kargo_ID", "ID"), ("Gelis_Tarihi", "Geliş"), ("Firma", "Firma"),
                 ("Takip_No", "Takip No"), ("Durum", "Durum")],
                id_cols=["Kargo_ID"], status_cols=["Durum"],
            )
        else:
            st.success("Bekleyen kargonuz yok.")

    # Son ziyaretçiler
    df_z = load_data("ziyaretci")
    if not df_z.empty:
        daire_z = df_z[df_z["Daire_ID"].astype(str) == str(daire_id)].sort_values("Tarih", ascending=False).head(10)
        if not daire_z.empty:
            st.subheader("👥 Son Ziyaretçilerim")
            data_table(
                daire_z,
                [("Tarih", "Tarih"), ("Giris_Saati", "Giriş"), ("Cikis_Saati", "Çıkış"),
                 ("Isim", "Ziyaretçi"), ("Tip", "Tip")],
                avatar_cols=["Isim"],
            )
