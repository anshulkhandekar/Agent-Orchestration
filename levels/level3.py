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
from utils.state import complete_level, reset_level_state
from utils.supabase import save_score


_DETAILS = [
    {
        "icon": "🐕",
        "label": "Violated Constraint #1",
        "text": "User required dog-friendly accommodation — Reveille ignored this.",
    },
    {
        "icon": "💸",
        "label": "Violated Constraint #2",
        "text": "Budget cap was $150/night — Reveille found a $280/night hotel.",
    },
    {
        "icon": "🧠",
        "label": "AI Safety Concept",
        "text": "Agents can satisfy their sub-goal (find a hotel) while violating the original intent.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Intervention 100 pts · Outcome Quality 75 pts · Efficiency 50 pts = 225 max.",
    },
]

_HINT = (
    "Continuing, searching more, or finalizing all risk locking in the violated constraints. "
    "The agent needs to be reset to its original requirements before any new action is taken."
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
            "This is a core challenge in AI safety: an agent can optimize for its immediate sub-goal "
            "(find a hotel) while completely ignoring the original intent (dog-friendly, under-budget). "
            "Read the terminal output carefully, then decide how to intervene as the human supervisor."
        ),
        details=_DETAILS,
        hint=_HINT,
        height=400,
    )

    st.markdown("")

    # ── Always show the drift terminal ──
    drift_logs = [
        {"tag": "system",     "text": "Reveille agent running trip planner..."},
        {"tag": "observe",    "text": "User constraints loaded: dog-friendly · budget < $150/night"},
        {"tag": "act",        "text": "Searching hotels in Barcelona..."},
        {"tag": "observe",    "text": "Result: Hotel Luxe — $280/night · No pets allowed"},
        {"tag": "plan",       "text": "This looks great! High rating, central location. Proceeding..."},
        {"tag": "warning",    "text": "⚠ Budget constraint violated: $280 > $150/night"},
        {"tag": "warning",    "text": "⚠ Pet policy constraint violated: dogs not permitted"},
        {"tag": "checkpoint", "text": "🛑 CHECKPOINT — Agent has drifted from user constraints. Supervisor action required."},
    ]
    render_terminal(drift_logs, height=300)
    st.markdown("")

    if st.session_state.l3_submitted and st.session_state.l3_result:
        result = st.session_state.l3_result

        choice_label = next(
            o["label"] for o in LEVEL3_OPTIONS if o["id"] == st.session_state.l3_choice
        )
        response_logs = [
            {"tag": "system",  "text": f"Supervisor chose: {choice_label}"},
            {"tag": "act",     "text": "Executing supervisor directive..."},
            {"tag": "observe", "text": result["outcome_text"]},
        ]
        if st.session_state.l3_choice == "B":
            response_logs.append({"tag": "success", "text": "Constraints restored — agent back on track!"})
        else:
            response_logs.append({"tag": "error", "text": "Suboptimal intervention — constraints still at risk."})

        render_terminal(response_logs, height=200)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL3_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=3,
        )

        if not st.session_state.get("l3_score_saved", False):
            save_score(
                st.session_state.team_name,
                st.session_state.level_best,
                st.session_state.total_score,
            )
            st.session_state.l3_score_saved = True

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(3)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state.current_level = 4
                st.session_state.page = "level4"
                st.rerun()
        return

    # ── Decision UI ──
    st.markdown("##### 🎯 What should the supervisor do?")
    choice = render_decision_cards(LEVEL3_OPTIONS, key_prefix="l3")

    if choice:
        st.session_state.l3_choice    = choice
        st.session_state.l3_submitted = True
        st.session_state.level_attempts[3] += 1
        attempt = st.session_state.level_attempts[3]

        eval_result  = evaluate_level3(choice)
        score_result = compute_score(LEVEL3_CONFIG, eval_result["decisions"], attempt)

        st.session_state.l3_result = {
            "score":        score_result,
            "outcome_text": eval_result["outcome_text"],
        }
        complete_level(3, score_result["total"], score_result["breakdown"])
        st.rerun()
