"""Level 3 — Checkpoint Rescue: Intervene when the agent drifts."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_decision_cards
from components.progress import render_progress, render_score_screen
from utils.scoring import (
    LEVEL3_CONFIG,
    LEVEL3_OPTIONS,
    evaluate_level3,
    compute_score,
)
from utils.state import complete_level, reset_level_state


def render():
    render_progress(3)

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(168,85,247,0.04));
            border: 1px solid #3b82f633;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
        ">
            <div style="color:#3b82f6;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                🔵 Level 3 — Checkpoint Rescue
            </div>
            <div style="color:#e2e8f0;font-size:20px;font-weight:700;margin-bottom:8px;">
                Reveille Has Gone Off the Rails!
            </div>
            <div style="color:#94a3b8;font-size:14px;">
                The agent is booking a trip but has <strong>ignored key constraints</strong>:
                dog-friendly accommodation and a strict budget.
                Review the terminal output and decide what to do.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Show the drift scenario in terminal ──
    drift_logs = [
        {"tag": "system", "text": "Reveille agent running trip planner..."},
        {"tag": "observe", "text": "User constraints: dog-friendly, budget < $150/night"},
        {"tag": "act", "text": "Searching hotels in Barcelona..."},
        {"tag": "observe", "text": "Found: Hotel Luxe — $280/night, no pets allowed"},
        {"tag": "plan", "text": "This looks great! Proceeding with booking..."},
        {"tag": "warning", "text": "⚠ Budget constraint violated: $280 > $150"},
        {"tag": "warning", "text": "⚠ Pet policy constraint violated: no dogs allowed"},
        {"tag": "checkpoint", "text": "🛑 CHECKPOINT — Agent has drifted from constraints. Supervisor action required."},
    ]
    render_terminal(drift_logs, height=300)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if st.session_state.l3_submitted and st.session_state.l3_result:
        result = st.session_state.l3_result

        choice_label = next(o["label"] for o in LEVEL3_OPTIONS if o["id"] == st.session_state.l3_choice)
        response_logs = [
            {"tag": "system", "text": f"Supervisor chose: {choice_label}"},
            {"tag": "act", "text": "Executing supervisor directive..."},
            {"tag": "observe", "text": result["outcome_text"]},
        ]
        if st.session_state.l3_choice == "B":
            response_logs.append({"tag": "success", "text": "Constraints restored — agent back on track!"})
        else:
            response_logs.append({"tag": "error", "text": "Suboptimal intervention — constraints still at risk."})

        render_terminal(response_logs, height=200)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        render_score_screen(
            result["score"]["total"],
            LEVEL3_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=3,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
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
        st.session_state.l3_choice = choice
        st.session_state.l3_submitted = True
        st.session_state.level_attempts[3] += 1
        attempt = st.session_state.level_attempts[3]

        eval_result = evaluate_level3(choice)
        score_result = compute_score(LEVEL3_CONFIG, eval_result["decisions"], attempt)

        st.session_state.l3_result = {
            "score": score_result,
            "outcome_text": eval_result["outcome_text"],
        }
        complete_level(3, score_result["total"], score_result["breakdown"])
        st.rerun()
