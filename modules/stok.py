from style import section_header, data_table
import streamlit as st
import pandas as pd
from datetime import date
from db import load_data, save_data
from auth import current_user
from barkod import yeni_id
from constants import STOK_KATEGORI


def render(secilen_tarih: date):
    section_header("Stok & Yedek Parça", "Envanter ve kritik seviye uyarıları", pill="DEPO")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📦 Stok Listesi", "➕ Yeni Ürün", "✏️ Düzenle", "🔁 Giriş/Çıkış", "📜 Hareket Geçmişi"]
    )
    with tab1: _liste()
    with tab2: _yeni()
    with tab3: _duzenle()
    with tab4: _hareket()
    with tab5: _gecmis()


def _liste():
    df = load_data("stok")
    if df.empty:
        st.info("Henüz ürün yok.")
        return

    df = df.copy()
    df["_m"] = pd.to_numeric(df["Mevcut"], errors="coerce").fillna(0)
    df["_k"] = pd.to_numeric(df["Kritik"], errors="coerce").fillna(0)
    df["Uyarı"] = df.apply(
        lambda r: "🔴 Kritik" if r["_m"] <= r["_k"] else "🟢 Normal", axis=1
    )

    c1, c2 = st.columns(2)
    sf = c1.selectbox("Filtre", ["Tümü", "Sadece Kritik", "Sadece Normal"])
    kf = c2.selectbox("Kategori", ["Tümü"] + sorted(df["Kategori"].dropna().unique().tolist()))
    g = df.copy()
    if sf == "Sadece Kritik": g = g[g["_m"] <= g["_k"]]
    elif sf == "Sadece Normal": g = g[g["_m"] > g["_k"]]
    if kf != "Tümü": g = g[g["Kategori"] == kf]

    kritik_sayi = int((df["_m"] <= df["_k"]).sum())
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Toplam Ürün", len(df))
    c2m.metric("Kritik Seviyede", kritik_sayi,
               delta="⚠️ Sipariş Ver" if kritik_sayi > 0 else None, delta_color="inverse")
    toplam_deger = (df["_m"] * pd.to_numeric(df.get("Birim_Fiyat", 0), errors="coerce").fillna(0)).sum()
    c3m.metric("Stok Değeri", f"{toplam_deger:,.0f} ₺")

    data_table(
        g,
        [("Stok_ID", "ID"), ("Urun_Adi", "Ürün"), ("Kategori", "Kategori"),
         ("Mevcut", "Mevcut"), ("Kritik", "Kritik"), ("Birim", "Birim"),
         ("Depo_Yeri", "Depo"), ("Birim_Fiyat", "Birim ₺"), ("Uyarı", "Durum")],
        id_cols=["Stok_ID"], max_text=40,
    )


def _yeni():
    with st.form("add_st"):
        c1, c2 = st.columns(2)
        ad = c1.text_input("Ürün Adı *")
        kat = c2.selectbox("Kategori", STOK_KATEGORI)
        c3, c4, c5 = st.columns(3)
        bir = c3.selectbox("Birim", ["adet", "metre", "litre", "kg", "kutu", "paket"])
        mev = c4.number_input("Başlangıç Stoğu", min_value=0.0, value=0.0)
        krt = c5.number_input("Kritik Seviye", min_value=0.0, value=5.0)
        c6, c7 = st.columns(2)
        depo = c6.text_input("Depo Yeri", placeholder="Depo-1 / Raf-A3")
        bf = c7.number_input("Birim Fiyat (₺)", min_value=0.0, value=0.0)
        n = st.text_area("Notlar")
        if st.form_submit_button("💾 Kaydet", type="primary"):
            if ad.strip():
                row = {
                    "Stok_ID": yeni_id("STK"), "Urun_Adi": ad.strip(),
                    "Kategori": kat, "Birim": bir,
                    "Mevcut": mev, "Kritik": krt,
                    "Depo_Yeri": depo, "Birim_Fiyat": bf, "Notlar": n,
                }
                df = load_data("stok")
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                save_data(df, "stok")
                st.success("Eklendi.")
                st.rerun()
            else:
                st.error("Ürün adı zorunlu.")


