"""Progress bar component for level navigation."""
import streamlit as st


def render_progress(current_level: int):
    """Render a top progress bar showing Level 1 → 2 → 3 → 4."""
    levels = [
        {"num": 1, "name": "Loadout", "color": "#22c55e"},
        {"num": 2, "name": "Workflow", "color": "#f59e0b"},
        {"num": 3, "name": "Checkpoint", "color": "#3b82f6"},
        {"num": 4, "name": "Mission Control", "color": "#ef4444"},
    ]

    items_html = ""
    for i, lev in enumerate(levels):
        is_current = current_level == lev["num"]
        is_done = st.session_state.level_completed.get(lev["num"], False)

        if is_current:
            bg = f"{lev['color']}22"
            border = lev["color"]
            text_color = lev["color"]
            icon = "▶"
        elif is_done:
            bg = "rgba(34, 197, 94, 0.1)"
            border = "#22c55e55"
            text_color = "#22c55e"
            icon = "✓"
        else:
            bg = "rgba(30, 41, 59, 0.4)"
            border = "#1e293b"
            text_color = "#475569"
            icon = str(lev["num"])

        items_html += f"""
        <div style="
            flex: 1;
            text-align: center;
            padding: 10px 8px;
            background: {bg};
            border: 1px solid {border};
            border-radius: 10px;
            color: {text_color};
            font-size: 12px;
            font-weight: 600;
        ">
            <span style="font-size: 14px;">{icon}</span> L{lev['num']}: {lev['name']}
        </div>
        """
        if i < 3:
            arrow_color = "#22c55e" if is_done else "#1e293b"
            items_html += f'<div style="color:{arrow_color};font-size:18px;display:flex;align-items:center;">→</div>'

    st.markdown(
        f"""
        <div style="
            display: flex;
            gap: 8px;
            align-items: center;
            margin-bottom: 24px;
            padding: 8px;
            background: rgba(10, 14, 20, 0.5);
            border-radius: 14px;
            border: 1px solid #1e293b;
        ">
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_screen(score: int, max_score: int, breakdown: dict, level: int):
    """Render animated score screen with breakdown bars."""
    pct = int((score / max(max_score, 1)) * 100)
    multiplier = breakdown.get("retry_multiplier", 1.0)
    attempts = st.session_state.level_attempts.get(level, 1)

    grade_color = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"
    grade = "S" if pct == 100 else "A" if pct >= 80 else "B" if pct >= 60 else "C" if pct >= 40 else "D"

    bars_html = ""
    for cat, pts in breakdown.items():
        if cat == "retry_multiplier":
            continue
        bars_html += f"""
        <div style="margin-bottom: 10px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:#94a3b8;font-size:13px;">{cat}</span>
                <span style="color:#e2e8f0;font-size:13px;font-weight:600;">{pts} pts</span>
            </div>
            <div style="background:#1e293b;border-radius:6px;height:8px;overflow:hidden;">
                <div style="
                    background: linear-gradient(90deg, #00d4ff, #a855f7);
                    height: 100%;
                    width: {min(100, pts * 2)}%;
                    border-radius: 6px;
                    animation: barGrow 1s ease-out;
                "></div>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <style>
            @keyframes barGrow {{
                from {{ width: 0%; }}
            }}
            @keyframes countUp {{
                from {{ opacity: 0; transform: scale(0.5); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
        </style>
        <div style="
            text-align: center;
            padding: 32px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #1e293b;
            border-radius: 16px;
        ">
            <div style="font-size: 14px; color: #64748b; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px;">
                Level {level} Complete
            </div>
            <div style="
                font-size: 72px;
                font-weight: 800;
                color: {grade_color};
                animation: countUp 0.6s ease-out;
                line-height: 1;
            ">{score}</div>
            <div style="color: #64748b; font-size: 14px; margin-bottom: 4px;">out of {max_score}</div>
            <div style="
                display: inline-block;
                background: {grade_color}22;
                border: 1px solid {grade_color};
                color: {grade_color};
                padding: 4px 16px;
                border-radius: 20px;
                font-weight: 700;
                font-size: 18px;
                margin-bottom: 8px;
            ">Grade: {grade}</div>
            <div style="color: #64748b; font-size: 12px; margin-bottom: 20px;">
                Attempt #{attempts} · Multiplier: {multiplier:.0%}
            </div>
            <div style="text-align: left; max-width: 400px; margin: 0 auto;">
                {bars_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
