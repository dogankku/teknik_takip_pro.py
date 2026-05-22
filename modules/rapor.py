from style import section_header
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from db import load_data
from report import df_to_excel, df_to_pdf


ALL_SHEETS = [
    "daire", "sakin", "kullanici", "ekipman", "ariza", "talep",
    "bakim_plan", "bakim_log", "tahakkuk", "odeme", "stok",
    "stok_hrk", "sayac", "okuma", "gider", "checklist",
    "vardiya", "personel", "lokasyon", "sablon", "tekrar",
    "yorum", "aktivite", "media",
]


def render(secilen_tarih: date):
    section_header("Raporlar", "PDF, Excel, analiz ve yedekleme", pill="ANALİZ")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Günlük", "📆 Dönem", "📊 SLA & Maliyet",
        "✅ Checklist Puan", "📦 Tam Yedek",
    ])

    with tab1: _gunluk(secilen_tarih)
    with tab2: _donem()
    with tab3: _sla_maliyet()
    with tab4: _checklist_puan()
    with tab5: _yedek()


# ── Günlük Rapor ──────────────────────────────────────────────────────────────
def _gunluk(t: date):
    ts = str(t)
    df_c = load_data("checklist")
    df_a = load_data("ariza")
    df_v = load_data("vardiya")
    df_tl = load_data("talep")

    gc = df_c[df_c["Tarih"] == ts] if not df_c.empty else pd.DataFrame()
    ga = df_a[df_a["Tarih"] == ts] if not df_a.empty else pd.DataFrame()
    gv = df_v[df_v["Tarih"] == ts] if not df_v.empty else pd.DataFrame()
    gt = df_tl[df_tl["Tarih"] == ts] if not df_tl.empty else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kontrol", len(gc))
    c2.metric("Arıza", len(ga))
    c3.metric("Talep", len(gt))
    c4.metric("Vardiya Devri", len(gv))

    if not gc.empty:
        sorunlu = len(gc[gc["Durum"] == "Sorunlu"])
        puan = len(gc[gc["Durum"] == "Tamam"])
        yuzde = int(puan / len(gc) * 100) if len(gc) else 0
        st.info(f"Checklist puan: **{yuzde}%** — {sorunlu} sorunlu madde")

    st.divider()
    c1b, c2b = st.columns(2)
    if c1b.button("📄 PDF Raporu", use_container_width=True):
        pdf = df_to_pdf(
            f"Günlük Rapor - {t.strftime('%d.%m.%Y')}",
            [("Kontrol", gc), ("Arızalar", ga), ("Talepler", gt), ("Vardiya", gv)],
        )
        if pdf:
            st.download_button("⬇️ PDF İndir", pdf, f"gunluk_{ts}.pdf", "application/pdf")
        else:
            st.error("reportlab yüklü değil.")

    if c2b.button("📊 Excel Raporu", use_container_width=True):
        x = df_to_excel({"Kontrol": gc, "Arizalar": ga, "Talepler": gt, "Vardiya": gv})
        st.download_button("⬇️ Excel İndir", x, f"gunluk_{ts}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ── Dönem Raporu ──────────────────────────────────────────────────────────────
def _donem():
    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today().replace(day=1))
    bit = c2.date_input("Bitiş", date.today())

    df_a = load_data("ariza")
    df_t = load_data("talep")
    df_g = load_data("gider")
    df_o = load_data("odeme")

    def _aralik(df, col="Tarih"):
        if df.empty or col not in df.columns: return df
        d = pd.to_datetime(df[col], errors="coerce")
        return df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]

    f_a = _aralik(df_a)
    f_t = _aralik(df_t)
    f_g = _aralik(df_g)
    f_o = _aralik(df_o)

    c1m, c2m, c3m, c4m = st.columns(4)
    c1m.metric("Arıza", len(f_a))
    c2m.metric("Talep", len(f_t))
    c3m.metric("Gider", f"{pd.to_numeric(f_g.get('Tutar', pd.Series()), errors='coerce').fillna(0).sum():,.0f} ₺")
    c4m.metric("Tahsilat", f"{pd.to_numeric(f_o.get('Tutar', pd.Series()), errors='coerce').fillna(0).sum():,.0f} ₺")

    st.divider()
    if st.button("📄 Dönem PDF Raporu", type="primary"):
        pdf = df_to_pdf(
            f"Dönem Raporu {bas} — {bit}",
            [("Arızalar", f_a), ("Talepler", f_t), ("Giderler", f_g), ("Tahsilatlar", f_o)],
        )
        if pdf:
            st.download_button("⬇️ PDF İndir", pdf, f"donem_{bas}_{bit}.pdf", "application/pdf")


