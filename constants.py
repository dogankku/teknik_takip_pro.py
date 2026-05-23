"""Sabitler: sheet adları, sütunlar, sorular, roller."""

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEETS = {
    "checklist":  "Checklist",
    "ariza":      "Arizalar",
    "vardiya":    "Vardiya",
    "personel":   "Personel",
    "ekipman":    "Ekipman",
    "kullanici":  "Kullanicilar",
    "daire":      "Daireler",
    "sakin":      "Sakinler",
    "talep":      "Talepler",
    "bakim_plan": "BakimPlani",
    "bakim_log":  "BakimKayitlari",
    "tahakkuk":   "AidatTahakkuk",
    "odeme":      "AidatOdeme",
    "stok":       "Stok",
    "stok_hrk":   "StokHareket",
    "sayac":      "Sayaclar",
    "okuma":      "SayacOkuma",
    "gider":      "Giderler",
    # ── Xenia tarzı yeni modüller ────────────────────────────────────────────
    "yorum":      "Yorumlar",
    "aktivite":   "AktiviteLog",
    "sablon":     "Sablonlar",
    "media":      "Medya",
    "lokasyon":   "Lokasyonlar",
    "tekrar":     "TekrarliGorevler",
    # ── Yeni tablolar ────────────────────────────────────────────────────────
    "yetki_rol":   "YetkiRol",
    "duyuru":      "Duyurular",
    "rezervasyon": "Rezervasyonlar",
    "ziyaretci":   "Ziyaretciler",
    "kargo":       "Kargolar",
}

