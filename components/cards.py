"""Reusable card UI components for tool and action selection."""
import streamlit as st


def render_tool_cards(tools: list, selected: list, key_prefix: str = "tool") -> list:
    """Render selectable tool cards and return selected IDs."""
    cols_per_row = 5
    for row_start in range(0, len(tools), cols_per_row):
        row_tools = tools[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, tool in enumerate(row_tools):
            with cols[i]:
                is_selected = tool["id"] in selected
                c = st.container(border=True)
                with c:
                    if is_selected:
                        st.markdown(f"### {tool['icon']}")
                        st.markdown(f":blue[**✓ {tool['name']}**]")
                    else:
                        st.markdown(f"### {tool['icon']}")
                        st.markdown(f"**{tool['name']}**")
                    st.caption(tool.get("desc", ""))
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
                c = st.container(border=True)
                with c:
                    order_num = ""
                    if is_selected and action["id"] in ordered:
                        order_num = f" `#{ordered.index(action['id']) + 1}`"
                    if is_selected:
                        st.markdown(f":violet[**{action['icon']} {action['name']}**]{order_num}")
                    else:
                        st.markdown(f"{action['icon']} **{action['name']}**")
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
                c = st.container(border=True)
                with c:
                    st.markdown(f":violet[**#{i + 1}**]")
                    st.markdown(f"{action['icon']} {action['name']}")
                if st.button("→ End", key=f"reorder_{oid}", use_container_width=True):
                    ordered.remove(oid)
                    ordered.append(oid)
                    st.rerun()

    return selected, ordered


def render_decision_cards(
    options: list,
    key_prefix: str = "decision",
    require_confirmation: bool = False,
    confirm_label: str = "Confirm Decision",
):
    """Render large decision buttons and return chosen ID.

    Uses session state to persist the choice across Streamlit reruns,
    which avoids losing button clicks when components.html iframes
    (e.g. the terminal panel) are on the same page.
    """
    state_key = f"_dc_{key_prefix}_result"

    selected_key = f"{key_prefix}_selected"
    selected_id = st.session_state.get(selected_key)

    if not require_confirmation:
        # If a choice was stored on a previous run, consume and return it
        chosen = st.session_state.pop(state_key, None)
        if chosen is not None:
            return chosen

    cols = st.columns(2)
    for i, opt in enumerate(options):
        with cols[i % 2]:
            c = st.container(border=True)
            with c:
                is_selected = selected_id == opt["id"]
                st.markdown(f"### {opt['icon']}")
                if is_selected:
                    st.markdown(f":blue[**{opt['label']}**]")
                    st.caption("Selected")
                else:
                    st.markdown(f"**{opt['label']}**")
            if st.button(
                "Selected" if is_selected else f"Choose {opt['id']}",
                key=f"{key_prefix}_{opt['id']}",
                use_container_width=True,
            ):
                st.session_state[selected_key] = opt["id"]
                if not require_confirmation:
                    st.session_state[state_key] = opt["id"]
                st.rerun()

    if require_confirmation and selected_id:
        if st.button(confirm_label, key=f"{key_prefix}_confirm", use_container_width=True, type="primary"):
            return selected_id
    return None
