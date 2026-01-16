import json
from typing import Any, Dict, List, Tuple

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from .config import CACHE_TTL_SECONDS, DEFAULT_WORKSHEET_NAME, SHEETS_SCOPES


def is_configured() -> bool:
    """Check if required sheets secrets exist."""
    secrets = st.secrets.get("sheets", {})
    has_id = bool(secrets.get("spreadsheet_id"))
    has_creds = bool(secrets.get("service_account") or secrets.get("service_account_json"))
    return has_id and has_creds


def _parse_service_account() -> Dict[str, Any] | None:
    """Parse service account JSON from secrets (dict or stringified)."""
    secrets = st.secrets.get("sheets", {})
    service_account = secrets.get("service_account")
    if isinstance(service_account, str):
        try:
            service_account = json.loads(service_account)
        except json.JSONDecodeError as exc:
            raise ValueError("service_account is not valid JSON") from exc
    if not service_account and secrets.get("service_account_json"):
        try:
            service_account = json.loads(secrets["service_account_json"])
        except json.JSONDecodeError as exc:
            raise ValueError("service_account_json is not valid JSON") from exc
    return service_account


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

    secrets = st.secrets.get("sheets", {})
    ss_id = spreadsheet_id or secrets.get("spreadsheet_id")
    ws_name = worksheet_name or secrets.get("worksheet_name") or DEFAULT_WORKSHEET_NAME

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

    secrets = st.secrets.get("sheets", {})
    ss_id = secrets.get("spreadsheet_id")
    ws_name = secrets.get("worksheet_name") or DEFAULT_WORKSHEET_NAME
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