COLS = {
    "checklist":  ["Tarih", "Bolum", "Alt_Grup", "Soru", "Durum", "Aciklama", "Kontrol_Eden", "Puan", "Sablon_ID", "Lokasyon_ID"],
    "ariza":      ["ID", "Tarih", "Saat", "Bolum", "Lokasyon", "Lokasyon_ID", "Ariza_Tanimi", "Sorumlu", "Durum", "Kapanis_Tarihi", "Sure_Saat", "Malzeme_Maliyet", "Iscilik_Maliyet"],
    "vardiya":    ["Tarih", "Vardiya", "Teslim_Eden", "Teslim_Alan", "Notlar"],
    "personel":   ["Isim", "Gorev", "Telefon", "Email", "Adres", "Dogum_Tarihi", "Sertifikalar", "Aktif"],
    "ekipman":    ["Barkod_ID", "Ekipman_Adi", "Kategori", "Lokasyon", "Marka_Model", "Seri_No", "Satin_Alma", "Sonraki_Bakim", "Durum", "Notlar"],
    "kullanici":  ["Kullanici_Adi", "Sifre_Hash", "Ad_Soyad", "Rol", "Daire_ID", "Telefon", "Email", "Aktif", "Olusturma", "Ekstra_Modul", "Kapali_Modul"],
    "daire":      ["Daire_ID", "Blok", "Kat", "Daire_No", "M2", "Oda_Tipi", "Durum", "Notlar"],
    "sakin":      ["Sakin_ID", "Daire_ID", "Ad_Soyad", "Tip", "Telefon", "Email", "Giris_Tarihi", "Cikis_Tarihi", "Aktif"],
    "talep":      ["Talep_ID", "Tarih", "Saat", "Daire_ID", "Sakin", "Kategori", "Baslik", "Aciklama", "Oncelik", "Durum", "Atanan", "SLA_Saat", "Cozum_Tarihi", "Cozum_Notu", "Lokasyon_ID", "Sure_Saat", "Malzeme_Maliyet", "Iscilik_Maliyet"],
    "bakim_plan": ["Plan_ID", "Baslik", "Ekipman", "Lokasyon", "Periyot_Gun", "Sorumlu", "Yasal_Zorunlu", "Son_Yapilma", "Sonraki_Tarih", "Durum", "Notlar"],
    "bakim_log":  ["Log_ID", "Plan_ID", "Tarih", "Yapan", "Aciklama", "Sonraki_Tarih", "Malzeme_Maliyet", "Iscilik_Maliyet"],
    "tahakkuk":   ["Tahakkuk_ID", "Daire_ID", "Donem", "Tutar", "Son_Odeme", "Aciklama"],
    "odeme":      ["Odeme_ID", "Daire_ID", "Tarih", "Tutar", "Yontem", "Aciklama"],
    "stok":       ["Stok_ID", "Urun_Adi", "Kategori", "Birim", "Mevcut", "Kritik", "Depo_Yeri", "Birim_Fiyat", "Notlar"],
    "stok_hrk":   ["Hareket_ID", "Stok_ID", "Tarih", "Tip", "Miktar", "Kalan", "Aciklama", "Kim"],
    "sayac":      ["Sayac_ID", "Tip", "Lokasyon", "Daire_ID", "Birim_Fiyat", "Aktif"],
    "okuma":      ["Okuma_ID", "Sayac_ID", "Tarih", "Endeks", "Tuketim", "Tutar"],
    "gider":      ["Gider_ID", "Tarih", "Kategori", "Aciklama", "Tutar", "Belge_No", "Tedarikci"],
    # ── Yeni modüller ────────────────────────────────────────────────────────
    "yorum":      ["Yorum_ID", "Parent_Tip", "Parent_ID", "Kullanici", "Tarih", "Saat", "Metin"],
    "aktivite":   ["Log_ID", "Parent_Tip", "Parent_ID", "Kullanici", "Tarih", "Saat", "Aksiyon", "Detay"],
    "sablon":     ["Sablon_ID", "Ad", "Kategori", "Aciklama", "Sorular_JSON", "Olusturan", "Tarih", "Puanlama_Aktif"],
    "media":      ["Media_ID", "Parent_Tip", "Parent_ID", "Dosya_Adi", "Mime", "Boyut", "Base64", "Yukleme_Tarihi", "Yukleyen"],
    "lokasyon":   ["Lokasyon_ID", "Ana_Lokasyon", "Ad", "Tip", "Adres", "Notlar"],
    "tekrar":     ["Tekrar_ID", "Baslik", "Aciklama", "Hedef_Tip", "Periyot_Gun", "Sonraki_Tarih", "Sorumlu", "Lokasyon_ID", "Sablon_ID", "Aktif", "Son_Olusturma"],
    # ── Yeni modüller (Yetki/Duyuru/Rezervasyon/Ziyaretçi) ──────────────────
    "yetki_rol":  ["Rol", "Modul_JSON"],
    "duyuru":     ["Duyuru_ID", "Baslik", "Icerik", "Tip", "Hedef", "Aktif", "Olusturan", "Tarih", "Son_Tarih"],
    "rezervasyon":["Rezervasyon_ID", "Tarih", "Saat", "Alan", "Daire_ID", "Talep_Eden", "Katilimci", "Notlar", "Durum", "Olusturma"],
    "ziyaretci":  ["Ziyaret_ID", "Daire_ID", "Ziyaretci_Adi", "Giris_Saati", "Cikis_Saati", "Amac", "Plaka", "Kaydeden", "Tarih"],
    "kargo":      ["Kargo_ID", "Daire_ID", "Firma", "Takip_No", "Gelis_Tarihi", "Teslim_Tarihi", "Durum", "Notlar"],
}

ROLLER = ["Admin", "Yonetici", "Teknisyen", "Sakin"]

# Modul erişim yetkileri
YETKI = {
    "Admin":     "*",  # tüm modüller
    "Yonetici":  ["ana", "rapor", "checklist", "ariza", "ekipman", "daire", "talep",
                  "bakim", "aidat", "stok", "sayac", "vardiya", "personel", "ayarlar",
                  "lokasyon", "sablon", "tekrar", "maliyet", "aktivite_log", "media",
                  "duyuru", "rezervasyon", "ziyaretci"],
    "Teknisyen": ["ana", "checklist", "ariza", "ekipman", "talep", "bakim", "stok",
                  "vardiya", "tekrar", "ziyaretci"],
    "Sakin":     ["ana", "sakin_talep", "sakin_aidat", "sakin_daire",
                  "sakin_duyuru", "sakin_rezervasyon", "sakin_ziyaretci"],
}

