# Teknik Takip Pro — Kurulum & Kullanım Kılavuzu

> **Sürüm:** 2.0 · **Platform:** Streamlit · **Veritabanı:** SQLite (varsayılan) / Google Sheets

---

## İçindekiler

1. [Genel Bakış](#1-genel-bakış)
2. [Kurulum Seçenekleri](#2-kurulum-seçenekleri)
   - 2.1 [Docker ile Kurulum (Önerilen)](#21-docker-ile-kurulum-önerilen)
   - 2.2 [Yerel Python ile Kurulum](#22-yerel-python-ile-kurulum)
   - 2.3 [Streamlit Community Cloud](#23-streamlit-community-cloud)
3. [İlk Kurulum Sihirbazı](#3-i̇lk-kurulum-sihirbazı)
4. [Kullanıcı Rolleri & Yetkiler](#4-kullanıcı-rolleri--yetkiler)
5. [Modüller Rehberi](#5-modüller-rehberi)
6. [Bildirim Ayarları](#6-bildirim-ayarları)
7. [Google Sheets Entegrasyonu](#7-google-sheets-entegrasyonu)
8. [Şifre Sıfırlama](#8-şifre-sıfırlama)
9. [Yedek Alma & Geri Yükleme](#9-yedek-alma--geri-yükleme)
10. [Sık Sorulan Sorular](#10-sık-sorulan-sorular)

---

## 1. Genel Bakış

**Teknik Takip Pro**, otel ve toplu konut yönetimine özel bir teknik operasyon sistemidir. Her tesis kendi bağımsız kurulumunu yönetir.

### Temel Özellikler

| Kategori | Özellikler |
|----------|------------|
| **Operasyon** | Arıza takip, kontrol listeleri, bakım planı, vardiya defteri, tekrarlı görevler |
| **Mülk** | Daire & sakin yönetimi, aidat takibi, talepler |
| **Envanter** | Ekipman & barkod, stok yönetimi, sayaç & gider |
| **Analiz** | Maliyet paneli, aktivite günlüğü, raporlar |
| **İletişim** | Duyurular, rezervasyon, ziyaretçi & kargo takibi |
| **Yönetim** | Kullanıcı & yetki yönetimi, personel, şablonlar, ayarlar |

### Veri Depolama Önceliği

```
Google Sheets (yapılandırıldıysa)
       ↓
  SQLite (varsayılan)
       ↓
     CSV (yedek)
```

---

## 2. Kurulum Seçenekleri

### 2.1 Docker ile Kurulum (Önerilen)

En hızlı ve güvenilir yöntemdir. Sunucu, VPS veya yerel bilgisayarda çalışır.

**Gereksinimler:**
- Docker Engine 20+ ([kurulum](https://docs.docker.com/engine/install/))
- Docker Compose V2

**Adımlar:**

```bash
# 1. Depoyu klonlayın
git clone https://github.com/KULLANICI_ADI/teknik_takip_pro.py.git
cd teknik_takip_pro.py

# 2. Ortam değişkenlerini yapılandırın
cp .env.example .env
nano .env   # veya istediğiniz metin editörüyle açın

# 3. Uygulamayı başlatın
docker compose up -d

# 4. Logları izleyin
docker compose logs -f
```

Uygulama `http://SUNUCU_IP:8501` adresinde çalışmaya başlar.

**`.env` dosyası örneği:**

```env
APP_PORT=8501

# E-posta bildirimleri için (isteğe bağlı)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=bildirim@firmaniz.com
SMTP_PASS=uygulama-sifresi
```

**Güncelleme:**

```bash
git pull
docker compose up -d --build
```

---

### 2.2 Yerel Python ile Kurulum

Geliştirme ortamı veya test için uygundur.

**Gereksinimler:** Python 3.11+

```bash
# 1. Sanal ortam oluşturun
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Uygulamayı başlatın
streamlit run tekniktakip_pro.py
```

Tarayıcıda otomatik `http://localhost:8501` açılır.

---

### 2.3 Streamlit Community Cloud

Ücretsiz bulut dağıtımı. Her tesis için ayrı bir Streamlit hesabı ve depo gerekir.

1. [share.streamlit.io](https://share.streamlit.io) adresinde hesap açın
2. GitHub deponuzu bağlayın
3. `tekniktakip_pro.py` dosyasını ana dosya olarak seçin
4. **Secrets** bölümüne (isteğe bağlı) Google Sheets bilgilerini girin:

```toml
# .streamlit/secrets.toml içeriği (Streamlit Cloud → Settings → Secrets)
spreadsheet_id = "GOOGLE_SHEETS_ID"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "..."
# ... diğer alanlar
```

> ⚠️ Streamlit Community Cloud'da sayfa yenilemede oturum sıfırlanır.
> Kalıcı oturum için Docker kurulumu tercih edin.

---

## 3. İlk Kurulum Sihirbazı

Uygulama **ilk kez açıldığında** (hiç kullanıcı yokken) otomatik olarak kurulum sihirbazı başlar.

### Adım 1 — Tesis Bilgileri

| Alan | Açıklama |
|------|----------|
| **Tesis / Bina Adı** *(zorunlu)* | Örn: "Güneş Residence A Blok" |
| **Adres** | Tesisin tam adresi |

➡ **İleri** butonuna tıklayın.

### Adım 2 — Admin Hesabı

| Alan | Kural |
|------|-------|
| **Ad Soyad** | Zorunlu |
| **E-posta** | Şifre sıfırlama için kullanılır |
| **Kullanıcı Adı** | En az 3 karakter |
| **Şifre** | En az 8 karakter |

➡ **İleri** butonuna tıklayın.

### Adım 3 — Özet & Başlatma

Girilen bilgileri kontrol edin. **🚀 Sistemi Başlat** butonuna tıkladığınızda:
- Admin hesabı oluşturulur
- Sistem otomatik giriş yapar
- Ana sayfaya yönlendirilirsiniz

> ✅ **Kurulum tamamlandı!** Artık diğer kullanıcıları ekleyebilir, modülleri yapılandırabilirsiniz.

---

## 4. Kullanıcı Rolleri & Yetkiler

### Rol Hiyerarşisi

```
Admin
  └─ Tüm modüller + kullanıcı yönetimi

Yönetici
  └─ Operasyonel tüm modüller (kullanıcı yönetimi hariç)

Teknisyen
  └─ İş emirleri: arıza, talep, kontrol, bakım, stok, vardiya

Sakin
  └─ Kendi talebi, aidat borcu, duyurular, rezervasyon, kargo
```

### Kullanıcı Ekleme

**⚙️ Ayarlar → Kullanıcılar** veya **👤 Kullanıcılar** menüsünden:

1. **Yeni Kullanıcı** sekmesini açın
2. Ad soyad, kullanıcı adı, şifre, rol ve daire bilgilerini girin
3. **Kaydet**

### Yetki Özelleştirme (Admin)

**⚙️ Ayarlar → 🔒 Yetki Yönetimi**:

- **Rol bazlı**: Her rol için erişilebilir modülleri seçin
- **Kullanıcı bazlı**: Belirli kullanıcıya ek izin verin ya da modül engelleyin

---

## 5. Modüller Rehberi

### 🏠 Ana Sayfa
Özet istatistikler, aktif arızalar, bekleyen talepler ve yaklaşan bakımlar.

---

### 🛠️ Arıza Takip
Tüm arızaları kayıt altına alın, atayın ve izleyin.

**Yeni Arıza:**
1. **➕ Yeni Arıza** sekmesi
2. Bölüm, lokasyon, arıza tanımı, sorumlu ve öncelik seçin
3. **Kaydet** → Otomatik barkod ID oluşturulur (ARZ-XXXX)

**Durum Akışı:** `Açık` → `Devam Ediyor` → `Beklemede` → `Kapalı`

---

### ✅ Kontrol Listeleri (Checklist)
Günlük/vardiya kontrol turlarını dijital olarak kayıt altına alın.

**Kullanım:**
1. Bölüm seçin (Elektrik, Mekanik, vb.)
2. Her soruya ✅ / ❌ / ⚠️ işaretleyin
3. Gerekiyorsa not ekleyin
4. **Turu Tamamla** — Puan ve özet otomatik hesaplanır

**Şablon Oluşturma (Admin):** 📝 Şablonlar → Yeni şablon → Sorularınızı girin

---

### 📅 Bakım Planı
Periyodik bakımları planlayın ve takip edin.

**Plan Ekleme:**
- Ekipman / lokasyon seçin
- Periyot (Günlük / Haftalık / Aylık / Yıllık...)
- Sorumlu teknisyen ve son yapılma tarihi girin

**Uyarı:** Son tarihi geçen bakımlar kırmızı ile gösterilir.

---

### 🔄 Vardiya Defteri
Vardiya teslim tutanağını dijital olarak kayıt altına alın.

**Devir Kaydı:**
1. Vardiya saatini seçin (08-16 / 16-00 / 00-08)
2. Teslim eden ve alan personeli seçin
3. Açık arızalar, tamamlanan işler ve notları girin
4. **💾 Devir Kaydet**

---

### 📨 Talepler
Sakin ve yönetici taleplerini yönetin.

**Talep Akışı:** `Açık` → `Atandı` → `Devam` → `Çözüldü`

SLA süreleri önceliğe göre otomatik hesaplanır:
- Kritik: 4 saat · Yüksek: 24 saat · Normal: 72 saat · Düşük: 168 saat

---

### 📦 Ekipman & Barkod
Tesis ekipmanlarını barkod sistemiyle takip edin.

**Yeni Ekipman:**
1. Ad, kategori, lokasyon, seri no girin
2. Sistem otomatik barkod üretir (EKP-XXXX)
3. **QR Kod / Barkod yazdır** → Ekipmana yapıştırın

**Mobil Tarama:** Kamera QR kodunu okuyunca ekipman detayı açılır.

---

### 📋 Stok
Yedek parça ve malzeme stoğunu yönetin.

- Kritik seviye uyarısı: Stok kritik miktarın altına düşünce uyarı verir
- Hareket kaydı: Her giriş/çıkış otomatik loglanır

---

### ⚡ Sayaç & Gider
Elektrik, su, doğalgaz sayaç okumalarını ve giderleri takip edin.

**Sayaç Okuma:**
1. Sayacı seçin
2. Endeks değerini girin
3. Sistem tüketim ve tutarı otomatik hesaplar

---

### 💰 Aidat
Daire bazlı aidat tahakkuk ve ödeme takibi.

**Tahakkuk Oluşturma:**
1. Daire / blok seçin veya tümünü işaretleyin
2. Dönem ve tutar girin
3. **Toplu Tahakkuk** → Tüm dairelere tek seferde oluşturulur

---

### 🏢 Daire & Sakin
Daire bilgilerini ve sakin kayıtlarını yönetin.

- Daire: blok, kat, m², oda tipi, durum
- Sakin: giriş/çıkış tarihi, iletişim bilgileri

---

### 📢 Duyurular
Tüm sakinlere veya belirli gruplara duyuru gönderin.

- **Hedef:** Tümü / Sakinler / Teknisyenler
- **Son tarih** belirlenebilir — tarih geçince otomatik pasifleşir

---

### 📅 Rezervasyon
Ortak alan rezervasyonlarını yönetin (toplantı salonu, spor alanı vb.).

---

### 👥 Ziyaretçi & Kargo
- **Ziyaretçi:** Giriş/çıkış kayıtları, araç plakası
- **Kargo:** Daire bazlı kargo takibi, teslim durumu

---

### 💸 Maliyet Paneli
Arıza, bakım ve stok hareketlerinden otomatik hesaplanan maliyet özeti. Aylık/yıllık grafik ve karşılaştırma.

---

### 📑 Raporlar
PDF/Excel formatında dışa aktarılabilir raporlar:
- Arıza özet raporu
- Bakım raporu
- Aidat durum raporu
- Maliyet raporu

---

## 6. Bildirim Ayarları

**⚙️ Ayarlar → 🔔 Bildirim Ayarları**

### E-posta (SMTP)

| Alan | Örnek |
|------|-------|
| SMTP Sunucu | `smtp.gmail.com` |
| Port | `587` (TLS) |
| Kullanıcı Adı | `bildirim@firmaniz.com` |
| Şifre | Gmail için *App Password* kullanın |

> **Gmail App Password:** Google Hesabı → Güvenlik → 2 Adımlı Doğrulama → Uygulama Şifreleri

### Telegram Bot

1. [@BotFather](https://t.me/BotFather)'a mesaj atın: `/newbot`
2. Bot token'ını kopyalayın
3. Bildirim alınacak **Chat ID**'yi [bu yöntemle](https://api.telegram.org/bot<TOKEN>/getUpdates) bulun
4. Ayarlar → Telegram: token ve chat_id girin

### Tetikleyiciler

Hangi olaylarda bildirim gönderileceğini seçin:

| Tetikleyici | Açıklama |
|-------------|----------|
| Yeni arıza | Arıza oluşturulduğunda |
| Kritik arıza | Öncelik "Kritik" olduğunda |
| Vardiya devri | Vardiya teslimi yapıldığında |
| Bakım hatırlatma | Bakım tarihi yaklaştığında |
| Stok uyarısı | Kritik stok seviyesinde |

---

## 7. Google Sheets Entegrasyonu

SQLite yerine veya ek olarak Google Sheets kullanabilirsiniz.

### Adımlar

**1. GCP Service Account oluşturun:**

1. [Google Cloud Console](https://console.cloud.google.com) → IAM & Admin → Service Accounts
2. **Create Service Account** → İsim verin → **Create**
3. **Keys** sekmesi → **Add Key** → JSON → İndirin

**2. Spreadsheet hazırlayın:**

1. Google Sheets'te yeni dosya oluşturun
2. Service account email adresini **düzenleyici** olarak paylaşın
3. URL'deki Spreadsheet ID'yi kopyalayın:
   `https://docs.google.com/spreadsheets/d/**SPREADSHEET_ID**/edit`

**3. Streamlit secrets yapılandırın:**

*Yerel kurulum için* `.streamlit/secrets.toml` dosyası oluşturun:

```toml
spreadsheet_id = "BURAYA_SPREADSHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "proje-id"
private_key_id = "key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "servis@proje.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

*Docker kurulumu için* aynı içeriği `.streamlit/secrets.toml` dosyasına ekleyin ve `docker-compose.yml`'de volume olarak mount edin.

**4. Bağlantıyı doğrulayın:**

⚙️ Ayarlar → ☁️ Google Sheets → **Bağlantıyı Test Et**

> **Not:** Google Sheets bağlıyken veriler orada saklanır. Bağlantı kesilirse SQLite'a geçilir.

---

## 8. Şifre Sıfırlama

### Yöntem 1 — "Şifremi Unuttum" (Kullanıcı)

1. Giriş sayfasında **🔑 Şifremi Unuttum** butonuna tıklayın
2. E-posta veya kullanıcı adınızı girin
3. Uygulama URL'sini girin (örn: `https://uygulamaniz.streamlit.app`)
4. **Sıfırlama Linki Gönder**
5. E-postaya gelen bağlantıya tıklayın (60 dakika geçerli)
6. Yeni şifrenizi belirleyin

### Yöntem 2 — Admin Panelinden Sıfırlama

1. **👤 Kullanıcılar** → Kullanıcıyı seçin → **✏️ Düzenle**
2. Yeni şifre girin → **Kaydet**

### SMTP Yoksa

Şifre sıfırlama e-postası gönderilemiyorsa sistem ekranda token gösterir:

```
Sıfırlama token'ı: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
URL'ye ?reset=TOKEN ekleyerek sıfırlayabilirsiniz.
```

Bu durumda URL şu şekilde açılır:
`http://localhost:8501/?reset=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 9. Yedek Alma & Geri Yükleme

### SQLite Veritabanı Yedeği

```bash
# Manuel yedek
cp data/teknik_takip.db data/teknik_takip_backup_$(date +%Y%m%d).db

# Docker ile
docker compose exec teknik-takip cp /app/data/teknik_takip.db /app/data/backup_$(date +%Y%m%d).db
```

### Otomatik Yedek (Cron)

```bash
# Her gece saat 02:00'de yedek al
0 2 * * * cp /path/to/data/teknik_takip.db /path/to/backups/teknik_$(date +\%Y\%m\%d).db
```

### Geri Yükleme

```bash
# Uygulamayı durdur
docker compose down

# Yedeği geri yükle
cp data/teknik_takip_backup_20250101.db data/teknik_takip.db

# Uygulamayı başlat
docker compose up -d
```

---

## 10. Sık Sorulan Sorular

### ❓ Sayfa yenilenince oturumum kapanıyor

**Neden:** Streamlit'in varsayılan davranışı her yenilemede session_state'i sıfırlar.

**Çözüm:** `streamlit-cookies-controller` paketi kuruluysa otomatik çalışır.
Docker veya yerel kurulumda oturum 30 gün korunur.
Streamlit Community Cloud'da bu özellik kısıtlı olabilir.

---

### ❓ "Modül yüklenemedi" hatası alıyorum

```
Geliştirici hata detayı → kodu inceleyin
```

Genellikle eksik paket nedeniyle olur:
```bash
pip install -r requirements.txt
```

---

### ❓ Google Sheets bağlantısı çalışmıyor

1. Service account e-postasının Spreadsheet'e **düzenleyici** erişimi olduğunu kontrol edin
2. `secrets.toml` dosyasındaki `private_key` satırlarında `\n` karakterlerinin doğru olduğunu kontrol edin
3. ⚙️ Ayarlar → ☁️ Google Sheets → **Bağlantıyı Test Et** ile durumu görün

---

### ❓ Barcode / QR kod baskısı çalışmıyor

`Pillow` ve `python-barcode` paketlerinin kurulu olduğunu kontrol edin:
```bash
pip install "python-barcode[images]" Pillow
```

---

### ❓ E-posta bildirimleri gitmiyor

1. SMTP ayarlarını kontrol edin (**⚙️ Ayarlar → Bildirim**)
2. Gmail kullanıyorsanız normal şifre yerine **App Password** kullanın
3. Hesapta "Az güvenli uygulama erişimi" açık olmalı ya da 2FA + App Password kullanılmalı

---

### ❓ Birden fazla tesis için nasıl kullanırım?

Her tesis için ayrı bir kurulum yapın:
- **Docker:** Farklı port veya farklı sunucu
- **Streamlit Cloud:** Her tesis için ayrı GitHub deposu ve uygulama
- **Yerel:** `APP_PORT=8502`, `APP_PORT=8503`... şeklinde farklı portlar

Her tesisin verisi birbirinden tamamen bağımsızdır.

---

### ❓ Admin şifresini unuttum, SMTP de yok

Doğrudan SQLite veritabanından sıfırlayın:

```python
# Python konsolunda çalıştırın (uygulama dizininde)
import sys, os
sys.path.insert(0, '.')
from auth import hash_password
import sqlite3

conn = sqlite3.connect('data/teknik_takip.db')
new_hash = hash_password('YeniSifre123')
conn.execute("UPDATE tbl_kullanici SET Sifre_Hash=? WHERE Kullanici_Adi='admin'", (new_hash,))
conn.commit()
conn.close()
print("Şifre güncellendi.")
```

---

## Destek & Katkı

- Hata bildirimi: GitHub Issues
- Dokümantasyon güncellemeleri: Pull Request

---

*Teknik Takip Pro — Tesis operasyon yönetimini dijitalleştirin.*
