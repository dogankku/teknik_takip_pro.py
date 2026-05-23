from style import section_header, data_table
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from barkod import yeni_id


GOREVLER = [
    "Teknisyen", "Elektrikçi", "Sıhhi Tesisatçı", "Kalorifer Teknisyeni",
    "Güvenlik", "Temizlik", "Asansör Teknisyeni", "Bahçıvan",
    "Vardiya Şefi", "Teknik Müdür", "Diğer",
]


def render(secilen_tarih: date):
    section_header("Personel", "Personel listesi ve görev bilgileri", pill="İNSAN KAYNAKLARI")
    df_p = load_data("personel")

    tabs = st.tabs(["👥 Personel Listesi", "➕ Yeni Ekle", "✏️ Düzenle / Sil"])

    # ── TAB 0: Liste ─────────────────────────────────────────────────────────
    with tabs[0]:
        if df_p.empty:
            st.info("Henüz personel eklenmemiş.")
        else:
            gorev_f = st.selectbox("Göreve Göre Filtrele",
                                   ["Tümü"] + GOREVLER)
            aktif_f = st.checkbox("Sadece Aktif", value=True)

            g = df_p.copy()
            if gorev_f != "Tümü":
                g = g[g["Gorev"].astype(str) == gorev_f]
            if aktif_f and "Aktif" in g.columns:
                g = g[g["Aktif"].astype(str).isin(["Evet", "True", "1", "true"])]

            data_table(
                g,
                [("Isim", "İsim"), ("Gorev", "Görev"), ("Telefon", "Telefon"),
                 ("Email", "E-posta"), ("Sertifikalar", "Sertifikalar"), ("Aktif", "Durum")],
                avatar_cols=["Isim"], bool_cols=["Aktif"], max_text=40,
            )
            st.metric("Toplam", len(g))

    # ── TAB 1: Yeni Ekle ─────────────────────────────────────────────────────
    with tabs[1]:
        with st.form("add_p"):
            c1, c2 = st.columns(2)
            isim = c1.text_input("Ad Soyad *")
            gorev = c2.selectbox("Görev", GOREVLER)
            c3, c4 = st.columns(2)
            tel = c3.text_input("Telefon")
            email = c4.text_input("Email")
            c5, c6 = st.columns(2)
            dogum = c5.date_input("Doğum Tarihi", value=date(1990, 1, 1))
            aktif = c6.selectbox("Durum", ["Evet", "Hayır"])
            adres = st.text_input("Adres")
            sertifikalar = st.text_area("Sertifikalar / Yetki Belgeleri",
                                        placeholder="Elektrik Ustası (E1), Asansör Bakım Sertifikası...")

            if st.form_submit_button("➕ Ekle", type="primary"):
                if isim.strip():
                    row = {
                        "Isim": isim.strip(), "Gorev": gorev,
                        "Telefon": tel, "Email": email,
                        "Adres": adres,
                        "Dogum_Tarihi": str(dogum),
                        "Sertifikalar": sertifikalar.strip(),
                        "Aktif": aktif,
                    }
                    df_p = pd.concat([df_p, pd.DataFrame([row])], ignore_index=True)
                    save_data(df_p, "personel")
                    st.success(f"Eklendi: {isim}")
                    st.rerun()
                else:
                    st.error("İsim zorunlu.")

    # ── TAB 2: Düzenle / Sil ─────────────────────────────────────────────────
    with tabs[2]:
        if df_p.empty:
            st.info("Henüz personel yok.")
        else:
            sec = st.selectbox("Personel seç", df_p["Isim"].tolist())
            row = df_p[df_p["Isim"] == sec].iloc[0]

            # Bilgi kartı
            col_info, col_form = st.columns([1, 2])
            with col_info:
                st.markdown(
                    f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;'
                    f'padding:14px;">'
                    f'<b style="font-size:1.1rem">{row.get("Isim","")}</b><br>'
                    f'<span style="color:#64748B">{row.get("Gorev","")}</span><br><br>'
                    f'📞 {row.get("Telefon","—")}<br>'
                    f'📧 {row.get("Email","—")}<br>'
                    f'📍 {row.get("Adres","—")}<br>'
                    f'🎂 {row.get("Dogum_Tarihi","—")}<br>'
                    f'<br><b>Sertifikalar:</b><br>'
                    f'{str(row.get("Sertifikalar","")).replace(chr(10),"<br>") or "—"}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Arıza yükleri
                df_a = load_data("ariza")
                if not df_a.empty and "Sorumlu" in df_a.columns:
                    acik = len(df_a[(df_a["Sorumlu"] == sec) & (df_a["Durum"].isin(["Açık", "Devam Ediyor"]))])
                    tam = len(df_a[(df_a["Sorumlu"] == sec) & (df_a["Durum"] == "Tamamlandı")])
                    st.markdown("---")
                    st.markdown(f"**Arıza Yükü:** {acik} açık / {tam} tamamlandı")

            with col_form:
                with st.form(f"edit_p_{sec}"):
                    c1, c2 = st.columns(2)
                    new_gorev = c1.selectbox("Görev", GOREVLER,
                                             index=GOREVLER.index(row.get("Gorev"))
                                             if row.get("Gorev") in GOREVLER else 0)
                    new_aktif = c2.selectbox("Durum", ["Evet", "Hayır"],
                                             index=0 if str(row.get("Aktif", "Evet")) in ["Evet", "True", "1"] else 1)
                    c3, c4 = st.columns(2)
                    new_tel = c3.text_input("Telefon", value=str(row.get("Telefon", "")))
                    new_email = c4.text_input("Email", value=str(row.get("Email", "")))
                    new_adres = st.text_input("Adres", value=str(row.get("Adres", "")))
                    new_sert = st.text_area("Sertifikalar", value=str(row.get("Sertifikalar", "")),
                                            height=100)

                    col_s, col_d = st.columns(2)
                    if col_s.form_submit_button("💾 Güncelle", type="primary"):
                        df_p.loc[df_p["Isim"] == sec, "Gorev"] = new_gorev
                        df_p.loc[df_p["Isim"] == sec, "Aktif"] = new_aktif
                        df_p.loc[df_p["Isim"] == sec, "Telefon"] = new_tel
                        df_p.loc[df_p["Isim"] == sec, "Email"] = new_email
                        df_p.loc[df_p["Isim"] == sec, "Adres"] = new_adres
                        df_p.loc[df_p["Isim"] == sec, "Sertifikalar"] = new_sert
                        save_data(df_p, "personel")
                        st.success("Güncellendi.")
                        st.rerun()
                    if col_d.form_submit_button("🗑️ Sil"):
                        df_p = df_p[df_p["Isim"] != sec]
                        save_data(df_p, "personel")
                        st.warning("Silindi.")
                        st.rerun()
