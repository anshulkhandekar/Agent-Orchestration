"""Leaderboard persistence — Supabase if configured, else in-memory fallback.

To enable Supabase, set credentials in ONE of these locations:

  1. .streamlit/secrets.toml  (recommended for Streamlit Cloud)
       SUPABASE_URL = "https://your-project.supabase.co"
       SUPABASE_KEY = "your-anon-or-service-key"

  2. Environment variables
       export SUPABASE_URL="https://your-project.supabase.co"
       export SUPABASE_KEY="your-anon-or-service-key"

Required Supabase table schema:
    CREATE TABLE leaderboard (
        id          BIGSERIAL PRIMARY KEY,
        team        TEXT UNIQUE NOT NULL,
        l1          INT DEFAULT 0,
        l2          INT DEFAULT 0,
        l3          INT DEFAULT 0,
        l4          INT DEFAULT 0,
        l5          INT DEFAULT 0,
        l6          INT DEFAULT 0,
        total       INT DEFAULT 0,
        updated_at  TIMESTAMPTZ DEFAULT NOW()
    );

Schema migration for existing tables:
    ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS l5 INT DEFAULT 0;
    ALTER TABLE leaderboard ADD COLUMN IF NOT EXISTS l6 INT DEFAULT 0;
"""
import os
from datetime import datetime, timezone
from typing import Dict, Optional

import streamlit as st

# ── Resolve credentials at import time ──
_supabase_url = ""
_supabase_key = ""

try:
    _supabase_url = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "")
    _supabase_key = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
except Exception:
    _supabase_url = os.environ.get("SUPABASE_URL", "")
    _supabase_key = os.environ.get("SUPABASE_KEY", "")

# ── Lazy Supabase client ──
_client = None


def _get_client():
    """Return a cached Supabase client, or None if not configured / unavailable."""
    global _client
    if _client is not None:
        return _client
    if not (_supabase_url and _supabase_key):
        return None
    try:
        from supabase import create_client  # optional dependency
        _client = create_client(_supabase_url, _supabase_key)
    except Exception:
        # supabase package not installed or credentials invalid
        _client = None
    return _client


