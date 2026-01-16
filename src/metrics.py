import pandas as pd

from . import schema

def _win_rate_from_series(net_series: pd.Series) -> float:
    """Compute win rate for a series of net values."""
    wins = (net_series > 0).sum()
    losses = (net_series < 0).sum()
    total = wins + losses
    return wins / total if total else 0.0


def calculate_standings(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate standings by player."""
    columns = [
        "player",
        "games_played",
        "total_net",
        "win_rate",
        "avg_net",
        "best_session_net",
        "worst_session_net",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=columns)

    grouped = df.groupby("player", dropna=False)
    standings = grouped.agg(
        games_played=("session_id", "count"),
        total_net=("net", "sum"),
        avg_net=("net", "mean"),
        best_session_net=("net", "max"),
        worst_session_net=("net", "min"),
    ).reset_index()

    win_rates = grouped["net"].apply(_win_rate_from_series).reset_index(name="win_rate")
    standings = standings.merge(win_rates, on="player", how="left")
    standings = standings[columns].sort_values("total_net", ascending=False).reset_index(drop=True)
    return standings


def summary_kpis(df: pd.DataFrame) -> dict:
    """High-level KPIs for the overview page."""
    if df is None or df.empty:
        return {
            "total_sessions": 0,
            "total_net": 0.0,
            "top_winner": None,
            "top_winner_net": 0.0,
            "biggest_loser": None,
            "biggest_loser_net": 0.0,
        }

    standings = calculate_standings(df)
    top_winner_row = standings.iloc[0] if not standings.empty else None
    loser_row = standings.iloc[standings["total_net"].idxmin()] if not standings.empty else None

    return {
        "total_sessions": int(df["session_id"].nunique()),
        "total_net": float(df["net"].sum()),
        "top_winner": None if top_winner_row is None else top_winner_row["player"],
        "top_winner_net": 0.0 if top_winner_row is None else float(top_winner_row["total_net"]),
        "biggest_loser": None if loser_row is None else loser_row["player"],
        "biggest_loser_net": 0.0 if loser_row is None else float(loser_row["total_net"]),
    }


def compute_streaks(net_series: pd.Series) -> dict:
    """
    Calculate current streak, longest win streak, and longest loss streak.
    Win = net>0, loss = net<0, neutral = net==0 resets streak.
    """
    longest_win = 0
    longest_loss = 0
    current = 0

    for value in net_series:
        if value > 0:
            current = current + 1 if current > 0 else 1
            longest_win = max(longest_win, current)
        elif value < 0:
            current = current - 1 if current < 0 else -1
            longest_loss = min(longest_loss, current)
        else:
            current = 0

    if current > 0:
        current_label = f"Win {current}"
        current_type = "win"
    elif current < 0:
        current_label = f"Loss {abs(current)}"
        current_type = "loss"
    else:
        current_label = "Neutral"
        current_type = "neutral"

    return {
        "current": {"type": current_type, "count": abs(current), "label": current_label},
        "longest_win": int(longest_win),
        "longest_loss": int(abs(longest_loss)),
    }


def player_profile(df: pd.DataFrame, player: str) -> dict:
    """Compute per-player insights."""
    player_df = df[df["player"] == player].sort_values("date")
    if player_df.empty:
        return {
            "games_played": 0,
            "win_rate": 0.0,
            "avg_net": 0.0,
            "median_net": 0.0,
            "best_session_net": 0.0,
            "worst_session_net": 0.0,
            "streaks": compute_streaks(pd.Series(dtype=float)),
            "recent": pd.DataFrame(),
        }

    wins = (player_df["net"] > 0).sum()
    losses = (player_df["net"] < 0).sum()
    total_decisions = wins + losses
    win_rate = wins / total_decisions if total_decisions else 0.0

    best_idx = player_df["net"].idxmax()
    worst_idx = player_df["net"].idxmin()

    return {
        "games_played": int(player_df.shape[0]),
        "win_rate": float(win_rate),
        "avg_net": float(player_df["net"].mean()),
        "median_net": float(player_df["net"].median()),
        "best_session_net": float(player_df.loc[best_idx, "net"]),
        "worst_session_net": float(player_df.loc[worst_idx, "net"]),
        "streaks": compute_streaks(player_df["net"]),
        "recent": player_df.sort_values("date", ascending=False).head(10),
    }


def cumulative_net(df: pd.DataFrame) -> pd.DataFrame:
    """Add a cumulative_net column grouped by player for plotting."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "player", "cumulative_net"])
    temp = df.sort_values("date").copy()
    temp["cumulative_net"] = temp.groupby("player")["net"].cumsum()
    return temp[["date", "player", "cumulative_net", "net"]]


def compute_biggest_swing_session(df: pd.DataFrame) -> dict:
    """
    Find the single player-session with largest absolute net.
    Returns dict with player, net, date, group, session_id, reason(optional).
    """
    norm = schema.normalize_results_df(df)
    required = {"player", "date", "net"}
    if norm.empty or not required.issubset(norm.columns):
        return {"player": None, "net": None, "date": None, "group": None, "session_id": None, "reason": "No data"}

    norm["abs_net"] = norm["net"].abs()
    # Tie-break: abs desc, date desc, player asc
    norm = norm.sort_values(
        by=["abs_net", "date", "player"], ascending=[False, False, True], ignore_index=True
    )
    top = norm.iloc[0]
    return {
        "player": top.get("player"),
        "net": float(top.get("net")),
        "date": top.get("date"),
        "group": top.get("group") if "group" in norm.columns else None,
        "session_id": top.get("session_id") if "session_id" in norm.columns else None,
        "reason": None,
    }
