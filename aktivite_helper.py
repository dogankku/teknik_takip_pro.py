"""Aktivite log — kayıt değişikliklerini izleme."""
from __future__ import annotations
from datetime import datetime
import pandas as pd
from db import load_data, save_data
from barkod import yeni_id


def log_ekle(parent_tip: str, parent_id: str, kullanici: str,
             aksiyon: str, detay: str = ""):
    df = load_data("aktivite")
    row = {
        "Log_ID": yeni_id("LOG"),
        "Parent_Tip": parent_tip,
        "Parent_ID": str(parent_id),
        "Kullanici": kullanici,
        "Tarih": datetime.now().strftime("%Y-%m-%d"),
        "Saat": datetime.now().strftime("%H:%M"),
        "Aksiyon": aksiyon,
        "Detay": detay,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_data(df, "aktivite")


def log_getir(parent_tip: str, parent_id: str) -> list[dict]:
    df = load_data("aktivite")
    if df.empty:
        return []
    m = df[(df["Parent_Tip"].astype(str) == parent_tip) &
           (df["Parent_ID"].astype(str) == str(parent_id))]
    return m.sort_values("Tarih", ascending=False).to_dict("records") if not m.empty else []
