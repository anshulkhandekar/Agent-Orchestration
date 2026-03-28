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
        total       INT DEFAULT 0,
        updated_at  TIMESTAMPTZ DEFAULT NOW()
    );
"""
import os
from datetime import datetime, timezone

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


# ── In-memory fallback (scoped to browser session) ──
if "leaderboard_data" not in st.session_state:
    st.session_state.leaderboard_data = {}


def save_score(team_name: str, level_scores: dict, total: int) -> None:
    """Save team scores — only updates when the new total is strictly better.

    Args:
        team_name:    Team identifier.
        level_scores: Dict mapping level int → best score for that level.
        total:        Sum of best scores across all levels.
    """
    if not team_name:
        return

    existing = st.session_state.leaderboard_data.get(team_name)
    existing_total = existing.get("total", 0) if existing else 0

    # Only persist if this is a new high-score
    if total < existing_total:
        return

    # Update in-memory cache
    st.session_state.leaderboard_data[team_name] = {
        "team": team_name,
        "L1": level_scores.get(1, 0),
        "L2": level_scores.get(2, 0),
        "L3": level_scores.get(3, 0),
        "L4": level_scores.get(4, 0),
        "total": total,
    }

    # Persist to Supabase if configured
    client = _get_client()
    if client is None:
        return

    row = {
        "team": team_name,
        "l1": level_scores.get(1, 0),
        "l2": level_scores.get(2, 0),
        "l3": level_scores.get(3, 0),
        "l4": level_scores.get(4, 0),
        "total": total,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client.table("leaderboard").upsert(row, on_conflict="team").execute()
    except Exception as exc:
        st.toast(f"⚠️ Leaderboard save failed: {exc}", icon="⚠️")


def get_leaderboard() -> list:
    """Return leaderboard sorted by total score descending.

    Supabase is the source of truth when available; falls back to in-memory.
    """
    client = _get_client()
    if client is not None:
        try:
            resp = (
                client.table("leaderboard")
                .select("team, l1, l2, l3, l4, total")
                .order("total", desc=True)
                .limit(50)
                .execute()
            )
            return [
                {
                    "team": r["team"],
                    "L1": r.get("l1", 0),
                    "L2": r.get("l2", 0),
                    "L3": r.get("l3", 0),
                    "L4": r.get("l4", 0),
                    "total": r.get("total", 0),
                }
                for r in resp.data
            ]
        except Exception:
            pass  # fall through to in-memory

    entries = list(st.session_state.leaderboard_data.values())
    entries.sort(key=lambda x: x["total"], reverse=True)
    return entries
