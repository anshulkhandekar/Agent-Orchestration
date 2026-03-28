"""Agent Reveille Runs the Loop — Main App."""
import streamlit as st
from utils.state import init_state, reset_level_state
from components.leaderboard import render_leaderboard


# ── Page Config ──
st.set_page_config(
    page_title="Agent Reveille Runs the Loop",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Init State ──
init_state()

# ── Global CSS (style tags work reliably across Streamlit versions) ──
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background-color: #0E1117; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Syne', sans-serif !important; }
        .stButton > button {
            border-radius: 10px; font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 8px 20px; transition: all 0.2s ease;
            border: 1px solid #1e293b;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.15);
        }
        .stTextInput > div > div > input {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #1e293b; border-radius: 10px;
            color: #e2e8f0; font-family: 'Inter', sans-serif;
            padding: 12px 16px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #00d4ff;
            box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15);
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════
def render_landing():
    st.markdown("")
    st.markdown("")
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("# 🤖 Agent Reveille Runs the Loop")
        st.caption("AGGIE DATA SCIENCE CLUB")
        st.markdown(
            "Guide an AI agent through **4 levels** of decision-making. "
            "Select tools, build workflows, catch errors, and supervise the full loop."
        )
        st.markdown("---")
        team_name = st.text_input(
            "Team Name",
            placeholder="Enter your team name...",
            label_visibility="collapsed",
        )
        if st.button("🚀 Start Mission", use_container_width=True, type="primary"):
            if team_name.strip():
                st.session_state.team_name = team_name.strip()
                st.session_state.game_started = True
                st.session_state.page = "instructions"
                st.rerun()
            else:
                st.error("Enter a team name to begin!")

    st.markdown("")
    cols = st.columns(4)
    previews = [
        ("🟢", 1, "Vacation Loadout", "Select the right tools", 100),
        ("🟡", 2, "Route Workflow", "Order the action pipeline", 150),
        ("🔵", 3, "Checkpoint Rescue", "Catch the agent's drift", 225),
        ("🔴", 4, "Mission Control", "Full loop supervision", 325),
    ]
    for i, (icon, num, name, desc, pts) in enumerate(previews):
        with cols[i]:
            c = st.container(border=True)
            with c:
                st.markdown(f"### {icon} Level {num}")
                st.markdown(f"**{name}**")
                st.caption(desc)
                st.markdown(f":blue[{pts} pts]")


# ═══════════════════════════════════════════
# INSTRUCTIONS
# ═══════════════════════════════════════════
def render_instructions():
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.markdown("## 📋 Mission Briefing")
        st.caption(f"Team: {st.session_state.team_name}")
        st.markdown("---")

        st.markdown("**🎯 OBJECTIVE**")
        st.markdown(
            "Guide agent Reveille through 4 levels. "
            "Make smart decisions to earn the highest score."
        )

        st.markdown("**📊 SCORING**")
        st.markdown(
            "Each level scores on **correctness**, **efficiency**, and "
            "**outcome quality**. Total possible: **800 points**."
        )

        st.markdown("**🔄 RETRIES**")
        st.markdown(
            "You can retry any level, but each attempt reduces max score: "
            "**100% → 92% → 85% → 75%**"
        )

        st.markdown("**💡 TIPS**")
        st.markdown(
            "Think before you click. Read the terminal output carefully. "
            "Discuss with your team!"
        )

        st.markdown("---")
        if st.button("⚡ Begin Level 1", use_container_width=True, type="primary"):
            st.session_state.current_level = 1
            st.session_state.page = "level1"
            st.rerun()


# ═══════════════════════════════════════════
# LEADERBOARD PAGE
# ═══════════════════════════════════════════
def render_leaderboard_page():
    st.markdown("## 🏆 Leaderboard")
    st.caption("Best scores across all teams")

    if st.session_state.team_name:
        total = st.session_state.total_score
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Total Score", total)
        with col2:
            st.metric("Max Possible", 800)
        with col3:
            pct = int((total / 800) * 100)
            st.metric("Percentage", f"{pct}%")

    st.markdown("---")
    render_leaderboard()

    # ── Level navigation ──
    if st.session_state.game_started:
        st.markdown("")
        st.markdown("**Jump to a Level:**")
        level_meta = [
            ("🟢", 1, 100),
            ("🟡", 2, 150),
            ("🔵", 3, 225),
            ("🔴", 4, 325),
        ]
        nav_cols = st.columns(4)
        for (icon, lev, max_pts), col in zip(level_meta, nav_cols):
            with col:
                completed = st.session_state.level_completed.get(lev, False)
                best = st.session_state.level_best.get(lev, 0)
                c = st.container(border=True)
                with c:
                    st.markdown(f"**{icon} Level {lev}**")
                    if completed:
                        st.markdown(f":green[{best} / {max_pts} ✓]")
                    else:
                        st.caption(f"Max: {max_pts} pts")
                if st.button(f"Go to Level {lev}", key=f"lb_nav_{lev}", use_container_width=True):
                    st.session_state.current_level = lev
                    st.session_state.page = f"level{lev}"
                    st.rerun()


# ═══════════════════════════════════════════
# TOP NAV — Leaderboard always accessible
# ═══════════════════════════════════════════
if st.session_state.game_started and st.session_state.page != "leaderboard":
    nav_col1, nav_col2 = st.columns([6, 1])
    with nav_col2:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()


# ═══════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════
page = st.session_state.page

if page == "landing":
    render_landing()
elif page == "instructions":
    render_instructions()
elif page == "level1":
    from levels.level1 import render
    render()
elif page == "level2":
    from levels.level2 import render
    render()
elif page == "level3":
    from levels.level3 import render
    render()
elif page == "level4":
    from levels.level4 import render
    render()
elif page == "leaderboard":
    render_leaderboard_page()
else:
    render_landing()
