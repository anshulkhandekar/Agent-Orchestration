"""Level 4 — Mission Control: Supervise the full agent loop across 3 rounds."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_decision_cards
from components.progress import render_progress, render_score_screen
from utils.scoring import (
    LEVEL4_CONFIG,
    LEVEL4_ROUNDS,
    evaluate_level4,
    compute_score,
)
from utils.state import complete_level, reset_level_state
from utils.supabase import save_score


def render():
    render_progress(4)

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(168,85,247,0.04));
            border: 1px solid #ef444433;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
        ">
            <div style="color:#ef4444;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                🔴 Level 4 — Mission Control
            </div>
            <div style="color:#e2e8f0;font-size:20px;font-weight:700;margin-bottom:8px;">
                Aggie Weekend Planner — Full Loop
            </div>
            <div style="color:#94a3b8;font-size:14px;">
                Supervise Reveille through <strong>3 decision rounds</strong>.
                Each round presents a critical decision point in the agent loop.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── If fully submitted → show final results ──
    if st.session_state.l4_submitted and st.session_state.l4_result:
        result = st.session_state.l4_result
        choices = st.session_state.l4_choices

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
            all_logs.append({"tag": "success", "text": "🎉 Perfect supervision across all rounds!"})
        else:
            all_logs.append({"tag": "checkpoint", "text": "Mission complete — room for improvement."})

        render_terminal(all_logs, height=380)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        render_score_screen(
            result["score"]["total"],
            LEVEL4_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=4,
        )

        # Save to leaderboard
        save_score(
            st.session_state.team_name,
            st.session_state.level_best,
            st.session_state.total_score,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(4)
                st.rerun()
        with col2:
            if st.button("🏆 View Leaderboard", use_container_width=True, type="primary"):
                st.session_state.page = "leaderboard"
                st.rerun()
        return

    # ── Round-by-round play ──
    current_round = st.session_state.l4_round
    rdata = LEVEL4_ROUNDS[current_round]

    # Show previous rounds' results
    for r in range(1, current_round):
        choice = st.session_state.l4_choices.get(r)
        prev_data = LEVEL4_ROUNDS[r]
        outcome = prev_data["outcomes"].get(choice, {"text": ""})
        is_correct = prev_data["correct"] == choice
        icon = "✅" if is_correct else "⚠️"
        choice_label = next((o["label"] for o in prev_data["options"] if o["id"] == choice), "")
        st.markdown(
            f"""
            <div style="
                background: rgba(15,23,42,0.4);
                border: 1px solid {'#22c55e33' if is_correct else '#f59e0b33'};
                border-radius: 10px;
                padding: 12px 16px;
                margin-bottom: 8px;
                font-size: 13px;
                color: #94a3b8;
            ">
                {icon} <strong style="color:#e2e8f0;">Round {r}:</strong> {choice_label} — {outcome['text']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Current round
    st.markdown(
        f"""
        <div style="
            background: rgba(239,68,68,0.06);
            border: 1px solid #ef444433;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
        ">
            <div style="color:#ef4444;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">
                {rdata['title']}
            </div>
            <div style="color:#e2e8f0;font-size:15px;">
                {rdata['scenario']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Round progress
    round_dots = ""
    for r in [1, 2, 3]:
        if r < current_round:
            round_dots += '<span style="width:12px;height:12px;border-radius:50%;background:#22c55e;display:inline-block;margin:0 4px;"></span>'
        elif r == current_round:
            round_dots += '<span style="width:12px;height:12px;border-radius:50%;background:#ef4444;display:inline-block;margin:0 4px;box-shadow:0 0 8px #ef4444;"></span>'
        else:
            round_dots += '<span style="width:12px;height:12px;border-radius:50%;background:#1e293b;border:1px solid #334155;display:inline-block;margin:0 4px;"></span>'
    st.markdown(f'<div style="text-align:center;margin-bottom:16px;">{round_dots}</div>', unsafe_allow_html=True)

    choice = render_decision_cards(rdata["options"], key_prefix=f"l4_r{current_round}")

    if choice:
        st.session_state.l4_choices[current_round] = choice
        if current_round < 3:
            st.session_state.l4_round = current_round + 1
            st.rerun()
        else:
            # All rounds complete
            st.session_state.l4_submitted = True
            st.session_state.level_attempts[4] += 1
            attempt = st.session_state.level_attempts[4]

            eval_result = evaluate_level4(st.session_state.l4_choices)
            score_result = compute_score(LEVEL4_CONFIG, eval_result["decisions"], attempt)

            st.session_state.l4_result = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            complete_level(4, score_result["total"], score_result["breakdown"])
            st.rerun()
