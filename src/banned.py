import pandas as pd
import streamlit as st
from pathlib import Path
import re

from . import sheets


@st.cache_data(ttl=60, show_spinner=False)
def load_banned_players() -> pd.DataFrame:
    """
    Load banned players from the Google Sheet tab `banned_players`.
    If sheets secrets are missing or tab not found, return empty DataFrame.
    """
    if not sheets.is_configured():
        return pd.DataFrame()
    try:
        df, _ = sheets.fetch_sheet(worksheet_name="banned_players")
        return pd.DataFrame(df)
    except Exception:
        return pd.DataFrame()


def validate_banned_players_df(df: pd.DataFrame):
    """
    Clean and validate banned players data.
    - Drop rows without player_name
    - Normalize ban_type (Permanent/Temporary) default Temporary
    - Fill missing reason
    - Attach optional local mugshot path (PNG) from assets/banned/
    Returns cleaned_df, warnings_list
    """
    warnings = []
    if df is None or df.empty:
        return pd.DataFrame(columns=["player_name", "reason", "ban_type", "mugshot_path"]), warnings

    working = df.copy()
    working.columns = [str(c).strip().lower() for c in working.columns]

    if "player_name" not in working.columns:
        warnings.append("Missing required column: player_name")
        return pd.DataFrame(columns=["player_name", "reason", "ban_type", "mugshot_path"]), warnings

    # Trim strings
    for col in ["player_name", "reason", "ban_type"]:
        if col in working.columns:
            working[col] = working[col].astype(str).str.strip()

    before = len(working)
    working = working[working["player_name"] != ""]
    dropped = before - len(working)
    if dropped:
        warnings.append(f"Dropped {dropped} row(s) with empty player_name.")

    # Normalize ban_type
    def normalize_ban_type(val: str) -> str:
        if isinstance(val, str) and val.lower() in ["permanent"]:
            return "Permanent"
        if isinstance(val, str) and val.lower() in ["temporary"]:
            return "Temporary"
        return "Temporary"

    working["ban_type"] = working.get("ban_type", pd.Series(dtype=str)).apply(normalize_ban_type)

    # Fill reason
    if "reason" not in working.columns:
        working["reason"] = "Failure to pay out"
    working["reason"] = working["reason"].replace("", "Failure to pay out")

    # Attach mugshot path if available
    working["mugshot_path"] = working["player_name"].apply(_lookup_mugshot_path)

    return working, warnings


def _normalize_player_name_to_filename(name: str) -> str:
    """
    Convert player name to a safe filename:
    - lowercase
    - strip whitespace
    - replace spaces with underscores
    - remove non-alphanumeric characters
    """
    safe = re.sub(r"[^a-z0-9_]", "", name.strip().lower().replace(" ", "_"))
    return f"{safe}.png" if safe else ""


def _lookup_mugshot_path(player_name: str) -> str | None:
    """
    Look for a PNG in assets/banned/ matching the normalized player name.
    Returns a string path if found, else None. PNG-only, local files only.
    """
    filename = _normalize_player_name_to_filename(str(player_name))
    if not filename:
        return None
    path = Path("assets") / "banned" / filename
    return str(path) if path.exists() else None