# Tüm modül listesi (Yetki yönetimi UI için)
ALL_MODULES: dict[str, str] = {
    "ana":          "🏠 Ana Sayfa",
    "rapor":        "📑 Raporlar",
    "daire":        "🏢 Daire & Sakin",
    "talep":        "📨 Talepler",
    "aidat":        "💰 Aidat",
    "ariza":        "🛠️ Arıza Takip",
    "checklist":    "✅ Kontroller",
    "bakim":        "📅 Bakım Planı",
    "vardiya":      "🔄 Vardiya",
    "tekrar":       "🔁 Tekrarlı Görevler",
    "ekipman":      "📦 Ekipman",
    "stok":         "📋 Stok",
    "sayac":        "⚡ Sayaç & Gider",
    "lokasyon":     "📍 Lokasyonlar",
    "maliyet":      "💸 Maliyet Paneli",
    "aktivite_log": "📋 Aktivite Günlüğü",
    "media":        "🖼️ Medya Yönetimi",
    "duyuru":       "📢 Duyurular",
    "rezervasyon":  "📅 Rezervasyon",
    "ziyaretci":    "👥 Ziyaretçi & Kargo",
    "sablon":       "📝 Şablonlar",
    "personel":     "👥 Personel",
    "kullanici":    "👤 Kullanıcılar",
    "ayarlar":      "⚙️ Ayarlar",
}

# Talep öncelik → SLA (saat)
ONCELIK_SLA = {"Kritik": 4, "Yuksek": 24, "Normal": 72, "Dusuk": 168}

# Bakım periyot şablonları (gün)
BAKIM_PERIYOT = {
    "Günlük": 1, "Haftalık": 7, "Aylık": 30, "3 Aylık": 90,
    "6 Aylık": 180, "Yıllık": 365, "2 Yıllık": 730,
}

GIDER_KATEGORI = [
    "Elektrik", "Su", "Doğalgaz", "Personel Maaş", "Bakım & Onarım",
    "Yedek Parça", "Temizlik", "Güvenlik", "Asansör Bakım",
    "Yangın & Güvenlik", "Vergi & SGK", "Genel Gider", "Diğer",
]

EKIPMAN_KATEGORI = [
    "Elektrik", "Mekanik", "HVAC", "Yangın", "Asansör",
    "Jeneratör", "Otomasyon", "Hidrofor", "Pompa", "Diğer",
]

STOK_KATEGORI = [
    "Elektrik Malzeme", "Mekanik Yedek", "Hırdavat", "Boya & Kimyasal",
    "Temizlik Malzemesi", "Yangın Ekipmanı", "Diğer",
]

TALEP_KATEGORI = ["Elektrik", "Mekanik", "Tesisat", "Temizlik", "Asansör", "Bahçe", "Genel", "Şikayet"]

