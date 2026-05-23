from style import section_header
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from auth import current_user
from barkod import yeni_id
from yorum_helper import render_yorumlar
from media import upload_widget, render_photo_grid


VARDIYA_SAATLERI = ["08:00-16:00", "16:00-00:00", "00:00-08:00"]


def render(secilen_tarih: date):
    section_header("Vardiya Defteri", "Dijital teslim tutanağı", pill="OPERASYON")
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    df_v = load_data("vardiya")
    df_p = load_data("personel")
    pl = df_p["Isim"].tolist() if not df_p.empty else ["-"]

    tabs = st.tabs(["📋 Kayıtlar", "➕ Yeni Devir", "🔍 Detay"])

    # ── TAB 0: Liste ─────────────────────────────────────────────────────────
    with tabs[0]:
        if df_v.empty:
            st.info("Henüz vardiya kaydı yok.")
        else:
            c1, c2, c3 = st.columns(3)
            bas = c1.date_input("Başlangıç", value=date.today().replace(day=1), key="vb")
            bit = c2.date_input("Bitiş", value=date.today(), key="vbit")
            pers_f = c3.selectbox("Personel", ["Tümü"] + pl)

            g = df_v.copy()
            try:
                g["_d"] = pd.to_datetime(g["Tarih"], errors="coerce")
                g = g[(g["_d"] >= pd.Timestamp(bas)) & (g["_d"] <= pd.Timestamp(bit))]
            except Exception:
                pass
            if pers_f != "Tümü":
                g = g[(g["Teslim_Eden"] == pers_f) | (g["Teslim_Alan"] == pers_f)]

            st.dataframe(
                g[["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar"]].sort_values(
                    "Tarih", ascending=False),
                use_container_width=True, hide_index=True,
            )

            st.markdown(f"**Toplam:** {len(g)} kayıt")

    # ── TAB 1: Yeni Devir ────────────────────────────────────────────────────
    with tabs[1]:
        with st.form("add_v"):
            c1, c2, c3 = st.columns(3)
            v = c1.selectbox("Vardiya", VARDIYA_SAATLERI)
            te = c2.selectbox("Teslim Eden", pl)
            ta = c3.selectbox("Teslim Alan", [p for p in pl if p != te] or pl)
            n = st.text_area("Notlar / Devir Bilgileri", height=150,
                             placeholder="Açık arızalar, bekleyen işler, önemli notlar...")

            col_f1, col_f2 = st.columns(2)
            acik_ariza = col_f1.text_area("Açık Arızalar", height=80,
                                           placeholder="ARZ-xxx: Pompa arızası...")
            tamamlanan = col_f2.text_area("Tamamlanan İşler", height=80,
                                           placeholder="...")

            if st.form_submit_button("💾 Devir Kaydet", type="primary"):
                notlar_tam = n.strip()
                if acik_ariza.strip():
                    notlar_tam += f"\n\n📋 Açık Arızalar:\n{acik_ariza.strip()}"
                if tamamlanan.strip():
                    notlar_tam += f"\n\n✅ Tamamlananlar:\n{tamamlanan.strip()}"

                vid = yeni_id("VRD")
                row = {
                    "Vardiya_ID": vid,
                    "Tarih": str(secilen_tarih), "Vardiya": v,
                    "Teslim_Eden": te, "Teslim_Alan": ta,
                    "Notlar": notlar_tam.strip(),
                }
                df_v = pd.concat([df_v, pd.DataFrame([row])], ignore_index=True)
                save_data(df_v, "vardiya")
                # ── Vardiya devir bildirimi ──
                try:
                    tetikler = st.session_state.get("bildirim_tetikler", {})
                    if tetikler.get("vardiya_devir", False):
                        from bildirim_helper import bildirim_gonder, personel_iletisim
                        email_ta, tel_ta = personel_iletisim(ta)
                        bildirim_gonder(
                            baslik=f"🔄 Vardiya Devri — {v}",
                            icerik=f"Teslim Eden: {te}\nTeslim Alan: {ta}\nTarih: {secilen_tarih}\nNotlar:\n{notlar_tam[:300]}",
                            email_list=[email_ta] if email_ta else [],
                            telefon_list=[tel_ta] if tel_ta else [],
                        )
                except Exception:
                    pass
                st.success("Vardiya devri kaydedildi.")
                st.rerun()

    # ── TAB 2: Detay ─────────────────────────────────────────────────────────
    with tabs[2]:
        if df_v.empty:
            st.info("Henüz kayıt yok.")
        else:
            id_col = "Vardiya_ID" if "Vardiya_ID" in df_v.columns else None
            if id_col:
                opts = df_v[id_col].tolist()
                fmt = lambda x: (
                    f"{df_v[df_v[id_col]==x]['Tarih'].values[0]} "
                    f"{df_v[df_v[id_col]==x]['Vardiya'].values[0]} — "
                    f"{df_v[df_v[id_col]==x]['Teslim_Eden'].values[0]} → "
                    f"{df_v[df_v[id_col]==x]['Teslim_Alan'].values[0]}"
                ) if x in df_v[id_col].values else x
                sec_id = st.selectbox("Kayıt seç", opts, format_func=fmt)
                row = df_v[df_v[id_col] == sec_id].iloc[0]
            else:
                # Eski kayıtlarda ID yok — satır indeksine göre
                opts = list(range(len(df_v)))
                sec_idx = st.selectbox("Kayıt seç (sıra)",
                                       opts,
                                       format_func=lambda i: f"{df_v.iloc[i]['Tarih']} {df_v.iloc[i]['Vardiya']}")
                row = df_v.iloc[sec_idx]
                sec_id = str(sec_idx)

            st.markdown(
                f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px;">'
                f'<b>📅 {row.get("Tarih","")} | {row.get("Vardiya","")}</b><br>'
                f'Teslim Eden: <b>{row.get("Teslim_Eden","")}</b> → '
                f'Teslim Alan: <b>{row.get("Teslim_Alan","")}</b><br><br>'
                f'{str(row.get("Notlar","")).replace(chr(10),"<br>")}'
                f'</div>',
                unsafe_allow_html=True,
            )

            col_up, col_del = st.columns(2)

            # Düzenleme
            with col_up.expander("✏️ Notları Düzenle"):
                yeni_not = st.text_area("Notlar", value=str(row.get("Notlar", "")),
                                        key=f"vnot_{sec_id}", height=120)
                if st.button("💾 Güncelle", key=f"vupd_{sec_id}"):
                    if id_col:
                        df_v.loc[df_v[id_col] == sec_id, "Notlar"] = yeni_not
                    else:
                        df_v.iloc[sec_idx, df_v.columns.get_loc("Notlar")] = yeni_not
                    save_data(df_v, "vardiya")
                    st.success("Güncellendi.")
                    st.rerun()

            # Silme
            if col_del.button("🗑️ Kaydı Sil", key=f"vdel_{sec_id}"):
                if id_col:
                    df_v = df_v[df_v[id_col] != sec_id]
                else:
                    df_v = df_v.drop(index=sec_idx).reset_index(drop=True)
                save_data(df_v, "vardiya")
                st.warning("Silindi.")
                st.rerun()

            st.divider()
            col_y, col_m = st.columns(2)
            with col_y:
                render_yorumlar("vardiya", sec_id, kullanici)
            with col_m:
                upload_widget("vardiya", sec_id, kullanici)
                render_photo_grid("vardiya", sec_id, cols_per_row=2)
