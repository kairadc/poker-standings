import pandas as pd

from src import metrics


def _make_df():
    df = pd.DataFrame(
        {
            "session_id": ["s1", "s1", "s2", "s2", "s3"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-05", "2024-01-05", "2024-01-10"]),
            "player": ["Alice", "Bob", "Alice", "Bob", "Alice"],
            "buy_in": [50, 50, 40, 40, 40],
            "cash_out": [70, 30, 60, 60, 20],
        }
    )
    df["net"] = df["cash_out"] - df["buy_in"]
    return df


def test_net_calculation():
    df = _make_df()
    assert list(df["net"]) == [20, -20, 20, 20, -20]


def test_standings_totals():
    df = _make_df()
    standings = metrics.calculate_standings(df)
    alice = standings.loc[standings["player"] == "Alice"].iloc[0]
    bob = standings.loc[standings["player"] == "Bob"].iloc[0]
    assert alice["total_net"] == 20
    assert bob["total_net"] == 0
    assert alice["games_played"] == 3
    assert bob["games_played"] == 2


def test_win_rate_logic():
    df = _make_df()
    standings = metrics.calculate_standings(df)
    alice_rate = standings.loc[standings["player"] == "Alice", "win_rate"].iloc[0]
    bob_rate = standings.loc[standings["player"] == "Bob", "win_rate"].iloc[0]
    assert round(alice_rate, 3) == round(2 / 3, 3)
    assert bob_rate == 0.5


def test_streak_calculation():
    df = _make_df()
    alice_df = df[df["player"] == "Alice"]
    streaks = metrics.compute_streaks(alice_df["net"])
    assert streaks["longest_win"] == 2
    assert streaks["longest_loss"] == 1
    assert streaks["current"]["label"].startswith("Loss")