"""Duyuru & Anons modülü — sakinlere ve personele bildirim yönetimi."""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import load_data, save_data
from style import section_header, data_table, status_badge
from auth import current_user, current_role
from barkod import yeni_id


DUYURU_TIPLER = ["Genel", "Bakım", "Toplantı", "Acil", "Güvenlik", "Ortak Alan", "Mali", "Diğer"]
HEDEF_GRUPLAR = ["Tüm Sakinler", "A Blok", "B Blok", "C Blok", "Tüm Personel", "Yönetim", "Hepsi"]


def render(secilen_tarih: date):
    rol = current_role()
    u = current_user() or {}
    kullanici = u.get("Ad_Soyad", "Sistem")

    if rol == "Sakin":
        _sakin_view()
        return

    section_header("Duyuru & Anons", "Sakin ve personel bildirim yönetimi", pill="İLETİŞİM")

    tabs = st.tabs(["📢 Duyurular", "➕ Yeni Duyuru", "📊 Özet"])

    with tabs[0]:
        _liste()
    with tabs[1]:
        _yeni(kullanici)
    with tabs[2]:
        _ozet()


def _liste():
    df = load_data("duyuru")
    if df.empty:
        st.info("Henüz duyuru oluşturulmamış.")
        return

    c1, c2, c3 = st.columns(3)
    tip_f = c1.selectbox("Tip", ["Tümü"] + DUYURU_TIPLER)
    hedef_f = c2.selectbox("Hedef", ["Tümü"] + HEDEF_GRUPLAR)
    aktif_f = c3.checkbox("Sadece Aktif", value=True)

    g = df.copy()
    if tip_f != "Tümü":
        g = g[g["Tip"] == tip_f]
    if hedef_f != "Tümü":
        g = g[g["Hedef_Grup"] == hedef_f]
    if aktif_f and "Aktif" in g.columns:
        g = g[g["Aktif"].astype(str).isin(["True", "true", "1", "Evet"])]

    # Tarih sırası (en yeni önce)
    if "Tarih" in g.columns:
        g = g.sort_values("Tarih", ascending=False)

    data_table(
        g,
        [("Duyuru_ID", "ID"), ("Tarih", "Tarih"), ("Baslik", "Başlık"),
         ("Tip", "Tip"), ("Hedef_Grup", "Hedef"), ("Son_Gecerlilik", "Geçerlilik"),
         ("Olusturan", "Oluşturan"), ("Aktif", "Durum")],
        id_cols=["Duyuru_ID"], bool_cols=["Aktif"], avatar_cols=["Olusturan"],
        max_text=60,
    )

    st.divider()
    st.subheader("✏️ Düzenle / Sil")
    if not df.empty:
        sec_id = st.selectbox("Duyuru seç", df["Duyuru_ID"].tolist(),
                              format_func=lambda x: f"{df[df['Duyuru_ID']==x]['Baslik'].values[0]} ({x})"
                              if x in df["Duyuru_ID"].values else x)
        row = df[df["Duyuru_ID"] == sec_id].iloc[0]

        with st.expander("🔍 İçerik Görüntüle"):
            st.markdown(
                f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:16px;">'
                f'<b style="font-size:1rem;">{row.get("Baslik","")}</b>'
                f'<span style="margin-left:8px;font-size:.75rem;color:#64748B;">{row.get("Tarih","")} · {row.get("Tip","")}</span><br><br>'
                f'{str(row.get("Icerik","")).replace(chr(10),"<br>")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        with st.form(f"duyuru_edit_{sec_id}"):
            c1, c2 = st.columns(2)
            new_baslik = c1.text_input("Başlık", value=str(row.get("Baslik", "")))
            new_tip = c2.selectbox("Tip", DUYURU_TIPLER,
                                   index=DUYURU_TIPLER.index(row.get("Tip")) if row.get("Tip") in DUYURU_TIPLER else 0)
            c3, c4 = st.columns(2)
            new_hedef = c3.selectbox("Hedef Grup", HEDEF_GRUPLAR,
                                     index=HEDEF_GRUPLAR.index(row.get("Hedef_Grup")) if row.get("Hedef_Grup") in HEDEF_GRUPLAR else 0)
            try:
                son_val = pd.to_datetime(row.get("Son_Gecerlilik")).date()
            except Exception:
                son_val = date.today() + timedelta(days=30)
            new_son = c4.date_input("Son Geçerlilik", value=son_val)
            new_icerik = st.text_area("İçerik", value=str(row.get("Icerik", "")), height=120)
            new_aktif = st.checkbox("Aktif", value=str(row.get("Aktif", "True")) in ["True", "true", "1", "Evet"])

            col_s, col_d = st.columns(2)
            if col_s.form_submit_button("💾 Güncelle", type="primary"):
                df.loc[df["Duyuru_ID"] == sec_id, "Baslik"] = new_baslik
                df.loc[df["Duyuru_ID"] == sec_id, "Tip"] = new_tip
                df.loc[df["Duyuru_ID"] == sec_id, "Hedef_Grup"] = new_hedef
                df.loc[df["Duyuru_ID"] == sec_id, "Son_Gecerlilik"] = str(new_son)
                df.loc[df["Duyuru_ID"] == sec_id, "Icerik"] = new_icerik
                df.loc[df["Duyuru_ID"] == sec_id, "Aktif"] = new_aktif
                save_data(df, "duyuru")
                st.success("Güncellendi.")
                st.rerun()
            if col_d.form_submit_button("🗑️ Sil"):
                df = df[df["Duyuru_ID"] != sec_id]
                save_data(df, "duyuru")
                st.warning("Silindi.")
                st.rerun()


def _yeni(kullanici: str):
    df = load_data("duyuru")
    with st.form("yeni_duyuru"):
        c1, c2 = st.columns(2)
        baslik = c1.text_input("Başlık *")
        tip = c2.selectbox("Duyuru Tipi", DUYURU_TIPLER)
        c3, c4 = st.columns(2)
        hedef = c3.selectbox("Hedef Grup", HEDEF_GRUPLAR)
        son_tarih = c4.date_input("Son Geçerlilik", date.today() + timedelta(days=30))
        icerik = st.text_area("İçerik *", height=160,
                              placeholder="Duyuru metni...")
        aktif = st.checkbox("Hemen Yayınla", value=True)

        if st.form_submit_button("📢 Duyuruyu Yayınla", type="primary"):
            if baslik.strip() and icerik.strip():
                row = {
                    "Duyuru_ID": yeni_id("DUY"),
                    "Tarih": str(date.today()),
                    "Baslik": baslik.strip(),
                    "Tip": tip,
                    "Hedef_Grup": hedef,
                    "Icerik": icerik.strip(),
                    "Son_Gecerlilik": str(son_tarih),
                    "Olusturan": kullanici,
                    "Aktif": aktif,
                }
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "duyuru")
                st.success(f"Duyuru yayınlandı: {baslik} → {hedef}")
                st.rerun()
            else:
                st.error("Başlık ve içerik zorunlu.")


