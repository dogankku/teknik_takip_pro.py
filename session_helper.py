"""Cookie-tabanlı oturum kalıcılığı.

Gereksinim: streamlit-cookies-controller (pip install streamlit-cookies-controller)
Kütüphane yoksa sessizce devre dışı kalır — uygulama çalışmaya devam eder,
sadece sayfa yenilemede oturum kaybolur.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import streamlit as st

SESSION_DAYS = 30
_COOKIE_KEY = "auth_token"


# ── Yardımcı: kütüphane varlığını kontrol et ─────────────────────────────────

def _cookie_cls():
    try:
        from streamlit_cookies_controller import CookieController  # type: ignore
        return CookieController
    except ImportError:
        return None


# ── Cookie controller'ı başlat ───────────────────────────────────────────────

def init_cookies():
    """
    İlk çağrıda CookieController oluşturur ve session_state'e kaydeder.
    Controller hazır değilse None döner.

    Sayfa yenilemede cookie değerinin okunabilmesi için uygulamanın
    en başında (herhangi bir widget render edilmeden önce) çağrılmalıdır.
    """
    cls = _cookie_cls()
    if cls is None:
        return None
    if "_cookie_ctrl" not in st.session_state:
        st.session_state["_cookie_ctrl"] = cls()
    return st.session_state["_cookie_ctrl"]


def _ctrl():
    return st.session_state.get("_cookie_ctrl")


# ── Giriş sonrası token kaydet ────────────────────────────────────────────────

def save_session_cookie(kullanici_adi: str) -> str:
    """
    Başarılı girişten sonra çağır.
    UUID token oluşturur → SQLite `oturum` tablosuna yazar → tarayıcı cookie'si set eder.
    Token'ı döner (hata durumunda boş string).
    """
    from db import append_row

    token = str(uuid.uuid4())
    now = datetime.now()
    row = {
        "Token": token,
        "Kullanici_Adi": kullanici_adi,
        "Olusturma": now.strftime("%Y-%m-%d %H:%M"),
        "Son_Kullanma": (now + timedelta(days=SESSION_DAYS)).strftime("%Y-%m-%d %H:%M"),
        "Aktif": "Evet",
    }
    try:
        append_row("oturum", row)
    except Exception:
        pass

    ctrl = _ctrl()
    if ctrl:
        try:
            ctrl.set(_COOKIE_KEY, token, max_age=SESSION_DAYS * 86400)
            st.session_state["_auth_token"] = token
        except Exception:
            pass

    return token


# ── Sayfa yenilemede oturumu geri yükle ──────────────────────────────────────

def restore_from_cookie() -> bool:
    """
    Cookie'yi okur, token'ı SQLite'ta doğrular, kullanıcıyı session_state'e yükler.
    Başarılı olursa True döner.
    """
    ctrl = _ctrl()
    if ctrl is None:
        return False

    try:
        token = ctrl.get(_COOKIE_KEY)
        if not token:
            return False

        from db import load_data

        # Token geçerlilik kontrolü
        df_o = load_data("oturum")
        if df_o.empty:
            return False

        row = df_o[(df_o["Token"] == token) & (df_o["Aktif"] == "Evet")]
        if row.empty:
            return False

        r = row.iloc[0]
        try:
            expiry = datetime.strptime(str(r.get("Son_Kullanma", "")), "%Y-%m-%d %H:%M")
            if expiry < datetime.now():
                return False
        except Exception:
            pass

        # Kullanıcıyı yükle
        kullanici_adi = str(r.get("Kullanici_Adi", ""))
        df_u = load_data("kullanici")
        if df_u.empty:
            return False

        df_u["Kullanici_Adi"] = df_u["Kullanici_Adi"].astype(str)
        user_row = df_u[df_u["Kullanici_Adi"].str.lower() == kullanici_adi.lower()]
        if user_row.empty:
            return False

        u = user_row.iloc[0].to_dict()
        if str(u.get("Aktif", "")).lower() not in ("evet", "true", "1", "yes"):
            return False

        st.session_state["current_user"] = u
        st.session_state["_auth_token"] = token
        return True

    except Exception:
        return False


# ── Çıkışta token geçersiz kıl ───────────────────────────────────────────────

def clear_session_cookie():
    """Çıkış (logout) sırasında çağır: cookie'yi siler, token'ı SQLite'ta pasifleştirir."""
    token = st.session_state.get("_auth_token")

    # SQLite'ta pasifleştir
    if token:
        try:
            from db import load_data, save_data

            df = load_data("oturum")
            if not df.empty and "Token" in df.columns:
                df.loc[df["Token"] == token, "Aktif"] = "Hayir"
                save_data(df, "oturum")
        except Exception:
            pass

    # Cookie'yi sil
    ctrl = _ctrl()
    if ctrl:
        try:
            ctrl.remove(_COOKIE_KEY)
        except Exception:
            pass

    # session_state temizle
    for key in ("_auth_token", "_cookie_ctrl"):
        st.session_state.pop(key, None)
