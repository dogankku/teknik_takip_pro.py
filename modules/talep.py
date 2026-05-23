from style import section_header
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from db import load_data, save_data
from auth import current_user, current_role
from barkod import yeni_id
from constants import TALEP_KATEGORI, ONCELIK_SLA
from yorum_helper import render_yorumlar
from aktivite_helper import log_ekle
from media import upload_widget, render_photo_grid


def render(secilen_tarih: date):
    rol = current_role()
    if rol == "Sakin":
        _sakin_talep_view()
    else:
        _yonetim_talep_view(secilen_tarih)


def _sakin_talep_view():
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
                    tid = _yeni_talep_kaydet(daire_id, ad_soyad, kat, basl, ack, onc, atanan="")
                    log_ekle("talep", tid, ad_soyad, "Oluşturuldu", f"Sakin talebi: {basl}")
                    st.success("Talebiniz iletildi.")
                    st.rerun()
                else:
                    st.error("Başlık ve açıklama zorunlu.")

    df = load_data("talep")
    if not df.empty:
        mine = df[df["Daire_ID"].astype(str) == str(daire_id)].sort_values("Tarih", ascending=False)
        st.subheader("📋 Geçmiş Taleplerim")
        if not mine.empty:
            sec = st.selectbox("Talep seç", mine["Talep_ID"].tolist())
            row = mine[mine["Talep_ID"] == sec].iloc[0]
            st.markdown(f"**{row['Baslik']}** — {row.get('Aciklama','')}")
            st.info(f"Durum: **{row.get('Durum','')}** | Atanan: **{row.get('Atanan','')}**")
            if row.get("Cozum_Notu"):
                st.success(f"Çözüm: {row['Cozum_Notu']}")
            render_photo_grid("talep", sec, cols_per_row=3)
        st.dataframe(mine[["Talep_ID", "Tarih", "Kategori", "Baslik", "Oncelik",
                           "Durum", "Atanan", "Cozum_Notu"]],
                     use_container_width=True, hide_index=True)


