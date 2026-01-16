import pandas as pd

from src import data


def test_normalize_uses_group_when_present():
    df = pd.DataFrame(
        {
            "session_id": ["s1"],
            "date": ["2024-01-01"],
            "player": ["Alice"],
            "buy_in": [10],
            "cash_out": [20],
            "group": ["Home Crew"],
        }
    )
    norm, dq = data.normalize_dataframe(df)
    assert "group" in norm.columns
    assert norm.loc[0, "group"] == "Home Crew"
    assert "game_type" not in norm.columns
    assert not dq.issues


def test_normalize_legacy_game_type_mapped_to_group():
    df = pd.DataFrame(
        {
            "session_id": ["s1"],
            "date": ["2024-01-01"],
            "player": ["Bob"],
            "buy_in": [15],
            "cash_out": [5],
            "game_type": ["Work Friends"],
        }
    )
    norm, dq = data.normalize_dataframe(df)
    assert "group" in norm.columns
    assert norm.loc[0, "group"] == "Work Friends"
    assert not dq.issues


def test_normalize_errors_when_missing_group_and_game_type():
    df = pd.DataFrame(
        {
            "session_id": ["s1"],
            "date": ["2024-01-01"],
            "player": ["Bob"],
            "buy_in": [15],
            "cash_out": [5],
        }
    )
    norm, dq = data.normalize_dataframe(df)
    assert norm.empty
    assert any("group" in issue for issue in dq.issues)