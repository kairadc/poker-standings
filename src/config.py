from pathlib import Path

CACHE_TTL_SECONDS = 60

REQUIRED_COLUMNS = ["session_id", "date", "player", "buy_in", "cash_out"]
OPTIONAL_COLUMNS = ["venue", "game_type", "season", "notes"]
DERIVED_COLUMNS = ["net"]
NUMERIC_COLUMNS = ["buy_in", "cash_out"]

DATE_FORMAT = "%Y-%m-%d"

DEFAULT_WORKSHEET_NAME = "sessions"
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

ROOT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CSV_PATH = ROOT_DIR / "data" / "sessions_sample.csv"