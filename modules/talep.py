from style import section_header
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from db import load_data, save_data
from auth import current_user, current_role
from barkod import yeni_id
from constants import TALEP_KATEGORI, ONCELIK_SLA


def render(secilen_tarih: date):
    rol = current_role()
    if rol == "Sakin":
        _sakin_talep_view()
    else:
        _yonetim_talep_view(secilen_tarih)


def _sakin_talep_view():
    """Sakinin sadece kendi taleplerini görüp yeni talep oluşturduğu görünüm."""
    u = current_user() or {}
    daire_id = u.get("Daire_ID", "")
    ad_soyad = u.get("Ad_Soyad", "")

    section_header("Talep & Şikayet", "Yeni talep oluşturun ve geçmişi görüntüleyin", pill="DAİRENİZ")
    st.caption(f"Daire: **{daire_id or '(atanmamış)'}**")

    if not daire_id:
        st.warning("Hesabınıza daire atanmamış. Yöneticiden talep edin.")
        return

    with st.expander("➕ Yeni Talep / Şikayet Oluştur", expanded=True):
        with st.form("sakin_talep"):
            c1, c2 = st.columns(2)
            kat = c1.selectbox("Kategori", TALEP_KATEGORI)
            onc = c2.selectbox("Öncelik", list(ONCELIK_SLA.keys()), index=2)
            basl = st.text_input("Başlık *")
            ack = st.text_area("Açıklama *")
            if st.form_submit_button("📨 Gönder", type="primary"):
                if basl.strip() and ack.strip():
                    _yeni_talep_kaydet(daire_id, ad_soyad, kat, basl, ack, onc, atanan="")
                    st.success("Talebiniz iletildi.")
                    st.rerun()
                else:
                    st.error("Başlık ve açıklama zorunlu.")

    df = load_data("talep")
    if not df.empty:
        mine = df[df["Daire_ID"].astype(str) == str(daire_id)].sort_values("Tarih", ascending=False)
        st.subheader("📋 Geçmiş Taleplerim")
        st.dataframe(mine[["Talep_ID", "Tarih", "Kategori", "Baslik", "Oncelik",
                           "Durum", "Atanan", "Cozum_Notu"]],
                     use_container_width=True, hide_index=True)


