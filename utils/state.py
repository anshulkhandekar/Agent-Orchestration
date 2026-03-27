"""Game state management using st.session_state."""
import streamlit as st
from datetime import datetime


def init_state():
    """Initialize all session state variables."""
    defaults = {
        "page": "landing",
        "team_name": "",
        "current_level": 0,
        "level_scores": {1: None, 2: None, 3: None, 4: None},
        "level_attempts": {1: 0, 2: 0, 3: 0, 4: 0},
        "level_best": {1: 0, 2: 0, 3: 0, 4: 0},
        "level_completed": {1: False, 2: False, 3: False, 4: False},
        "total_score": 0,
        "game_started": False,
        "show_instructions": False,
        # Level-specific state
        "l1_selected": [],
        "l1_submitted": False,
        "l1_result": None,
        "l2_selected": [],
        "l2_order": [],
        "l2_submitted": False,
        "l2_result": None,
        "l3_choice": None,
        "l3_submitted": False,
        "l3_result": None,
        "l4_round": 1,
        "l4_choices": {},
        "l4_submitted": False,
        "l4_result": None,
        # Animation triggers
        "show_terminal": False,
        "terminal_done": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_level_state(level: int):
    """Reset state for a specific level for retry."""
    if level == 1:
        st.session_state.l1_selected = []
        st.session_state.l1_submitted = False
        st.session_state.l1_result = None
    elif level == 2:
        st.session_state.l2_selected = []
        st.session_state.l2_order = []
        st.session_state.l2_submitted = False
        st.session_state.l2_result = None
    elif level == 3:
        st.session_state.l3_choice = None
        st.session_state.l3_submitted = False
        st.session_state.l3_result = None
    elif level == 4:
        st.session_state.l4_round = 1
        st.session_state.l4_choices = {}
        st.session_state.l4_submitted = False
        st.session_state.l4_result = None
    st.session_state.show_terminal = False
    st.session_state.terminal_done = False


def set_page(page: str):
    st.session_state.page = page


def complete_level(level: int, score: int, breakdown: dict):
    """Mark a level complete and store score."""
    st.session_state.level_scores[level] = {"total": score, "breakdown": breakdown}
    if score > st.session_state.level_best[level]:
        st.session_state.level_best[level] = score
    st.session_state.level_completed[level] = True
    st.session_state.total_score = sum(
        st.session_state.level_best[i] for i in range(1, 5)
    )
