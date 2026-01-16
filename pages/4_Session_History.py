import streamlit as st

from src import data, ui

ui.apply_centered_layout()

st.title("Session History")

df, dq = data.load_dataset()
ui.show_mode_banner(dq)
ui.render_refresh_button()

filters = ui.render_global_filters(df)
filtered_df = data.apply_filters(df, filters)

if filtered_df is None or filtered_df.empty:
    st.warning("No data after filters. Try expanding your date range or players.")
    st.stop()

st.download_button(
    "Download filtered CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="poker_sessions_filtered.csv",
    mime="text/csv",
)

try:
    st.dataframe(filtered_df.sort_values("date", ascending=False), width="stretch")
except TypeError:
    st.dataframe(filtered_df.sort_values("date", ascending=False), width="stretch")

st.subheader("Data quality")
ui.render_data_quality(dq)
