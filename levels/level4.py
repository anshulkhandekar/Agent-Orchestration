"""Level 4 — Mission Control: Supervise the full agent loop across 3 rounds."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_decision_cards
from components.progress import render_level_header, render_progress, render_score_screen
from utils.scoring import (
    LEVEL4_CONFIG,
    LEVEL4_ROUNDS,
    evaluate_level4,
    compute_score,
)
from utils.state import complete_level, get_level_hint, persist_score_once, reset_level_state, unlock_level_hint


_LEVEL4_HINT = (
    "Use each round to tighten the loop: compare first, resolve tradeoffs second, and re-check the original goal before finalizing."
)

_DETAILS = [
    {
        "icon": "🎯",
        "label": "Your Goal",
        "text": "Guide Reveille through a full three-step planning loop, choosing the best supervisory action at each checkpoint.",
    },
    {
        "icon": "🧠",
        "label": "What You Control",
        "text": "You are not building the itinerary directly. You are deciding how the agent should compare, adjust, and validate its work.",
    },
    {
        "icon": "🔄",
        "label": "Round Flow",
        "text": "Round 1 compares plans, Round 2 resolves tradeoffs, and Round 3 checks whether the final plan still matches the original goals.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Plan Comparison 110 pts · Constraint Balance 110 pts · Goal Alignment 105 pts = 325 max.",
    },
]


def render():
    render_progress(4)

    render_level_header(
        level=4,
        color="#ef4444",
        icon="🎛️",
        title="Mission Control — Aggie Weekend Planner",
        description=(
            "This level simulates a <strong>full agent loop from start to finish</strong>. "
            "Reveille is already planning the weekend, and your job is to intervene at the right moments: "
            "first when plans need comparison, then when constraints conflict, and finally when the agent is ready to ship a result. "
            "Treat each round like a mission-control checkpoint where the quality of your supervision determines the final outcome."
        ),
        details=_DETAILS,
        hint=get_level_hint(4, _LEVEL4_HINT),
        height=398,
    )
    st.markdown("")

    # ── If fully submitted → show final results ──
    if st.session_state.get("l4_submitted") and st.session_state.get("l4_result"):
        result = st.session_state.get("l4_result")
        choices = st.session_state.get("l4_choices", {})

        all_logs = [{"tag": "system", "text": "Mission Control — Full agent loop review"}]
        for r in [1, 2, 3]:
            rdata = LEVEL4_ROUNDS[r]
            choice = choices.get(r, "?")
            outcome = rdata["outcomes"].get(choice, {"text": "Unknown"})
            choice_label = next((o["label"] for o in rdata["options"] if o["id"] == choice), "Unknown")
            all_logs.append({"tag": "plan", "text": f"Round {r}: {rdata['title']}"})
            all_logs.append({"tag": "act", "text": f"Decision: {choice_label}"})
            tag = "success" if rdata["correct"] == choice else "warning"
            all_logs.append({"tag": tag, "text": outcome["text"]})

        all_correct = all(LEVEL4_ROUNDS[r]["correct"] == choices.get(r) for r in [1, 2, 3])
        if all_correct:
            all_logs.append({"tag": "success", "text": "Perfect supervision across all rounds!"})
        else:
            all_logs.append({"tag": "checkpoint", "text": "Mission complete — room for improvement."})

        render_terminal(all_logs, height=380)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL4_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=4,
            categories=LEVEL4_CONFIG["categories"],
        )

        persist_score_once(4)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                unlock_level_hint(4)
                reset_level_state(4)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state["current_level"] = 5
                st.session_state["page"] = "level5"
                st.rerun()
        return

    # ── Round-by-round play ──
    current_round = st.session_state.get("l4_round", 1)
    rdata = LEVEL4_ROUNDS[current_round]

    # Show previous rounds' results
    for r in range(1, current_round):
        choice = st.session_state.get("l4_choices", {}).get(r)
        prev_data = LEVEL4_ROUNDS[r]
        outcome = prev_data["outcomes"].get(choice, {"text": ""})
        is_correct = prev_data["correct"] == choice
        choice_label = next((o["label"] for o in prev_data["options"] if o["id"] == choice), "")
        icon = "✅" if is_correct else "⚠️"
        st.info(f"{icon} **Round {r}:** {choice_label} — {outcome['text']}")

    # Current round
    st.markdown(f"#### {rdata['title']}")
    st.markdown(rdata["scenario"])

    # Round progress dots
    dots = []
    for r in [1, 2, 3]:
        if r < current_round:
            dots.append("🟢")
        elif r == current_round:
            dots.append("🔴")
        else:
            dots.append("⚪")
    st.caption(f"Round progress: {' '.join(dots)}")

    choice = render_decision_cards(rdata["options"], key_prefix=f"l4_r{current_round}")

    if choice:
        l4_choices = st.session_state.get("l4_choices", {})
        l4_choices[current_round] = choice
        st.session_state["l4_choices"] = l4_choices
        if current_round < 3:
            st.session_state["l4_round"] = current_round + 1
            st.rerun()
        else:
            # All rounds complete
            level_attempts = st.session_state.get("level_attempts", {})
            level_attempts[4] = level_attempts.get(4, 0) + 1
            st.session_state["level_attempts"] = level_attempts
            attempt = level_attempts[4]

            eval_result = evaluate_level4(st.session_state.get("l4_choices", {}))
            score_result = compute_score(LEVEL4_CONFIG, eval_result["decisions"], attempt)

            st.session_state["l4_result"] = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            st.session_state["l4_submitted"] = True
            st.session_state["l4_score_saved"] = False
            complete_level(4, score_result["total"], score_result["breakdown"])
            st.rerun()
