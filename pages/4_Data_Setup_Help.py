import pandas as pd
import streamlit as st

from src import config, data, sheets

st.title("Data Setup Help")
st.write(
    "Add rows directly in Google Sheets. Each row is one player in one session. "
    "Headers must match the required schema below."
)

st.subheader("Required headers")
st.markdown(
    """
    - `session_id` (text, e.g., `2024-02-16-home-01`)
    - `date` (YYYY-MM-DD)
    - `player` (text)
    - `buy_in` (number)
    - `cash_out` (number)
    Optional: `venue`, `game_type` (`cash|tournament|other`), `season`, `notes`
    """
)

st.subheader("CSV template to copy into Sheets")
template_rows = [
    {
        "session_id": "S-2024-02-01",
        "date": "2024-02-01",
        "player": "Alice",
        "buy_in": 50,
        "cash_out": 120,
        "venue": "Home",
        "game_type": "cash",
        "season": "Spring",
        "notes": "Example row",
    },
    {
        "session_id": "S-2024-02-01",
        "date": "2024-02-01",
        "player": "Bob",
        "buy_in": 50,
        "cash_out": 20,
        "venue": "Home",
        "game_type": "cash",
        "season": "Spring",
        "notes": "Example row",
    },
]
template_df = pd.DataFrame(template_rows, columns=config.REQUIRED_COLUMNS + [c for c in config.OPTIONAL_COLUMNS if c != "notes"] + ["notes"])
st.download_button(
    "Download CSV template",
    data=template_df.to_csv(index=False).encode("utf-8"),
    file_name="poker_sessions_template.csv",
    mime="text/csv",
)

st.subheader("Connection diagnostics")
status = sheets.connection_diagnostics()
col_a, col_b = st.columns(2)
col_a.write(f"Secrets configured: {status['configured']}")
col_a.write(f"Spreadsheet found: {status['spreadsheet_found']}")
col_a.write(f"Worksheet found: {status['worksheet_found']}")
col_b.write(f"Detected headers: {status.get('headers', [])}")
if status.get("error"):
    st.error(f"Connection error: {status['error']}")

st.subheader("Current data preview")
df, dq = data.load_dataset()
if df.empty:
    st.warning("No data available yet. Add rows to your Google Sheet or use the template above.")
else:
    st.dataframe(df.head(10), use_container_width=True)

st.subheader("Secrets format (example)")
st.code(
    """
[sheets]
spreadsheet_id = "YOUR_SHEET_ID"
worksheet_name = "sessions"
service_account = { type="service_account", project_id="your-project", private_key_id="abc", private_key="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n", client_email="service-account@project.iam.gserviceaccount.com", client_id="123", token_uri="https://oauth2.googleapis.com/token" }
# Alternatively:
# service_account_json = '''{ "type": "service_account", ... }'''
""",
    language="toml",
)