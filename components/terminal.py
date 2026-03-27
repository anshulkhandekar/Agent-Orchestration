"""Terminal panel component with animated typing and color-coded tags."""
import streamlit as st
import streamlit.components.v1 as components


TAG_COLORS = {
    "observe": "#00d4ff",
    "plan": "#a855f7",
    "act": "#22c55e",
    "warning": "#f59e0b",
    "checkpoint": "#ef4444",
    "system": "#64748b",
    "success": "#10b981",
    "error": "#ef4444",
}


def render_terminal(logs: list, height: int = 400, speed: int = 25):
    """
    Render a terminal panel with typing animation.

    logs: list of dicts with keys 'tag', 'text'
          e.g. [{"tag": "observe", "text": "Scanning destinations..."}]
    """
    lines_html = ""
    for i, log in enumerate(logs):
        tag = log.get("tag", "system")
        text = log.get("text", "")
        color = TAG_COLORS.get(tag, "#94a3b8")
        delay = i * 600
        lines_html += f"""
        <div class="log-line" style="animation-delay: {delay}ms;">
            <span class="tag" style="color: {color}; border-color: {color}33;">[{tag.upper()}]</span>
            <span class="log-text">{text}</span>
        </div>
        """

    total_time = len(logs) * 600 + 500
    html = f"""
    <div id="terminal-container">
        <div class="terminal-header">
            <div class="terminal-dots">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
            </div>
            <span class="terminal-title">reveille-agent v1.0</span>
        </div>
        <div class="terminal-body" id="term-body">
            {lines_html}
            <div class="cursor-line" style="animation-delay: {total_time}ms;">
                <span class="cursor">▊</span>
            </div>
        </div>
    </div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        #terminal-container {{
            background: #0a0e14;
            border: 1px solid #1e293b;
            border-radius: 12px;
            overflow: hidden;
            font-family: 'Space Mono', monospace;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.08);
        }}
        .terminal-header {{
            background: #111827;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #1e293b;
        }}
        .terminal-dots {{
            display: flex;
            gap: 6px;
        }}
        .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .dot.red {{ background: #ef4444; }}
        .dot.yellow {{ background: #f59e0b; }}
        .dot.green {{ background: #22c55e; }}
        .terminal-title {{
            color: #64748b;
            font-size: 11px;
        }}
        .terminal-body {{
            padding: 16px 20px;
            max-height: {height}px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: #1e293b transparent;
        }}
        .log-line {{
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
            font-size: 13px;
            opacity: 0;
            transform: translateY(4px);
            animation: fadeIn 0.3s ease forwards;
            align-items: flex-start;
        }}
        @keyframes fadeIn {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border: 1px solid;
            border-radius: 4px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .log-text {{
            color: #cbd5e1;
            line-height: 1.5;
        }}
        .cursor-line {{
            opacity: 0;
            animation: fadeIn 0.3s ease forwards;
        }}
        .cursor {{
            color: #00d4ff;
            animation: blink 1s step-end infinite;
        }}
        @keyframes blink {{
            50% {{ opacity: 0; }}
        }}
    </style>
    """
    components.html(html, height=height + 60, scrolling=False)