def _yonetim_talep_view(secilen_tarih: date):
    section_header("Talep Yönetimi", "Tüm sakin talepleri, atama ve SLA takibi", pill="OPERASYON")

    df = load_data("talep")
    df_d = load_data("daire")
    df_p = load_data("personel")

    daire_ops = df_d["Daire_ID"].tolist() if not df_d.empty else []
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    with st.expander("➕ Talep Oluştur (yönetici)"):
        if not daire_ops:
            st.warning("Önce daire ekleyin.")
        else:
            with st.form("y_talep"):
                c1, c2, c3 = st.columns(3)
                d = c1.selectbox("Daire", daire_ops)
                k = c2.selectbox("Kategori", TALEP_KATEGORI)
                o = c3.selectbox("Öncelik", list(ONCELIK_SLA.keys()), index=2)
                ad = st.text_input("Talep Eden Ad Soyad")
                b = st.text_input("Başlık *")
                ack = st.text_area("Açıklama *")
                at = st.selectbox("Atanan Personel (boş bırakılabilir)", ["-"] + pers)
                if st.form_submit_button("💾 Kaydet", type="primary"):
                    if b.strip():
                        _yeni_talep_kaydet(d, ad, k, b, ack, o, at if at != "-" else "")
                        st.success("Kaydedildi.")
                        st.rerun()

    if df.empty:
        st.info("Henüz talep yok.")
        return

    # Filtreler
    c1, c2, c3, c4 = st.columns(4)
    dur_opts = ["Tümü", "Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"]
    onc_opts = ["Tümü"] + list(ONCELIK_SLA.keys())
    df_dur = c1.selectbox("Durum", dur_opts)
    df_onc = c2.selectbox("Öncelik", onc_opts)
    df_kat = c3.selectbox("Kategori", ["Tümü"] + TALEP_KATEGORI)
    df_at = c4.selectbox("Atanan", ["Tümü", "Atanmamış"] + pers)

    g = df.copy()
    if df_dur != "Tümü": g = g[g["Durum"] == df_dur]
    if df_onc != "Tümü": g = g[g["Oncelik"] == df_onc]
    if df_kat != "Tümü": g = g[g["Kategori"] == df_kat]
    if df_at == "Atanmamış":
        g = g[g["Atanan"].astype(str).isin(["", "nan", "None"])]
    elif df_at != "Tümü":
        g = g[g["Atanan"] == df_at]

    # SLA gecikmiş işaretle
    g = _sla_durum_ekle(g)
    st.dataframe(g.sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("✏️ Talep Güncelle / Çöz")
    sec = st.selectbox("Talep", df["Talep_ID"].tolist())
    row = df[df["Talep_ID"] == sec].iloc[0]
    st.write(f"**{row['Baslik']}** — {row.get('Aciklama','')}")

    c1, c2 = st.columns(2)
    yd = c1.selectbox("Yeni Durum", ["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"],
                      index=["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"].index(row.get("Durum", "Açık"))
                      if row.get("Durum", "Açık") in ["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"] else 0)
    ya = c2.selectbox("Atanan", ["-"] + pers,
                      index=(["-"] + pers).index(row.get("Atanan")) if row.get("Atanan") in pers else 0)
    cn = st.text_area("Çözüm Notu", value=str(row.get("Cozum_Notu", "")))
    if st.button("💾 Güncelle", type="primary"):
        df.loc[df["Talep_ID"] == sec, "Durum"] = yd
        df.loc[df["Talep_ID"] == sec, "Atanan"] = "" if ya == "-" else ya
        df.loc[df["Talep_ID"] == sec, "Cozum_Notu"] = cn
        if yd == "Çözüldü":
            df.loc[df["Talep_ID"] == sec, "Cozum_Tarihi"] = str(date.today())
        save_data(df, "talep")
        st.success("Güncellendi.")
        st.rerun()


def _yeni_talep_kaydet(daire_id, sakin_ad, kategori, baslik, aciklama, oncelik, atanan):
    df = load_data("talep")
    tid = yeni_id("TLP")
    durum = "Atandı" if atanan else "Açık"
    row = {
        "Talep_ID": tid, "Tarih": str(date.today()),
        "Saat": datetime.now().strftime("%H:%M"),
        "Daire_ID": daire_id, "Sakin": sakin_ad,
        "Kategori": kategori, "Baslik": baslik.strip(),
        "Aciklama": aciklama.strip(), "Oncelik": oncelik,
        "Durum": durum, "Atanan": atanan,
        "SLA_Saat": ONCELIK_SLA.get(oncelik, 72),
        "Cozum_Tarihi": "", "Cozum_Notu": "",
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, "talep")


def _sla_durum_ekle(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    def _sla_kontrol(r):
        if r.get("Durum") in ("Çözüldü", "Kapatıldı"):
            return "✅"
        try:
            olus = datetime.strptime(f"{r['Tarih']} {r['Saat']}", "%Y-%m-%d %H:%M")
            sla_saat = float(r.get("SLA_Saat", 72))
            son_tarih = olus + timedelta(hours=sla_saat)
            kalan = son_tarih - datetime.now()
            if kalan.total_seconds() < 0:
                return f"🔴 Gecikti ({-int(kalan.total_seconds()//3600)}s)"
            elif kalan.total_seconds() < 3600 * 4:
                return f"🟡 {int(kalan.total_seconds()//3600)}s kaldı"
            else:
                return f"🟢 {int(kalan.total_seconds()//3600)}s kaldı"
        except Exception:
            return ""
    df["SLA"] = df.apply(_sla_kontrol, axis=1)
    return df
