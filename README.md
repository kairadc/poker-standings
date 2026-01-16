# Friends Poker Standings (Streamlit)

Track poker results for your friend group. Data lives in Google Sheets so everyone can add rows from their phone. The app reads the sheet, calculates standings and streaks, and is ready to deploy on Streamlit Community Cloud for free.

## What the app does
- Reads a Google Sheet (`sessions` worksheet) as the single source of truth.
- Shows standings, player insights, streaks, charts, and session history.
- Optional demo mode with a bundled CSV sample if secrets are missing.

## Local setup (Windows/macOS)
1) Install Python 3.11+
2) Create and activate a virtual environment
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3) Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4) Run the app
   ```bash
   streamlit run app.py
   ```

## Google Sheets setup
1) Create a Google Sheet and add a worksheet named `sessions`.
2) Add headers in row 1: `session_id,date,player,buy_in,cash_out,venue,game_type,season,notes`.
3) Each row = one player in one session. `net` is computed by the app.

## Google Cloud service account setup
1) In Google Cloud Console, create a project.
2) Enable the **Google Sheets API**.
3) Create a **service account**, then create a **JSON key** and download it.
4) Copy the service account email (ends with `iam.gserviceaccount.com`) and **share your Sheet** with it as Viewer (or Editor).
5) Paste the JSON into Streamlit secrets (see below).

## Add Streamlit secrets (local)
Create `.streamlit/secrets.toml` (do not commit):
```toml
[sheets]
spreadsheet_id = "YOUR_SHEET_ID"
worksheet_name = "sessions"
service_account = { ...paste full JSON here... }
# or: service_account_json = """{...}"""
```
Find your `spreadsheet_id` in the Sheet URL between `/d/` and `/edit`.

## Deploy to Streamlit Community Cloud
1) Push this repo to GitHub.
2) Go to https://share.streamlit.io, create a new app, and pick your repo/branch.
3) In the app settings, add the same secrets under **Secrets**.
4) Deploy. Share the public URL with friends.

## Troubleshooting
- **Permission denied**: Share the Sheet with the service account email.
- **Worksheet not found**: Ensure `worksheet_name` matches the tab name (default `sessions`).
- **Secrets parsing errors**: Validate JSON; try the inline table shown in `secrets.example.toml`.
- **Missing columns**: Headers must match required names; see Data Setup Help page.
- **`streamlit` or `pip` not found**: Activate your venv or reinstall Python 3.11+.
- **Empty dashboard**: Add rows to the sheet or use the bundled sample CSV.

## Dev mode
If no secrets are provided, the app shows "Running in demo mode" and loads `data/sessions_sample.csv`.