def _ozet():
    df = load_data("duyuru")
    if df.empty:
        st.info("Henüz duyuru yok.")
        return

    aktif = df[df["Aktif"].astype(str).isin(["True", "true", "1", "Evet"])]
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Duyuru", len(df))
    c2.metric("Aktif", len(aktif))
    c3.metric("Pasif/Sona Eren", len(df) - len(aktif))

    if "Tip" in df.columns:
        st.markdown("---")
        st.markdown("**Tipe Göre Dağılım**")
        st.bar_chart(df["Tip"].value_counts())


def _sakin_view():
    u = current_user() or {}
    daire_id = u.get("Daire_ID", "")
    section_header("Duyurular", "Yönetim ve bina duyuruları", pill="BİLGİ")

    df = load_data("duyuru")
    if df.empty:
        st.info("Henüz duyuru yok.")
        return

    # Aktif duyuruları filtrele
    df_aktif = df[df["Aktif"].astype(str).isin(["True", "true", "1", "Evet"])].copy()

    # Son geçerlilik kontrolü
    try:
        df_aktif["_son"] = pd.to_datetime(df_aktif["Son_Gecerlilik"], errors="coerce")
        df_aktif = df_aktif[df_aktif["_son"] >= pd.Timestamp(date.today())]
    except Exception:
        pass

    if df_aktif.empty:
        st.info("Şu anda aktif duyuru bulunmuyor.")
        return

    df_aktif = df_aktif.sort_values("Tarih", ascending=False)

    for _, row in df_aktif.head(20).iterrows():
        tip = str(row.get("Tip", "Genel"))
        tip_renk = {
            "Acil": "#EF4444", "Güvenlik": "#F59E0B", "Bakım": "#3B82F6",
            "Toplantı": "#8B5CF6", "Mali": "#10B981",
        }.get(tip, "#64748B")

        st.markdown(
            f'<div style="background:#F8FAFC;border-left:4px solid {tip_renk};'
            f'border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:10px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'<span style="background:{tip_renk}18;color:{tip_renk};font-size:.7rem;'
            f'font-weight:700;padding:2px 8px;border-radius:9999px;">{tip}</span>'
            f'<span style="font-size:.75rem;color:#94A3B8;">{row.get("Tarih","")} · {row.get("Hedef_Grup","")}</span>'
            f'</div>'
            f'<b style="font-size:.95rem;color:#1E293B;">{row.get("Baslik","")}</b><br>'
            f'<span style="font-size:.85rem;color:#475569;">{str(row.get("Icerik",""))[:300]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