SORU_GRUPLARI = {
    "Elektrik": {
        "1. Vardiya Başlangıç & Genel": [
            "1. Vardiya defteri incelendi mi?",
            "2. Bir önceki vardiyadan kalan işler tamamlandı mı?",
            "3. Vardiya boyunca olağandışı bir elektrik arızası yaşandı mı?",
        ],
        "2. Çevre & Dış Aydınlatma": [
            "4. Sokak ve bahçe aydınlatmaları yanıyor mu?",
            "5. Bina dış cephe kayar ışıklar ve yazıları çalışıyor mu?",
            "6. Cam üstü ledler (taç ışıkları) yanıyor mu?",
            "7. Çevre aydınlatma otomasyon zaman saatleri normal mi?",
        ],
        "3. Teknik Odalar Pano Kontrolleri (A Blok)": [
            "8. A Blok Kazan Dairesi: Panolarda arıza ışığı/sigorta atığı var mı?",
            "9. A Blok 25. Kat: Panolarda arıza ışığı var mı?",
            "10. A Blok 1. Bodrum: Panolarda arıza ışığı var mı?",
            "11. A Blok Asansör Makine Dairesi: Panolar ve klimalar enerjili mi?",
        ],
        "4. Teknik Odalar Pano Kontrolleri (B Blok)": [
            "12. B Blok Kazan Dairesi: Panolarda arıza ışığı var mı?",
            "13. B Blok 25. Kat: Panolarda arıza ışığı var mı?",
            "14. B Blok 1. Bodrum: Panolarda arıza ışığı var mı?",
            "15. B Blok Asansör Makine Dairesi: Panolar ve klimalar enerjili mi?",
        ],
        "5. Ortak Alan & Sosyal Tesis Panoları": [
            "16. Zemin Kat Restoran: Panolarda arıza ışığı var mı?",
            "17. Sosyal Tesis: Panolarda arıza ışığı var mı?",
            "18. 5. Bodrum Pompalar: Panolarda arıza ışığı var mı?",
            "19. 5. Bodrum Pompalar: Şalterler otomatik konumda mı?",
        ],
        "6. Jeneratör & Zayıf Akım Sistemleri": [
            "20. Jeneratör kumanda panelleri 'Otomatik' konumda mı?",
            "21. Jeneratör ön ısıtıcıları çalışıyor mu?",
            "22. Ana dağıtım ve kompanzasyon panolarında arıza alarmı var mı?",
            "23. Asansör içi müzik yayın sistemi çalışıyor mu?",
            "24. Otomasyon bilgisayarında 'Kırmızı' (Arıza) veren cihaz var mı?",
        ],
    },
    "Mekanik": {
        "1. Vardiya Başlangıç & Genel": [
            "1. Vardiya defteri incelendi mi?",
            "2. Bir önceki vardiyadan kalan işler tamamlandı mı?",
            "3. Vardiya boyunca su kesintisi veya mekanik arıza yaşandı mı?",
        ],
        "2. A Blok - Isıtma & Soğutma": [
            "4. A Blok Kazan Dairesi: Su basınçları normal mi?",
            "5. A Blok Kazan Dairesi: Su kaçağı var mı?",
            "6. A Blok 25. Kat: Sirkülasyon pompaları çalışıyor mu?",
            "7. A Blok 25. Kat: Taze hava ve egzoz santralleri çalışıyor mu?",
            "8. A Blok 1. Bodrum: Pompalar ve eşanjörler normal mi?",
        ],
        "3. B Blok - Isıtma & Soğutma": [
            "9. B Blok Kazan Dairesi: Su basınçları normal mi?",
            "10. B Blok Kazan Dairesi: Su kaçağı var mı?",
            "11. B Blok 25. Kat: Sirkülasyon pompaları çalışıyor mu?",
            "12. B Blok 25. Kat: Taze hava ve egzoz santralleri çalışıyor mu?",
            "13. B Blok 1. Bodrum: Pompalar ve eşanjörler normal mi?",
        ],
        "4. Su Basınçlandırma & Hidroforlar": [
            "14. Kullanma suyu hidroforları basıncı normal mi?",
            "15. Su depoları seviyeleri yeterli mi?",
            "16. Arıtma sistemi (Yumuşatma) cihazları devrede mi?",
            "17. Hidrofor odalarında su kaçağı var mı?",
        ],
        "5. Yangın Söndürme Sistemleri": [
            "18. Yangın pompaları 'Otomatik' konumda bekliyor mu?",
            "19. Yangın hattı (Sprinkler/Dolap) basıncı normal mi?",
            "20. Yangın suyu deposu tam dolu mu?",
            "21. Jokey pompalar sık devreye giriyor mu?",
        ],
        "6. Sosyal Tesis & Mutfaklar": [
            "22. Havuz mekanik dairesi: Pompalar ve filtreler normal mi?",
            "23. Restoran/Mutfak: Giderlerde tıkanıklık veya koku var mı?",
            "24. Mutfak davlumbaz fanları çalışıyor mu?",
            "25. Sosyal tesis havalandırma santralleri çalışıyor mu?",
        ],
    },
}
