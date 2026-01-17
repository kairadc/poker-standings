import streamlit as st

from src import banned, ui

ui.apply_centered_layout()

st.title("?? Banned")
st.markdown(
    """
    <div class="arcade-card">
      <h2 style="margin:0;">?? BANNED FROM THE TABLE ??</h2>
      <p style="margin:4px 0 0 0; opacity:0.9;">Outstanding debts result in exile.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

raw_df = banned.load_banned_players()
clean_df, warnings = banned.validate_banned_players_df(raw_df)

if warnings:
    with st.expander("Data warnings"):
        for w in warnings:
            st.warning(w)

if clean_df.empty:
    st.info("Everyone has paid. Order has been restored. ???")
    st.stop()

# Sort: Permanent first, then alphabetical
clean_df["ban_order"] = clean_df["ban_type"].apply(lambda x: 0 if x == "Permanent" else 1)
clean_df = clean_df.sort_values(["ban_order", "player_name"], ascending=[True, True])

for _, row in clean_df.iterrows():
    ban_type = row.get("ban_type", "Temporary")
    badge_color = "#f43f5e" if ban_type == "Permanent" else "#22d3ee"
    mugshot = row.get("mugshot_path")
    with st.container():
        left, right = st.columns([1, 3]) if mugshot else (None, None)
        if mugshot and left is not None:
            with left:
                st.image(mugshot, use_column_width=True, caption=row["player_name"], clamp=True)
        target = right if mugshot and right is not None else st
        target.markdown(
            f"""
            <div class="arcade-card" style="border-color:{badge_color};">
              <div style="display:flex; align-items:center; gap:10px;">
                <h3 style=\"margin:0; font-size:1.4rem;\">{row['player_name']}</h3>
                <span style=\"padding:4px 10px; border-radius:999px; border:1px solid {badge_color}; color:{badge_color}; font-weight:700;\">{ban_type}</span>
              </div>
              <p style=\"margin:6px 0 0 0; opacity:0.9;\">Reason: {row.get('reason','Failure to pay out')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )