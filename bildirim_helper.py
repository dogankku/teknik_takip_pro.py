"""Çok kanallı bildirim sistemi — SMTP e-posta, Telegram Bot, WhatsApp (Twilio).

Kullanım:
    from bildirim_helper import bildirim_gonder
    bildirim_gonder("Yeni Arıza", "ARZ-001 kazan dairesi...",
                    email_list=["ali@site.com"], telefon_list=["+905..."])
"""
from __future__ import annotations
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st


# ── Yardımcı: ayarları al ─────────────────────────────────────────────────────
def _cfg(key: str) -> dict:
    """Session_state'ten ayar bloğunu al; yoksa secrets'ta ara."""
    if key in st.session_state:
        return dict(st.session_state[key])
    # Streamlit Secrets desteği (production'da kullanışlı)
    try:
        if key in st.secrets:
            return dict(st.secrets[key])
    except Exception:
        pass
    return {}


def _genel() -> dict:
    return _cfg("bildirim_genel")


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL (SMTP)
# ══════════════════════════════════════════════════════════════════════════════
def email_gonder(to_list: list[str], baslik: str, icerik: str) -> tuple[bool, str]:
    """HTML e-posta gönderir. (True, "") veya (False, "hata") döndürür."""
    cfg = _cfg("bildirim_email")
    sunucu = cfg.get("smtp_sunucu", "").strip()
    port   = int(cfg.get("smtp_port", 587) or 587)
    user   = cfg.get("smtp_user", "").strip()
    pwd    = cfg.get("smtp_pwd", "").strip()
    sender = cfg.get("smtp_sender", user).strip() or user

    if not (sunucu and user and pwd):
        return False, "SMTP ayarları eksik."

    alicilar = [t.strip() for t in to_list if t and "@" in t]
    if not alicilar:
        return False, "Geçerli alıcı yok."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Teknik Sistem] {baslik}"
        msg["From"]    = sender
        msg["To"]      = ", ".join(alicilar)

        html_body = f"""
        <html><body>
        <div style="font-family:Inter,Arial,sans-serif;max-width:600px;
                    margin:0 auto;padding:24px;">
          <div style="background:#4F46E5;padding:16px 20px;border-radius:10px 10px 0 0;">
            <span style="color:#fff;font-size:1.1rem;font-weight:700;">
              🏢 Teknik Operasyon Sistemi
            </span>
          </div>
          <div style="background:#F8FAFC;padding:20px;border:1px solid #E2E8F0;
                      border-radius:0 0 10px 10px;">
            <h2 style="color:#1E293B;margin-top:0;">{baslik}</h2>
            <p style="color:#475569;line-height:1.6;">
              {icerik.replace(chr(10), '<br>')}
            </p>
          </div>
          <p style="color:#94A3B8;font-size:.75rem;text-align:center;margin-top:12px;">
            Bu otomatik bir bildirimdir. Lütfen yanıtlamayın.
          </p>
        </div>
        </body></html>"""

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        ctx = ssl.create_default_context()
        with smtplib.SMTP(sunucu, port) as sv:
            sv.ehlo()
            sv.starttls(context=ctx)
            sv.login(user, pwd)
            sv.sendmail(sender, alicilar, msg.as_string())
        return True, ""
    except Exception as ex:
        return False, str(ex)


# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT
# ══════════════════════════════════════════════════════════════════════════════
def telegram_gonder(mesaj: str, chat_id: str | None = None) -> tuple[bool, str]:
    """Telegram Bot API ile mesaj gönderir."""
    try:
        import requests as _req
    except ImportError:
        return False, "'requests' paketi yüklü değil."

    cfg = _cfg("bildirim_telegram")
    token = cfg.get("bot_token", "").strip()
    cid   = (chat_id or cfg.get("chat_id", "")).strip()

    if not token or not cid:
        return False, "Telegram bot_token veya chat_id eksik."

    try:
        url  = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": cid, "text": mesaj, "parse_mode": "HTML"}
        resp = _req.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            return True, ""
        return False, resp.text[:200]
    except Exception as ex:
        return False, str(ex)


