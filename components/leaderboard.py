"""Leaderboard display component."""
import streamlit as st
from utils.supabase import get_leaderboard


def render_leaderboard():
    """Render the full leaderboard table."""
    entries = get_leaderboard()
    status = st.session_state.get("leaderboard_status", {})
    status_mode = status.get("mode", "memory")
    status_message = status.get("message", "")

    if status_message:
        badge = "Supabase" if status_mode == "supabase" else "Local fallback"
        st.caption(f"{badge}: {status_message}")

    if not entries:
        st.markdown("### 🏆")
        st.caption("No scores yet — be the first!")
        return

    # Build markdown table
    header = "| Rank | Team | L1 | L2 | L3 | L4 | Total |"
    sep = "|------|------|----|----|----|----|-------|"
    rows = []
    for i, entry in enumerate(entries):
        rank = i + 1
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        team = entry["team"]
        is_current = team == st.session_state.get("team_name", "")
        if is_current:
            team = f"**{team}**"
        rows.append(
            f"| {medal} | {team} | {entry.get('L1', 0)} | {entry.get('L2', 0)} "
            f"| {entry.get('L3', 0)} | {entry.get('L4', 0)} | **{entry['total']}** |"
        )

    st.markdown("\n".join([header, sep] + rows))
