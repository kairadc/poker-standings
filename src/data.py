from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from . import sheets
from .config import (
    CACHE_TTL_SECONDS,
    DATE_FORMAT,
    NUMERIC_COLUMNS,
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    SAMPLE_CSV_PATH,
)


@dataclass
class DataQuality:
    source: str = "sample"
    issues: List[str] = field(default_factory=list)
    warnings: Dict[str, int] = field(default_factory=dict)
    headers: List[str] = field(default_factory=list)


def clean_column_name(name: str) -> str:
    """Normalize a column header (lowercase, underscores)."""
    return str(name).strip().lower().replace(" ", "_")


def normalize_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, DataQuality]:
    """Standardize columns, coerce types, drop bad rows, compute net."""
    dq = DataQuality()
    if df is None or df.empty:
        dq.issues.append("No data found.")
        return pd.DataFrame(), dq

    working = df.copy()
    working.columns = [clean_column_name(c) for c in working.columns]
    dq.headers = list(working.columns)
    working.replace(r"^\s*$", pd.NA, regex=True, inplace=True)

    missing = [col for col in REQUIRED_COLUMNS if col not in working.columns]
    if missing:
        dq.issues.append(f"Missing required columns: {', '.join(missing)}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS + OPTIONAL_COLUMNS + ["net"]), dq

    keep_cols = [col for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if col in working.columns]
    working = working[keep_cols]

    # Dates (UK-friendly parsing)
    date_col = "date"
    raw_dates = working[date_col]
    cleaned_dates = raw_dates
    # If strings are present, clean NBSP and whitespace before parsing.
    if cleaned_dates.dtype == object or isinstance(cleaned_dates.iloc[0], str):
        cleaned_dates = (
            cleaned_dates.astype(str)
            .str.replace("\u00a0", " ", regex=False)
            .str.strip()
        )
    parsed_dates = pd.to_datetime(cleaned_dates, errors="coerce", dayfirst=True)
    working["date"] = parsed_dates
    invalid_dates = int(working["date"].isna().sum())
    if invalid_dates:
        dq.warnings["invalid_dates"] = invalid_dates
    working = working.dropna(subset=["date"])

    # Numbers
    for col in NUMERIC_COLUMNS:
        working[col] = pd.to_numeric(working[col], errors="coerce")
        invalid_numbers = int(working[col].isna().sum())
        if invalid_numbers:
            dq.warnings[f"invalid_{col}"] = invalid_numbers

    # Drop rows missing required fields after cleaning
    missing_required_rows = int(working[REQUIRED_COLUMNS].isna().any(axis=1).sum())
    if missing_required_rows:
        dq.warnings["dropped_missing_required"] = missing_required_rows
    working = working.dropna(subset=REQUIRED_COLUMNS)

    working["session_id"] = working["session_id"].astype(str)
    working["player"] = working["player"].astype(str)

    # Derived net
    working["net"] = working["cash_out"] - working["buy_in"]

    # Dedupe on (session_id, player), keep the last occurrence.
    dupe_mask = working.duplicated(subset=["session_id", "player"], keep="last")
    dupe_count = int(dupe_mask.sum())
    if dupe_count:
        dq.warnings["duplicate_session_player"] = dupe_count
        working = working.loc[~dupe_mask]

    working = working.sort_values(by="date").reset_index(drop=True)
    return working, dq


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_dataset() -> Tuple[pd.DataFrame, DataQuality]:
    """Load from Google Sheets if configured, else fall back to sample CSV."""
    dq = DataQuality()
    df = pd.DataFrame()
    headers: List[str] = []

    if sheets.is_configured():
        try:
            df, headers = sheets.fetch_sheet()
            dq.source = "sheets"
        except Exception as exc:  # pylint: disable=broad-except
            dq.issues.append(f"Sheets load failed: {type(exc).__name__}: {exc}")

    if df is None or df.empty:
        try:
            df = pd.read_csv(SAMPLE_CSV_PATH)
            dq.source = "sample"
            dq.issues.append("Using bundled sample data (demo mode).")
            headers = headers or list(df.columns)
        except FileNotFoundError:
            dq.issues.append(f"Sample data missing at {SAMPLE_CSV_PATH}")
            df = pd.DataFrame()

    normalized, norm_dq = normalize_dataframe(df)
    dq.issues.extend(norm_dq.issues)
    dq.warnings.update(norm_dq.warnings)
    dq.headers = headers or norm_dq.headers
    return normalized, dq


def available_filter_columns(df: pd.DataFrame) -> List[str]:
    """Return optional filter columns present in the dataset."""
    return [col for col in OPTIONAL_COLUMNS if col in df.columns]


def apply_filters(df: pd.DataFrame, filters: Dict[str, List]) -> pd.DataFrame:
    """Filter by date range, players, and optional dimensions."""
    if df is None or df.empty or not filters:
        return df

    filtered = df.copy()
    date_range = filters.get("date_range")
    if date_range:
        if isinstance(date_range, (list, tuple)):
            start = date_range[0]
            end = date_range[1] if len(date_range) > 1 else None
            if start:
                filtered = filtered[filtered["date"].dt.date >= start]
            if end:
                filtered = filtered[filtered["date"].dt.date <= end]

    players = filters.get("players") or []
    if players:
        filtered = filtered[filtered["player"].isin(players)]

    for col in ["venue", "game_type", "season"]:
        vals = filters.get(col) or []
        if vals and col in filtered.columns:
            filtered = filtered[filtered[col].isin(vals)]

    return filtered