def _yonetim_talep_view(secilen_tarih: date):
    section_header("Talep Yönetimi", "Tüm sakin talepleri, atama ve SLA takibi", pill="OPERASYON")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    df = load_data("talep")
    df_d = load_data("daire")
    df_p = load_data("personel")

    daire_ops = df_d["Daire_ID"].tolist() if not df_d.empty else []
    pers = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    tabs = st.tabs(["📋 Liste & Detay", "➕ Yeni Talep", "📊 İstatistikler"])

    with tabs[0]:
        if df.empty:
            st.info("Henüz talep yok.")
        else:
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

            g = _sla_durum_ekle(g)
            st.dataframe(g.sort_values("Tarih", ascending=False),
                         use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("🔍 Talep Detayı")
            sec = st.selectbox("Talep seç", df["Talep_ID"].tolist())
            row = df[df["Talep_ID"] == sec].iloc[0]
            _talep_detay(row, df, pers, kullanici, secilen_tarih)

    with tabs[1]:
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
                        tid = _yeni_talep_kaydet(d, ad, k, b, ack, o, at if at != "-" else "")
                        log_ekle("talep", tid, kullanici, "Oluşturuldu",
                                 f"Yönetici girişi: {b}")
                        st.success("Kaydedildi.")
                        st.rerun()

    with tabs[2]:
        _talep_istatistikler(df)


def _talep_detay(row: pd.Series, df: pd.DataFrame, pers: list, kullanici: str, secilen_tarih: date):
    talep_id = row["Talep_ID"]

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown(f"**{row['Baslik']}** — Daire {row.get('Daire_ID','')}")
        st.markdown(f"_{row.get('Aciklama','')}_")
        st.markdown(f"**Sakin:** {row.get('Sakin','')} | **Kategori:** {row.get('Kategori','')} | "
                    f"**Öncelik:** {row.get('Oncelik','')} | **SLA:** {row.get('SLA_Saat','')}s")

        sure = pd.to_numeric(row.get("Sure_Saat", 0), errors="coerce") or 0
        mal = pd.to_numeric(row.get("Malzeme_Maliyet", 0), errors="coerce") or 0
        isc = pd.to_numeric(row.get("Iscilik_Maliyet", 0), errors="coerce") or 0

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Süre (saat)", f"{sure:.1f}")
        mc2.metric("Malzeme ₺", f"{mal:,.0f}")
        mc3.metric("İşçilik ₺", f"{isc:,.0f}")

    with col_r:
        st.markdown("**✏️ Güncelle**")
        yd = st.selectbox("Yeni Durum",
                          ["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"],
                          index=["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"].index(
                              row.get("Durum", "Açık"))
                          if row.get("Durum") in ["Açık", "Atandı", "Devam", "Çözüldü", "Kapatıldı"] else 0,
                          key=f"td_{talep_id}")
        ya = st.selectbox("Atanan", ["-"] + pers,
                          index=(["-"] + pers).index(row.get("Atanan"))
                          if row.get("Atanan") in pers else 0,
                          key=f"ta_{talep_id}")
        cn = st.text_area("Çözüm Notu", value=str(row.get("Cozum_Notu", "")),
                          key=f"cn_{talep_id}")

        c_s, c_m, c_i = st.columns(3)
        new_sure = c_s.number_input("Süre (s)", value=float(sure), min_value=0.0, step=0.5,
                                     key=f"ts_{talep_id}")
        new_mal = c_m.number_input("Malzeme ₺", value=float(mal), min_value=0.0,
                                    key=f"tm_{talep_id}")
        new_isc = c_i.number_input("İşçilik ₺", value=float(isc), min_value=0.0,
                                    key=f"ti_{talep_id}")

        if st.button("💾 Güncelle", type="primary", key=f"tupd_{talep_id}"):
            old_durum = row.get("Durum", "")
            df.loc[df["Talep_ID"] == talep_id, "Durum"] = yd
            df.loc[df["Talep_ID"] == talep_id, "Atanan"] = "" if ya == "-" else ya
            df.loc[df["Talep_ID"] == talep_id, "Cozum_Notu"] = cn
            df.loc[df["Talep_ID"] == talep_id, "Sure_Saat"] = new_sure
            df.loc[df["Talep_ID"] == talep_id, "Malzeme_Maliyet"] = new_mal
            df.loc[df["Talep_ID"] == talep_id, "Iscilik_Maliyet"] = new_isc
            if yd == "Çözüldü":
                df.loc[df["Talep_ID"] == talep_id, "Cozum_Tarihi"] = str(date.today())
            save_data(df, "talep")
            if old_durum != yd:
                log_ekle("talep", talep_id, kullanici, "Durum Değişti",
                         f"{old_durum} → {yd}")
            st.success("Güncellendi.")
            st.rerun()

    st.divider()
    col_y, col_m = st.columns(2)
    with col_y:
        render_yorumlar("talep", talep_id, kullanici)
    with col_m:
        upload_widget("talep", talep_id, kullanici)
        render_photo_grid("talep", talep_id, cols_per_row=2)


def _yeni_talep_kaydet(daire_id, sakin_ad, kategori, baslik, aciklama, oncelik, atanan) -> str:
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
        "Lokasyon_ID": "", "Sure_Saat": 0,
        "Malzeme_Maliyet": 0, "Iscilik_Maliyet": 0,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, "talep")
    # ── Bildirim ──
    try:
        import streamlit as _st
        tetikler = _st.session_state.get("bildirim_tetikler", {})
        if tetikler.get("talep_yeni", True):
            from bildirim_helper import bildirim_gonder, personel_iletisim
            email_s, tel_s = personel_iletisim(atanan) if atanan else ("", "")
            bildirim_gonder(
                baslik=f"📨 Yeni Talep: {tid}",
                icerik=f"Başlık: {baslik}\nÖncelik: {oncelik}\nDaire: {daire_id}\nAtanan: {atanan or 'Atanmadı'}",
                email_list=[email_s] if email_s else [],
                telefon_list=[tel_s] if tel_s else [],
            )
    except Exception:
        pass
    return tid


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


def _talep_istatistikler(df: pd.DataFrame):
    if df.empty:
        st.info("İstatistik için veri yok.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam Talep", len(df))
    acik = len(df[~df["Durum"].isin(["Çözüldü", "Kapatıldı"])])
    c2.metric("Aktif", acik)
    tam = len(df[df["Durum"].isin(["Çözüldü", "Kapatıldı"])])
    c3.metric("Çözüldü", tam)
    toplam = (pd.to_numeric(df.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum() +
              pd.to_numeric(df.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum())
    c4.metric("Toplam Maliyet", f"{toplam:,.0f} ₺")

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Kategoriye Göre**")
        if "Kategori" in df.columns:
            st.bar_chart(df["Kategori"].value_counts())
    with col_r:
        st.markdown("**Önceliğe Göre Aktif Talepler**")
        aktif = df[~df["Durum"].isin(["Çözüldü", "Kapatıldı"])]
        if not aktif.empty and "Oncelik" in aktif.columns:
            st.bar_chart(aktif["Oncelik"].value_counts())
