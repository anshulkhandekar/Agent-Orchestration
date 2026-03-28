"""Progress bar, level header, and score screen components."""
import streamlit as st
import streamlit.components.v1 as components


# ─────────────────────────────────────────────
# LEVEL PROGRESS BAR
# ─────────────────────────────────────────────
def render_progress(current_level: int):
    """Render the Level 1 → 2 → 3 → 4 progress strip."""
    levels = [
        {"num": 1, "name": "Loadout",       "color": "#22c55e"},
        {"num": 2, "name": "Workflow",      "color": "#f59e0b"},
        {"num": 3, "name": "Checkpoint",    "color": "#3b82f6"},
        {"num": 4, "name": "Mission Control","color": "#ef4444"},
    ]

    items_html = ""
    for i, lev in enumerate(levels):
        is_current = current_level == lev["num"]
        is_done    = st.session_state.level_completed.get(lev["num"], False)

        if is_current:
            bg, border, text_color, icon = f"{lev['color']}22", lev["color"], lev["color"], "▶"
        elif is_done:
            bg, border, text_color, icon = "rgba(34,197,94,0.1)", "#22c55e55", "#22c55e", "✓"
        else:
            bg, border, text_color, icon = "rgba(30,41,59,0.4)", "#1e293b", "#475569", str(lev["num"])

        items_html += f"""
        <div style="flex:1;text-align:center;padding:10px 8px;
            background:{bg};border:1px solid {border};border-radius:10px;
            color:{text_color};font-size:12px;font-weight:600;">
            <span style="font-size:14px;">{icon}</span> L{lev['num']}: {lev['name']}
        </div>"""
        if i < 3:
            arrow_c = "#22c55e" if is_done else "#334155"
            items_html += f'<div style="color:{arrow_c};font-size:18px;display:flex;align-items:center;padding:0 2px;">→</div>'

    html = f"""
    <div style="display:flex;gap:6px;align-items:center;padding:8px;
        background:rgba(10,14,20,0.6);border-radius:14px;border:1px solid #1e293b;
        font-family:'Inter',sans-serif;">
        {items_html}
    </div>"""
    components.html(html, height=58, scrolling=False)


# ─────────────────────────────────────────────
# LEVEL HEADER / MISSION BRIEF
# ─────────────────────────────────────────────
def render_level_header(
    level: int,
    color: str,
    icon: str,
    title: str,
    description: str,
    details: list,
    hint: str = "",
    height: int = 360,
):
    """Render a styled mission-brief panel for a level.

    Args:
        level:       Level number (1–4).
        color:       Accent hex color for this level.
        icon:        Large emoji icon.
        title:       Level title shown in the header.
        description: Paragraph description of the challenge.
        details:     List of dicts with keys 'icon', 'label', 'text'.
        hint:        Optional hint string shown at the bottom.
        height:      iframe height in pixels.
    """
    detail_items = ""
    for d in details:
        detail_items += f"""
        <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">
            <span style="font-size:17px;line-height:1.4;flex-shrink:0;">{d['icon']}</span>
            <div>
                <div style="color:#e2e8f0;font-size:12.5px;font-weight:600;margin-bottom:2px;">{d['label']}</div>
                <div style="color:#94a3b8;font-size:12px;line-height:1.5;">{d['text']}</div>
            </div>
        </div>"""

    hint_block = ""
    if hint:
        hint_block = f"""
        <div style="margin-top:14px;padding:10px 14px;
            background:rgba(255,255,255,0.03);
            border:1px solid {color}44;border-radius:8px;
            display:flex;gap:10px;align-items:flex-start;">
            <span style="color:{color};font-size:15px;flex-shrink:0;">💡</span>
            <div style="color:#94a3b8;font-size:12px;line-height:1.55;">
                <strong style="color:{color};">Hint: </strong>{hint}
            </div>
        </div>"""

    html = f"""
    <div style="
        background:linear-gradient(135deg,{color}0d 0%,rgba(10,14,20,0.97) 100%);
        border:1px solid {color}33;
        border-left:4px solid {color};
        border-radius:12px;
        padding:20px 24px 20px 24px;
        font-family:'Inter',sans-serif;
    ">
        <!-- Title row -->
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
            <span style="font-size:34px;line-height:1;">{icon}</span>
            <div>
                <div style="color:{color};font-size:10.5px;font-weight:700;
                    text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">
                    Level {level}
                </div>
                <div style="color:#f1f5f9;font-size:18px;font-weight:700;line-height:1.25;">{title}</div>
            </div>
        </div>
        <!-- Description -->
        <div style="color:#cbd5e1;font-size:13.5px;line-height:1.65;
            padding-bottom:14px;margin-bottom:14px;
            border-bottom:1px solid #1e293b;">
            {description}
        </div>
        <!-- Detail grid (2 columns) -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 20px;">
            {detail_items}
        </div>
        {hint_block}
    </div>"""
    components.html(html, height=height, scrolling=False)