def _duzenle():
    df = load_data("stok")
    if df.empty:
        st.info("Henüz ürün yok.")
        return

    sec = st.selectbox("Ürün seç", df["Stok_ID"].tolist(),
                       format_func=lambda x: f"{df[df['Stok_ID']==x]['Urun_Adi'].values[0]} ({x})"
                       if x in df["Stok_ID"].values else x)
    row = df[df["Stok_ID"] == sec].iloc[0]

    with st.form(f"edit_st_{sec}"):
        c1, c2 = st.columns(2)
        new_ad = c1.text_input("Ürün Adı", value=str(row.get("Urun_Adi", "")))
        new_kat = c2.selectbox("Kategori", STOK_KATEGORI,
                                index=STOK_KATEGORI.index(row.get("Kategori"))
                                if row.get("Kategori") in STOK_KATEGORI else 0)
        c3, c4, c5 = st.columns(3)
        birler = ["adet", "metre", "litre", "kg", "kutu", "paket"]
        new_bir = c3.selectbox("Birim", birler,
                               index=birler.index(row.get("Birim")) if row.get("Birim") in birler else 0)
        new_krt = c4.number_input("Kritik Seviye",
                                   value=float(pd.to_numeric(row.get("Kritik", 5), errors="coerce") or 5),
                                   min_value=0.0)
        new_bf = c5.number_input("Birim Fiyat (₺)",
                                  value=float(pd.to_numeric(row.get("Birim_Fiyat", 0), errors="coerce") or 0),
                                  min_value=0.0)
        new_depo = st.text_input("Depo Yeri", value=str(row.get("Depo_Yeri", "")))
        new_not = st.text_area("Notlar", value=str(row.get("Notlar", "")))

        col_s, col_d = st.columns(2)
        if col_s.form_submit_button("💾 Güncelle", type="primary"):
            df.loc[df["Stok_ID"] == sec, "Urun_Adi"] = new_ad
            df.loc[df["Stok_ID"] == sec, "Kategori"] = new_kat
            df.loc[df["Stok_ID"] == sec, "Birim"] = new_bir
            df.loc[df["Stok_ID"] == sec, "Kritik"] = new_krt
            df.loc[df["Stok_ID"] == sec, "Birim_Fiyat"] = new_bf
            df.loc[df["Stok_ID"] == sec, "Depo_Yeri"] = new_depo
            df.loc[df["Stok_ID"] == sec, "Notlar"] = new_not
            save_data(df, "stok")
            st.success("Güncellendi.")
            st.rerun()
        if col_d.form_submit_button("🗑️ Sil"):
            df = df[df["Stok_ID"] != sec]
            save_data(df, "stok")
            st.warning("Silindi.")
            st.rerun()


def _hareket():
    df = load_data("stok")
    if df.empty:
        st.warning("Önce stok ekleyin.")
        return

    sec = st.selectbox("Ürün",
        [f"{r['Stok_ID']} - {r['Urun_Adi']} (mevcut: {r['Mevcut']} {r['Birim']})"
         for _, r in df.iterrows()])
    sid = sec.split(" - ")[0]
    row = df[df["Stok_ID"] == sid].iloc[0]
    mevcut = float(row.get("Mevcut", 0) or 0)

    with st.form("hrk"):
        c1, c2 = st.columns(2)
        tip = c1.selectbox("Hareket Tipi", ["Giriş", "Çıkış"])
        miktar = c2.number_input("Miktar", min_value=0.0, value=1.0, step=1.0)
        ack = st.text_area("Açıklama", placeholder="İş emri / sebep / arıza ID")
        if st.form_submit_button("💾 İşle", type="primary"):
            u = current_user() or {}
            kim = u.get("Ad_Soyad", "")
            yeni_mevcut = mevcut + miktar if tip == "Giriş" else mevcut - miktar
            if yeni_mevcut < 0:
                st.error("Çıkış miktarı stoktan fazla olamaz.")
            else:
                df.loc[df["Stok_ID"] == sid, "Mevcut"] = yeni_mevcut
                save_data(df, "stok")
                log = load_data("stok_hrk")
                log = pd.concat([log, pd.DataFrame([{
                    "Hareket_ID": yeni_id("HRK"), "Stok_ID": sid,
                    "Tarih": str(date.today()), "Tip": tip,
                    "Miktar": miktar, "Kalan": yeni_mevcut,
                    "Aciklama": ack, "Kim": kim,
                }])], ignore_index=True)
                save_data(log, "stok_hrk")
                st.success(f"İşlendi. Yeni stok: {yeni_mevcut} {row['Birim']}")
                st.rerun()


def _gecmis():
    df = load_data("stok_hrk")
    if df.empty:
        st.info("Henüz hareket yok.")
        return

    df_s = load_data("stok")
    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today().replace(day=1))
    bit = c2.date_input("Bitiş", date.today())

    try:
        d = pd.to_datetime(df["Tarih"], errors="coerce")
        df_f = df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]
    except Exception:
        df_f = df

    giris = df_f[df_f["Tip"] == "Giriş"]["Miktar"].apply(pd.to_numeric, errors="coerce").sum()
    cikis = df_f[df_f["Tip"] == "Çıkış"]["Miktar"].apply(pd.to_numeric, errors="coerce").sum()
    c1m, c2m, c3m = st.columns(3)
    c1m.metric("Toplam Hareket", len(df_f))
    c2m.metric("Giriş", f"{giris:,.1f}")
    c3m.metric("Çıkış", f"{cikis:,.1f}")

    st.dataframe(df_f.sort_values("Tarih", ascending=False),
                 use_container_width=True, hide_index=True)


def stok_malzeme_kullan(stok_id: str, miktar: float, aciklama: str, kim: str) -> bool:
    """Arıza/talep modülünden çağrılır: stoktan malzeme düşer."""
    df = load_data("stok")
    if df.empty:
        return False
    mask = df["Stok_ID"] == stok_id
    if not mask.any():
        return False
    mevcut = float(pd.to_numeric(df.loc[mask, "Mevcut"].values[0], errors="coerce") or 0)
    yeni = mevcut - miktar
    if yeni < 0:
        return False
    df.loc[mask, "Mevcut"] = yeni
    save_data(df, "stok")
    log = load_data("stok_hrk")
    birim = df.loc[mask, "Birim"].values[0]
    log = pd.concat([log, pd.DataFrame([{
        "Hareket_ID": yeni_id("HRK"), "Stok_ID": stok_id,
        "Tarih": str(date.today()), "Tip": "Çıkış",
        "Miktar": miktar, "Kalan": yeni,
        "Aciklama": aciklama, "Kim": kim,
    }])], ignore_index=True)
    save_data(log, "stok_hrk")
    return True