# ── SLA & Maliyet Analizi ─────────────────────────────────────────────────────
def _sla_maliyet():
    st.subheader("📊 SLA Performansı & Maliyet Analizi")

    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today() - timedelta(days=30), key="sla_bas")
    bit = c2.date_input("Bitiş", date.today(), key="sla_bit")

    df_t = load_data("talep")
    df_a = load_data("ariza")

    # ── SLA Analizi ───────────────────────────────────────────────────────────
    st.markdown("#### Talep SLA Performansı")
    if not df_t.empty:
        df_t2 = df_t.copy()
        d = pd.to_datetime(df_t2["Tarih"], errors="coerce")
        df_t2 = df_t2[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))]

        if not df_t2.empty:
            cozuldu = df_t2[df_t2["Durum"].isin(["Çözüldü", "Kapatıldı"])]
            zamaninda = 0
            gecikti = 0
            for _, r in cozuldu.iterrows():
                try:
                    acilis = datetime.strptime(f"{r['Tarih']} {r.get('Saat','00:00')}", "%Y-%m-%d %H:%M")
                    cozum = pd.to_datetime(r.get("Cozum_Tarihi"))
                    sla_saat = float(r.get("SLA_Saat", 72))
                    sure = (cozum - acilis).total_seconds() / 3600
                    if sure <= sla_saat:
                        zamaninda += 1
                    else:
                        gecikti += 1
                except Exception:
                    pass

            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Toplam Talep", len(df_t2))
            sc2.metric("Çözüldü", len(cozuldu))
            sc3.metric("SLA'da Çözülen", zamaninda)
            sc4.metric("SLA Aşan", gecikti, delta="⚠️" if gecikti > 0 else None, delta_color="inverse")

            if len(cozuldu) > 0:
                oran = int(zamaninda / len(cozuldu) * 100)
                st.progress(oran / 100, text=f"SLA Başarı Oranı: {oran}%")

            # Önceliğe göre dağılım
            if "Oncelik" in df_t2.columns:
                st.markdown("**Önceliğe Göre Ortalama Çözüm Süresi**")
                oncelik_sure = {}
                for _, r in cozuldu.iterrows():
                    try:
                        acilis = datetime.strptime(f"{r['Tarih']} {r.get('Saat','00:00')}", "%Y-%m-%d %H:%M")
                        cozum = pd.to_datetime(r.get("Cozum_Tarihi"))
                        sure_h = (cozum - acilis).total_seconds() / 3600
                        onc = r.get("Oncelik", "Normal")
                        oncelik_sure.setdefault(onc, []).append(sure_h)
                    except Exception:
                        pass
                if oncelik_sure:
                    ozet = pd.DataFrame([
                        {"Öncelik": k, "Ort. Süre (saat)": round(sum(v)/len(v), 1), "Adet": len(v)}
                        for k, v in oncelik_sure.items()
                    ])
                    st.dataframe(ozet, use_container_width=True, hide_index=True)
        else:
            st.caption("Bu dönemde talep yok.")
    else:
        st.caption("Talep kaydı yok.")

    st.markdown("---")

    # ── Maliyet Analizi ───────────────────────────────────────────────────────
    st.markdown("#### Toplam Maliyet Analizi")

    ariza_mal = ariza_isc = 0.0
    talep_mal = talep_isc = 0.0
    bakim_mal = bakim_isc = 0.0

    if not df_a.empty:
        ariza_mal = pd.to_numeric(df_a.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum()
        ariza_isc = pd.to_numeric(df_a.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum()

    if not df_t.empty:
        talep_mal = pd.to_numeric(df_t.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum()
        talep_isc = pd.to_numeric(df_t.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum()

    df_blog = load_data("bakim_log")
    if not df_blog.empty:
        bakim_mal = pd.to_numeric(df_blog.get("Malzeme_Maliyet", 0), errors="coerce").fillna(0).sum()
        bakim_isc = pd.to_numeric(df_blog.get("Iscilik_Maliyet", 0), errors="coerce").fillna(0).sum()

    ozet = pd.DataFrame({
        "Kaynak": ["Arıza", "Talep", "Bakım", "TOPLAM"],
        "Malzeme (₺)": [ariza_mal, talep_mal, bakim_mal, ariza_mal + talep_mal + bakim_mal],
        "İşçilik (₺)": [ariza_isc, talep_isc, bakim_isc, ariza_isc + talep_isc + bakim_isc],
        "Toplam (₺)": [
            ariza_mal + ariza_isc,
            talep_mal + talep_isc,
            bakim_mal + bakim_isc,
            ariza_mal + ariza_isc + talep_mal + talep_isc + bakim_mal + bakim_isc,
        ],
    })
    ozet["Malzeme (₺)"] = ozet["Malzeme (₺)"].apply(lambda v: f"{v:,.0f}")
    ozet["İşçilik (₺)"] = ozet["İşçilik (₺)"].apply(lambda v: f"{v:,.0f}")
    ozet["Toplam (₺)"] = ozet["Toplam (₺)"].apply(lambda v: f"{v:,.0f}")
    st.dataframe(ozet, use_container_width=True, hide_index=True)

    # Gider kategorileri
    df_g = load_data("gider")
    if not df_g.empty:
        st.markdown("---")
        st.markdown("**Gider Kategorileri (Tüm Zamanlar)**")
        gider_ozet = (
            df_g.groupby("Kategori")["Tutar"]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").fillna(0).sum())
            .sort_values(ascending=False)
            .reset_index()
        )
        gider_ozet.columns = ["Kategori", "Tutar (₺)"]
        gider_ozet["Tutar (₺)"] = gider_ozet["Tutar (₺)"].apply(lambda v: f"{v:,.0f}")
        st.dataframe(gider_ozet, use_container_width=True, hide_index=True)


# ── Checklist Puan Raporu ─────────────────────────────────────────────────────
def _checklist_puan():
    st.subheader("✅ Checklist Puan Raporu")

    c1, c2 = st.columns(2)
    bas = c1.date_input("Başlangıç", date.today() - timedelta(days=7), key="cp_bas")
    bit = c2.date_input("Bitiş", date.today(), key="cp_bit")

    df = load_data("checklist")
    if df.empty:
        st.info("Checklist kaydı yok.")
        return

    try:
        d = pd.to_datetime(df["Tarih"], errors="coerce")
        df_f = df[(d >= pd.Timestamp(bas)) & (d <= pd.Timestamp(bit))].copy()
    except Exception:
        df_f = df.copy()

    if df_f.empty:
        st.caption("Bu dönemde kayıt yok.")
        return

    df_f["Puan"] = pd.to_numeric(df_f.get("Puan", 0), errors="coerce").fillna(0)

    # Günlük puan trendi
    st.markdown("#### Günlük Puan Trendi")
    gunluk = df_f.groupby("Tarih").apply(
        lambda g: round(g["Puan"].sum() / len(g) * 100, 1) if len(g) > 0 else 0
    ).reset_index()
    gunluk.columns = ["Tarih", "Puan %"]
    gunluk = gunluk.sort_values("Tarih")
    st.line_chart(gunluk.set_index("Tarih")["Puan %"])

    # Bölüm bazlı puan
    st.markdown("#### Bölüme Göre Ortalama Puan")
    if "Bolum" in df_f.columns:
        bolum_puan = df_f.groupby("Bolum").apply(
            lambda g: round(g["Puan"].sum() / len(g) * 100, 1) if len(g) > 0 else 0
        ).reset_index()
        bolum_puan.columns = ["Bölüm", "Puan %"]
        st.dataframe(bolum_puan.sort_values("Puan %"), use_container_width=True, hide_index=True)

    # Sorunlu maddeler
    sorunlu = df_f[df_f["Durum"] == "Sorunlu"]
    if not sorunlu.empty:
        st.markdown(f"#### ⚠️ Sorunlu Maddeler ({len(sorunlu)} adet)")
        show_cols = [c for c in ["Tarih", "Bolum", "Alt_Grup", "Soru", "Aciklama", "Kontrol_Eden"]
                     if c in sorunlu.columns]
        st.dataframe(sorunlu[show_cols].sort_values("Tarih", ascending=False),
                     use_container_width=True, hide_index=True)

    # Kontrol eden bazlı
    if "Kontrol_Eden" in df_f.columns:
        st.markdown("#### Kontrol Eden Bazlı")
        ke_puan = df_f.groupby("Kontrol_Eden").apply(
            lambda g: round(g["Puan"].sum() / len(g) * 100, 1) if len(g) > 0 else 0
        ).reset_index()
        ke_puan.columns = ["Personel", "Puan %"]
        st.dataframe(ke_puan.sort_values("Puan %", ascending=False),
                     use_container_width=True, hide_index=True)

    if st.button("📊 Checklist Raporu Excel", type="primary"):
        x = df_to_excel({
            "Tüm Kontroller": df_f,
            "Sorunlu Maddeler": sorunlu if not sorunlu.empty else pd.DataFrame(),
            "Günlük Puan": gunluk,
        })
        st.download_button("⬇️ İndir", x, f"checklist_raporu_{bas}_{bit}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ── Tam Yedek ─────────────────────────────────────────────────────────────────
def _yedek():
    st.info(f"Tüm verilerin Excel yedeği ({len(ALL_SHEETS)} sheet).")
    st.markdown("Dahil olan sheet'ler: " + ", ".join(f"`{s}`" for s in ALL_SHEETS))

    if st.button("📦 Tüm Veriyi Yedekle (Excel)", type="primary"):
        with st.spinner("Veriler hazırlanıyor…"):
            sheets = {}
            for k in ALL_SHEETS:
                try:
                    sheets[k] = load_data(k)
                except Exception:
                    sheets[k] = pd.DataFrame()
        x = df_to_excel(sheets)
        st.download_button(
            "⬇️ Yedek İndir", x,
            f"tam_yedek_{date.today()}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
