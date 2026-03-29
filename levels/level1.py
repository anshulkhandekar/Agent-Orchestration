"""Level 1 — Vacation Loadout: Select 3 tools for Reveille's beach trip."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_tool_cards
from components.progress import render_progress, render_level_header, render_score_screen
from utils.scoring import (
    LEVEL1_CONFIG,
    LEVEL1_TOOLS,
    LEVEL1_CORRECT,
    evaluate_level1,
    compute_score,
)
from utils.state import complete_level, get_level_hint, persist_score_once, reset_level_state, unlock_level_hint


_DETAILS = [
    {
        "icon": "🎯",
        "label": "Your Goal",
        "text": "Pick exactly 3 tools that together cover travel, accommodation, and timing.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Correctness 60 pts · Efficiency 25 pts · Outcome Quality 15 pts = 100 max.",
    },
    {
        "icon": "⚠️",
        "label": "Common Trap",
        "text": "Maps, Currency, and Restaurants feel relevant but don't book the core trip.",
    },
    {
        "icon": "🔁",
        "label": "Retries",
        "text": "You may retry, but each attempt applies a score multiplier (100% → 92% → 85% → 75%).",
    },
]

_HINT = (
    "Every successful trip needs three things: a way to get there, "
    "a place to sleep, and knowing the weather so you pick the right week."
)


def render():
    render_progress(1)

    render_level_header(
        level=1,
        color="#22c55e",
        icon="🏖️",
        title="Vacation Loadout — European Beach Trip",
        description=(
            "Reveille has been asked to plan the perfect European beach vacation: "
            "warm weather, budget-friendly, and close to the sea. "
            "As Reveille's supervisor, you must equip it with exactly <strong>3 tools</strong> "
            "from the loadout below. Every extra tool wastes compute; every missing tool "
            "leaves a critical gap in the plan."
        ),
        details=_DETAILS,
        hint=get_level_hint(1, _HINT),
        height=390,
    )

    st.markdown("")

    # ── Already submitted → show results ──
    if st.session_state.get("l1_submitted") and st.session_state.get("l1_result"):
        result = st.session_state.get("l1_result")

        selected_names = [t["name"] for t in LEVEL1_TOOLS if t["id"] in st.session_state.get("l1_selected", [])]
        logs = [
            {"tag": "system",   "text": "Reveille agent initialized."},
            {"tag": "observe",  "text": f"Tools equipped: {', '.join(selected_names)}"},
            {"tag": "plan",     "text": "Planning European beach vacation..."},
            {"tag": "act",      "text": "Searching for destinations with equipped tools..."},
        ]
        missing = LEVEL1_CORRECT - set(st.session_state.get("l1_selected", []))
        if missing:
            missing_names = [t["name"] for t in LEVEL1_TOOLS if t["id"] in missing]
            logs.append({"tag": "warning", "text": f"Missing critical tools: {', '.join(missing_names)}"})
        logs.append({"tag": "observe", "text": result["outcome_text"]})
        if result["score"]["total"] == LEVEL1_CONFIG["max_score"]:
            logs.append({"tag": "success", "text": "Mission complete — perfect loadout!"})
        else:
            logs.append({"tag": "checkpoint", "text": "Mission complete with issues. Consider retrying."})

        render_terminal(logs, height=280)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL1_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=1,
            categories=LEVEL1_CONFIG["categories"],
        )

        # Save score once per submission
        persist_score_once(1)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                unlock_level_hint(1)
                reset_level_state(1)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state["current_level"] = 2
                st.session_state["page"] = "level2"
                st.rerun()
        return

    # ── Tool Selection ──
    st.markdown("##### ⚙️ Select exactly 3 tools")
    selected = render_tool_cards(LEVEL1_TOOLS, st.session_state.get("l1_selected", []), key_prefix="l1_tool")
    st.session_state["l1_selected"] = selected

    count = len(selected)
    if count == 3:
        st.success(f"{count}/3 tools selected ✓")
    elif count > 0:
        st.warning(f"{count}/3 tools selected — need exactly 3")
    else:
        st.caption("0/3 tools selected")

    if count == 3:
        if st.button("🚀 Deploy Reveille", use_container_width=True, type="primary"):
            level_attempts = st.session_state.get("level_attempts", {})
            level_attempts[1] = level_attempts.get(1, 0) + 1
            st.session_state["level_attempts"] = level_attempts
            attempt = level_attempts[1]

            eval_result = evaluate_level1(st.session_state.get("l1_selected", []))
            score_result = compute_score(LEVEL1_CONFIG, eval_result["decisions"], attempt)

            st.session_state["l1_result"] = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            st.session_state["l1_submitted"] = True
            st.session_state["l1_score_saved"] = False
            complete_level(1, score_result["total"], score_result["breakdown"])
            st.rerun()
    elif count > 3:
        st.error("Too many tools selected! Remove some to reach exactly 3.")
