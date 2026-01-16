import json
from typing import Any, Dict, List, Tuple

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from .config import CACHE_TTL_SECONDS, DEFAULT_WORKSHEET_NAME, SHEETS_SCOPES


def _load_json_string(raw: str, label: str) -> Dict[str, Any]:
    """Attempt to parse JSON; if pretty-printed, escape newlines and retry."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return json.loads(raw.replace("\n", "\\n"))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{label} is not valid JSON. Ensure it is a single JSON object and escape newlines in the private_key as \\n."
            ) from exc


def get_sheets_secrets() -> Tuple[str | None, str | None, Dict[str, Any] | None]:
    """
    Supports both:
    A) Nested secrets: st.secrets["sheets"][...]
    B) Flat secrets: st.secrets["service_account_json"], etc.
    """
    if "sheets" in st.secrets:
        cfg = st.secrets["sheets"]
        spreadsheet_id = cfg.get("spreadsheet_id")
        worksheet_name = cfg.get("worksheet_name")
        sa_raw = cfg.get("service_account") or cfg.get("service_account_json")
        if isinstance(sa_raw, dict):
            service_account_info = sa_raw
        elif isinstance(sa_raw, str):
            service_account_info = _load_json_string(sa_raw, "service_account_json")
        else:
            service_account_info = None
        return spreadsheet_id, worksheet_name, service_account_info

    spreadsheet_id = st.secrets.get("spreadsheet_id")
    worksheet_name = st.secrets.get("worksheet_name")
    sa_raw = st.secrets.get("service_account") or st.secrets.get("service_account_json")
    if isinstance(sa_raw, dict):
        service_account_info = sa_raw
    elif isinstance(sa_raw, str):
        service_account_info = _load_json_string(sa_raw, "service_account_json")
    else:
        service_account_info = None
    return spreadsheet_id, worksheet_name, service_account_info


def is_configured() -> bool:
    """Check if required sheets secrets exist."""
    spreadsheet_id, _, service_account_info = get_sheets_secrets()
    return bool(spreadsheet_id) and bool(service_account_info)


def _parse_service_account() -> Dict[str, Any] | None:
    """Parse service account JSON from secrets (dict or stringified)."""
    _, _, service_account_info = get_sheets_secrets()
    return service_account_info


def _get_client() -> gspread.Client:
    """Create an authenticated gspread client."""
    info = _parse_service_account()
    if not info:
        raise ValueError("Service account details are missing in secrets.")
    credentials = Credentials.from_service_account_info(info, scopes=SHEETS_SCOPES)
    return gspread.authorize(credentials)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_sheet(
    spreadsheet_id: str | None = None, worksheet_name: str | None = None
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Read the worksheet into a DataFrame.

    Returns a tuple of (dataframe, header_row_list).
    """
    if not is_configured():
        raise RuntimeError("Sheets secrets are missing. Add them to .streamlit/secrets.toml.")

    ss_id, ws_name_cfg, _ = get_sheets_secrets()
    ss_id = spreadsheet_id or ss_id
    ws_name = worksheet_name or ws_name_cfg or DEFAULT_WORKSHEET_NAME

    try:
        client = _get_client()
        sheet = client.open_by_key(ss_id)
        worksheet = sheet.worksheet(ws_name)
        headers = worksheet.row_values(1)
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        return df, headers
    except gspread.SpreadsheetNotFound as exc:
        raise RuntimeError("Spreadsheet not found. Check spreadsheet_id.") from exc
    except gspread.WorksheetNotFound as exc:
        raise RuntimeError(f"Worksheet '{ws_name}' not found. Check worksheet_name.") from exc


def connection_diagnostics() -> Dict[str, Any]:
    """Return connection status and detected headers for the help page."""
    status: Dict[str, Any] = {
        "configured": is_configured(),
        "spreadsheet_found": False,
        "worksheet_found": False,
        "headers": [],
        "error": None,
    }
    if not status["configured"]:
        status["error"] = "Secrets missing or incomplete."
        return status

    ss_id, ws_name_cfg, _ = get_sheets_secrets()
    ws_name = ws_name_cfg or DEFAULT_WORKSHEET_NAME
    try:
        client = _get_client()
        sheet = client.open_by_key(ss_id)
        status["spreadsheet_found"] = True
        worksheet = sheet.worksheet(ws_name)
        status["worksheet_found"] = True
        status["headers"] = worksheet.row_values(1)
    except Exception as exc:  # pylint: disable=broad-except
        status["error"] = str(exc)
    return status


def clear_cache() -> None:
    """Clear cached sheet reads so refresh works."""
    fetch_sheet.clear()
