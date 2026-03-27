"""Reusable card UI components for tool and action selection."""
import streamlit as st
import streamlit.components.v1 as components


def render_tool_cards(tools: list, selected: list, key_prefix: str = "tool") -> list:
    """Render selectable tool cards using Streamlit columns and return selected IDs."""
    cols_per_row = 5
    for row_start in range(0, len(tools), cols_per_row):
        row_tools = tools[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, tool in enumerate(row_tools):
            with cols[i]:
                is_selected = tool["id"] in selected
                border_color = "#00d4ff" if is_selected else "#1e293b"
                bg = "rgba(0, 212, 255, 0.08)" if is_selected else "rgba(15, 23, 42, 0.6)"
                check = "✓ " if is_selected else ""

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid {border_color};
                        border-radius: 12px;
                        padding: 16px 10px;
                        text-align: center;
                        background: {bg};
                        transition: all 0.2s;
                        min-height: 100px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        gap: 4px;
                    ">
                        <div style="font-size: 28px;">{tool['icon']}</div>
                        <div style="color: {'#00d4ff' if is_selected else '#e2e8f0'}; font-size: 13px; font-weight: 600;">
                            {check}{tool['name']}
                        </div>
                        <div style="color: #64748b; font-size: 10px;">{tool.get('desc', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                btn_label = "Remove" if is_selected else "Select"
                if st.button(btn_label, key=f"{key_prefix}_{tool['id']}", use_container_width=True):
                    if is_selected:
                        selected.remove(tool["id"])
                    else:
                        selected.append(tool["id"])
                    st.rerun()
    return selected


def render_ordering_interface(actions: list, selected: list, ordered: list, key_prefix: str = "order"):
    """Render an interface for selecting and ordering actions."""
    st.markdown("#### 📋 Step 1: Select 4 actions")

    cols_per_row = 3
    for row_start in range(0, len(actions), cols_per_row):
        row_actions = actions[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, action in enumerate(row_actions):
            with cols[i]:
                is_selected = action["id"] in selected
                border_color = "#a855f7" if is_selected else "#1e293b"
                bg = "rgba(168, 85, 247, 0.08)" if is_selected else "rgba(15, 23, 42, 0.6)"
                idx_str = ""
                if is_selected and action["id"] in ordered:
                    idx_str = f'<div style="position:absolute;top:6px;right:10px;background:#a855f7;color:white;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;">{ordered.index(action["id"])+1}</div>'

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid {border_color};
                        border-radius: 12px;
                        padding: 18px 12px;
                        text-align: center;
                        background: {bg};
                        position: relative;
                        min-height: 80px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        gap: 6px;
                    ">
                        {idx_str}
                        <div style="font-size: 24px;">{action['icon']}</div>
                        <div style="color: {'#a855f7' if is_selected else '#e2e8f0'}; font-size: 13px; font-weight: 600;">
                            {action['name']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if is_selected:
                    if st.button("Remove", key=f"{key_prefix}_rm_{action['id']}", use_container_width=True):
                        selected.remove(action["id"])
                        if action["id"] in ordered:
                            ordered.remove(action["id"])
                        st.rerun()
                else:
                    if st.button("Select", key=f"{key_prefix}_sel_{action['id']}", use_container_width=True):
                        if len(selected) < 4:
                            selected.append(action["id"])
                            ordered.append(action["id"])
                        st.rerun()

    if ordered:
        st.markdown("#### 🔀 Step 2: Reorder (click to move to end)")
        reorder_cols = st.columns(len(ordered))
        for i, oid in enumerate(ordered):
            action = next(a for a in actions if a["id"] == oid)
            with reorder_cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(0,212,255,0.08));
                        border: 1px solid #a855f7;
                        border-radius: 10px;
                        padding: 12px 8px;
                        text-align: center;
                    ">
                        <div style="color:#a855f7;font-weight:800;font-size:18px;">#{i+1}</div>
                        <div style="font-size: 20px;">{action['icon']}</div>
                        <div style="color:#e2e8f0;font-size:11px;font-weight:600;">{action['name']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("→ End", key=f"reorder_{oid}", use_container_width=True):
                    ordered.remove(oid)
                    ordered.append(oid)
                    st.rerun()

    return selected, ordered


def render_decision_cards(options: list, key_prefix: str = "decision") -> str:
    """Render large decision buttons and return chosen ID."""
    cols = st.columns(2)
    chosen = None
    for i, opt in enumerate(options):
        with cols[i % 2]:
            border = "#1e293b"
            bg = "rgba(15, 23, 42, 0.6)"
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {border};
                    border-radius: 14px;
                    padding: 24px 16px;
                    text-align: center;
                    background: {bg};
                    min-height: 100px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    margin-bottom: 4px;
                ">
                    <div style="font-size: 36px;">{opt['icon']}</div>
                    <div style="color: #e2e8f0; font-size: 15px; font-weight: 700;">{opt['label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Choose {opt['id']}", key=f"{key_prefix}_{opt['id']}", use_container_width=True):
                chosen = opt["id"]
    return chosen
