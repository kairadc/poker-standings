import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, List

from . import sheets


NEON = {
    "body_bg": "#040714",
    "body_gradient": "radial-gradient(circle at 20% 20%, rgba(79,70,229,0.12), transparent 35%), radial-gradient(circle at 80% 0%, rgba(16,185,129,0.12), transparent 30%), #040714",
    "text": "#e5e7eb",
    "axis": "#94a3b8",
    "card_bg": "linear-gradient(135deg, #0b1224 0%, #0a0f1f 100%)",
    "card_border": "rgba(34, 211, 238, 0.35)",
    "card_text": "#e2e8f0",
    "accent_pos": "#22d3ee",
    "accent_neg": "#f472b6",
    "neutral": "#94a3b8",
    "shadow": "0 10px 30px rgba(0,0,0,0.35), 0 0 18px rgba(139, 92, 246, 0.15)",
}


def apply_centered_layout(max_width: int = 1200) -> None:
    """Apply the arcade leaderboard theme and centered layout."""
    c = NEON
    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"] {{
            background: {c['body_bg']};
            background-image: {c['body_gradient']};
            color: {c['text']};
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        [data-testid="stSidebar"] {{
            background: #0b1224;
            color: {c['text']};
        }}
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stMarkdownContainer"] {{
            color: {c['text']} !important;
        }}
        a {{
            color: {c['accent_pos']} !important;
        }}
        [data-testid="stTable"], [data-testid="stDataFrame"] {{
            color: {c['text']} !important;
            background: transparent;
        }}
        .stTextInput>div>div input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] *, .stMultiSelect div[data-baseweb="select"] * {{
            color: {c['text']} !important;
        }}
        .stTextInput>div>div input::placeholder,
        .stTextArea textarea::placeholder {{
            color: {c['neutral']} !important;
            opacity: 0.8;
        }}
        .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"], .stDateInput > div > div {{
            background: {c['card_bg']};
            border: 2px solid {c['card_border']};
            border-radius: 12px;
            color: {c['text']};
            box-shadow: {c['shadow']};
        }}
        .stSelectbox div[data-baseweb="select"]:hover, .stMultiSelect div[data-baseweb="select"]:hover, .stDateInput > div > div:hover {{
            border-color: {c['accent_pos']};
            box-shadow: 0 0 12px rgba(34,211,238,0.35);
        }}
        .stSelectbox svg, .stMultiSelect svg {{
            fill: {c['text']};
        }}
        .stSelectbox div[role="listbox"], .stMultiSelect div[role="listbox"] {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
            color: {c['text']};
            box-shadow: {c['shadow']};
        }}
        /* BaseWeb portal (dropdown menu) */
        [data-baseweb=\"popover\"] {{
            z-index: 9999;
        }}
        [data-baseweb=\"popover\"] [role=\"listbox\"] {{
            background: {c['card_bg']} !important;
            border: 1px solid {c['card_border']} !important;
            color: {c['text']} !important;
            box-shadow: {c['shadow']} !important;
        }}
        .stMultiSelect [data-baseweb="tag"] {{
            background: rgba(34,211,238,0.15);
            color: {c['card_text']};
            border: 1px solid {c['card_border']};
            border-radius: 10px;
            box-shadow: none;
        }}
        .stMultiSelect span[aria-hidden="true"] {{
            color: {c['card_text']};
        }}
        .stDateInput input {{
            color: {c['text']} !important;
        }}
        .stDateInput input::placeholder {{
            color: {c['neutral']} !important;
            opacity: 0.8;
        }}
        .stDateInput button svg {{
            stroke: {c['text']};
        }}
        /* Slider */
        .stSlider > div[data-baseweb="slider"] > div {{
            color: {c['text']};
        }}
        .stSlider [data-baseweb="slider"] [role="slider"] {{
            background: {c['accent_pos']};
            border: 2px solid {c['card_border']};
            box-shadow: 0 0 12px rgba(34,211,238,0.35);
        }}
        .stSlider [data-baseweb="slider"] div[role="presentation"] > div {{
            background: {c['card_border']};
        }}
        [data-testid="block-container"] {{
            max-width: {max_width}px;
            margin: 0 auto;
            padding: 2rem 1.5rem 3rem 1.5rem;
            background: transparent;
            color: {c['text']};
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem;
        }}
        /* Dim first and last nav items (root app + data setup) */
        [data-testid="stSidebarNav"] ul li:first-child button,
        [data-testid="stSidebarNav"] ul li:last-child button {{
            opacity: 0.35 !important;
            filter: grayscale(0.6);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 12px 0 20px;
        }}
        @media (max-width: 1100px) {{
            .metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (max-width: 640px) {{
            .metric-grid {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}
        }}
        .metric-card {{
            background: {c['card_bg']};
            border: 2px solid {c['card_border']};
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: {c['shadow']};
        }}
        .metric-label {{
            color: {c['neutral']};
            font-size: 0.95rem;
            letter-spacing: 0.02em;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {c['card_text']};
            line-height: 1.2;
        }}
        .metric-delta {{
            font-size: 0.95rem;
            margin-top: 6px;
        }}
        .arcade-card {{
            background: {c['card_bg']};
            border: 2px solid {c['card_border']};
            border-radius: 18px;
            padding: 18px;
            box-shadow: {c['shadow']};
            margin-bottom: 14px;
        }}
        .arcade-btn button {{
            border-radius: 999px;
            border: 2px solid {c['accent_pos']};
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(6, 182, 212, 0.05));
            color: {c['text']};
            box-shadow: 0 0 12px rgba(34,211,238,0.35);
            transition: all 0.2s ease;
        }}
        .arcade-btn button:hover {{
            box-shadow: 0 0 18px rgba(34,211,238,0.55);
            transform: translateY(-1px);
        }}
        .stButton > button {{
            border-radius: 999px;
            border: 2px solid {c['accent_pos']};
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(6, 182, 212, 0.05));
            color: {c['text']};
            box-shadow: 0 0 12px rgba(34,211,238,0.35);
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            box-shadow: 0 0 18px rgba(34,211,238,0.55);
            transform: translateY(-1px);
        }}
        .arcade-section-title {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin: 12px 0 8px;
        }}
        .arcade-chip {{
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(34, 211, 238, 0.12);
            border: 1px solid rgba(34,211,238,0.35);
            color: {c['text']};
            font-size: 0.85rem;
        }}
        .leaderboard-table {{
            width: 100%;
            border-collapse: collapse;
            color: {c['text']};
        }}
        .leaderboard-table th, .leaderboard-table td {{
            padding: 10px 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }}
        .rank-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 12px;
            font-weight: 800;
            color: #0b1224;
        }}
        .rank-1 {{ background: linear-gradient(135deg, #facc15, #f97316); box-shadow: 0 0 12px rgba(250,204,21,0.5); }}
        .rank-2 {{ background: linear-gradient(135deg, #e5e7eb, #cbd5e1); box-shadow: 0 0 12px rgba(203,213,225,0.4); }}
        .rank-3 {{ background: linear-gradient(135deg, #f59e0b, #d97706); box-shadow: 0 0 12px rgba(245,158,11,0.4); }}
        .rank-other {{ background: linear-gradient(135deg, #1e293b, #0f172a); color: {c['text']}; }}
        .player-cell {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .player-avatar {{
            width: 18px;
            height: 18px;
            border-radius: 6px;
            background: linear-gradient(135deg, #22d3ee, #6366f1);
            box-shadow: 0 0 8px rgba(99,102,241,0.6);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _style_fig(fig):
    """Apply shared styling to all charts for a cohesive arcade look."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=NEON["text"], family="serif"),
        legend_title_text="",
        margin=dict(t=40, b=10, l=10, r=10),
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)", zeroline=False, color=NEON["axis"])
    fig.update_xaxes(showgrid=False, zeroline=False, color=NEON["axis"])
    return fig


def section_header(title: str, chip: str | None = None) -> None:
    """Render a styled section header with optional chip."""
    chip_html = f"<span class='arcade-chip'>{chip}</span>" if chip else ""
    st.markdown(
        f"<div class='arcade-section-title'><h3>{title}</h3>{chip_html}</div>",
        unsafe_allow_html=True,
    )


def show_mode_banner(dq) -> None:
    """Notify whether we are in demo or Sheets mode."""
    if dq.source != "sheets":
        st.info("Running in demo mode (sample data). Add secrets to use your Google Sheet.")
    else:
        st.success("Connected to Google Sheets. Use refresh if you've added new rows.")


def render_refresh_button() -> None:
    """Provide a refresh control that clears caches."""
    with st.container():
        if st.button("Refresh data", help="Clears cached reads and reloads the sheet", type="primary"):
            sheets.clear_cache()
            st.cache_data.clear()
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

        for col in ["venue", "group", "season"]:
            if col in df.columns:
                options = sorted(df[col].dropna().unique())
                if options:
                    display_label = "Group" if col == "group" else col.replace("_", " ").title()
                    filters[col] = st.multiselect(display_label, options=options, key=f"filter_{col}")

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
    c = NEON
    cards = []
    for item in items:
        label = item.get("label", "")
        value = item.get("value", "")
        delta = item.get("delta")
        delta_color = c["accent_pos"]
        if isinstance(delta, str) and delta.strip().startswith("-"):
            delta_color = c["accent_neg"]
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
    """Show standings in a stylized leaderboard table with rank badges."""
    if standings is None or standings.empty:
        st.info("No standings to display yet.")
        return

    rows_html = []
    for idx, row in standings.reset_index(drop=True).iterrows():
        rank = idx + 1
        if rank == 1:
            badge_class, badge_text = "rank-1", "🥇"
        elif rank == 2:
            badge_class, badge_text = "rank-2", "🥈"
        elif rank == 3:
            badge_class, badge_text = "rank-3", "🥉"
        else:
            badge_class, badge_text = "rank-other", rank
        net = row.get("total_net", 0)
        net_color = NEON["accent_pos"] if net > 0 else NEON["accent_neg"] if net < 0 else NEON["neutral"]
        win_rate = row.get("win_rate", 0) * 100
        rows_html.append(
            f"<tr>"
            f"<td><span class='rank-badge {badge_class}'>{badge_text}</span></td>"
            f"<td><div class='player-cell'><span class='player-avatar'></span><strong>{row['player']}</strong></div></td>"
            f"<td style='color:{net_color}'>{net:.2f}</td>"
            f"<td>{int(row.get('games_played',0))}</td>"
            f"<td>{win_rate:.0f}%</td>"
            f"</tr>"
        )

    table_html = (
        "<table class='leaderboard-table'>"
        "<thead><tr><th>Rank</th><th>Player</th><th>Net</th><th>Games</th><th>Win %</th></tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody></table>"
    )
    st.markdown(f"<div class='arcade-card'>{table_html}</div>", unsafe_allow_html=True)


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
    st.plotly_chart(fig, width="stretch")


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
        color_continuous_scale=[(0, NEON["accent_neg"]), (0.5, NEON["neutral"]), (1, NEON["accent_pos"])],
        color_continuous_midpoint=0,
    )
    fig = _style_fig(fig)
    fig.update_layout(legend=None)
    fig.update_xaxes(title=None)
    st.plotly_chart(fig, width="stretch")


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
    st.plotly_chart(fig, width="stretch")


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
        color_continuous_scale=[(0, NEON["accent_neg"]), (1, NEON["accent_pos"])],
    )
    fig = _style_fig(fig)
    fig.update_layout(legend=None)
    fig.update_xaxes(title=None)
    st.plotly_chart(fig, width="stretch")


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
