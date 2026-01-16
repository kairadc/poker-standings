import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, List

from . import sheets


def apply_centered_layout(max_width: int = 1100) -> None:
    """Constrain the main content width and center it for a cleaner card-like layout."""
    st.markdown(
        f"""
        <style>
        [data-testid="block-container"] {{
            max-width: {max_width}px;
            margin: 0 auto;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin: 12px 0 20px;
        }}
        .metric-card {{
            background: white;
            border: 1px solid #e6e9ef;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 6px 18px rgba(12, 18, 38, 0.06);
        }}
        .metric-label {{
            color: #52606d;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #0b1b32;
            line-height: 1.2;
        }}
        .metric-delta {{
            font-size: 0.95rem;
            margin-top: 4px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _style_fig(fig):
    """Apply shared styling to all charts for a cohesive look."""
    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e5e7eb", family="serif"),
        legend_title_text="",
        margin=dict(t=40, b=10, l=10, r=10),
    )
    fig.update_yaxes(showgrid=False, zeroline=False, color="#cbd5e1")
    fig.update_xaxes(showgrid=False, zeroline=False, color="#cbd5e1")
    return fig


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
        # st.rerun is the supported refresh call in newer Streamlit versions.
        st.rerun()


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
    """Display top-level KPIs as cards."""
    items = [
        {"label": "Total sessions", "value": kpis.get("total_sessions", 0)},
        {"label": "Total net", "value": f"{kpis.get('total_net', 0.0):.2f}"},
        {
            "label": "Top winner",
            "value": kpis.get("top_winner") or "-",
            "delta": None if kpis.get("top_winner") is None else f"{kpis.get('top_winner_net', 0.0):.2f}",
        },
        {
            "label": "Biggest loser",
            "value": kpis.get("biggest_loser") or "-",
            "delta": None if kpis.get("biggest_loser") is None else f"{kpis.get('biggest_loser_net', 0.0):.2f}",
        },
    ]
    render_metric_cards(items)


def render_metric_cards(items: List[Dict]) -> None:
    """Render metrics in a grid of cards."""
    cards = []
    for item in items:
        label = item.get("label", "")
        value = item.get("value", "")
        delta = item.get("delta")
        delta_color = "#0f9d58"
        if isinstance(delta, str) and delta.strip().startswith("-"):
            delta_color = "#d9534f"
        delta_html = f"<div class='metric-delta' style='color:{delta_color}'>{delta}</div>" if delta else ""
        cards.append(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>{label}</div>"
            f"<div class='metric-value'>{value}</div>"
            f"{delta_html}"
            f"</div>"
        )
    st.markdown(f"<div class='metric-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def render_standings_table(standings: pd.DataFrame) -> None:
    """Show standings in a sortable table."""
    if standings is None or standings.empty:
        st.info("No standings to display yet.")
        return
    try:
        st.dataframe(
            standings,
            width="stretch",
            column_config={
                "win_rate": st.column_config.ProgressColumn("Win rate", format="%.0f%%", min_value=0, max_value=1),
                "total_net": st.column_config.NumberColumn(format="%.2f"),
                "avg_net": st.column_config.NumberColumn(format="%.2f"),
                "best_session_net": st.column_config.NumberColumn(format="%.2f"),
                "worst_session_net": st.column_config.NumberColumn(format="%.2f"),
            },
        )
    except TypeError:
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
        title="Cumulative net",
        labels={"date": "", "cumulative_net": ""},
    )
    fig = _style_fig(fig)
    fig.update_xaxes(title=None)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def plot_total_net_bar(standings: pd.DataFrame) -> None:
    """Bar chart of total net by player."""
    if standings is None or standings.empty:
        return
    fig = px.bar(
        standings,
        x="player",
        y="total_net",
        title="Total net",
        labels={"player": "", "total_net": ""},
        color="total_net",
        color_continuous_scale=[(0, "#d9534f"), (0.5, "#f1f5f9"), (1, "#16a34a")],
        color_continuous_midpoint=0,
    )
    fig = _style_fig(fig)
    fig.update_layout(legend=None)
    fig.update_xaxes(title=None)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
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
        title=f"{player} · cumulative net",
        markers=True,
        labels={"date": "", "cumulative_net": ""},
    )
    fig = _style_fig(fig)
    fig.update_layout(legend=None)
    fig.update_xaxes(title=None)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
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
        title=f"{player} · per session",
        labels={"date": "", "net": ""},
        color="net",
        color_continuous_scale=["#d9534f", "#16a34a"],
    )
    fig = _style_fig(fig)
    fig.update_layout(legend=None)
    fig.update_xaxes(title=None)
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
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
