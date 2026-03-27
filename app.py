"""Agent Reveille Runs the Loop — Main App."""
import streamlit as st
from utils.state import init_state, set_page
from components.leaderboard import render_leaderboard
from utils.supabase import save_score

# ── Page Config ──
st.set_page_config(
    page_title="Agent Reveille Runs the Loop",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Init State ──
init_state()

# ── Global Styles ──
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}

        /* Global font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Dark theme overrides */
        .stApp {
            background-color: #0E1117;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Syne', sans-serif !important;
        }

        /* Button styling */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 8px 20px;
            transition: all 0.2s ease;
            border: 1px solid #1e293b;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.15);
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00d4ff, #a855f7) !important;
            color: white !important;
            border: none !important;
        }

        /* Input styling */
        .stTextInput > div > div > input {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #1e293b;
            border-radius: 10px;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            padding: 12px 16px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #00d4ff;
            box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15);
        }

        /* Divider */
        hr {
            border-color: #1e293b;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 3px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════
def render_landing():
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align: center; max-width: 700px; margin: 0 auto;">
            <div style="font-size: 64px; margin-bottom: 16px;">🤖</div>
            <h1 style="
                font-family: 'Syne', sans-serif;
                font-size: 42px;
                font-weight: 800;
                background: linear-gradient(135deg, #00d4ff, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 4px;
                line-height: 1.2;
            ">Agent Reveille<br>Runs the Loop</h1>
            <div style="
                color: #64748b;
                font-size: 16px;
                font-weight: 500;
                letter-spacing: 3px;
                text-transform: uppercase;
                margin-bottom: 40px;
            ">Aggie Data Science Club</div>
            <div style="
                color: #94a3b8;
                font-size: 15px;
                max-width: 500px;
                margin: 0 auto 32px;
                line-height: 1.6;
            ">
                Guide an AI agent through 4 levels of decision-making.
                Select tools, build workflows, catch errors, and supervise the full loop.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        team_name = st.text_input(
            "Team Name",
            placeholder="Enter your team name...",
            label_visibility="collapsed",
        )
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("🚀 Start Mission", use_container_width=True, type="primary"):
            if team_name.strip():
                st.session_state.team_name = team_name.strip()
                st.session_state.game_started = True
                st.session_state.page = "instructions"
                st.rerun()
            else:
                st.error("Enter a team name to begin!")

    # Level preview cards
    st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    levels_preview = [
        {"num": 1, "name": "Vacation Loadout", "icon": "🟢", "desc": "Select the right tools", "pts": 100},
        {"num": 2, "name": "Route Workflow", "icon": "🟡", "desc": "Order the action pipeline", "pts": 150},
        {"num": 3, "name": "Checkpoint Rescue", "icon": "🔵", "desc": "Catch the agent's drift", "pts": 225},
        {"num": 4, "name": "Mission Control", "icon": "🔴", "desc": "Full loop supervision", "pts": 325},
    ]
    for i, lev in enumerate(levels_preview):
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background: rgba(15, 23, 42, 0.6);
                    border: 1px solid #1e293b;
                    border-radius: 14px;
                    padding: 20px 16px;
                    text-align: center;
                ">
                    <div style="font-size: 28px; margin-bottom: 8px;">{lev['icon']}</div>
                    <div style="color: #e2e8f0; font-size: 14px; font-weight: 700; margin-bottom: 4px;">
                        Level {lev['num']}
                    </div>
                    <div style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">
                        {lev['desc']}
                    </div>
                    <div style="color: #00d4ff; font-size: 12px; font-weight: 600;">
                        {lev['pts']} pts
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════
# INSTRUCTIONS
# ═══════════════════════════════════════════
def render_instructions():
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            max-width: 640px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #1e293b;
            border-radius: 18px;
            padding: 36px;
        ">
            <div style="text-align:center;margin-bottom:24px;">
                <div style="font-size:40px;margin-bottom:8px;">📋</div>
                <h2 style="font-family:'Syne',sans-serif;color:#e2e8f0;font-size:26px;margin:0;">
                    Mission Briefing
                </h2>
                <div style="color:#64748b;font-size:14px;">Team: {st.session_state.team_name}</div>
            </div>

            <div style="margin-bottom:20px;">
                <div style="color:#00d4ff;font-size:13px;font-weight:700;margin-bottom:8px;">🎯 OBJECTIVE</div>
                <div style="color:#94a3b8;font-size:14px;line-height:1.6;">
                    Guide agent Reveille through 4 levels. Make smart decisions to earn the highest score.
                </div>
            </div>

            <div style="margin-bottom:20px;">
                <div style="color:#a855f7;font-size:13px;font-weight:700;margin-bottom:8px;">📊 SCORING</div>
                <div style="color:#94a3b8;font-size:14px;line-height:1.6;">
                    Each level scores on <strong style="color:#e2e8f0;">correctness</strong>,
                    <strong style="color:#e2e8f0;">efficiency</strong>, and
                    <strong style="color:#e2e8f0;">outcome quality</strong>.
                    Total possible: <strong style="color:#00d4ff;">800 points</strong>.
                </div>
            </div>

            <div style="margin-bottom:20px;">
                <div style="color:#f59e0b;font-size:13px;font-weight:700;margin-bottom:8px;">🔄 RETRIES</div>
                <div style="color:#94a3b8;font-size:14px;line-height:1.6;">
                    You can retry any level, but each attempt reduces max score:
                    <strong style="color:#e2e8f0;">100% → 92% → 85% → 75%</strong>
                </div>
            </div>

            <div>
                <div style="color:#22c55e;font-size:13px;font-weight:700;margin-bottom:8px;">💡 TIPS</div>
                <div style="color:#94a3b8;font-size:14px;line-height:1.6;">
                    Think before you click. Read the terminal output carefully. Discuss with your team!
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚡ Begin Level 1", use_container_width=True, type="primary"):
            st.session_state.current_level = 1
            st.session_state.page = "level1"
            st.rerun()


# ═══════════════════════════════════════════
# LEADERBOARD PAGE
# ═══════════════════════════════════════════
def render_leaderboard_page():
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:24px;">
            <div style="font-size:48px;margin-bottom:8px;">🏆</div>
            <h2 style="font-family:'Syne',sans-serif;color:#e2e8f0;font-size:28px;margin:0;">
                Leaderboard
            </h2>
            <div style="color:#64748b;font-size:14px;">Best scores across all teams</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show current team summary
    if st.session_state.team_name:
        total = st.session_state.total_score
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(0,212,255,0.06), rgba(168,85,247,0.04));
                border: 1px solid #00d4ff33;
                border-radius: 14px;
                padding: 20px;
                text-align: center;
                margin-bottom: 24px;
            ">
                <div style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:2px;">Your Total Score</div>
                <div style="color:#00d4ff;font-size:48px;font-weight:800;font-family:'Syne',sans-serif;">{total}</div>
                <div style="color:#94a3b8;font-size:14px;">out of 800</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_leaderboard()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Back to Start", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with col2:
        # Allow replaying from level 1
        if st.session_state.game_started:
            if st.button("🔄 Play Again", use_container_width=True, type="primary"):
                # Reset all level states but keep team name
                for lev in [1, 2, 3, 4]:
                    from utils.state import reset_level_state
                    reset_level_state(lev)
                    st.session_state.level_completed[lev] = False
                    st.session_state.level_attempts[lev] = 0
                    st.session_state.level_scores[lev] = None
                st.session_state.current_level = 1
                st.session_state.page = "level1"
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
