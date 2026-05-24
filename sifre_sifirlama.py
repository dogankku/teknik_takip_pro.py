"""Şifre sıfırlama: token üretimi, email gönderimi, token doğrulama."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

RESET_MINUTES = 60  # token geçerlilik süresi


def create_reset_token(email_or_username: str) -> tuple[str, str] | None:
    """
    Email veya kullanıcı adıyla eşleşen hesap varsa reset token oluşturur.
    Başarılıysa (token, kullanici_adi) döner; bulunamazsa None döner.
    """
    from db import load_data, append_row

    df = load_data("kullanici")
    if df.empty:
        return None

    # Email veya kullanıcı adı ile eşleş
    df["Email"] = df["Email"].astype(str)
    df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
    val = email_or_username.strip().lower()
    match = df[
        (df["Email"].str.lower() == val) | (df["Kullanici_Adi"].str.lower() == val)
    ]
    if match.empty:
        return None

    kullanici_adi = str(match.iloc[0]["Kullanici_Adi"])
    email = str(match.iloc[0]["Email"])

    token = str(uuid.uuid4())
    row = {
        "Token": token,
        "Kullanici_Adi": kullanici_adi,
        "Olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Kullanildi": "Hayir",
    }
    try:
        append_row("sifre_sifir", row)
    except Exception:
        return None

    return token, kullanici_adi


def validate_reset_token(token: str) -> str | None:
    """
    Token'ı doğrular. Geçerliyse kullanici_adi döner, değilse None.
    """
    from db import load_data

    df = load_data("sifre_sifir")
    if df.empty:
        return None

    row = df[(df["Token"] == token) & (df["Kullanildi"] == "Hayir")]
    if row.empty:
        return None

    r = row.iloc[0]
    try:
        created = datetime.strptime(str(r.get("Olusturma", "")), "%Y-%m-%d %H:%M")
        if datetime.now() - created > timedelta(minutes=RESET_MINUTES):
            return None
    except Exception:
        pass

    return str(r.get("Kullanici_Adi", ""))


def use_reset_token(token: str, yeni_sifre: str) -> bool:
    """
    Token geçerliyse şifreyi günceller, token'ı kullanıldı olarak işaretler.
    Başarılıysa True döner.
    """
    from db import load_data, save_data
    from auth import update_user, hash_password

    kullanici_adi = validate_reset_token(token)
    if not kullanici_adi:
        return False

    # Şifreyi güncelle
    update_user(kullanici_adi, sifre=yeni_sifre)

    # Token'ı kullanıldı işaretle
    try:
        df = load_data("sifre_sifir")
        if not df.empty:
            df.loc[df["Token"] == token, "Kullanildi"] = "Evet"
            save_data(df, "sifre_sifir")
    except Exception:
        pass

    return True


def send_reset_email(email: str, token: str, base_url: str = "") -> bool:
    """
    Şifre sıfırlama bağlantısını email ile gönderir.
    bildirim_helper.py kullanılır; SMTP ayarları yoksa False döner.
    """
    try:
        from bildirim_helper import bildirim_gonder

        link = f"{base_url.rstrip('/')}/?reset={token}"
        icerik = (
            f"Şifre sıfırlama bağlantınız:\n\n{link}\n\n"
            f"Bu bağlantı {RESET_MINUTES} dakika geçerlidir.\n\n"
            "Bu isteği siz yapmadıysanız bu e-postayı görmezden gelin."
        )
        bildirim_gonder(
            baslik="🔑 Şifre Sıfırlama — Teknik Takip Pro",
            icerik=icerik,
            email_list=[email],
        )
        return True
    except Exception:
        return False
