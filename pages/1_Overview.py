import streamlit as st

from src import data, metrics, ui


st.title("Overview")

df, dq = data.load_dataset()
ui.show_mode_banner(dq)
ui.render_refresh_button()

filters = ui.render_global_filters(df)
filtered_df = data.apply_filters(df, filters)

if filtered_df is None or filtered_df.empty:
    st.warning("No data after applying filters. Try widening your selections.")
    st.stop()

kpis = metrics.summary_kpis(filtered_df)
ui.render_kpi_row(kpis)

st.subheader("Standings")
standings = metrics.calculate_standings(filtered_df)
ui.render_standings_table(standings)

st.subheader("Trends")
ui.plot_cumulative_net(filtered_df)
ui.plot_total_net_bar(standings)