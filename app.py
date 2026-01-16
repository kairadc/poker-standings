import streamlit as st

st.set_page_config(
    page_title="Poker Standings",
    layout="wide"
)

st.title("Friends Poker Standings")
st.caption("Track group results with Google Sheets as the single source of truth.")

# Load data once; downstream pages will reuse cached data.
df, dq = data.load_dataset()
ui.show_mode_banner(dq)
ui.render_refresh_button()

st.write(
    "Use the sidebar to switch between Overview, Player Profile, Session History, and Data Setup Help. "
    "New rows can be added directly in Google Sheets from your phone."
)

if dq.issues:
    with st.expander("Data load notes"):
        for issue in dq.issues:
            st.warning(issue)

if df.empty:
    st.info("No data yet. Visit Data Setup Help to connect your Google Sheet or start with the sample template.")
else:
    st.success("Data loaded. Jump to Overview for KPIs, charts, and standings.")
