# Teknik Takip — Xenia Pro Full UI Patch

Bu paket sadece CSS düzeltmesi değildir. Aşağıdaki ekranları premium SaaS görünümüne yaklaştırır:

- `tekniktakip_pro.py` — sidebar/nav state bug fix + modern app shell
- `style.py` — tam UI kit: sidebar, KPI, tablo, badge, kart, avatar, asset kartları
- `modules/ana_sayfa.py` — dashboard KPI + modern arıza/kontrol özetleri
- `modules/ariza.py` — filtreli premium liste, detay/düzenleme, yeni arıza formu, istatistik
- `modules/checklist.py` — modern günlük kontrol formu + özet ekranı
- `modules/ekipman.py` — kart/tablo görünümü, yeni ekipman, QR/barkod
- `modules/talep.py` — talep listesi, yeni talep formu, SLA özeti
- `modules/bakim_plan.py` — bakım plan listesi ve yeni plan
- `modules/maliyet.py` — maliyet KPI ve gider tablosu
- `modules/media_yonetim.py` — medya galeri/listesi

## Kurulum

1. Mevcut projenin yedeğini alın.
2. Bu zip içindeki dosyaları proje klasörüne kopyalayın.
3. Eski dosyaların üzerine yazın.
4. Çalıştırın:

```bash
streamlit run tekniktakip_pro.py
```

## Not

Streamlit içinde Xenia gibi tamamen piksel-perfect bir web app yapmak sınırlıdır. Bu patch, Streamlit içinde alınabilecek en mantıklı premium SaaS seviyesine taşır. Daha ileri seviye için frontend ayrı React/Next.js yapılmalıdır.
