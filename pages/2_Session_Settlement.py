import streamlit as st
import pandas as pd

from src import data, settlement, ui

ui.apply_centered_layout()

st.title("Session Settlement")

# Load data
full_df, dq = data.load_dataset()
ui.show_mode_banner(dq)
ui.render_refresh_button()

if full_df is None or full_df.empty:
    st.warning("No data available. Add sessions first.")
    st.stop()

# Build session selector label: date - session_id
full_df = full_df.sort_values("date")
session_options = (
    full_df.groupby(["session_id", "date"], dropna=False)
    .size()
    .reset_index()[["session_id", "date"]]
)
session_options["label"] = session_options.apply(
    lambda r: f"{r['date'].date()} - {r['session_id']}", axis=1
)

selected_label = st.selectbox(
    "Select session",
    options=session_options["label"],
    index=len(session_options) - 1 if not session_options.empty else 0,
)
selected_session = session_options.loc[session_options["label"] == selected_label, "session_id"].iloc[0]

session_df = full_df[full_df["session_id"] == selected_session].copy()
if session_df.empty:
    st.warning("No rows found for this session.")
    st.stop()

# Per-player table
cols_to_show = [col for col in ["player", "buy_in", "cash_out", "net", "group", "venue"] if col in session_df.columns]
per_player = session_df[cols_to_show].sort_values("net", ascending=False)
st.subheader("Per-player results")
st.dataframe(per_player, width="stretch")

# Build net mapping
net_by_player = session_df.groupby("player")["net"].sum().to_dict()

# Validate sum near zero
imbalance = round(sum(net_by_player.values()), 6)
if abs(imbalance) > 1e-4:
    st.error(f"Net amounts do not balance to zero. Imbalance: {imbalance:.4f}. Check the session data.")
    st.stop()

transfers = settlement.compute_settlement(net_by_player, tol=1e-6)

st.subheader("Transfers")
if not transfers:
    st.info("No transfers needed.")
else:
    transfers_df = pd.DataFrame(transfers, columns=["payer", "payee", "amount"])
    st.dataframe(transfers_df, width="stretch")

    text_block = settlement.format_transfers_text(transfers)
    st.code(text_block)

    if st.button("Copy transfers"):
        st.session_state["_copy_text"] = text_block
        st.toast("Copied!", icon="Copied")
        safe_text = text_block.replace("`", "\\`")
        st.components.v1.html(
            f"""
            <script>
            navigator.clipboard.writeText(`{safe_text}`);
            </script>
            """,
            height=0,
        )