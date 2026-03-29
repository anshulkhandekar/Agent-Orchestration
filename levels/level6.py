"""Level 6 — Mission Control Swarm: coordinate a multi-agent capstone."""
import streamlit as st

from components.cards import render_decision_cards
from components.progress import render_level_header, render_progress, render_score_screen
from components.terminal import render_terminal
from utils.scoring import LEVEL6_CONFIG, LEVEL6_ROUNDS, compute_score, evaluate_level6
from utils.state import complete_level, persist_score_once, reset_level_state


_DETAILS = [
    {
        "icon": "🧠",
        "label": "Your Role",
        "text": "You are the orchestrator of a small swarm, not just a supervisor of one agent.",
    },
    {
        "icon": "⚖️",
        "label": "Hard Part",
        "text": "The swarm will surface conflicting recommendations. The best move balances the full brief, not one metric.",
    },
    {
        "icon": "🪓",
        "label": "Advanced Skill",
        "text": "Strong coordination means pruning noisy branches at the right time instead of delegating forever.",
    },
    {
        "icon": "📊",
        "label": "Scoring",
        "text": "Orchestration 220 pts · Conflict Resolution 180 pts · Efficiency 100 pts · Mission Quality 100 pts = 600 max.",
    },
]

_HINT = (
    "The best swarm is not the biggest one. Split work cleanly, reconcile against all constraints, then drop noise before final synthesis."
)


def render():
    render_progress(6)

    render_level_header(
        level=6,
        color="#14b8a6",
        icon="🧬",
        title="Mission Control Swarm — Coordinate the Capstone",
        description=(
            "A larger visiting group is arriving for ADSC weekend, and Reveille has spun up multiple helper agents. "
            "Now you must coordinate a small swarm: split the mission intelligently, resolve conflicts between branches, and finalize only when signal is stronger than noise."
        ),
        details=_DETAILS,
        hint=_HINT,
        height=405,
    )

    st.markdown("")

    if st.session_state.get("l6_submitted") and st.session_state.get("l6_result"):
        result = st.session_state.get("l6_result")
        choices = st.session_state.get("l6_choices", {})

        logs = [{"tag": "system", "text": "Mission Control Swarm review started."}]
        for round_num in (1, 2, 3):
            round_data = LEVEL6_ROUNDS[round_num]
            choice = choices.get(round_num, "?")
            choice_label = next((option["label"] for option in round_data["options"] if option["id"] == choice), "Unknown")
            outcome = round_data["outcomes"].get(choice, {"text": "Unknown"})
            status_tag = "success" if round_data["correct"] == choice else "warning"
            logs.append({"tag": "plan", "text": f"Round {round_num}: {round_data['title']}"})
            logs.append({"tag": "act", "text": f"Decision: {choice_label}"})
            logs.append({"tag": status_tag, "text": outcome["text"]})
        logs.append({"tag": "observe", "text": result["outcome_text"]})
        if result.get("ending") == "Elite orchestration":
            logs.append({"tag": "success", "text": "The swarm stays disciplined end to end. Elite orchestration."})
        else:
            logs.append({"tag": "checkpoint", "text": "Mission complete — the swarm finished, but the coordination tradeoffs are visible."})

        render_terminal(logs, height=420)
        st.markdown("")

        render_score_screen(
            result["score"]["total"],
            LEVEL6_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=6,
            categories=LEVEL6_CONFIG["categories"],
        )

        persist_score_once(6)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(6)
                st.rerun()
        with col2:
            if st.button("View Leaderboard", use_container_width=True, type="primary"):
                st.session_state["page"] = "leaderboard"
                st.rerun()
        return

    current_round = st.session_state.get("l6_round", 1)
    round_data = LEVEL6_ROUNDS[current_round]

    for round_num in range(1, current_round):
        prev_choice = st.session_state.get("l6_choices", {}).get(round_num)
        prev_data = LEVEL6_ROUNDS[round_num]
        choice_label = next((option["label"] for option in prev_data["options"] if option["id"] == prev_choice), "")
        outcome_text = prev_data["outcomes"].get(prev_choice, {"text": ""})["text"]
        is_correct = prev_data["correct"] == prev_choice
        st.info(f"{'✅' if is_correct else '⚠️'} Round {round_num}: {choice_label} — {outcome_text}")

    st.markdown(f"#### {round_data['title']}")
    st.markdown(round_data["scenario"])

    progress_badges = []
    for round_num in (1, 2, 3):
        if round_num < current_round:
            progress_badges.append("🟢")
        elif round_num == current_round:
            progress_badges.append("🟣")
        else:
            progress_badges.append("⚪")
    st.caption(f"Swarm progress: {' '.join(progress_badges)}")

    choice = render_decision_cards(round_data["options"], key_prefix=f"l6_r{current_round}")

    if choice:
        l6_choices = st.session_state.get("l6_choices", {})
        l6_choices[current_round] = choice
        st.session_state["l6_choices"] = l6_choices

        if current_round < 3:
            st.session_state["l6_round"] = current_round + 1
            st.rerun()

        level_attempts = st.session_state.get("level_attempts", {})
        level_attempts[6] = level_attempts.get(6, 0) + 1
        st.session_state["level_attempts"] = level_attempts
        attempt = level_attempts[6]

        eval_result = evaluate_level6(st.session_state.get("l6_choices", {}))
        score_result = compute_score(LEVEL6_CONFIG, eval_result["decisions"], attempt)

        st.session_state["l6_result"] = {
            "score": score_result,
            "outcome_text": eval_result["outcome_text"],
            "ending": eval_result["ending"],
        }
        st.session_state["l6_submitted"] = True
        st.session_state["l6_score_saved"] = False
        complete_level(6, score_result["total"], score_result["breakdown"])
        st.rerun()
