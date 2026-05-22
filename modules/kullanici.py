from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data
from auth import add_user, update_user, delete_user, current_user, hash_password
from constants import ROLLER
from aktivite_helper import log_ekle


def render(secilen_tarih: date):
    section_header("Kullanıcı Yönetimi", "Rol ve yetki tanımları", pill="ADMİN")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Kullanıcılar", "➕ Yeni Kullanıcı", "✏️ Düzenle", "📜 Aktivite"
    ])

    df = load_data("kullanici")

    # ── TAB 0: Liste ──────────────────────────────────────────────────────────
    with tab1:
        if df.empty:
            st.info("Henüz kullanıcı yok.")
        else:
            gor = df.drop(columns=["Sifre_Hash"], errors="ignore")
            aktif_f = st.checkbox("Sadece aktif", value=True)
            if aktif_f and "Aktif" in gor.columns:
                gor = gor[gor["Aktif"].astype(str).str.lower().isin(["evet", "true", "1"])]

            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam", len(df))
            aktif_sayi = len(df[df.get("Aktif", pd.Series()).astype(str).str.lower().isin(["evet", "true", "1"])]) if "Aktif" in df.columns else len(df)
            c2.metric("Aktif", aktif_sayi)
            c3.metric("Pasif", len(df) - aktif_sayi)

            st.dataframe(gor, use_container_width=True, hide_index=True)

    # ── TAB 1: Yeni Kullanıcı ─────────────────────────────────────────────────
    with tab2:
        df_d = load_data("daire")
        daire_ops = [""] + (df_d["Daire_ID"].tolist() if not df_d.empty else [])
        with st.form("add_u"):
            c1, c2 = st.columns(2)
            ka = c1.text_input("Kullanıcı Adı *")
            sf = c2.text_input("Şifre *", type="password")
            c3, c4 = st.columns(2)
            ad = c3.text_input("Ad Soyad *")
            rol = c4.selectbox("Rol", ROLLER)
            c5, c6, c7 = st.columns(3)
            d = c5.selectbox("Daire (Sakin için)", daire_ops)
            tel = c6.text_input("Telefon")
            em = c7.text_input("Email")
            if st.form_submit_button("➕ Ekle", type="primary"):
                if ka.strip() and sf and ad.strip():
                    ok, msg = add_user(ka, sf, ad, rol, d, tel, em)
                    if ok:
                        u = current_user() or {}
                        log_ekle("kullanici", ka, u.get("Ad_Soyad", "Sistem"),
                                 "Oluşturuldu", f"Rol: {rol}")
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Zorunlu alanlar boş.")

    # ── TAB 2: Düzenle / Sil + Şifre Sıfırla ────────────────────────────────
    with tab3:
        if df.empty:
            st.info("Önce kullanıcı ekleyin.")
        else:
            u = current_user() or {}
            kullanicilar = df["Kullanici_Adi"].tolist()
            sec = st.selectbox("Kullanıcı", kullanicilar)
            row = df[df["Kullanici_Adi"] == sec].iloc[0]

            col_l, col_r = st.columns(2)

            with col_l:
                st.markdown("**✏️ Bilgileri Güncelle**")
                with st.form(f"edit_u_{sec}"):
                    c1, c2 = st.columns(2)
                    ad_y = c1.text_input("Ad Soyad", value=str(row.get("Ad_Soyad", "")))
                    rol_y = c2.selectbox("Rol", ROLLER,
                                         index=ROLLER.index(row.get("Rol")) if row.get("Rol") in ROLLER else 0)
                    c3, c4 = st.columns(2)
                    tel_y = c3.text_input("Telefon", value=str(row.get("Telefon", "")))
                    em_y = c4.text_input("Email", value=str(row.get("Email", "")))
                    df_d2 = load_data("daire")
                    daire_ops2 = [""] + (df_d2["Daire_ID"].tolist() if not df_d2.empty else [])
                    cur_d = str(row.get("Daire_ID", ""))
                    d_y = st.selectbox("Daire",
                                        daire_ops2,
                                        index=daire_ops2.index(cur_d) if cur_d in daire_ops2 else 0)
                    akt = st.selectbox("Aktif", ["Evet", "Hayır"],
                                        index=0 if str(row.get("Aktif", "Evet")).lower() in ["evet", "true"] else 1)

                    if st.form_submit_button("💾 Güncelle", type="primary"):
                        fields = {"Ad_Soyad": ad_y, "Rol": rol_y, "Telefon": tel_y,
                                  "Email": em_y, "Daire_ID": d_y, "Aktif": akt}
                        update_user(sec, **fields)
                        log_ekle("kullanici", sec, u.get("Ad_Soyad", "Sistem"),
                                 "Güncellendi", f"Rol: {rol_y}, Aktif: {akt}")
                        st.success("Güncellendi.")
                        st.rerun()

            with col_r:
                st.markdown("**🔑 Şifre Sıfırla**")
                with st.form(f"sifre_{sec}"):
                    yeni_sf = st.text_input("Yeni Şifre *", type="password")
                    yeni_sf2 = st.text_input("Şifre Tekrar *", type="password")
                    if st.form_submit_button("🔑 Şifreyi Güncelle", type="primary"):
                        if not yeni_sf:
                            st.error("Şifre boş olamaz.")
                        elif yeni_sf != yeni_sf2:
                            st.error("Şifreler eşleşmiyor.")
                        elif len(yeni_sf) < 6:
                            st.error("En az 6 karakter olmalı.")
                        else:
                            update_user(sec, sifre=yeni_sf)
                            log_ekle("kullanici", sec, u.get("Ad_Soyad", "Sistem"),
                                     "Şifre Sıfırlandı", "")
                            st.success(f"{sec} şifresi güncellendi.")

                st.markdown("---")
                st.markdown("**🗑️ Kullanıcı Sil**")
                if st.button("🗑️ Sil", key=f"sil_{sec}", type="secondary"):
                    if sec == u.get("Kullanici_Adi"):
                        st.error("Kendinizi silemezsiniz.")
                    elif sec == "admin":
                        st.error("Varsayılan admin silinemez.")
                    else:
                        delete_user(sec)
                        log_ekle("kullanici", sec, u.get("Ad_Soyad", "Sistem"),
                                 "Silindi", "")
                        st.success("Silindi.")
                        st.rerun()

    # ── TAB 3: Kullanıcı Aktivite Log ────────────────────────────────────────
    with tab4:
        df_akt = load_data("aktivite")
        if df_akt.empty:
            st.info("Henüz aktivite kaydı yok.")
        else:
            if not df.empty:
                sec_kul = st.selectbox("Kullanıcı", ["Tümü"] + df["Kullanici_Adi"].tolist(),
                                       key="akt_kul")
            else:
                sec_kul = "Tümü"

            g = df_akt.copy()
            if sec_kul != "Tümü":
                # Ad Soyad ile de filtrele
                kul_row = df[df["Kullanici_Adi"] == sec_kul]
                if not kul_row.empty:
                    ad_soyad = str(kul_row.iloc[0].get("Ad_Soyad", ""))
                    g = g[g["Kullanici"].astype(str).isin([sec_kul, ad_soyad])]

            g = g.sort_values("Tarih", ascending=False).head(100)
            st.metric("Toplam Olay", len(g))
            show_cols = [c for c in ["Tarih", "Saat", "Parent_Tip", "Parent_ID",
                                      "Kullanici", "Aksiyon", "Detay"] if c in g.columns]
            st.dataframe(g[show_cols], use_container_width=True, hide_index=True)
