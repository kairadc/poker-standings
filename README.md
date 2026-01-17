# Friends Poker Standings (Streamlit)

Track poker results for your friend group. Data lives in Google Sheets so everyone can add rows from their phone. The app reads the sheet, calculates standings and streaks, and is ready to deploy on Streamlit Community Cloud for free. Sessions can be tagged by **group** (e.g., Home Crew, Work Friends) to separate different circles.

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
2) Add headers in row 1: `session_id,date,player,buy_in,cash_out,venue,group,season,notes`. If you have older data with `game_type`, the app will treat `game_type` as `group`.
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

## Settlement page
- New **Session Settlement** page computes a minimal set of transfers for a single session.
- Select a session to view per-player nets and who pays whom.
- Requires columns: `session_id`, `player`, `net` (or `buy_in` and `cash_out`).
- Copy the suggested transfers for easy sharing.

## Optional pixel font
To enable the arcade pixel font for headings, place `PressStart2P-Regular.ttf` into `assets/fonts/`. The CSS already includes a `@font-face` rule pointing to that path; once the file is present, headings will use the pixel font (class `pixel`).

## Banned players (fun/social)
- A tab named `banned_players` in the Google Sheet (case-sensitive) drives the 🚫 Banned page.
- Required headers: `player_name` (required), `reason` (optional, defaults to "Failure to pay out"), `ban_type` (optional: Permanent|Temporary, defaults to Temporary).
- The page is display-only and does not affect standings or calculations.
- Example row:
  ```
  player_name,reason,ban_type
  Alice,Did not settle last session,Temporary
  ```

## Migration: game_type -> group
- The canonical column is now `group` (friend group name).
- Existing data with `game_type` will be read as `group` automatically.
- If neither `group` nor `game_type` exists, the app will show a clear error.
- To migrate CSVs on disk, run:
  ```bash
  python scripts/migrate_game_type_to_group.py your_file.csv
  ```
  A `.bak` copy is kept alongside the original.