# ─────────────────────────────────────────────
# SCORE SCREEN
# ─────────────────────────────────────────────
def render_score_screen(score: int, max_score: int, breakdown: dict, level: int):
    """Render an animated score panel with grade, breakdown bars, and retry info."""
    pct        = int((score / max(max_score, 1)) * 100)
    multiplier = breakdown.get("retry_multiplier", 1.0)
    attempts   = st.session_state.level_attempts.get(level, 1)

    grade_color = "#22c55e" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"
    grade       = "S" if pct == 100 else "A" if pct >= 80 else "B" if pct >= 60 else "C" if pct >= 40 else "D"

    bars_html = ""
    cats = [(k, v) for k, v in breakdown.items() if k != "retry_multiplier"]
    for i, (cat, pts) in enumerate(cats):
        bar_pct = min(100, int(pts * 100 / max(max_score, 1)) * 2)
        delay_ms = i * 150
        bars_html += f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#94a3b8;font-size:12.5px;">{cat}</span>
                <span style="color:#e2e8f0;font-size:12.5px;font-weight:700;">{pts} pts</span>
            </div>
            <div style="background:#1e293b;border-radius:6px;height:9px;overflow:hidden;">
                <div style="
                    background:linear-gradient(90deg,#00d4ff,#a855f7);
                    height:100%;width:{bar_pct}%;border-radius:6px;
                    animation:barGrow 0.9s ease-out {delay_ms}ms both;">
                </div>
            </div>
        </div>"""

    num_cats = len(cats)
    height   = 310 + num_cats * 56

    html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=Inter:wght@400;600;700&display=swap');
        @keyframes countUp  {{ from {{ transform:scale(0.5);opacity:0; }} to {{ transform:scale(1);opacity:1; }} }}
        @keyframes barGrow  {{ from {{ width:0%; }} }}
    </style>
    <div style="
        background:rgba(15,23,42,0.96);
        border:1px solid #1e293b;
        border-top:3px solid {grade_color};
        border-radius:16px;
        padding:28px 32px;
        font-family:'Inter',sans-serif;
        text-align:center;
    ">
        <div style="font-size:11px;color:#64748b;text-transform:uppercase;
            letter-spacing:2.5px;margin-bottom:8px;">
            Level {level} Complete
        </div>
        <div style="
            font-size:66px;font-weight:800;color:{grade_color};
            font-family:'Syne',sans-serif;line-height:1;
            animation:countUp 0.55s ease-out;">
            {score}
        </div>
        <div style="color:#64748b;font-size:13px;margin-bottom:12px;">out of {max_score}</div>
        <div style="
            display:inline-block;
            background:{grade_color}1a;
            border:1px solid {grade_color};
            color:{grade_color};
            padding:4px 22px;border-radius:20px;
            font-weight:700;font-size:15px;margin-bottom:8px;">
            Grade: {grade}
        </div>
        <div style="color:#475569;font-size:12px;margin-bottom:22px;">
            Attempt #{attempts} &nbsp;·&nbsp; Retry multiplier: {multiplier:.0%}
        </div>
        <div style="text-align:left;max-width:460px;margin:0 auto;">
            {bars_html}
        </div>
    </div>"""
    components.html(html, height=height, scrolling=False)
