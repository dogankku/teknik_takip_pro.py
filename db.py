"""Google Sheets veri katmanı (CSV yedekli)."""
from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from constants import GOOGLE_SCOPES, SHEETS, COLS

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

FILES = {k: f"vt_{k}.csv" for k in COLS}


def _build_client(creds_dict: dict):
    creds = Credentials.from_service_account_info(creds_dict, scopes=GOOGLE_SCOPES)
    # gspread 6.x kaldırdı gspread.authorize() → gspread.Client kullan
    if hasattr(gspread, "authorize"):
        return gspread.authorize(creds)          # gspread < 6
    return gspread.Client(auth=creds)            # gspread >= 6


def get_gs_client():
    if not GSPREAD_OK:
        return None
    if "gs_client_obj" in st.session_state:
        return st.session_state["gs_client_obj"]

    creds_dict = st.session_state.get("gs_creds")
    if creds_dict is None:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            st.session_state["gs_creds"] = creds_dict
        else:
            return None
    try:
        client = _build_client(creds_dict)
        st.session_state["gs_client_obj"] = client
        return client
    except Exception as e:
        st.error(f"Google bağlantı hatası: {e}")
        return None


def _sid() -> str:
    sid = st.session_state.get("gs_sid", "").strip()
    if not sid and "spreadsheet_id" in st.secrets:
        sid = st.secrets["spreadsheet_id"]
        st.session_state["gs_sid"] = sid
    return sid


def get_worksheet(key: str):
    client = get_gs_client()
    sid = _sid()
    if client is None or not sid:
        return None
    try:
        sh = client.open_by_key(sid)
        try:
            return sh.worksheet(SHEETS[key])
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=SHEETS[key], rows=2000, cols=len(COLS[key]))
            ws.append_row(COLS[key])
            return ws
    except Exception as e:
        st.error(f"Google Sheets erişim hatası: {e}")
        return None


def gs_connected() -> bool:
    return bool(get_gs_client() and _sid())


def load_data(key: str) -> pd.DataFrame:
    cols = COLS[key]
    ws = get_worksheet(key)
    if ws:
        try:
            records = ws.get_all_records()
            df = pd.DataFrame(records) if records else pd.DataFrame(columns=cols)
            for c in cols:
                if c not in df.columns:
                    df[c] = ""
            return df[cols] if not df.empty else df
        except Exception as e:
            st.warning(f"Google Sheets okuma hatası ({key}): {e}")
    if os.path.exists(FILES[key]):
        try:
            df = pd.read_csv(FILES[key])
            for c in cols:
                if c not in df.columns:
                    df[c] = ""
            return df[cols] if not df.empty else df
        except Exception:
            pass
    return pd.DataFrame(columns=cols)


def save_data(df: pd.DataFrame, key: str):
    ws = get_worksheet(key)
    if ws:
        try:
            ws.clear()
            rows = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
            ws.update(rows)
            return
        except Exception as e:
            st.warning(f"Google Sheets yazma hatası ({key}): {e}")
    df.to_csv(FILES[key], index=False)


def append_row(key: str, row: dict):
    """Hızlı satır ekleme - tüm sheet'i yeniden yazmak yerine append."""
    df = load_data(key)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, key)
    return df
