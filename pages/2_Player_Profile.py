import streamlit as st

from src import data, metrics, ui

ui.apply_centered_layout()

st.title("Player Profile")

df, dq = data.load_dataset()
ui.show_mode_banner(dq)
ui.render_refresh_button()

filters = ui.render_global_filters(df)
filtered_df = data.apply_filters(df, filters)

if filtered_df is None or filtered_df.empty:
    st.warning("No data after filters. Select more players or dates.")
    st.stop()

players = sorted(filtered_df["player"].unique())
selected_player = st.selectbox("Player", players)

player_profile = metrics.player_profile(filtered_df, selected_player)

ui.render_metric_cards(
    [
        {"label": "Games played", "value": player_profile["games_played"]},
        {"label": "Win rate", "value": f"{player_profile['win_rate']*100:.1f}%"},
        {"label": "Avg net", "value": f"{player_profile['avg_net']:.2f}"},
        {"label": "Median net", "value": f"{player_profile['median_net']:.2f}"},
        {"label": "Best session", "value": f"{player_profile['best_session_net']:.2f}"},
        {"label": "Worst session", "value": f"{player_profile['worst_session_net']:.2f}"},
    ]
)

st.subheader("Streaks (win = net>0, loss = net<0, neutral resets)")
ui.render_streaks(player_profile["streaks"])

player_df = filtered_df[filtered_df["player"] == selected_player]

st.subheader("Charts")
ui.plot_player_cumulative(player_df, selected_player)
ui.plot_player_sessions(player_df, selected_player)

st.subheader("Recent sessions")
try:
    st.dataframe(player_profile["recent"], width="stretch")
except TypeError:
    st.dataframe(player_profile["recent"], use_container_width=True)
