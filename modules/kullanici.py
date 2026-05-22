import streamlit as st
import pandas as pd
from datetime import date
from db import load_data
from auth import add_user, update_user, delete_user, current_user
from constants import ROLLER


def render(secilen_tarih: date):
    st.header("👤 Kullanıcı Yönetimi (Admin)")

    tab1, tab2, tab3 = st.tabs(["📋 Kullanıcılar", "➕ Yeni Kullanıcı", "✏️ Düzenle / Sil"])

    df = load_data("kullanici")

    with tab1:
        if df.empty:
            st.info("Henüz kullanıcı yok.")
        else:
            gor = df.drop(columns=["Sifre_Hash"], errors="ignore")
            st.dataframe(gor, use_container_width=True, hide_index=True)

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
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Zorunlu alanlar boş.")

    with tab3:
        if df.empty:
            st.info("Önce kullanıcı ekleyin.")
            return
        u = current_user() or {}
        kullanicilar = df["Kullanici_Adi"].tolist()
        sec = st.selectbox("Kullanıcı", kullanicilar)
        row = df[df["Kullanici_Adi"] == sec].iloc[0]

        c1, c2 = st.columns(2)
        ad_y = c1.text_input("Ad Soyad", value=str(row.get("Ad_Soyad", "")))
        rol_y = c2.selectbox("Rol", ROLLER,
                             index=ROLLER.index(row.get("Rol")) if row.get("Rol") in ROLLER else 0)
        c3, c4 = st.columns(2)
        tel_y = c3.text_input("Telefon", value=str(row.get("Telefon", "")))
        em_y = c4.text_input("Email", value=str(row.get("Email", "")))
        c5, c6 = st.columns(2)
        df_d = load_data("daire")
        daire_ops = [""] + (df_d["Daire_ID"].tolist() if not df_d.empty else [])
        cur_d = str(row.get("Daire_ID", ""))
        d_y = c5.selectbox("Daire",
            daire_ops, index=daire_ops.index(cur_d) if cur_d in daire_ops else 0)
        akt = c6.selectbox("Aktif", ["Evet", "Hayır"],
            index=0 if str(row.get("Aktif", "Evet")).lower() == "evet" else 1)
        yeni_sf = st.text_input("Yeni Şifre (boş = değişmesin)", type="password")

        c1, c2 = st.columns(2)
        if c1.button("💾 Güncelle", type="primary"):
            fields = {"Ad_Soyad": ad_y, "Rol": rol_y, "Telefon": tel_y,
                      "Email": em_y, "Daire_ID": d_y, "Aktif": akt}
            if yeni_sf:
                fields["sifre"] = yeni_sf
            update_user(sec, **fields)
            st.success("Güncellendi.")
            st.rerun()

        if c2.button("🗑️ Sil", type="secondary"):
            if sec == u.get("Kullanici_Adi"):
                st.error("Kendinizi silemezsiniz.")
            elif sec == "admin":
                st.error("Varsayılan admin silinemez.")
            else:
                delete_user(sec)
                st.success("Silindi.")
                st.rerun()
