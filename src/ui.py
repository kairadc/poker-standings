import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, List

from . import sheets


def show_mode_banner(dq) -> None:
    """Notify whether we are in demo or Sheets mode."""
    if dq.source != "sheets":
        st.info("Running in demo mode (sample data). Add secrets to use your Google Sheet.")
    else:
        st.success("Connected to Google Sheets. Use refresh if you\'ve added new rows.")


def render_refresh_button() -> None:
    """Provide a refresh control that clears caches."""
    if st.button("Refresh data", help="Clears cached reads and reloads the sheet"):
        sheets.clear_cache()
        st.cache_data.clear()
        st.experimental_rerun()


def render_global_filters(df: pd.DataFrame) -> Dict:
    """Sidebar filters shared by all pages."""
    with st.sidebar:
        st.header("Filters")
        if df is None or df.empty:
            st.info("No data available yet.")
            return {}

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        default_range = (min_date, max_date)
        date_range = st.date_input(
            "Date range", value=default_range, min_value=min_date, max_value=max_date, key="filter_date"
        )

        players = sorted(df["player"].dropna().unique())
        selected_players = st.multiselect("Players", options=players, default=players, key="filter_players")

        filters: Dict[str, List] = {"date_range": date_range, "players": selected_players}

        for col in ["venue", "game_type", "season"]:
            if col in df.columns:
                options = sorted(df[col].dropna().unique())
                if options:
                    filters[col] = st.multiselect(col.replace("_", " ").title(), options=options, key=f"filter_{col}")

        return filters


def render_kpi_row(kpis: Dict) -> None:
    """Display top-level KPIs."""
    cols = st.columns(4)
    cols[0].metric("Total sessions", kpis.get("total_sessions", 0))
    cols[1].metric("Total net", f"{kpis.get('total_net', 0.0):.2f}")
    cols[2].metric(
        "Top winner",
        kpis.get("top_winner") or "-",
        delta=None if kpis.get("top_winner") is None else f"{kpis.get('top_winner_net', 0.0):.2f}",
    )
    cols[3].metric(
        "Biggest loser",
        kpis.get("biggest_loser") or "-",
        delta=None if kpis.get("biggest_loser") is None else f"{kpis.get('biggest_loser_net', 0.0):.2f}",
    )


def render_standings_table(standings: pd.DataFrame) -> None:
    """Show standings in a sortable table."""
    if standings is None or standings.empty:
        st.info("No standings to display yet.")
        return
    st.dataframe(
        standings,
        use_container_width=True,
        column_config={
            "win_rate": st.column_config.ProgressColumn("Win rate", format="%.0f%%", min_value=0, max_value=1),
            "total_net": st.column_config.NumberColumn(format="%.2f"),
            "avg_net": st.column_config.NumberColumn(format="%.2f"),
            "best_session_net": st.column_config.NumberColumn(format="%.2f"),
            "worst_session_net": st.column_config.NumberColumn(format="%.2f"),
        },
    )


def plot_cumulative_net(df: pd.DataFrame) -> None:
    """Plot cumulative net over time by player."""
    if df is None or df.empty:
        st.info("Add data to see cumulative trends.")
        return
    plot_df = df.sort_values("date").copy()
    plot_df["cumulative_net"] = plot_df.groupby("player")["net"].cumsum()
    fig = px.line(
        plot_df,
        x="date",
        y="cumulative_net",
        color="player",
        markers=True,
        title="Cumulative net over time",
        labels={"date": "Date", "cumulative_net": "Cumulative net"},
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_total_net_bar(standings: pd.DataFrame) -> None:
    """Bar chart of total net by player."""
    if standings is None or standings.empty:
        return
    fig = px.bar(
        standings,
        x="player",
        y="total_net",
        title="Total net by player",
        labels={"player": "Player", "total_net": "Total net"},
        color="total_net",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_player_cumulative(player_df: pd.DataFrame, player: str) -> None:
    """Plot cumulative net for a single player."""
    if player_df.empty:
        st.info("No sessions for this player.")
        return
    temp = player_df.sort_values("date").copy()
    temp["cumulative_net"] = temp["net"].cumsum()
    fig = px.line(
        temp,
        x="date",
        y="cumulative_net",
        title=f"{player}: cumulative net over time",
        markers=True,
        labels={"date": "Date", "cumulative_net": "Cumulative net"},
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_player_sessions(player_df: pd.DataFrame, player: str) -> None:
    """Bar chart of per-session net for a single player."""
    if player_df.empty:
        return
    temp = player_df.sort_values("date")
    fig = px.bar(
        temp,
        x="date",
        y="net",
        title=f"{player}: net per session",
        labels={"date": "Date", "net": "Net"},
        color="net",
        color_continuous_scale=["#d9534f", "#5cb85c"],
    )
    st.plotly_chart(fig, use_container_width=True)


def render_streaks(streaks: Dict) -> None:
    """Show streak metrics."""
    cols = st.columns(3)
    cols[0].metric("Current streak", streaks["current"]["label"])
    cols[1].metric("Longest win streak", streaks["longest_win"])
    cols[2].metric("Longest loss streak", streaks["longest_loss"])


def render_data_quality(dq) -> None:
    """Display validation warnings."""
    if dq.issues:
        st.error("Issues: " + " | ".join(dq.issues))
    if dq.warnings:
        friendly = [f"{k.replace('_', ' ')}: {v}" for k, v in dq.warnings.items()]
        st.warning("Data quality warnings: " + " | ".join(friendly))