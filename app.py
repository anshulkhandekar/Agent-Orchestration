"""Agent Reveille Runs the Loop — Main App."""
import streamlit as st
import streamlit.components.v1 as components
from utils.state import init_state
from components.leaderboard import render_leaderboard
from utils.supabase import get_existing_team_names


LEVEL_PAGES = {
    1: "level1",
    2: "level2",
    3: "level3",
    4: "level4",
    5: "level5",
    6: "level6",
}

LEVEL_PREVIEWS = [
    {"level": 1, "name": "Vacation Loadout", "desc": "Select the right tools", "pts": 100, "color": "#3ccf6e"},
    {"level": 2, "name": "Route Workflow", "desc": "Order the action pipeline", "pts": 150, "color": "#f2b84b"},
    {"level": 3, "name": "Checkpoint Rescue", "desc": "Catch the agent's drift", "pts": 225, "color": "#4f8cff"},
    {"level": 4, "name": "Mission Control", "desc": "Full loop supervision", "pts": 325, "color": "#ff6b5f"},
    {"level": 5, "name": "Route the Agent Team", "desc": "Delegate specialists in the right order", "pts": 450, "color": "#8b5cf6"},
    {"level": 6, "name": "Mission Control Swarm", "desc": "Resolve conflicts and finalize smartly", "pts": 600, "color": "#14b8a6"},
]


