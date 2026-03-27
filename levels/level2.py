"""Level 2 — Route the Workflow: Select and order 4 actions."""
import streamlit as st
from components.terminal import render_terminal
from components.cards import render_ordering_interface
from components.progress import render_progress, render_score_screen
from utils.scoring import (
    LEVEL2_CONFIG,
    LEVEL2_ACTIONS,
    LEVEL2_CORRECT_ORDER,
    evaluate_level2,
    compute_score,
)
from utils.state import complete_level, reset_level_state


def render():
    render_progress(2)

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(168,85,247,0.04));
            border: 1px solid #f59e0b33;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
        ">
            <div style="color:#f59e0b;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
                🟡 Level 2 — Route the Workflow
            </div>
            <div style="color:#e2e8f0;font-size:20px;font-weight:700;margin-bottom:8px;">
                Build Reveille's Action Pipeline
            </div>
            <div style="color:#94a3b8;font-size:14px;">
                Select <strong>4 actions</strong> and put them in the <strong>right order</strong>.
                Reveille needs a logical workflow to plan the trip efficiently.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.l2_submitted and st.session_state.l2_result:
        result = st.session_state.l2_result
        ordered_names = []
        for oid in st.session_state.l2_order:
            action = next((a for a in LEVEL2_ACTIONS if a["id"] == oid), None)
            if action:
                ordered_names.append(action["name"])

        logs = [
            {"tag": "system", "text": "Workflow engine started."},
            {"tag": "plan", "text": f"Pipeline: {' → '.join(ordered_names)}"},
        ]
        for i, name in enumerate(ordered_names):
            logs.append({"tag": "act", "text": f"Step {i+1}: {name}"})

        correct_names = [next(a["name"] for a in LEVEL2_ACTIONS if a["id"] == oid) for oid in LEVEL2_CORRECT_ORDER]
        if ordered_names == correct_names:
            logs.append({"tag": "success", "text": "Perfect workflow sequence!"})
        else:
            logs.append({"tag": "warning", "text": f"Optimal order was: {' → '.join(correct_names)}"})
        logs.append({"tag": "observe", "text": result["outcome_text"]})

        render_terminal(logs, height=300)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        render_score_screen(
            result["score"]["total"],
            LEVEL2_CONFIG["max_score"],
            result["score"]["breakdown"],
            level=2,
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry Level", use_container_width=True):
                reset_level_state(2)
                st.rerun()
        with col2:
            if st.button("Next Level →", use_container_width=True, type="primary"):
                st.session_state.current_level = 3
                st.session_state.page = "level3"
                st.rerun()
        return

    # ── Selection & Ordering UI ──
    selected, ordered = render_ordering_interface(
        LEVEL2_ACTIONS,
        st.session_state.l2_selected,
        st.session_state.l2_order,
        key_prefix="l2",
    )
    st.session_state.l2_selected = selected
    st.session_state.l2_order = ordered

    count = len(selected)
    color = "#22c55e" if count == 4 else "#f59e0b" if count > 0 else "#64748b"
    st.markdown(
        f'<div style="text-align:center;color:{color};font-size:14px;font-weight:600;margin:12px 0;">'
        f'{count}/4 actions selected</div>',
        unsafe_allow_html=True,
    )

    if count == 4 and len(ordered) == 4:
        if st.button("🚀 Execute Workflow", use_container_width=True, type="primary"):
            st.session_state.l2_submitted = True
            st.session_state.level_attempts[2] += 1
            attempt = st.session_state.level_attempts[2]

            eval_result = evaluate_level2(selected, ordered)
            score_result = compute_score(LEVEL2_CONFIG, eval_result["decisions"], attempt)

            st.session_state.l2_result = {
                "score": score_result,
                "outcome_text": eval_result["outcome_text"],
            }
            complete_level(2, score_result["total"], score_result["breakdown"])
            st.rerun()
