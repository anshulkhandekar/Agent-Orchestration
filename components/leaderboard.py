"""Leaderboard display component."""
import streamlit as st
from utils.supabase import get_leaderboard, save_score


def render_leaderboard():
    """Render the full leaderboard table."""
    entries = get_leaderboard()

    if not entries:
        st.markdown(
            """
            <div style="text-align:center; padding: 40px; color: #64748b;">
                <div style="font-size: 48px; margin-bottom: 12px;">🏆</div>
                <div style="font-size: 16px;">No scores yet — be the first!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    header_html = """
    <div style="
        display: grid;
        grid-template-columns: 50px 1fr 70px 70px 70px 70px 80px;
        gap: 8px;
        padding: 12px 16px;
        background: rgba(0, 212, 255, 0.06);
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    ">
        <div>Rank</div>
        <div>Team</div>
        <div style="text-align:center;">L1</div>
        <div style="text-align:center;">L2</div>
        <div style="text-align:center;">L3</div>
        <div style="text-align:center;">L4</div>
        <div style="text-align:center;">Total</div>
    </div>
    """

    rows_html = ""
    for i, entry in enumerate(entries):
        rank = i + 1
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        is_current = entry["team"] == st.session_state.get("team_name", "")
        highlight = "border: 1px solid #00d4ff; background: rgba(0, 212, 255, 0.05);" if is_current else "border: 1px solid #1e293b; background: rgba(15, 23, 42, 0.4);"

        rows_html += f"""
        <div style="
            display: grid;
            grid-template-columns: 50px 1fr 70px 70px 70px 70px 80px;
            gap: 8px;
            padding: 12px 16px;
            {highlight}
            border-radius: 10px;
            margin-bottom: 4px;
            font-size: 14px;
            color: #e2e8f0;
            align-items: center;
        ">
            <div style="font-size: 18px;">{medal}</div>
            <div style="font-weight: 600; color: {'#00d4ff' if is_current else '#e2e8f0'};">{entry['team']}</div>
            <div style="text-align:center;">{entry.get('L1', 0)}</div>
            <div style="text-align:center;">{entry.get('L2', 0)}</div>
            <div style="text-align:center;">{entry.get('L3', 0)}</div>
            <div style="text-align:center;">{entry.get('L4', 0)}</div>
            <div style="text-align:center; font-weight: 800; color: #00d4ff; font-size: 16px;">{entry['total']}</div>
        </div>
        """

    st.markdown(header_html + rows_html, unsafe_allow_html=True)