# ── Page Config ──
st.set_page_config(
    page_title="Agent Reveille Runs the Loop",
    page_icon="🤖🐶",
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
        .stApp {
            background:
                radial-gradient(circle at top, rgba(79, 140, 255, 0.12), transparent 28%),
                radial-gradient(circle at 80% 0%, rgba(60, 207, 110, 0.08), transparent 20%),
                #0E1117;
        }
        h1, h2, h3, h4, h5, h6 { font-family: 'Syne', sans-serif !important; }
        .stButton > button {
            border-radius: 12px; font-weight: 600;
            font-family: 'Inter', sans-serif;
            padding: 10px 20px; transition: all 0.2s ease;
            border: 1px solid #22324a;
            background: rgba(15, 23, 42, 0.9);
            color: #e2e8f0;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(79, 140, 255, 0.5);
            box-shadow: 0 10px 24px rgba(79, 140, 255, 0.16);
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f8cff 0%, #22c1c3 100%);
            border: 1px solid rgba(128, 210, 255, 0.35);
            color: #f8fafc;
        }
        .stTextInput > div > div > input {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #22324a; border-radius: 12px;
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
        .landing-shell {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(8, 12, 19, 0.92));
            border: 1px solid rgba(34, 50, 74, 0.95);
            border-radius: 28px;
            padding: 34px 36px 30px 36px;
            box-shadow: 0 24px 70px rgba(2, 8, 23, 0.35);
        }
        .landing-kicker {
            color: #7dd3fc;
            font-size: 0.95rem;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 14px;
        }
        .landing-title {
            color: #f8fafc;
            font-family: 'Syne', sans-serif;
            font-size: clamp(3rem, 5vw, 4.4rem);
            line-height: 0.98;
            font-weight: 800;
            margin: 0 0 18px 0;
        }
        .landing-copy {
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.75;
            max-width: 760px;
            margin-bottom: 24px;
        }
        .landing-preview {
            background: rgba(10, 14, 20, 0.78);
            border: 1px solid #22324a;
            border-radius: 18px;
            padding: 20px 18px 18px 18px;
            min-height: 168px;
        }
        .landing-preview:hover {
            border-color: rgba(79, 140, 255, 0.45);
            box-shadow: 0 16px 34px rgba(8, 15, 30, 0.22);
        }
        .landing-preview-top {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
            color: #f8fafc;
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 1.7rem;
        }
        .landing-preview-dot {
            width: 14px;
            height: 14px;
            border-radius: 999px;
            flex-shrink: 0;
            box-shadow: 0 0 24px currentColor;
        }
        .landing-preview-name {
            color: #f8fafc;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .landing-preview-desc {
            color: #94a3b8;
            font-size: 0.98rem;
            line-height: 1.5;
            margin-bottom: 16px;
        }
        .landing-preview-points {
            color: #7dd3fc;
            font-weight: 700;
            font-size: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_route():
    """Keep page state consistent across reruns and manual navigation."""
    page = st.session_state.get("page", "landing")
    team_name = (st.session_state.get("team_name") or "").strip()
    game_started = bool(st.session_state.get("game_started"))
    protected_pages = {"instructions", "leaderboard", *LEVEL_PAGES.values()}

    if page in protected_pages and not (game_started and team_name):
        st.session_state["page"] = "landing"
        st.session_state["current_level"] = 0
        st.session_state["game_started"] = False
        return

    if page in LEVEL_PAGES.values():
        level = int(page[-1])
        st.session_state["current_level"] = level


def render_agentic_workflow_animation():
    """Render lightweight animated workflow nodes for the landing page hero."""
    html = """
    <div style="
        position:relative;
        background:linear-gradient(135deg, rgba(8,12,20,0.96), rgba(15,23,42,0.85));
        border:1px solid rgba(34,50,74,0.95);
        border-radius:22px;
        padding:20px 22px 18px 22px;
        overflow:hidden;
        min-height:210px;
        font-family:'Inter',sans-serif;">
        
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:22px;">
            <div style="color:#e2e8f0;font-size:14px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">
                Agentic Workflow
            </div>
            <div style="color:#64748b;font-size:12px;">Observe → Plan → Act → Verify</div>
        </div>

        <div style="position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;z-index:2;">
            <div class="wf-node wf-node-1" style="--wf-color:#3ccf6e;">
                <span>Observe</span>
                <small>Collect constraints</small>
            </div>
            <div class="wf-node wf-node-2" style="--wf-color:#f2b84b;">
                <span>Plan</span>
                <small>Sequence actions</small>
            </div>
            <div class="wf-node wf-node-3" style="--wf-color:#4f8cff;">
                <span>Act</span>
                <small>Run the workflow</small>
            </div>
            <div class="wf-node wf-node-4" style="--wf-color:#ff6b5f;">
                <span>Verify</span>
                <small>Catch drift and score</small>
            </div>
        </div>

        <div class="wf-line"></div>
    </div>

    <style>
        .wf-node{
            position:relative;
            background:rgba(15,23,42,0.74);
            border:1px solid rgba(34,50,74,0.95);
            border-radius:16px;
            min-height:112px;
            padding:18px 16px;
            display:flex;
            flex-direction:column;
            justify-content:flex-end;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
            transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }

        .wf-node::before{
            content:"";
            position:absolute;
            top:16px;
            left:16px;
            width:12px;
            height:12px;
            border-radius:999px;
            background:var(--wf-color);
            box-shadow:0 0 14px var(--wf-color);
            opacity:0.8;
        }

        .wf-node span{
            color:#f8fafc;
            font-size:18px;
            font-weight:700;
            margin-bottom:7px;
        }

        .wf-node small{
            color:#94a3b8;
            font-size:12px;
            line-height:1.5;
        }

        .wf-line{
            position:absolute;
            top:78px;
            left:11%;
            right:11%;
            height:2px;
            background:linear-gradient(
                90deg,
                rgba(60,207,110,0.18),
                rgba(242,184,75,0.18),
                rgba(79,140,255,0.22),
                rgba(255,107,95,0.22)
            );
            z-index:1;
        }

        .wf-node-1 { animation:wf-highlight-1 8s infinite; }
        .wf-node-2 { animation:wf-highlight-2 8s infinite; }
        .wf-node-3 { animation:wf-highlight-3 8s infinite; }
        .wf-node-4 { animation:wf-highlight-4 8s infinite; }

        @keyframes wf-highlight-1 {
            0%, 20% {
                border-color: color-mix(in srgb, var(--wf-color) 65%, white 10%);
                box-shadow:
                    0 0 0 1px color-mix(in srgb, var(--wf-color) 40%, transparent),
                    0 0 22px color-mix(in srgb, var(--wf-color) 24%, transparent),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                transform: translateY(-1px);
            }
            25%, 100% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
        }

        @keyframes wf-highlight-2 {
            0%, 24% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
            25%, 45% {
                border-color: color-mix(in srgb, var(--wf-color) 65%, white 10%);
                box-shadow:
                    0 0 0 1px color-mix(in srgb, var(--wf-color) 40%, transparent),
                    0 0 22px color-mix(in srgb, var(--wf-color) 24%, transparent),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                transform: translateY(-1px);
            }
            50%, 100% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
        }

        @keyframes wf-highlight-3 {
            0%, 49% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
            50%, 70% {
                border-color: color-mix(in srgb, var(--wf-color) 65%, white 10%);
                box-shadow:
                    0 0 0 1px color-mix(in srgb, var(--wf-color) 40%, transparent),
                    0 0 22px color-mix(in srgb, var(--wf-color) 24%, transparent),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                transform: translateY(-1px);
            }
            75%, 100% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
        }

        @keyframes wf-highlight-4 {
            0%, 74% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
            75%, 95% {
                border-color: color-mix(in srgb, var(--wf-color) 65%, white 10%);
                box-shadow:
                    0 0 0 1px color-mix(in srgb, var(--wf-color) 40%, transparent),
                    0 0 22px color-mix(in srgb, var(--wf-color) 24%, transparent),
                    inset 0 1px 0 rgba(255,255,255,0.05);
                transform: translateY(-1px);
            }
            100% {
                border-color: rgba(34,50,74,0.95);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
                transform: translateY(0);
            }
        }
    </style>
    """
    components.html(html, height=230, scrolling=False)


# ═══════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════
def render_landing():
    _, center, _ = st.columns([0.6, 2.8, 0.6])
    with center:
        st.markdown(
            """
            <div class="landing-shell">
                <div class="landing-kicker">Aggie Data Science Club</div>
                <div class="landing-title">Agent Reveille Runs the Loop</div>
                <div class="landing-copy">
                    Guide Texas A&M's favorite AI agent through six escalating levels of decision-making.
                    Select tools, supervise execution, orchestrate specialist agents, and coordinate the full loop all the way up to swarm control.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        render_agentic_workflow_animation()
        st.markdown("")
        team_name = st.text_input(
            "Team Name",
            placeholder="Enter your team name...",
            label_visibility="collapsed",
        )
        normalized_team_name = team_name.strip()
        existing_team_names = get_existing_team_names() if normalized_team_name else set()
        duplicate_name = normalized_team_name.lower() in existing_team_names
        if duplicate_name:
            st.error("That team name has already been claimed. Choose a different team name.")
        if st.button("Start Mission", use_container_width=True, type="primary"):
            if not normalized_team_name:
                st.error("Enter a team name to begin!")
            elif duplicate_name:
                st.error("That team name has already been claimed. Choose a different team name.")
            else:
                st.session_state["team_name"] = normalized_team_name
                st.session_state["game_started"] = True
                st.session_state["page"] = "instructions"
                st.session_state["current_level"] = 0
                st.rerun()

    st.markdown("")
    for row_start in range(0, len(LEVEL_PREVIEWS), 3):
        cols = st.columns(3)
        row_previews = LEVEL_PREVIEWS[row_start : row_start + 3]
        for i, preview in enumerate(row_previews):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="landing-preview">
                        <div class="landing-preview-top">
                            <span class="landing-preview-dot" style="color:{preview['color']}; background:{preview['color']};"></span>
                            <span>Level {preview['level']}</span>
                        </div>
                        <div class="landing-preview-name">{preview['name']}</div>
                        <div class="landing-preview-desc">{preview['desc']}</div>
                        <div class="landing-preview-points">{preview['pts']} pts</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════
# INSTRUCTIONS
# ═══════════════════════════════════════════
def render_instructions():
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.markdown("## 📋 Mission Briefing")
        st.caption(f"Team: {st.session_state.get('team_name', '')}")
        st.markdown("---")

        st.markdown("**🎯 OBJECTIVE**")
        st.markdown(
            "Guide agent Reveille through 6 levels. "
            "Make smart decisions to earn the highest score."
        )

        st.markdown("**📊 SCORING**")
        st.markdown(
            "Each level scores on **correctness**, **efficiency**, and "
            "**outcome quality**. Total possible: **1850 points**."
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
            st.session_state["current_level"] = 1
            st.session_state["page"] = "level1"
            st.rerun()


# ═══════════════════════════════════════════
# LEADERBOARD PAGE
# ═══════════════════════════════════════════
def render_leaderboard_page():
    st.markdown("## Leaderboard")
    st.caption("Live team standings across all six levels")

    if st.session_state.get("team_name"):
        total = st.session_state.get("total_score", 0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Total Score", total)
        with col2:
            st.metric("Max Possible", 1850)
        with col3:
            pct = int((total / 1850) * 100)
            st.metric("Percentage", f"{pct}%")

    st.markdown("---")
    render_leaderboard()

    # ── Level navigation ──
    if st.session_state.get("game_started"):
        st.markdown("")
        st.markdown("**Jump to a Level:**")
        for row_start in range(0, len(LEVEL_PREVIEWS), 3):
            row_previews = LEVEL_PREVIEWS[row_start : row_start + 3]
            nav_cols = st.columns(3)
            for preview, col in zip(row_previews, nav_cols):
                with col:
                    lev = preview["level"]
                    max_pts = preview["pts"]
                    completed = st.session_state.get("level_completed", {}).get(lev, False)
                    best = st.session_state.get("level_best", {}).get(lev, 0)
                    st.markdown(
                        f"""
                        <div class="landing-preview" style="min-height:132px;">
                            <div class="landing-preview-top" style="font-size:1.2rem; margin-bottom:12px;">
                                <span class="landing-preview-dot" style="color:{preview['color']}; background:{preview['color']};"></span>
                                <span>Level {lev}</span>
                            </div>
                            <div class="landing-preview-desc" style="margin-bottom:8px;">{preview['name']}</div>
                            <div class="landing-preview-points">{f'{best} / {max_pts}' if completed else f'Max {max_pts}'}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Go to Level {lev}", key=f"lb_nav_{lev}", use_container_width=True):
                        st.session_state["current_level"] = lev
                        st.session_state["page"] = f"level{lev}"
                        st.rerun()


# ═══════════════════════════════════════════
# TOP NAV — Leaderboard always accessible
# ═══════════════════════════════════════════
if st.session_state.get("game_started") and st.session_state.get("page") != "leaderboard":
    nav_col1, nav_col2 = st.columns([6, 1])
    with nav_col2:
        if st.button("Leaderboard", use_container_width=True):
            st.session_state["page"] = "leaderboard"
            st.rerun()


# ═══════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════
normalize_route()
page = st.session_state.get("page", "landing")

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
elif page == "level5":
    from levels.level5 import render
    render()
elif page == "level6":
    from levels.level6 import render
    render()
elif page == "leaderboard":
    render_leaderboard_page()
else:
    render_landing()
