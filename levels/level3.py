"""Level 3 — Checkpoint Rescue: Intervene when the agent drifts."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_decision_cards
from components.progress import render_progress, render_level_header, render_score_screen
from utils.scoring import (
    LEVEL3_CONFIG,
    LEVEL3_OPTIONS,
    evaluate_level3,
    compute_score,
)
from utils.state import complete_level, get_level_hint, persist_score_once, reset_level_state, unlock_level_hint


_DETAILS = [
    {
        "icon": "🧩",
        "label": "What Changed",
        "text": "The agent quietly narrowed its objective to 'best-rated central hotel' and stopped prioritizing the full user request.",
    },
    {
        "icon": "📝",
        "label": "Your Job",
        "text": "Read the log like an operator. The safest move is the one that restores the right constraints before more search happens.",
    },
    {
        "icon": "⚠️",
        "label": "Subtle Trap",
        "text": "Some responses sound responsible but still leave the corrupted shortlist or rewritten objective in place.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Intervention 100 pts · Outcome Quality 75 pts · Efficiency 50 pts = 225 max.",
    },
]

_HINT = (
    "Look for the first action that actually repairs the drift. Diagnosis helps, but the best intervention also clears the bad objective before the agent keeps searching."
)


def render():
    render_progress(3)

    render_level_header(
        level=3,
        color="#3b82f6",
        icon="🚨",
        title="Checkpoint Rescue — Agent Alignment & Safety",
        description=(
            "Reveille is mid-task and has <strong>drifted from the user's original constraints</strong>. "
            "The failure is not just one bad hotel result. Somewhere in the loop, the agent rewrote the task into an easier but incorrect version. "
            "Read the log carefully, find the drift signal, and choose the intervention that restores alignment with the fewest wasted steps."
        ),
        details=_DETAILS,
        hint=get_level_hint(3, _HINT),
        height=400,
    )

    st.markdown("")

    # ── Always show the drift terminal ──
    drift_logs = [
        {"tag": "system", "text": "Reveille agent running trip planner..."},
        {"tag": "observe", "text": "Original user brief loaded: Barcelona stay · dog-friendly hotel · budget <= $150/night"},
        {"tag": "plan", "text": "Planner notes: prioritize central location, walkability, strong guest rating."},
        {"tag": "act", "text": "Hotel search returned only 2 results under strict filters."},
        {"tag": "warning", "text": "Search helper rewrote objective to: 'Find the best central hotel with strong reviews.'"},
        {"tag": "observe", "text": "Current shortlist leader: Hotel Luxe Central — $280/night · pets not allowed · rating 9.4"},
        {"tag": "plan", "text": "Rationale: higher budget may be acceptable if experience quality is excellent."},
        {"tag": "warning", "text": "Constraint audit: budget violated, pet policy violated, rewritten objective no longer matches user brief."},
        {"tag": "checkpoint", "text": "🛑 CHECKPOINT — Supervisor must decide whether to continue, inspect, or reset the search."},
    ]
    render_terminal(drift_logs, height=300)
    st.markdown("")

    if st.session_state.get("l3_submitted") and st.session_state.get("l3_result"):
        result = st.session_state.get("l3_result")

        choice_label = next(
            o["label"] for o in LEVEL3_OPTIONS if o["id"] == st.session_state.get("l3_choice")
        )
        response_logs = [
            {"tag": "system", "text": f"Supervisor chose: {choice_label}"},
            {"tag": "act", "text": "Executing supervisor directive..."},
            {"tag": "observe", "text": result["outcome_text"]},
        ]
        if st.session_state.get("l3_choice") == "B":
            response_logs.append({"tag": "success", "text": "Objective repaired, invalid shortlist discarded, and search resumed with the right guardrails."})
        elif st.session_state.get("l3_choice") == "C":
            response_logs.append({"tag": "warning", "text": "Good catch, but the agent still needs an explicit reset before it can be trusted again."})
        else:
            response_logs.append({"tag": "error", "text": "Suboptimal intervention — the corrupted objective keeps influencing the next step."})

        render_terminal(response_logs, height=200)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL3_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=3,
            categories=LEVEL3_CONFIG["categories"],
        )

        persist_score_once(3)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                unlock_level_hint(3)
                reset_level_state(3)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state["current_level"] = 4
                st.session_state["page"] = "level4"
                st.rerun()
        return

    # ── Decision UI ──
    st.markdown("##### 🎯 What should the supervisor do?")
    choice = render_decision_cards(
        LEVEL3_OPTIONS,
        key_prefix="l3",
        require_confirmation=True,
        confirm_label="Apply Intervention",
    )
    selected_choice = st.session_state.get("l3_selected")

    if selected_choice:
        selected_label = next(
            (option["label"] for option in LEVEL3_OPTIONS if option["id"] == selected_choice),
            selected_choice,
        )
        st.caption(f"Selected intervention: {selected_label}")

    if choice:
        level_attempts = st.session_state.get("level_attempts", {})
        level_attempts[3] = level_attempts.get(3, 0) + 1
        st.session_state["level_attempts"] = level_attempts
        attempt = level_attempts[3]

        eval_result = evaluate_level3(choice)
        score_result = compute_score(LEVEL3_CONFIG, eval_result["decisions"], attempt)

        st.session_state["l3_choice"] = choice
        st.session_state["l3_result"] = {
            "score": score_result,
            "outcome_text": eval_result["outcome_text"],
        }
        st.session_state["l3_submitted"] = True
        st.session_state["l3_score_saved"] = False
        complete_level(3, score_result["total"], score_result["breakdown"])
        st.rerun()
