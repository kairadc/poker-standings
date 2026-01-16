import argparse
import shutil
from pathlib import Path

import pandas as pd


def migrate_csv(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy(path, backup)

    df = pd.read_csv(path)
    if "group" not in df.columns and "game_type" in df.columns:
        df = df.rename(columns={"game_type": "group"})
    if "group" not in df.columns:
        raise ValueError("Neither 'group' nor legacy 'game_type' found. Add a group column and rerun.")

    df.to_csv(path, index=False)
    print(f"Migrated {path} (backup at {backup})")


def main():
    parser = argparse.ArgumentParser(description="Rename game_type to group in a CSV (keeps .bak backup)")
    parser.add_argument("csv", type=Path, help="Path to sessions CSV")
    args = parser.parse_args()
    migrate_csv(args.csv)


if __name__ == "__main__":
    main()