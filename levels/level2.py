"""Level 2 — Route the Workflow: Select and order 4 actions."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_ordering_interface
from components.progress import render_progress, render_level_header, render_score_screen
from utils.scoring import (
    LEVEL2_CONFIG,
    LEVEL2_ACTIONS,
    LEVEL2_CORRECT_ORDER,
    evaluate_level2,
    compute_score,
)
from utils.state import complete_level, get_level_hint, persist_score_once, reset_level_state, unlock_level_hint


_DETAILS = [
    {
        "icon": "🎯",
        "label": "Your Goal",
        "text": "Select 4 of the 6 actions and arrange them in the correct dependency order.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Selection 70 pts · Order 50 pts · Efficiency 30 pts = 150 max.",
    },
    {
        "icon": "🔗",
        "label": "Key Insight",
        "text": "Steps have dependencies: you need a destination before you can check flights or hotels.",
    },
    {
        "icon": "🚫",
        "label": "Watch Out",
        "text": "'Convert prices' and 'Generate recommendation' are nice-to-haves, not core steps.",
    },
]

_HINT = (
    "Think in dependency order: where are we going? → is the weather right? "
    "→ can we get there? → where do we stay? Lock in each answer before moving to the next."
)


def render():
    render_progress(2)

    render_level_header(
        level=2,
        color="#f59e0b",
        icon="🔀",
        title="Route the Workflow — Build Reveille's Action Pipeline",
        description=(
            "Reveille has the right tools — now it needs a <strong>logical execution order</strong>. "
            "AI agents make mistakes when they act before gathering enough information. "
            "Select 4 of the 6 available actions and sequence them so that "
            "each step has everything it needs from the steps before it."
        ),
        details=_DETAILS,
        hint=get_level_hint(2, _HINT),
        height=380,
    )

    st.markdown("")

    if st.session_state.get("l2_submitted") and st.session_state.get("l2_result"):
        result = st.session_state.get("l2_result")

        ordered_names = []
        for oid in st.session_state.get("l2_order", []):
            action = next((a for a in LEVEL2_ACTIONS if a["id"] == oid), None)
            if action:
                ordered_names.append(action["name"])

        correct_names = [
            next(a["name"] for a in LEVEL2_ACTIONS if a["id"] == oid)
            for oid in LEVEL2_CORRECT_ORDER
        ]

        logs = [
            {"tag": "system", "text": "Workflow engine started."},
            {"tag": "plan",   "text": f"Pipeline: {' → '.join(ordered_names)}"},
        ]
        for i, name in enumerate(ordered_names):
            logs.append({"tag": "act", "text": f"Step {i + 1}: {name}"})
        if ordered_names == correct_names:
            logs.append({"tag": "success", "text": "Perfect workflow sequence — dependencies satisfied!"})
        else:
            logs.append({"tag": "warning", "text": f"Optimal order: {' → '.join(correct_names)}"})
        logs.append({"tag": "observe", "text": result["outcome_text"]})

        render_terminal(logs, height=300)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL2_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=2,
            categories=LEVEL2_CONFIG["categories"],
        )

        persist_score_once(2)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                unlock_level_hint(2)
                reset_level_state(2)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state["current_level"] = 3
                st.session_state["page"] = "level3"
                st.rerun()
        return

    # ── Selection & Ordering UI ──
    selected, ordered = render_ordering_interface(
        LEVEL2_ACTIONS,
        st.session_state.get("l2_selected", []),
        st.session_state.get("l2_order", []),
        key_prefix="l2",
    )
    st.session_state["l2_selected"] = selected
    st.session_state["l2_order"] = ordered

    count = len(selected)
    if count == 4:
        st.success(f"{count}/4 actions selected ✓")
    elif count > 0:
        st.warning(f"{count}/4 actions selected — need exactly 4")
    else:
        st.caption("0/4 actions selected")

    if count == 4 and len(ordered) == 4:
        if st.button("🚀 Execute Workflow", use_container_width=True, type="primary"):
            level_attempts = st.session_state.get("level_attempts", {})
            level_attempts[2] = level_attempts.get(2, 0) + 1
            st.session_state["level_attempts"] = level_attempts
            attempt = level_attempts[2]

            eval_result = evaluate_level2(selected, ordered)
            score_result = compute_score(LEVEL2_CONFIG, eval_result["decisions"], attempt)

            st.session_state["l2_result"] = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            st.session_state["l2_submitted"] = True
            st.session_state["l2_score_saved"] = False
            complete_level(2, score_result["total"], score_result["breakdown"])
            st.rerun()
