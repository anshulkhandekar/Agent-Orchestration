"""Level 1 — Vacation Loadout: Select 3 tools for Reveille's beach trip."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_tool_cards
from components.progress import render_progress, render_score_screen
from utils.scoring import (
    LEVEL1_CONFIG,
    LEVEL1_TOOLS,
    LEVEL1_CORRECT,
    evaluate_level1,
    compute_score,
)
from utils.state import complete_level, reset_level_state


def render():
    render_progress(1)

    # ── Mission Brief ──
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(0,212,255,0.04));
            border: 1px solid #22c55e33;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
        ">
            <div style="color:#22c55e;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                🟢 Level 1 — Vacation Loadout
            </div>
            <div style="color:#e2e8f0;font-size:20px;font-weight:700;margin-bottom:8px;">
                Equip Reveille for a European Beach Vacation
            </div>
            <div style="color:#94a3b8;font-size:14px;">
                Your agent needs tools to plan the perfect trip: <strong>warm weather, cheap, near the beach</strong>.
                Select exactly <strong>3 tools</strong> from the loadout below.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Already submitted → show results ──
    if st.session_state.l1_submitted and st.session_state.l1_result:
        result = st.session_state.l1_result

        # Terminal output
        selected_names = [t["name"] for t in LEVEL1_TOOLS if t["id"] in st.session_state.l1_selected]
        correct_names = [t["name"] for t in LEVEL1_TOOLS if t["id"] in LEVEL1_CORRECT]
        logs = [
            {"tag": "system", "text": "Reveille agent initialized."},
            {"tag": "observe", "text": f"Tools equipped: {', '.join(selected_names)}"},
            {"tag": "plan", "text": "Planning European beach vacation..."},
            {"tag": "act", "text": "Searching for destinations with equipped tools..."},
        ]
        missing = LEVEL1_CORRECT - set(st.session_state.l1_selected)
        if missing:
            missing_names = [t["name"] for t in LEVEL1_TOOLS if t["id"] in missing]
            logs.append({"tag": "warning", "text": f"Missing critical tools: {', '.join(missing_names)}"})
        logs.append({"tag": "observe", "text": result["outcome_text"]})
        if result["score"]["total"] == LEVEL1_CONFIG["max_score"]:
            logs.append({"tag": "success", "text": "Mission complete — perfect loadout!"})
        else:
            logs.append({"tag": "checkpoint", "text": "Mission complete with issues. Consider retrying."})

        render_terminal(logs, height=280)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        render_score_screen(
            result["score"]["total"],
            LEVEL1_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=1,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(1)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state.current_level = 2
                st.session_state.page = "level2"
                st.rerun()
        return

    # ── Tool Selection ──
    st.markdown("##### ⚙️ Select exactly 3 tools")
    selected = render_tool_cards(LEVEL1_TOOLS, st.session_state.l1_selected, key_prefix="l1_tool")
    st.session_state.l1_selected = selected

    count = len(selected)
    color = "#22c55e" if count == 3 else "#f59e0b" if count > 0 else "#64748b"
    st.markdown(
        f'<div style="text-align:center;color:{color};font-size:14px;font-weight:600;margin:12px 0;">'
        f'{count}/3 tools selected</div>',
        unsafe_allow_html=True,
    )

    if count == 3:
        if st.button("🚀 Deploy Reveille", use_container_width=True, type="primary"):
            st.session_state.l1_submitted = True
            st.session_state.level_attempts[1] += 1
            attempt = st.session_state.level_attempts[1]

            eval_result = evaluate_level1(st.session_state.l1_selected)
            score_result = compute_score(LEVEL1_CONFIG, eval_result["decisions"], attempt)

            st.session_state.l1_result = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            complete_level(1, score_result["total"], score_result["breakdown"])
            st.rerun()
    elif count > 3:
        st.warning("Too many tools selected! Remove some to get to exactly 3.")
