"""Level 5 — Route the Agent Team: delegate specialist sub-agents."""
import streamlit as st

from components.cards import render_ordering_interface
from components.progress import render_level_header, render_progress, render_score_screen
from components.terminal import render_terminal
from utils.scoring import (
    LEVEL5_AGENTS,
    LEVEL5_CONFIG,
    LEVEL5_CORRECT_ORDER,
    compute_score,
    evaluate_level5,
)
from utils.state import complete_level, persist_score_once, reset_level_state


_DETAILS = [
    {
        "icon": "🧠",
        "label": "Your Goal",
        "text": "Choose exactly 4 specialist sub-agents and route them in the smartest delegation order.",
    },
    {
        "icon": "🧩",
        "label": "Key Tension",
        "text": "Too few agents misses signal. Too many overlapping specialists create coordination drag.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Selection 180 pts · Order 150 pts · Efficiency 70 pts · Output Quality 50 pts = 450 max.",
    },
    {
        "icon": "⚠️",
        "label": "Critical Rule",
        "text": "Final Synthesizer is strongest at the end, after the discovery specialists have already done their work.",
    },
]

_HINT = (
    "Delegate exploration first, reconcile cost before final assembly, and avoid pulling in extra helpers unless they clearly reduce risk."
)


def render():
    render_progress(5)

    render_level_header(
        level=5,
        color="#8b5cf6",
        icon="🛰️",
        title="Route the Agent Team — Delegate the Specialist Crew",
        description=(
            "Reveille now has access to a small team of specialist helper agents. "
            "Your job is no longer just supervising one agent. You are the orchestrator: decide which specialists join the mission, "
            "what order they work in, and when synthesis happens. Strong orchestration creates a better Aggie Weekend package with less coordination waste."
        ),
        details=_DETAILS,
        hint=_HINT,
        height=405,
    )

    st.markdown("")

    if st.session_state.get("l5_submitted") and st.session_state.get("l5_result"):
        result = st.session_state.get("l5_result")
        ordered_names = [
            next(agent["name"] for agent in LEVEL5_AGENTS if agent["id"] == agent_id)
            for agent_id in st.session_state.get("l5_order", [])
        ]
        optimal_names = [
            next(agent["name"] for agent in LEVEL5_AGENTS if agent["id"] == agent_id)
            for agent_id in LEVEL5_CORRECT_ORDER
        ]

        logs = [
            {"tag": "system", "text": "Agent team orchestrator initialized."},
            {"tag": "plan", "text": f"Delegation chain: {' → '.join(ordered_names)}"},
        ]
        for idx, name in enumerate(ordered_names, start=1):
            logs.append({"tag": "act", "text": f"Hand-off {idx}: {name}"})
        if st.session_state.get("l5_order", []) == LEVEL5_CORRECT_ORDER:
            logs.append({"tag": "success", "text": "Perfect orchestration chain — discovery first, synthesis last."})
        else:
            logs.append({"tag": "warning", "text": f"Reference flow: {' → '.join(optimal_names)}"})
        logs.append({"tag": "observe", "text": result["outcome_text"]})

        render_terminal(logs, height=340)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL5_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=5,
            categories=LEVEL5_CONFIG["categories"],
        )

        persist_score_once(5)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(5)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state["current_level"] = 6
                st.session_state["page"] = "level6"
                st.rerun()
        return

    selected, ordered = render_ordering_interface(
        LEVEL5_AGENTS,
        st.session_state.get("l5_selected", []),
        st.session_state.get("l5_order", []),
        key_prefix="l5",
        expected_count=4,
        selection_title="#### Step 1: Select exactly 4 specialist agents",
        reorder_title="#### Step 2: Reorder the hand-off chain (click to move to end)",
    )
    st.session_state["l5_selected"] = selected
    st.session_state["l5_order"] = ordered

    count = len(selected)
    if count == 4:
        st.success("4/4 specialists selected")
    elif count > 0:
        st.warning(f"{count}/4 specialists selected — choose exactly 4")
    else:
        st.caption("0/4 specialists selected")

    if count == 4 and len(ordered) == 4:
        if st.button("Deploy Agent Team", use_container_width=True, type="primary"):
            level_attempts = st.session_state.get("level_attempts", {})
            level_attempts[5] = level_attempts.get(5, 0) + 1
            st.session_state["level_attempts"] = level_attempts
            attempt = level_attempts[5]

            eval_result = evaluate_level5(selected, ordered)
            score_result = compute_score(LEVEL5_CONFIG, eval_result["decisions"], attempt)

            st.session_state["l5_result"] = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            st.session_state["l5_submitted"] = True
            st.session_state["l5_score_saved"] = False
            complete_level(5, score_result["total"], score_result["breakdown"])
            st.rerun()
