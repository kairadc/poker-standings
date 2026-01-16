from typing import Tuple

import pandas as pd


def detect_results_schema(df: pd.DataFrame) -> str:
    """Detect which schema the results DataFrame follows."""
    cols = {c.lower() for c in df.columns}
    if {"player", "date", "net"}.issubset(cols):
        return "net_direct"
    if {"player", "date", "buy_in", "cash_out"}.issubset(cols):
        return "buyin_cashout"
    return "unknown"


def normalize_results_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize incoming results to standard columns:
    player, date (datetime), net (float), optional group, session_id.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["player", "date", "net", "group", "session_id"])

    working = df.copy()
    # Standardize column names
    working.columns = [str(c).strip().lower() for c in working.columns]

    schema = detect_results_schema(working)

    # Compute net if needed
    if schema == "buyin_cashout":
        working["net"] = pd.to_numeric(working["cash_out"], errors="coerce") - pd.to_numeric(
            working["buy_in"], errors="coerce"
        )
    elif schema == "net_direct":
        working["net"] = pd.to_numeric(working["net"], errors="coerce")
    else:
        return pd.DataFrame(columns=["player", "date", "net", "group", "session_id"])

    # Parse dates
    working["date"] = pd.to_datetime(working["date"], errors="coerce", dayfirst=True)

    # Trim strings
    for col in ["player", "group", "session_id"]:
        if col in working.columns:
            working[col] = working[col].astype(str).str.strip()

    # Keep standard columns
    keep = [col for col in ["player", "date", "net", "group", "session_id"] if col in working.columns]
    normalized = working[keep].dropna(subset=["player", "date", "net"])

    return normalized
