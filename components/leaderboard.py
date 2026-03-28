"""Leaderboard display component."""
import streamlit as st
from utils.supabase import get_leaderboard


def render_leaderboard():
    """Render the full leaderboard table."""
    entries = get_leaderboard()
    status = st.session_state.get("leaderboard_status", {})
    status_mode = status.get("mode", "memory")
    status_message = status.get("message", "")

    if status_message and status_mode != "supabase":
        st.caption("Live ranking service is temporarily unavailable. Showing recent results.")

    if not entries:
        st.markdown("### Standings")
        st.caption("No scores yet — be the first!")
        return

    top_entries = entries[:3]
    top_cols = st.columns(3)
    for idx, (entry, col) in enumerate(zip(top_entries, top_cols), start=1):
        accent = ["#f2b84b", "#94a3b8", "#d4a574"][idx - 1]
        with col:
            st.markdown(
                f"""
                <div style="
                    background:linear-gradient(180deg, rgba(15,23,42,0.94), rgba(8,12,19,0.96));
                    border:1px solid rgba(34,50,74,0.96);
                    border-top:3px solid {accent};
                    border-radius:18px;
                    padding:18px 18px 16px 18px;
                    min-height:148px;">
                    <div style="color:{accent}; font-size:12px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:10px;">
                        Rank {idx}
                    </div>
                    <div style="color:#f8fafc; font-size:1.3rem; font-weight:700; margin-bottom:8px;">
                        {entry['team']}
                    </div>
                    <div style="color:#7dd3fc; font-size:2rem; font-family:'Syne',sans-serif; font-weight:800; margin-bottom:8px;">
                        {entry['total']}
                    </div>
                    <div style="color:#94a3b8; font-size:0.95rem;">L1 {entry.get('L1', 0)} · L2 {entry.get('L2', 0)} · L3 {entry.get('L3', 0)} · L4 {entry.get('L4', 0)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")
    st.markdown(
        """
        <div style="
            display:grid;
            grid-template-columns: 0.8fr 2.3fr repeat(4, 0.8fr) 1fr;
            gap:10px;
            padding:12px 14px;
            margin-bottom:10px;
            color:#7c93b7;
            font-size:12px;
            font-weight:700;
            letter-spacing:0.12em;
            text-transform:uppercase;
            background:rgba(15,23,42,0.6);
            border:1px solid rgba(34,50,74,0.96);
            border-radius:14px;">
            <div>Rank</div>
            <div>Team</div>
            <div>L1</div>
            <div>L2</div>
            <div>L3</div>
            <div>L4</div>
            <div>Total</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, entry in enumerate(entries):
        rank = i + 1
        is_current = entry["team"] == st.session_state.get("team_name", "")
        accent = "#4f8cff" if is_current else "#22324a"
        label = {1: "1", 2: "2", 3: "3"}.get(rank, str(rank))
        st.markdown(
            f"""
            <div style="
                display:grid;
                grid-template-columns: 0.8fr 2.3fr repeat(4, 0.8fr) 1fr;
                gap:10px;
                align-items:center;
                padding:16px 14px;
                margin-bottom:8px;
                background:rgba(10,14,20,0.82);
                border:1px solid {accent};
                border-radius:16px;
                box-shadow:{'0 12px 32px rgba(79,140,255,0.12)' if is_current else 'none'};">
                <div style="color:#94a3b8;font-weight:700;">{label}</div>
                <div>
                    <div style="color:#f8fafc;font-weight:700;">{entry['team']}</div>
                    <div style="color:#64748b;font-size:12px;">{'Your team' if is_current else 'Workshop team'}</div>
                </div>
                <div style="color:#cbd5e1;">{entry.get('L1', 0)}</div>
                <div style="color:#cbd5e1;">{entry.get('L2', 0)}</div>
                <div style="color:#cbd5e1;">{entry.get('L3', 0)}</div>
                <div style="color:#cbd5e1;">{entry.get('L4', 0)}</div>
                <div style="color:#7dd3fc;font-weight:800;font-size:1.05rem;">{entry['total']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
