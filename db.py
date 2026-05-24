"""Veri katmanı: Google Sheets → SQLite → CSV öncelik sırasıyla."""
from __future__ import annotations
import os
import sqlite3
import pandas as pd
import streamlit as st
from constants import GOOGLE_SCOPES, SHEETS, COLS

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False

# ── Dosya yolları ────────────────────────────────────────────────────────────
FILES = {k: f"vt_{k}.csv" for k in COLS}

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_DB_PATH = os.path.join(_DATA_DIR, "teknik_takip.db")


# ═══════════════════════════════════════════════════════════════════════════════
# Google Sheets katmanı (değişmedi)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_client(creds_dict: dict):
    creds = Credentials.from_service_account_info(creds_dict, scopes=GOOGLE_SCOPES)
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
        try:
            if "gcp_service_account" in st.secrets:
                creds_dict = dict(st.secrets["gcp_service_account"])
                st.session_state["gs_creds"] = creds_dict
            else:
                return None
        except Exception:
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
    if not sid:
        try:
            if "spreadsheet_id" in st.secrets:
                sid = st.secrets["spreadsheet_id"]
                st.session_state["gs_sid"] = sid
        except Exception:
            pass
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
    """True if Google Sheets is configured AND working."""
    if not GSPREAD_OK:
        return False
    try:
        return bool(get_gs_client() and _sid())
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# SQLite katmanı
# ═══════════════════════════════════════════════════════════════════════════════

def sqlite_enabled() -> bool:
    """True if SQLite file exists OR data/ directory exists."""
    return os.path.exists(_DB_PATH) or os.path.isdir(_DATA_DIR)


def _get_conn() -> sqlite3.Connection:
    """Her çağrı için yeni bağlantı döner (thread-safe)."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _table_name(key: str) -> str:
    return f"tbl_{key}"


def _ensure_table(conn: sqlite3.Connection, key: str):
    """Tablo yoksa oluştur, eksik sütunları ekle."""
    cols = COLS[key]
    tbl = _table_name(key)
    # Tablo yoksa oluştur
    col_defs = ", ".join(f'"{c}" TEXT' for c in cols)
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{tbl}" ({col_defs})')
    conn.commit()

    # Mevcut sütunları kontrol et, eksik olanları ekle
    existing = {row[1] for row in conn.execute(f'PRAGMA table_info("{tbl}")')}
    for c in cols:
        if c not in existing:
            conn.execute(f'ALTER TABLE "{tbl}" ADD COLUMN "{c}" TEXT DEFAULT ""')
    conn.commit()


def _sqlite_load(key: str) -> pd.DataFrame:
    cols = COLS[key]
    tbl = _table_name(key)
    try:
        conn = _get_conn()
        try:
            _ensure_table(conn, key)
            rows = conn.execute(f'SELECT * FROM "{tbl}"').fetchall()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                # Eksik sütunları ekle
                for c in cols:
                    if c not in df.columns:
                        df[c] = ""
                # Sadece bilinen sütunlar, doğru sırada
                return df[cols]
            return pd.DataFrame(columns=cols)
        finally:
            conn.close()
    except Exception as e:
        st.warning(f"SQLite okuma hatası ({key}): {e}")
        return pd.DataFrame(columns=cols)


def _sqlite_save(df: pd.DataFrame, key: str):
    cols = COLS[key]
    tbl = _table_name(key)
    try:
        conn = _get_conn()
        try:
            _ensure_table(conn, key)
            conn.execute(f'DELETE FROM "{tbl}"')
            if not df.empty:
                # Sadece bilinen sütunlar
                save_df = df.copy()
                for c in cols:
                    if c not in save_df.columns:
                        save_df[c] = ""
                save_df = save_df[cols].fillna("").astype(str)
                placeholders = ", ".join("?" for _ in cols)
                col_names = ", ".join(f'"{c}"' for c in cols)
                conn.executemany(
                    f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})',
                    save_df.values.tolist()
                )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        st.warning(f"SQLite yazma hatası ({key}): {e}")


def _sqlite_append(key: str, row: dict):
    cols = COLS[key]
    tbl = _table_name(key)
    try:
        conn = _get_conn()
        try:
            _ensure_table(conn, key)
            # Sadece bilinen sütunlar
            row_vals = [str(row.get(c, "") or "") for c in cols]
            col_names = ", ".join(f'"{c}"' for c in cols)
            placeholders = ", ".join("?" for _ in cols)
            conn.execute(
                f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})',
                row_vals
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        st.warning(f"SQLite append hatası ({key}): {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Ortak arayüz (öncelik: Google Sheets → SQLite → CSV)
# ═══════════════════════════════════════════════════════════════════════════════

def load_data(key: str) -> pd.DataFrame:
    cols = COLS[key]

    # 1. Google Sheets
    if gs_connected():
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

    # 2. SQLite (varsayılan)
    if sqlite_enabled():
        return _sqlite_load(key)

    # 3. CSV (eski yedek)
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
    # 1. Google Sheets
    if gs_connected():
        ws = get_worksheet(key)
        if ws:
            try:
                ws.clear()
                rows = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
                ws.update(rows)
                return
            except Exception as e:
                st.warning(f"Google Sheets yazma hatası ({key}): {e}")

    # 2. SQLite (varsayılan)
    if sqlite_enabled():
        _sqlite_save(df, key)
        return

    # 3. CSV (eski yedek)
    df.to_csv(FILES[key], index=False)


def append_row(key: str, row: dict):
    """Hızlı satır ekleme."""
    # 1. Google Sheets
    if gs_connected():
        ws = get_worksheet(key)
        if ws:
            try:
                cols = COLS[key]
                vals = [str(row.get(c, "") or "") for c in cols]
                ws.append_row(vals)
                return load_data(key)
            except Exception as e:
                st.warning(f"Google Sheets append hatası ({key}): {e}")

    # 2. SQLite (varsayılan)
    if sqlite_enabled():
        _sqlite_append(key, row)
        return load_data(key)

    # 3. CSV (eski yedek)
    df = load_data(key)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, key)
    return df
