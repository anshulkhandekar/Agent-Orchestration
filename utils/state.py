"""Game state management using st.session_state."""
from copy import deepcopy

import streamlit as st


LEVEL_NUMBERS = (1, 2, 3, 4, 5, 6)

STATE_DEFAULTS = {
    "page": "landing",
    "team_name": "",
    "current_level": 0,
    "level_scores": {level: None for level in LEVEL_NUMBERS},
    "level_attempts": {level: 0 for level in LEVEL_NUMBERS},
    "level_best": {level: 0 for level in LEVEL_NUMBERS},
    "level_completed": {level: False for level in LEVEL_NUMBERS},
    "total_score": 0,
    "game_started": False,
    "show_instructions": False,
    "leaderboard_data": {},
    "leaderboard_status": {"mode": "memory", "message": "Using in-memory leaderboard cache."},
    # Level-specific interaction state
    "l1_selected": [],
    "l1_submitted": False,
    "l1_result": None,
    "l1_score_saved": False,
    "l2_selected": [],
    "l2_order": [],
    "l2_submitted": False,
    "l2_result": None,
    "l2_score_saved": False,
    "l3_choice": None,
    "l3_submitted": False,
    "l3_result": None,
    "l3_score_saved": False,
    "l4_round": 1,
    "l4_choices": {},
    "l4_submitted": False,
    "l4_result": None,
    "l4_score_saved": False,
    "l5_selected": [],
    "l5_order": [],
    "l5_submitted": False,
    "l5_result": None,
    "l5_score_saved": False,
    "l6_round": 1,
    "l6_choices": {},
    "l6_submitted": False,
    "l6_result": None,
    "l6_score_saved": False,
    # Animation helpers
    "show_terminal": False,
    "terminal_done": False,
}


def _clone_default(value):
    """Return an isolated copy for mutable defaults."""
    return deepcopy(value)


def _merge_level_dict(state_key: str, default_value: dict):
    current = st.session_state.get(state_key)
    if not isinstance(current, dict):
        st.session_state[state_key] = _clone_default(default_value)
        return

    merged = _clone_default(default_value)
    merged.update(current)
    st.session_state[state_key] = merged


def init_state():
    """Initialize and normalize all session state variables."""
    for key, default_value in STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = _clone_default(default_value)

    _merge_level_dict("level_scores", STATE_DEFAULTS["level_scores"])
    _merge_level_dict("level_attempts", STATE_DEFAULTS["level_attempts"])
    _merge_level_dict("level_best", STATE_DEFAULTS["level_best"])
    _merge_level_dict("level_completed", STATE_DEFAULTS["level_completed"])
    _merge_level_dict("leaderboard_status", STATE_DEFAULTS["leaderboard_status"])
    recalculate_total_score()


def reset_level_state(level: int):
    """Reset interaction state for a specific level (retry support)."""
    if level == 1:
        st.session_state["l1_selected"] = []
        st.session_state["l1_submitted"] = False
        st.session_state["l1_result"] = None
        st.session_state["l1_score_saved"] = False
    elif level == 2:
        st.session_state["l2_selected"] = []
        st.session_state["l2_order"] = []
        st.session_state["l2_submitted"] = False
        st.session_state["l2_result"] = None
        st.session_state["l2_score_saved"] = False
    elif level == 3:
        st.session_state["l3_choice"] = None
        st.session_state.pop("l3_selected", None)
        st.session_state["l3_submitted"] = False
        st.session_state["l3_result"] = None
        st.session_state["l3_score_saved"] = False
    elif level == 4:
        st.session_state["l4_round"] = 1
        st.session_state["l4_choices"] = {}
        for round_num in LEVEL_NUMBERS[:3]:
            st.session_state.pop(f"l4_r{round_num}_selected", None)
        st.session_state["l4_submitted"] = False
        st.session_state["l4_result"] = None
        st.session_state["l4_score_saved"] = False
    elif level == 5:
        st.session_state["l5_selected"] = []
        st.session_state["l5_order"] = []
        st.session_state["l5_submitted"] = False
        st.session_state["l5_result"] = None
        st.session_state["l5_score_saved"] = False
    elif level == 6:
        st.session_state["l6_round"] = 1
        st.session_state["l6_choices"] = {}
        for round_num in (1, 2, 3):
            st.session_state.pop(f"l6_r{round_num}_selected", None)
        st.session_state["l6_submitted"] = False
        st.session_state["l6_result"] = None
        st.session_state["l6_score_saved"] = False
    st.session_state["show_terminal"] = False
    st.session_state["terminal_done"] = False


def set_page(page: str):
    st.session_state["page"] = page


def recalculate_total_score() -> int:
    """Recompute total score from the best known score for each level."""
    level_best = st.session_state.get("level_best", {})
    total = sum(int(level_best.get(level, 0) or 0) for level in LEVEL_NUMBERS)
    st.session_state["total_score"] = total
    return total


def complete_level(level: int, score: int, breakdown: dict):
    """Mark a level complete and update the running best score."""
    level_scores = st.session_state.get("level_scores", {})
    level_scores[level] = {"total": score, "breakdown": breakdown}
    st.session_state["level_scores"] = level_scores

    level_best = st.session_state.get("level_best", {})
    level_best[level] = max(int(level_best.get(level, 0) or 0), int(score))
    st.session_state["level_best"] = level_best

    level_completed = st.session_state.get("level_completed", {})
    level_completed[level] = True
    st.session_state["level_completed"] = level_completed

    recalculate_total_score()


def persist_score_once(level: int) -> bool:
    """Persist the current team's best score exactly once per completed attempt."""
    save_flag_key = f"l{level}_score_saved"
    if st.session_state.get(save_flag_key, False):
        return False

    team_name = (st.session_state.get("team_name") or "").strip()
    if not team_name:
        return False

    from utils.supabase import save_score

    save_score(
        team_name=team_name,
        level_scores=st.session_state.get("level_best", {}),
        total=st.session_state.get("total_score", 0),
    )
    st.session_state[save_flag_key] = True
    return True
