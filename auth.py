"""Kullanıcı yönetimi, parola hash, RBAC."""
from __future__ import annotations
import hashlib
import json
import streamlit as st
from datetime import datetime
import pandas as pd
from db import load_data, save_data, append_row
from constants import YETKI


SALT = "tknk_op_sys_v1"


def hash_password(pw: str) -> str:
    return hashlib.sha256((SALT + pw).encode("utf-8")).hexdigest()


def verify_password(pw: str, h: str) -> bool:
    return hash_password(pw) == h


def ensure_default_admin():
    """Hiç kullanıcı yoksa varsayılan admin oluştur."""
    df = load_data("kullanici")
    if df.empty:
        row = {
            "Kullanici_Adi": "admin",
            "Sifre_Hash": hash_password("admin123"),
            "Ad_Soyad": "Sistem Yöneticisi",
            "Rol": "Admin",
            "Daire_ID": "",
            "Telefon": "",
            "Email": "",
            "Aktif": "Evet",
            "Olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        append_row("kullanici", row)


def login(username: str, password: str) -> dict | None:
    df = load_data("kullanici")
    if df.empty:
        return None
    df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
    match = df[df["Kullanici_Adi"].str.lower() == username.lower().strip()]
    if match.empty:
        return None
    u = match.iloc[0].to_dict()
    if str(u.get("Aktif", "")).lower() not in ("evet", "true", "1", "yes"):
        return None
    if not verify_password(password, str(u.get("Sifre_Hash", ""))):
        return None
    return u


def current_user() -> dict | None:
    return st.session_state.get("current_user")


def current_role() -> str | None:
    u = current_user()
    return u.get("Rol") if u else None


def is_logged_in() -> bool:
    return current_user() is not None


def has_access(modul_key: str) -> bool:
    """3 katlı RBAC: Admin bypass → kullanıcı override → DB rol tablosu → sabit fallback."""
    rol = current_role()
    if not rol:
        return False
    if rol == "Admin":
        return True

    u = current_user() or {}

    # Katman 1: Kullanıcı bazlı engel
    try:
        kapali = json.loads(str(u.get("Kapali_Modul", "") or "[]"))
        if modul_key in kapali:
            return False
    except Exception:
        pass

    # Katman 2: Kullanıcı bazlı ek izin
    try:
        ekstra = json.loads(str(u.get("Ekstra_Modul", "") or "[]"))
        if modul_key in ekstra:
            return True
    except Exception:
        pass

    # Katman 3: Dinamik rol tablosu (Google Sheets / CSV)
    try:
        df_yr = load_data("yetki_rol")
        if not df_yr.empty:
            row = df_yr[df_yr["Rol"].astype(str) == str(rol)]
            if not row.empty:
                modul_list = json.loads(str(row.iloc[0].get("Modul_JSON", "[]") or "[]"))
                if modul_list == ["*"]:
                    return True
                return modul_key in modul_list
    except Exception:
        pass

    # Katman 4: Sabit fallback
    yetki = YETKI.get(rol, [])
    if yetki == "*":
        return True
    return modul_key in yetki


def logout():
    for k in ("current_user", "menu_radio"):
        if k in st.session_state:
            del st.session_state[k]


def add_user(kullanici_adi: str, sifre: str, ad_soyad: str, rol: str,
             daire_id: str = "", telefon: str = "", email: str = "") -> tuple[bool, str]:
    df = load_data("kullanici")
    if not df.empty:
        df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
        if (df["Kullanici_Adi"].str.lower() == kullanici_adi.lower().strip()).any():
            return False, "Bu kullanıcı adı zaten kayıtlı."
    row = {
        "Kullanici_Adi": kullanici_adi.strip(),
        "Sifre_Hash": hash_password(sifre),
        "Ad_Soyad": ad_soyad.strip(),
        "Rol": rol,
        "Daire_ID": daire_id,
        "Telefon": telefon,
        "Email": email,
        "Aktif": "Evet",
        "Olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    append_row("kullanici", row)
    return True, "Kullanıcı eklendi."


def update_user(kullanici_adi: str, **fields):
    df = load_data("kullanici")
    if df.empty:
        return
    df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
    mask = df["Kullanici_Adi"].str.lower() == kullanici_adi.lower().strip()
    if not mask.any():
        return
    for k, v in fields.items():
        if k == "sifre" and v:
            df.loc[mask, "Sifre_Hash"] = hash_password(v)
        elif k in df.columns:
            df.loc[mask, k] = v
    save_data(df, "kullanici")


def delete_user(kullanici_adi: str):
    df = load_data("kullanici")
    if df.empty:
        return
    df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
    df = df[df["Kullanici_Adi"].str.lower() != kullanici_adi.lower().strip()]
    save_data(df, "kullanici")
