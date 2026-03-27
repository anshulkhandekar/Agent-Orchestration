"""Leaderboard persistence — falls back to in-memory dict."""
import streamlit as st

# In-memory fallback
if "leaderboard_data" not in st.session_state:
    st.session_state.leaderboard_data = {}


def save_score(team_name: str, level_scores: dict, total: int):
    """Save team scores."""
    existing = st.session_state.leaderboard_data.get(team_name)
    if existing is None or total > existing.get("total", 0):
        st.session_state.leaderboard_data[team_name] = {
            "team": team_name,
            "L1": level_scores.get(1, 0),
            "L2": level_scores.get(2, 0),
            "L3": level_scores.get(3, 0),
            "L4": level_scores.get(4, 0),
            "total": total,
        }


def get_leaderboard() -> list:
    """Return sorted leaderboard list."""
    entries = list(st.session_state.leaderboard_data.values())
    entries.sort(key=lambda x: x["total"], reverse=True)
    return entries