@st.cache_data(ttl=3, show_spinner=False)
def _cached_remote_entry(supabase_url: str, supabase_key: str, team_name: str):
    """Fetch one leaderboard row with a short TTL to reduce repeated reads."""
    from supabase import create_client

    client = create_client(supabase_url, supabase_key)
    response = (
        client.table("leaderboard")
        .select("team, l1, l2, l3, l4, l5, l6, total")
        .eq("team", team_name)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


@st.cache_data(ttl=3, show_spinner=False)
def _cached_remote_leaderboard(supabase_url: str, supabase_key: str):
    """Fetch leaderboard rows with a short TTL for multi-user traffic."""
    from supabase import create_client

    client = create_client(supabase_url, supabase_key)
    response = (
        client.table("leaderboard")
        .select("team, l1, l2, l3, l4, l5, l6, total")
        .order("total", desc=True)
        .limit(50)
        .execute()
    )
    return response.data


LEVEL_NUMBERS = (1, 2, 3, 4, 5, 6)


def _local_cache() -> dict:
    """Return the in-session leaderboard cache."""
    return st.session_state.setdefault("leaderboard_data", {})


def _set_status(mode: str, message: str) -> None:
    st.session_state["leaderboard_status"] = {"mode": mode, "message": message}


def _normalize_score(value) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _normalize_level_scores(level_scores: Optional[dict]) -> Dict[int, int]:
    safe_scores = level_scores or {}
    return {level: _normalize_score(safe_scores.get(level, 0)) for level in LEVEL_NUMBERS}


def _normalize_entry(entry: Optional[dict]) -> Optional[dict]:
    if not entry:
        return None

    level_scores = {
        1: _normalize_score(entry.get("L1", entry.get("l1", 0))),
        2: _normalize_score(entry.get("L2", entry.get("l2", 0))),
        3: _normalize_score(entry.get("L3", entry.get("l3", 0))),
        4: _normalize_score(entry.get("L4", entry.get("l4", 0))),
        5: _normalize_score(entry.get("L5", entry.get("l5", 0))),
        6: _normalize_score(entry.get("L6", entry.get("l6", 0))),
    }
    total = sum(level_scores.values())
    return {
        "team": (entry.get("team") or "").strip(),
        "L1": level_scores[1],
        "L2": level_scores[2],
        "L3": level_scores[3],
        "L4": level_scores[4],
        "L5": level_scores[5],
        "L6": level_scores[6],
        "total": total,
    }


def _fetch_remote_entry(team_name: str) -> Optional[dict]:
    client = _get_client()
    if client is None:
        return None

    try:
        response = _cached_remote_entry(_supabase_url, _supabase_key, team_name)
        if response:
            return _normalize_entry(response)
    except Exception:
        _set_status("memory", "Supabase lookup failed. Using in-memory leaderboard cache.")
    return None


def save_score(team_name: str, level_scores: dict, total: int) -> None:
    """Save team scores — only updates when the new total is strictly better.

    Args:
        team_name:    Team identifier.
        level_scores: Dict mapping level int → best score for that level.
        total:        Sum of best scores across all levels.
    """
    team_name = (team_name or "").strip()
    if not team_name:
        return

    current_scores = _normalize_level_scores(level_scores)
    local_existing = _normalize_entry(_local_cache().get(team_name))
    remote_existing = _fetch_remote_entry(team_name)

    merged_scores = {}
    for level in LEVEL_NUMBERS:
        merged_scores[level] = max(
            current_scores[level],
            (local_existing or {}).get(f"L{level}", 0),
            (remote_existing or {}).get(f"L{level}", 0),
        )

    merged_total = max(sum(merged_scores.values()), _normalize_score(total))
    merged_entry = {
        "team": team_name,
        "L1": merged_scores[1],
        "L2": merged_scores[2],
        "L3": merged_scores[3],
        "L4": merged_scores[4],
        "L5": merged_scores[5],
        "L6": merged_scores[6],
        "total": merged_total,
    }
    _local_cache()[team_name] = merged_entry

    # Persist to Supabase if configured
    client = _get_client()
    if client is None:
        _set_status("memory", "Supabase not configured. Using in-memory leaderboard cache.")
        return

    row = {
        "team": team_name,
        "l1": merged_scores[1],
        "l2": merged_scores[2],
        "l3": merged_scores[3],
        "l4": merged_scores[4],
        "l5": merged_scores[5],
        "l6": merged_scores[6],
        "total": merged_total,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client.table("leaderboard").upsert(row, on_conflict="team").execute()
        _cached_remote_entry.clear()
        _cached_remote_leaderboard.clear()
        _set_status("supabase", "Leaderboard synced with Supabase.")
    except Exception as exc:
        _set_status("memory", f"Supabase save failed. Using in-memory cache. ({exc})")


def get_leaderboard() -> list:
    """Return leaderboard sorted by total score descending.

    Supabase is the source of truth when available; falls back to in-memory.
    """
    client = _get_client()
    if client is not None:
        try:
            resp = _cached_remote_leaderboard(_supabase_url, _supabase_key)
            entries = []
            for row in resp:
                entry = _normalize_entry(row)
                if not entry or not entry["team"]:
                    continue
                entries.append(entry)
                _local_cache()[entry["team"]] = entry
            _set_status("supabase", "Leaderboard synced with Supabase.")
            return sorted(entries, key=lambda item: (-item["total"], item["team"].lower()))
        except Exception:
            _set_status("memory", "Supabase read failed. Showing in-memory leaderboard cache.")
            pass  # fall through to in-memory

    entries = list(_local_cache().values())
    entries.sort(key=lambda item: (-item["total"], item["team"].lower()))
    return entries


def get_existing_team_names() -> set:
    """Return normalized existing team names from the leaderboard source."""
    entries = get_leaderboard()
    return {
        (entry.get("team") or "").strip().lower()
        for entry in entries
        if (entry.get("team") or "").strip()
    }