# ══════════════════════════════════════════════════════════════════════════════
# WHATSAPP — Twilio
# ══════════════════════════════════════════════════════════════════════════════
def whatsapp_gonder(to_tel: str, mesaj: str) -> tuple[bool, str]:
    """Twilio WhatsApp API ile mesaj gönderir.
    to_tel örn: '+905001234567'  (başında + ve ülke kodu)
    """
    try:
        from twilio.rest import Client as _TwilioClient
    except ImportError:
        return False, "'twilio' paketi yüklü değil: pip install twilio"

    cfg  = _cfg("bildirim_whatsapp")
    sid  = cfg.get("account_sid", "").strip()
    auth = cfg.get("auth_token", "").strip()
    # Twilio sandbox: +14155238886  (canlıda kayıtlı numaranız)
    from_wa = cfg.get("from_number", "whatsapp:+14155238886").strip()

    if not (sid and auth):
        return False, "Twilio account_sid veya auth_token eksik."

    to_wa = f"whatsapp:{to_tel}" if not to_tel.startswith("whatsapp:") else to_tel

    try:
        client = _TwilioClient(sid, auth)
        client.messages.create(body=mesaj, from_=from_wa, to=to_wa)
        return True, ""
    except Exception as ex:
        return False, str(ex)


# ══════════════════════════════════════════════════════════════════════════════
# MERKEZ — tüm kanalları birden çağır
# ══════════════════════════════════════════════════════════════════════════════
def bildirim_gonder(
    baslik: str,
    icerik: str,
    email_list: list[str] | None = None,
    telefon_list: list[str] | None = None,
    telegram: bool = True,
) -> dict[str, bool | str]:
    """
    Aktif kanallardan bildirim gönderir.

    Returns:
        {"email": True, "telegram": True, "whatsapp": False, ...}
    """
    g = _genel()
    sonuc: dict = {}

    # E-posta
    if email_list and g.get("email_aktif"):
        ok, err = email_gonder(email_list, baslik, icerik)
        sonuc["email"] = ok if ok else f"HATA: {err}"

    # Telegram (grup bildirimi — kişi bazlı değil)
    if telegram and g.get("telegram_aktif"):
        ok, err = telegram_gonder(f"<b>🔔 {baslik}</b>\n\n{icerik}")
        sonuc["telegram"] = ok if ok else f"HATA: {err}"

    # WhatsApp (kişi bazlı)
    if telefon_list and g.get("whatsapp_aktif"):
        results = []
        for tel in telefon_list:
            if tel and tel.strip():
                ok, err = whatsapp_gonder(tel.strip(), f"🔔 {baslik}\n\n{icerik}")
                results.append(ok)
        sonuc["whatsapp"] = all(results) if results else False

    return sonuc


# ══════════════════════════════════════════════════════════════════════════════
# TEST fonksiyonu (Ayarlar sayfasında kullanılır)
# ══════════════════════════════════════════════════════════════════════════════
def test_email(to: str) -> tuple[bool, str]:
    return email_gonder([to], "Test E-postası", "Bu bir test mesajıdır. Sistem çalışıyor.")


def test_telegram(chat_id: str | None = None) -> tuple[bool, str]:
    return telegram_gonder("🧪 <b>Test Mesajı</b>\nTeknik sistem bağlantısı başarılı.", chat_id)


def test_whatsapp(to_tel: str) -> tuple[bool, str]:
    return whatsapp_gonder(to_tel, "🧪 Test: Teknik sistem WhatsApp bağlantısı başarılı.")


# ══════════════════════════════════════════════════════════════════════════════
# Yardımcı: personelden email/telefon listesi çek
# ══════════════════════════════════════════════════════════════════════════════
def personel_iletisim(isim: str) -> tuple[str, str]:
    """Personel adından email ve telefon döndürür (boş olabilir)."""
    try:
        from db import load_data
        df = load_data("personel")
        if df.empty:
            return "", ""
        row = df[df["Isim"] == isim]
        if row.empty:
            return "", ""
        r = row.iloc[0]
        return str(r.get("Email", "") or ""), str(r.get("Telefon", "") or "")
    except Exception:
        return "", ""


def kullanici_iletisim(kullanici_adi: str) -> tuple[str, str]:
    """Kullanıcı adından email ve telefon döndürür."""
    try:
        from db import load_data
        df = load_data("kullanici")
        if df.empty:
            return "", ""
        row = df[df["Kullanici_Adi"] == kullanici_adi]
        if row.empty:
            return "", ""
        r = row.iloc[0]
        return str(r.get("Email", "") or ""), str(r.get("Telefon", "") or "")
    except Exception:
        return "", ""
