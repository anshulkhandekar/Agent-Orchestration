"""
Tool Loadout Challenge — ADSC Workshop App
==========================================
Run: pip install streamlit filelock && streamlit run workshop_app.py
Requires: streamlit >= 1.28
"""

import streamlit as st
import streamlit.components.v1 as components
import json, os, time, re, html, fcntl
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tool Loadout Challenge — ADSC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
LEADERBOARD_FILE = "leaderboard.json"
DEPLOY_COOLDOWN  = 30          # seconds per-level between attempts
MAX_TOOLS        = 5
MIN_TEAM_LEN     = 2
MAX_TEAM_LEN     = 32

ROMAN = {3: "III", 2: "II", 1: "I", 0: "0"}

# ─────────────────────────────────────────────────────────────────────────────
# INPUT SANITIZATION
# ─────────────────────────────────────────────────────────────────────────────
_BAD = {
    "fuck","shit","bitch","cunt","dick","cock","pussy","nigger","nigga",
    "fag","faggot","retard","slut","whore","bastard","asshole",
    "motherfucker","bullshit","dumbass",
}

def sanitize_team_name(raw: str):
    """Returns (cleaned_str, error_str_or_None)."""
    s = raw.strip()
    s = re.sub(r"<[^>]*>",   "",  s)   # strip tags
    s = re.sub(r"[;'\"\\]",  "",  s)   # strip injection chars
    s = re.sub(r"[^\x20-\x7E]", "", s).strip()
    if len(s) < MIN_TEAM_LEN:
        return "", f"Team name must be at least {MIN_TEAM_LEN} characters."
    if len(s) > MAX_TEAM_LEN:
        return "", f"Team name must be {MAX_TEAM_LEN} characters or fewer."
    if not re.match(r"^[A-Za-z0-9 _\-\.]+$", s):
        return "", "Letters, numbers, spaces, hyphens, underscores, and periods only."
    for w in _BAD:
        if w in s.lower():
            return "", "Team name contains inappropriate content."
    return html.escape(s), None

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD  (file-locked for concurrent writers)
# ─────────────────────────────────────────────────────────────────────────────

def _read_lb() -> list:
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE) as f:
        try:
            return json.load(f)
        except Exception:
            return []

def load_leaderboard() -> list:
    try:
        return _read_lb()
    except Exception:
        return []

def upsert_leaderboard(team: str, level_key: str, level_score: int):
    """Atomic read-modify-write with file lock."""
    lock_path = LEADERBOARD_FILE + ".lock"
    now = datetime.now().strftime("%H:%M:%S")
    try:
        with open(lock_path, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                lb    = _read_lb()
                entry = next((e for e in lb if e["team"] == team), None)
                if entry is None:
                    entry = {"team": team, "level_scores": {},
                             "total_score": 0, "first_seen": now, "last_updated": now}
                    lb.append(entry)
                prev = entry["level_scores"].get(level_key, 0)
                if level_score > prev:
                    entry["level_scores"][level_key] = level_score
                entry["total_score"]  = sum(entry["level_scores"].values())
                entry["last_updated"] = now
                lb.sort(key=lambda x: x["total_score"], reverse=True)
                with open(LEADERBOARD_FILE, "w") as df:
                    json.dump(lb, df, indent=2)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        pass

def clear_leaderboard():
    lock_path = LEADERBOARD_FILE + ".lock"
    try:
        with open(lock_path, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                with open(LEADERBOARD_FILE, "w") as df:
                    json.dump([], df)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# GAME DATA
# ─────────────────────────────────────────────────────────────────────────────
LEVEL_ORDER = ["easy", "medium", "hard", "expert"]

LEVELS = {
    "easy": {
        "label":   "Level 01 — Easy",
        "accent":  "#3dffa0",
        "title":   "Coastal Weather Search",
        "instructions": (
            "Configure a travel agent by equipping it with tools from the pool. "
            "Drag a tool from the left panel into your loadout on the right. "
            "Click an equipped tool to remove it. "
            "You may select up to 5 tools."
        ),
        "task": (
            "A user wants to fly to a sunny European beach destination departing next week. "
            "Identify the best option and justify the recommendation."
        ),
        "tool_pool": [
            ("Flight Search API",  "Queries available flights, routes, and prices between cities."),
            ("Weather API",        "Returns current conditions and multi-day forecasts for any region."),
            ("Maps API",           "Provides geographic data, coastal boundaries, and location context."),
            ("Hotel Finder API",   "Searches hotel inventory, nightly rates, and availability windows."),
            ("Reviews API",        "Aggregates user ratings and sentiment scores for destinations."),
            ("Currency Converter", "Converts monetary values using live exchange rates."),
            ("Calculator",         "Performs arithmetic — sums, comparisons, and budget totals."),
            ("News API",           "Retrieves recent travel articles, alerts, and destination coverage."),
        ],
        "optimal":    frozenset(["Flight Search API", "Weather API", "Maps API"]),
        "acceptable": [
            frozenset(["Flight Search API", "Weather API", "Maps API"]),
            frozenset(["Flight Search API", "Weather API", "Hotel Finder API"]),
        ],
        "base_score": 40,
        "lives": 3,
    },
    "medium": {
        "label":   "Level 02 — Medium",
        "accent":  "#f7c948",
        "title":   "Multi-Constraint Destination Ranking",
        "instructions": (
            "This task has three simultaneous constraints. "
            "Think through every reasoning step the agent must take before committing. "
            "Select up to 5 tools."
        ),
        "task": (
            "Find the three cheapest European city destinations with consistently high visitor ratings "
            "and no rain forecast in the next 14 days. Return a ranked shortlist with justification."
        ),
        "tool_pool": [
            ("Flight Search API",  "Queries flights and compares prices across destinations."),
            ("Weather API",        "14-day forecasts including daily precipitation probability."),
            ("Reviews API",        "Aggregates destination ratings and visitor sentiment."),
            ("Maps API",           "Geographic data and regional classification."),
            ("Hotel Finder API",   "Hotel listings, nightly rates, and availability."),
            ("Currency Converter", "Live exchange rates between currencies."),
            ("Calculator",         "Arithmetic for cost comparisons and ranking."),
            ("News API",           "Recent travel news and destination advisories."),
            ("Booking API",        "Confirms real-time reservation availability."),
            ("Transit API",        "Local ground transport options and fare estimates."),
        ],
        "optimal":    frozenset(["Flight Search API", "Weather API", "Reviews API"]),
        "acceptable": [
            frozenset(["Flight Search API", "Weather API", "Reviews API"]),
            frozenset(["Flight Search API", "Weather API", "Reviews API", "Calculator"]),
            frozenset(["Flight Search API", "Weather API", "Reviews API", "Maps API"]),
        ],
        "base_score": 60,
        "lives": 3,
    },
    "hard": {
        "label":   "Level 03 — Hard",
        "accent":  "#ff6b6b",
        "title":   "Budget-Constrained Itinerary Planner",
        "instructions": (
            "Multi-step planning under a strict budget ceiling. "
            "A gap at any single reasoning step can cascade into total failure. "
            "Select up to 5 tools."
        ),
        "task": (
            "Plan a complete 3-day solo trip to Europe covering flights, accommodation, "
            "and a per-day spending estimate — guaranteed under $1,500 USD total. "
            "Produce a day-by-day itinerary with itemised cost breakdown."
        ),
        "tool_pool": [
            ("Flight Search API",     "Queries flights and round-trip prices."),
            ("Hotel Finder API",      "Searches hotel rates and multi-night availability."),
            ("Calculator",            "Aggregates and verifies total cost against a budget ceiling."),
            ("Weather API",           "Destination weather forecasts."),
            ("Reviews API",           "Destination and property quality scores."),
            ("Maps API",              "Geographic context and neighbourhood data."),
            ("Currency Converter",    "Converts local prices to USD using live rates."),
            ("News API",              "Travel advisories and safety alerts."),
            ("Booking API",           "Real-time reservation confirmation."),
            ("Dining & Activity API", "Local food, activity, and attraction cost estimates."),
            ("Transit API",           "In-city transport options and fare estimates."),
            ("Google Search",         "General web research and travel guides."),
        ],
        "optimal":    frozenset(["Flight Search API", "Hotel Finder API", "Calculator"]),
        "acceptable": [
            frozenset(["Flight Search API", "Hotel Finder API", "Calculator"]),
            frozenset(["Flight Search API", "Hotel Finder API", "Calculator", "Currency Converter"]),
            frozenset(["Flight Search API", "Hotel Finder API", "Calculator", "Dining & Activity API"]),
        ],
        "base_score": 80,
        "lives": 3,
    },
    "expert": {
        "label":   "Level 04 — Expert",
        "accent":  "#b06bff",
        "title":   "The Trending Destination Trap",
        "instructions": (
            "Read the task carefully before reaching for familiar tools. "
            "The framing may trigger instincts built from earlier levels — resist them. "
            "Consider precisely what category of information is being requested."
        ),
        "task": (
            "A travel brand wants to identify which European destination is generating the most "
            "organic social buzz and travel intent signals right now, to prioritise their next campaign. "
            "Identify the top destination and summarise the supporting evidence."
        ),
        "tool_pool": [
            ("Flight Search API",  "Queries flights and prices between cities."),
            ("Hotel Finder API",   "Searches hotel rates and availability."),
            ("Weather API",        "Current and forecast weather conditions."),
            ("Reviews API",        "Aggregate visitor ratings and satisfaction scores."),
            ("Maps API",           "Geographic data and distance calculations."),
            ("Google Search",      "Broad web research, real-time articles, and content indexing."),
            ("Social Trends API",  "Indexes trending mentions, hashtags, and content velocity across platforms."),
            ("News API",           "Recent articles, destination coverage, and media volume."),
            ("Booking API",        "Real-time reservation demand and availability data."),
            ("Currency Converter", "Live exchange rates."),
            ("Calculator",         "Arithmetic and numeric comparisons."),
            ("Transit API",        "In-city ground transport data."),
        ],
        "optimal":    frozenset(["Social Trends API", "Google Search", "News API"]),
        "acceptable": [
            frozenset(["Social Trends API", "Google Search", "News API"]),
            frozenset(["Social Trends API", "News API"]),
            frozenset(["Social Trends API", "Google Search"]),
        ],
        "base_score": 100,
        "lives": 3,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL DIALOG ENGINE
# All failure lines describe what the agent COULD NOT DO — never name the tool.
# ─────────────────────────────────────────────────────────────────────────────

def build_terminal_lines(level_key: str, tools: frozenset, success: bool) -> list:
    T = tools

    # ── EASY ─────────────────────────────────────────────────────────────────
    if level_key == "easy":
        L = [
            ("goal",    "OBJECTIVE   Find the best sunny European beach destination for a trip departing next week."),
            ("info",    "LOADOUT     " + " | ".join(sorted(T))),
            ("sep",     ""),
            ("thought", "Step 1   Survey European coastal regions for favourable weather over the coming week."),
        ]
        if "Weather API" in T:
            L += [("ok", "Retrieved 7-day forecast data   Algarve 27°C clear  ·  Barcelona 25°C clear  ·  Amalfi 23°C partly cloudy  ·  Dubrovnik 26°C clear")]
        else:
            L += [("guess", "!  Unable to retrieve live forecast data. Proceeding on general seasonal assumptions — result is unverified.")]

        L += [("thought", "Step 2   Identify available departing flights to shortlisted candidates.")]
        if "Flight Search API" in T:
            L += [("ok", "Retrieved flight availability   Faro (Algarve) from $285 rt  ·  Barcelona from $312 rt  ·  Dubrovnik from $341 rt")]
        else:
            L += [("guess", "!  Unable to query live flight availability or pricing. Cannot confirm the destination is currently bookable.")]

        L += [("thought", "Step 3   Verify top candidate qualifies as a genuine coastal beach location.")]
        if "Maps API" in T:
            L += [("ok", "Retrieved geographic data   Algarve — 150 km Atlantic coastline confirmed, multiple resort areas")]
        elif "Hotel Finder API" in T:
            L += [("ok", "Retrieved property data   Beachfront hotels found in Algarve — coastal access inferred from listings")]
        else:
            L += [("guess", "!  Unable to verify coastal classification. Assuming beach access based on destination name alone.")]

        L.append(("sep", ""))
        if success:
            L.append(("result_ok",   "RESULT   Algarve, Portugal recommended. Sunny forecast verified. Flights from $285. Coastal access confirmed."))
        else:
            L.append(("result_fail", "RESULT   Recommendation produced. One or more constraints were inferred rather than verified — output reliability reduced."))
        return L

    # ── MEDIUM ────────────────────────────────────────────────────────────────
    if level_key == "medium":
        L = [
            ("goal",    "OBJECTIVE   Rank the three cheapest European cities with high ratings and no rain over the next 14 days."),
            ("info",    "LOADOUT     " + " | ".join(sorted(T))),
            ("sep",     ""),
            ("thought", "Step 1   Filter candidate destinations by precipitation forecast across the 14-day window."),
        ]
        if "Weather API" in T:
            L += [("ok", "Retrieved precipitation forecasts   Lisbon 1 mm  ·  Athens 0 mm  ·  Seville 2 mm  ·  Porto 3 mm  (Amsterdam 38 mm — excluded)")]
        else:
            L += [("guess", "!  Unable to retrieve rainfall forecasts. Rain constraint cannot be applied — results may include high-precipitation destinations.")]

        L += [("thought", "Step 2   Compare flight prices to surviving candidates.")]
        if "Flight Search API" in T:
            L += [("ok", "Retrieved flight prices   Seville $195  ·  Lisbon $210  ·  Porto $228  ·  Athens $265")]
        else:
            L += [("guess", "!  Unable to retrieve live pricing. Price ranking estimated from historical averages — may not reflect current fares.")]

        L += [("thought", "Step 3   Score each candidate on visitor satisfaction.")]
        if "Reviews API" in T:
            L += [("ok", "Retrieved aggregate ratings   Seville 4.7  ·  Lisbon 4.6  ·  Porto 4.5  ·  Athens 4.4")]
        elif "Google Search" in T:
            L += [("ok", "Retrieved qualitative signals via web search   Seville and Lisbon rank highest — qualitative, not aggregated")]
        else:
            L += [("guess", "!  Unable to retrieve visitor satisfaction data. Quality constraint omitted — shortlist may include low-rated destinations.")]

        L.append(("sep", ""))
        if success:
            L.append(("result_ok",   "RESULT   1) Seville $195 (4.7★, 2 mm)   2) Lisbon $210 (4.6★, 1 mm)   3) Athens $265 (4.4★, 0 mm). All constraints verified."))
        else:
            L.append(("result_fail", "RESULT   Shortlist produced. At least one constraint was inferred rather than retrieved — ranking reliability reduced."))
        return L

    # ── HARD ──────────────────────────────────────────────────────────────────
    if level_key == "hard":
        L = [
            ("goal",    "OBJECTIVE   Plan a verified 3-day solo Europe trip under $1,500 USD with itemised costs."),
            ("info",    "LOADOUT     " + " | ".join(sorted(T))),
            ("sep",     ""),
            ("thought", "Step 1   Source round-trip flights to a candidate destination."),
        ]
        if "Flight Search API" in T:
            L += [("ok", "Retrieved live flight data   Lisbon round-trip $338 — lowest qualifying option")]
        else:
            L += [("guess", "!  Unable to retrieve live flight prices. Estimating ~$400 from training priors — no live verification.")]

        L += [("thought", "Step 2   Find a 3-night hotel within remaining budget headroom.")]
        if "Hotel Finder API" in T:
            L += [("ok", "Retrieved hotel availability   Hotel Lisboa Central — $89/night × 3 = $267")]
        else:
            L += [("guess", "!  Unable to retrieve live accommodation data. Estimating $100/night × 3 = $300 — actual pricing unknown.")]

        L += [("thought", "Step 3   Estimate daily spend — meals, local transit, activities.")]
        if "Dining & Activity API" in T:
            L += [("ok", "Retrieved local cost data   Lisbon daily estimate $62/day × 3 = $186")]
        elif "Google Search" in T:
            L += [("ok", "Retrieved travel guide estimates via web search   $55–75/day mid-range — using midpoint $65 × 3 = $195 (approximate)")]
        else:
            L += [("guess", "!  Unable to retrieve daily cost data. Applying generic $80/day estimate — actual costs may exceed this materially.")]

        L += [("thought", "Step 4   Sum all line items and verify against the $1,500 budget ceiling.")]
        if "Calculator" in T:
            L += [("ok", "Computed total   $338 + $267 + $186 = $791 — confirmed within budget")]
        elif "Currency Converter" in T:
            L += [("ok", "Computed total with currency conversion   All items summed ≈ $812 — within budget (exchange rate applied)")]
        else:
            L += [("guess", "!  Unable to perform verified arithmetic. Summing manually in reasoning: ≈ $791. Rounding and conversion errors possible — budget compliance not guaranteed.")]

        L.append(("sep", ""))
        if success:
            L.append(("result_ok",   "RESULT   3-day Lisbon plan produced. Day 1 Alfama. Day 2 Sintra. Day 3 Belém + departure. Total $791 — verified under $1,500."))
        else:
            L.append(("result_fail", "RESULT   Itinerary produced. One or more cost items were estimated rather than retrieved. Budget compliance cannot be guaranteed."))
        return L

    # ── EXPERT ────────────────────────────────────────────────────────────────
    if level_key == "expert":
        L = [
            ("goal",    "OBJECTIVE   Identify the European destination generating the highest social buzz and travel intent right now."),
            ("info",    "LOADOUT     " + " | ".join(sorted(T))),
            ("sep",     ""),
            ("thought", "Step 1   Measure real-time content velocity and mention volume by destination."),
        ]
        if "Social Trends API" in T:
            L += [("ok", "Retrieved social signal data   Lisbon +340% WoW  ·  Tbilisi +280%  ·  Porto +195%")]
        else:
            L += [("guess", "!  Unable to retrieve real-time social signal data. Falling back to historical satisfaction metrics — these measure past visitor experience, not current organic content trends. These are distinct signal types.")]

        # Warn about wrong-tool choices without naming the right tool
        if "Flight Search API" in T and "Social Trends API" not in T:
            L += [("guess", "!  Booking volume data retrieved — however, reservation demand is a lagging indicator and does not directly measure social content generation or viral travel intent.")]
        if "Weather API" in T and "Social Trends API" not in T:
            L += [("guess", "!  Weather forecast data retrieved — however, climate conditions have no direct relationship to social media trend velocity or campaign-relevant buzz.")]
        if "Reviews API" in T and "Social Trends API" not in T:
            L += [("guess", "!  Visitor satisfaction scores retrieved — however, historical ratings reflect past experience, not whether a destination is currently generating organic content momentum.")]

        L += [("thought", "Step 2   Corroborate with editorial coverage and media mention volume.")]
        if "News API" in T:
            L += [("ok", "Retrieved editorial coverage data   Lisbon 47 travel features (30 days)  ·  Porto 29  ·  Tbilisi 22 — corroborates signal from Step 1")]
        else:
            L += [("guess", "!  Unable to retrieve editorial coverage data. Cannot corroborate the trend signal — recommendation confidence reduced.")]

        L += [("thought", "Step 3   Validate with broad web content search for organic intent signals.")]
        if "Google Search" in T:
            L += [("ok", "Retrieved web content signals   Lisbon travel search volume +210% YoY · multiple viral pieces confirmed · strong intent signal")]
        else:
            L += [("guess", "!  Unable to retrieve web content reach data. Organic intent signal unavailable.")]

        L.append(("sep", ""))
        if success:
            L.append(("result_ok",   "RESULT   Top destination: Lisbon. Social velocity +340% WoW, 47 editorial features, confirmed viral search intent. Campaign confidence: high."))
        else:
            L.append(("result_fail", "RESULT   Destination identified. However, the evidence drawn upon does not directly measure social buzz or real-time travel intent. The core campaign objective was not fully addressed."))
        return L

    return []

# ─────────────────────────────────────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────────────────────────────────────

def is_correct(level_key: str, selected: frozenset) -> bool:
    level = LEVELS[level_key]
    # Exact match with any acceptable set
    for acc in level["acceptable"]:
        if selected == acc:
            return True
    # Superset of optimal also accepted (more tools, lower efficiency score)
    if selected.issuperset(level["optimal"]) and len(selected) <= MAX_TOOLS:
        return True
    return False

def compute_score(level_key: str, lives: int, n_tools: int) -> int:
    base       = LEVELS[level_key]["base_score"]
    lives_bon  = lives * 8
    efficiency = max(0, (MAX_TOOLS - n_tools) * 6)
    return base + lives_bon + efficiency

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    background: #080810 !important;
    color: #d0d0e0 !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0c0c18 !important; border-bottom: 1px solid #1c1c2c !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #444466 !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    padding: 14px 32px !important; border-bottom: 2px solid transparent !important;
    transition: color .2s !important;
}
.stTabs [aria-selected="true"] {
    color: #a09bff !important; border-bottom: 2px solid #a09bff !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 28px !important; }

/* ── buttons — tool toggles (default) ── */
.stButton > button {
    background: #0e0e1e !important; color: #666688 !important;
    border: 1px solid #1c1c2c !important; border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important; font-weight: 500 !important;
    letter-spacing: 0.8px !important; text-transform: none !important;
    padding: 8px 14px !important; width: 100% !important;
    transition: border-color .15s, color .15s, background .15s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    border-color: #a09bff !important; color: #c0c0d8 !important;
    background: #14142a !important;
}
/* Deploy / action buttons inside .deploy-btn wrapper */
div.deploy-btn .stButton > button {
    background: #a09bff !important; color: #080810 !important;
    border: none !important; font-weight: 700 !important;
    font-size: 11px !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; padding: 10px 28px !important;
    width: auto !important;
}
div.deploy-btn .stButton > button:hover { opacity: .85 !important; background: #a09bff !important; }
div.deploy-btn .stButton > button:disabled { background: #181828 !important; color: #333355 !important; border: none !important; }
/* Refresh / clear buttons */
div.action-btn .stButton > button {
    background: transparent !important; color: #555577 !important;
    border: 1px solid #1c1c2c !important; font-size: 11px !important;
    letter-spacing: 1px !important; text-transform: uppercase !important;
    padding: 8px 20px !important; width: auto !important;
}
div.action-btn .stButton > button:hover { border-color: #a09bff !important; color: #d0d0e0 !important; }
/* Start button */
div.start-btn .stButton > button {
    background: #a09bff !important; color: #080810 !important;
    border: none !important; font-weight: 700 !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; width: auto !important;
}
.stButton > button:disabled { background: #181828 !important; color: #333355 !important; border-color: #181828 !important; cursor: not-allowed !important; }

/* ── text input ── */
.stTextInput input {
    background: #0c0c18 !important; border: 1px solid #1c1c2c !important;
    color: #d0d0e0 !important; border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important; font-size: 14px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus { border-color: #a09bff !important; outline: none !important; }

/* ── HIDE the hidden bridge input ── */
[data-testid="stTextInput"]:has(input[aria-label*="_dnd_hidden_"]) {
    display: none !important;
}

/* ── Confirm button styling ── */
div.confirm-btn .stButton > button {
    background: #f7c948 !important; color: #080810 !important;
    border: none !important; font-weight: 700 !important;
    font-size: 11px !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; padding: 10px 28px !important;
    width: auto !important;
}
div.confirm-btn .stButton > button:hover { opacity: .85 !important; background: #f7c948 !important; }

/* ── Inline start button alignment ── */
div.inline-start-btn {
    margin-top: -8px !important;
}
div.inline-start-btn .stButton > button {
    background: #a09bff !important; color: #080810 !important;
    border: none !important; font-weight: 700 !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; width: 100% !important;
    height: 42px !important;
}

/* ── metrics ── */
[data-testid="metric-container"] {
    background: #0c0c18 !important; border: 1px solid #1c1c2c !important;
    border-radius: 6px !important; padding: 16px 20px !important;
}
[data-testid="metric-container"] label {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 9px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important; color: #444466 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important; font-size: 24px !important;
    font-weight: 800 !important; color: #f7c948 !important;
}

/* ── radio ── */
.stRadio > label { display: none !important; }
.stRadio > div { gap: 8px !important; flex-wrap: wrap !important; }
.stRadio label {
    background: #0c0c18 !important; border: 1px solid #1c1c2c !important;
    border-radius: 4px !important; padding: 8px 20px !important; font-size: 12px !important;
    font-family: 'IBM Plex Mono', monospace !important; color: #444466 !important;
    cursor: pointer !important; transition: border-color .15s, color .15s !important;
}
.stRadio label:hover { border-color: #a09bff !important; color: #d0d0e0 !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: #1c1c2c; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #a09bff; }

hr { border-color: #1c1c2c !important; margin: 24px 0 !important; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# DRAG-AND-DROP COMPONENT  (sole source of truth for tool selection)
# Uses Streamlit component value API to return selection back to Python.
# ─────────────────────────────────────────────────────────────────────────────

def drag_drop_selector(sel_key: str, tool_pool: list, level_key: str) -> tuple:
    """
    Drag-and-drop tool selector with a Confirm button to sync selection.
    
    Returns (confirmed_tools, pending_tools, needs_confirm):
    - confirmed_tools: list of tools that have been confirmed
    - pending_tools: list from the JS component (may differ if user dragged but didn't confirm)
    - needs_confirm: True if there are unconfirmed changes
    """
    hidden_key = f"_dnd_hidden_{sel_key}"
    confirmed_key = f"_confirmed_{sel_key}"
    
    # Initialize confirmed selection in session state
    if confirmed_key not in st.session_state:
        st.session_state[confirmed_key] = []
    
    confirmed = st.session_state[confirmed_key]
    valid = {n for n, _ in tool_pool}
    confirmed = [c for c in confirmed if c in valid][:MAX_TOOLS]
    
    pool_json = json.dumps([{"name": n, "desc": d} for n, d in tool_pool])
    sel_json  = json.dumps(confirmed)

    # Unique DOM id so multiple levels don't clash when switching tabs
    uid = sel_key.replace(" ", "_")

    component_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'IBM Plex Mono','Courier New',monospace; background:transparent; color:#d0d0e0; user-select:none; font-size:12px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
  .col-label {{ font-size:9px; letter-spacing:2px; text-transform:uppercase; color:#444466; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }}
  .status {{ font-size:9px; letter-spacing:1.5px; }}
  .n-ok {{ color:#3dffa0; }} .n-warn {{ color:#f7c948; }} .n-neutral {{ color:#555577; }}
  .panel {{ background:#0c0c18; border:1px solid #1c1c2c; border-radius:6px; padding:12px; max-height:400px; overflow-y:auto; }}
  .loadout-panel {{ border-color:#24243a; background:#09091a; min-height:180px; }}
  .chip {{ display:flex; align-items:flex-start; gap:10px; background:#111122; border:1px solid #1c1c2c; border-radius:4px; padding:9px 11px; margin-bottom:6px; cursor:grab; transition:border-color .12s,background .12s,opacity .12s; }}
  .chip:active {{ cursor:grabbing; }}
  .chip:hover {{ border-color:#a09bff; background:#14142a; }}
  .chip.dragging {{ opacity:.3; }}
  .chip.equipped {{ background:rgba(160,155,255,.07); border-color:rgba(160,155,255,.3); cursor:pointer; }}
  .chip.equipped:hover {{ border-color:#ff6b6b; background:rgba(255,107,107,.05); }}
  .handle {{ color:#2a2a44; font-size:14px; line-height:1.2; flex-shrink:0; margin-top:1px; }}
  .chip-name {{ font-weight:600; color:#c8c8d8; font-size:11px; line-height:1.3; }}
  .chip-desc {{ color:#3a3a55; font-size:10px; line-height:1.4; margin-top:2px; font-family:'Inter',sans-serif; }}
  .dropzone {{ min-height:52px; border:1px dashed #1c1c2c; border-radius:4px; display:flex; align-items:center; justify-content:center; color:#222240; font-size:9px; letter-spacing:1.5px; text-transform:uppercase; transition:border-color .12s,background .12s,color .12s; padding:10px; margin-top:4px; }}
  .dropzone.over {{ border-color:#a09bff; background:rgba(160,155,255,.04); color:#a09bff; }}
  .remove-hint {{ font-size:9px; letter-spacing:1px; color:#2a2a44; text-align:center; margin-top:8px; font-family:'Inter',sans-serif; }}
</style>
</head>
<body>
<div class="grid">
  <div>
    <div class="col-label">Tool Pool <span class="status n-neutral" id="{uid}-pool-count"></span></div>
    <div class="panel" id="{uid}-pool"></div>
  </div>
  <div>
    <div class="col-label">Loadout <span class="status" id="{uid}-lo-count"></span></div>
    <div class="panel loadout-panel" id="{uid}-loadout"></div>
    <div class="remove-hint" id="{uid}-hint"></div>
  </div>
</div>
<input type="hidden" id="{uid}-output" value="{"|".join(confirmed)}">

<script>
const MAX  = {MAX_TOOLS};
const POOL = {pool_json};
let sel    = {sel_json};

function updateHiddenInput() {{
  document.getElementById('{uid}-output').value = sel.join('|');
  // Also try to update the Streamlit text input
  try {{
    const inputs = window.parent.document.querySelectorAll('input[type="text"]');
    for (const inp of inputs) {{
      const container = inp.closest('[data-testid="stTextInput"]');
      if (container) {{
        const label = container.querySelector('label');
        if (label && label.textContent.trim() === '{hidden_key}') {{
          const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
          nativeInputValueSetter.call(inp, sel.join('|'));
          inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
          inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
          return;
        }}
      }}
    }}
  }} catch(e) {{ }}
}}

function mkChip(t, equipped) {{
  const d = document.createElement('div');
  d.className = 'chip' + (equipped ? ' equipped' : '');
  d.draggable = !equipped;
  d.dataset.name = t.name;
  d.innerHTML = '<span class="handle">⠿</span><div><div class="chip-name">' + t.name + '</div><div class="chip-desc">' + t.desc + '</div></div>';
  if (!equipped) {{
    d.addEventListener('dragstart', e => {{
      e.dataTransfer.setData('text/plain', t.name);
      e.dataTransfer.effectAllowed = 'move';
      setTimeout(() => d.classList.add('dragging'), 0);
    }});
    d.addEventListener('dragend', () => d.classList.remove('dragging'));
  }} else {{
    d.title = 'Click to remove';
    d.addEventListener('click', () => {{ sel = sel.filter(x => x !== t.name); render(); updateHiddenInput(); }});
  }}
  return d;
}}

function mkDropzone() {{
  const dz = document.createElement('div');
  dz.className = 'dropzone';
  dz.textContent = sel.length === 0 ? 'Drag tools here to equip' : '+ drag another tool';
  dz.addEventListener('dragover', e => {{ e.preventDefault(); e.dataTransfer.dropEffect='move'; dz.classList.add('over'); }});
  dz.addEventListener('dragleave', () => dz.classList.remove('over'));
  dz.addEventListener('drop', e => {{
    e.preventDefault(); dz.classList.remove('over');
    const name = e.dataTransfer.getData('text/plain');
    if (name && !sel.includes(name) && sel.length < MAX) {{ sel.push(name); render(); updateHiddenInput(); }}
  }});
  return dz;
}}

function render() {{
  const poolEl = document.getElementById('{uid}-pool');
  poolEl.innerHTML = '';
  POOL.forEach(t => {{ if (!sel.includes(t.name)) poolEl.appendChild(mkChip(t, false)); }});
  document.getElementById('{uid}-pool-count').textContent = (POOL.length - sel.length) + ' available';

  const loEl = document.getElementById('{uid}-loadout');
  loEl.innerHTML = '';
  sel.forEach(name => {{ const t = POOL.find(x => x.name === name); if (t) loEl.appendChild(mkChip(t, true)); }});
  if (sel.length < MAX) loEl.appendChild(mkDropzone());

  const n = sel.length;
  const cls = n === 0 ? 'n-neutral' : n <= 3 ? 'n-ok' : 'n-warn';
  const cEl = document.getElementById('{uid}-lo-count');
  cEl.className = 'status ' + cls;
  cEl.textContent = n === 0 ? '0 / ' + MAX : n + ' / ' + MAX + ' equipped';
  document.getElementById('{uid}-hint').textContent = sel.length > 0 ? 'Click an equipped tool to remove it' : '';
}}

render();
</script>
</body>
</html>
"""
    # Fixed height with scrolling inside the component
    height = 460
    components.html(component_html, height=height)

    # Hidden text input that JS updates when user drags tools
    pending_val = st.text_input(
        hidden_key,
        value="|".join(confirmed),
        key=hidden_key,
        label_visibility="collapsed",
    )
    
    # Parse pending selection from the hidden input
    pending = [v for v in pending_val.split("|") if v and v in valid] if pending_val else []
    pending = pending[:MAX_TOOLS]
    
    return confirmed, pending

# ─────────────────────────────────────────────────────────────────────────────
# AGENT STARTUP ANIMATION
# ─────────────────────────────────────────────────────────────────────────────

def agent_startup_animation(task: str, tools: list):
    n = len(tools)
    tool_rows = "".join(
        f'<div class="trow" style="animation-delay:{0.5 + i * 0.12}s">'
        f'<span class="dot" style="animation-delay:{0.5 + i * 0.12}s"></span>'
        f'{html.escape(t)}</div>'
        for i, t in enumerate(sorted(tools))
    )
    done = 0.5 + n * 0.12 + 0.28

    anim = f"""
<div style="background:#04040e;border:1px solid #1c1c2c;border-radius:8px;
            padding:24px 28px;margin-bottom:14px;
            font-family:'IBM Plex Mono','Courier New',monospace;font-size:12px;">
<style>
  @keyframes fi   {{ from{{opacity:0;transform:translateY(4px)}} to{{opacity:1;transform:none}} }}
  @keyframes pu   {{ 0%,100%{{opacity:1}} 50%{{opacity:.2}} }}
  @keyframes scan {{ from{{width:0}} to{{width:100%}} }}
  .ar  {{ animation:fi .32s ease both; }}
  .trow{{ animation:fi .28s ease both; color:#5a5a80; padding:3px 0;
           display:flex; align-items:center; gap:8px; }}
  .dot {{ width:5px;height:5px;border-radius:50%;background:#a09bff;
           display:inline-block;animation:pu 1.1s infinite; }}
  .sb  {{ height:1px;background:linear-gradient(90deg,transparent,#a09bff33,transparent);
           animation:scan .9s ease-out both; margin:10px 0; }}
  .lbl {{ font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#222240;margin-bottom:6px; }}
</style>
<div class="ar lbl" style="animation-delay:.0s">System</div>
<div class="ar"     style="animation-delay:.04s;color:#444466;">
  AGENT INITIALISING&nbsp;<span style="color:#a09bff;animation:pu .7s infinite;display:inline-block;">▌</span>
</div>
<div class="sb"     style="animation-delay:.14s"></div>
<div class="ar lbl" style="animation-delay:.22s;margin-top:2px;">Objective</div>
<div class="ar"     style="animation-delay:.26s;color:#7070a0;font-size:11px;line-height:1.65;">{html.escape(task)}</div>
<div class="sb"     style="animation-delay:.38s"></div>
<div class="ar lbl" style="animation-delay:.44s;margin-top:2px;">Loadout Registered</div>
{tool_rows}
<div class="sb"     style="animation-delay:{done - .06}s"></div>
<div class="ar"     style="animation-delay:{done}s;color:#3dffa0;">+ AGENT ONLINE — EXECUTING</div>
</div>
"""
    st.markdown(anim, unsafe_allow_html=True)
    time.sleep(done + 0.45)

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL RENDERER
# ─────────────────────────────────────────────────────────────────────────────

_TC = {
    "goal":        "#f7c948",
    "info":        "#a09bff",
    "sep":         "",
    "thought":     "#555577",
    "ok":          "#3dffa0",
    "fail":        "#ff6b6b",   # kept for internal use but never shown as a bare line
    "guess":       "#d08040",
    "result_ok":   "#3dffa0",
    "result_fail": "#ff6b6b",
}
_TD = {
    "goal":.06, "info":.06, "sep":.02,
    "thought":.32, "ok":.22, "fail":.18, "guess":.42,
    "result_ok":.08, "result_fail":.08,
}
_BOLD = {"goal", "guess", "result_ok", "result_fail"}

TERM_WRAP_OPEN = """
<div id="terminal-anchor" style="height:1px;margin-bottom:10px;"></div>
<div style="background:#04040e;border:1px solid #1c1c2c;border-radius:8px;overflow:hidden;">
  <div style="background:#0a0a16;padding:10px 16px;display:flex;align-items:center;
              gap:8px;border-bottom:1px solid #1c1c2c;">
    <div style="width:9px;height:9px;border-radius:50%;background:#ff5f57;"></div>
    <div style="width:9px;height:9px;border-radius:50%;background:#febc2e;"></div>
    <div style="width:9px;height:9px;border-radius:50%;background:#28c840;"></div>
    <span style="margin-left:10px;font-family:IBM Plex Mono,monospace;font-size:10px;
                 color:#222240;letter-spacing:1.5px;">AGENT TERMINAL</span>
  </div>
  <div style="padding:22px 26px;font-family:IBM Plex Mono,monospace;font-size:12px;line-height:1.9;">
"""
TERM_WRAP_CLOSE = "  </div></div>"

def render_terminal_animated(lines: list):
    holder   = st.empty()
    rendered = []

    for typ, text in lines:
        # Skip bare "fail" lines — failures are always followed by a guess line
        # that describes the capability gap; we don't want to expose tool names.
        if typ == "fail":
            time.sleep(_TD.get(typ, .1))
            continue

        time.sleep(_TD.get(typ, .1))
        color = _TC.get(typ, "#d0d0e0")
        bold  = "700" if typ in _BOLD else "400"

        if typ == "sep":
            rendered.append('<div style="border-bottom:1px solid #161628;margin:10px 0;"></div>')
        else:
            prefix = {
                "ok":          '<span style="color:#3dffa0;margin-right:10px;font-weight:700;">+</span>',
                "guess":       '<span style="color:#d08040;margin-right:10px;font-weight:700;">!</span>',
                "result_ok":   '<span style="color:#3dffa0;margin-right:10px;">&gt;</span>',
                "result_fail": '<span style="color:#ff6b6b;margin-right:10px;">&gt;</span>',
            }.get(typ, "")
            rendered.append(
                f'<div style="margin-bottom:2px;color:{color};font-weight:{bold};">'
                f'{prefix}{html.escape(text)}</div>'
            )

        cursor = '<span style="color:#a09bff;opacity:.6;">▌</span>'
        holder.markdown(
            TERM_WRAP_OPEN + "".join(rendered) + cursor + TERM_WRAP_CLOSE,
            unsafe_allow_html=True,
        )

    # Final render, no cursor
    holder.markdown(
        TERM_WRAP_OPEN + "".join(rendered) + TERM_WRAP_CLOSE,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-SCROLL
# ─────────────────────────────────────────────────────────────────────────────

def scroll_to_terminal():
    st.markdown("""
<script>
(function(){
  var t=0;
  function go(){
    var el=document.getElementById('terminal-anchor');
    if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}
    else if(t++<25){setTimeout(go,100);}
  }
  go();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "team_name":       "",
        "lives":           {k: LEVELS[k]["lives"] for k in LEVEL_ORDER},
        "level_scores":    {k: 0 for k in LEVEL_ORDER},
        "level_complete":  {k: False for k in LEVEL_ORDER},
        "terminal_data":   None,          # (level_key, lines, success, tools_list)
        "last_deploy_ts":  {k: 0.0 for k in LEVEL_ORDER},  # per-level cooldown
        "deploy_error":    "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# GAME TAB
# ─────────────────────────────────────────────────────────────────────────────

def game_tab():
    # ── HEADER ───────────────────────────────────────────────────────────────
    st.markdown("""
<div style="padding:28px 0 4px;">
  <div style="
    font-family: Syne, sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    text-shadow:
      -1px -1px 0 #ff8c00,
       1px -1px 0 #ff8c00,
      -1px  1px 0 #ff8c00,
       1px  1px 0 #ff8c00;
    margin-bottom: 4px;
    line-height: 1.1;
  ">Aggie Data Science Club (ADSC)</div>
  <div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;
              text-transform:uppercase;color:#333355;margin-bottom:14px;">
    Workshop — AI Agents &amp; Tool Use
  </div>
  <h1 style="font-family:Syne,sans-serif;font-size:34px;font-weight:800;
             color:#d0d0e0;letter-spacing:-1px;line-height:1.1;margin-bottom:10px;">
    The Tool Loadout Challenge
  </h1>
  <p style="color:#333355;font-size:14px;max-width:520px;line-height:1.7;">
    Equip your agent with the right tools. Watch it reason through the task.
    Learn from every inference failure.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── TEAM NAME GATE ────────────────────────────────────────────────────────
    if not st.session_state.team_name:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:IBM Plex Mono,monospace;font-size:9px;'
            'letter-spacing:2px;text-transform:uppercase;color:#444466;margin-bottom:8px;">'
            'Team Name</p>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([5, 1], gap="small")
        with c1:
            team_input = st.text_input(
                "team_name_input",
                placeholder="Enter your team name",
                label_visibility="collapsed",
                key="team_name_field",
            )
        with c2:
            st.markdown('<div class="inline-start-btn">', unsafe_allow_html=True)
            clicked = st.button("Start", key="start_btn", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Read value from session_state via widget key — safe across column scopes
        if clicked:
            raw = st.session_state.get("team_name_field", "")
            cleaned, err = sanitize_team_name(raw)
            if err:
                st.error(err)
            elif cleaned:
                st.session_state.team_name = cleaned
                st.rerun()
        return

    # ── LEVEL SELECTOR ───────────────────────────────────────────────────────
    st.markdown(
        f'<p style="font-family:IBM Plex Mono,monospace;font-size:10px;letter-spacing:1.5px;'
        f'color:#333355;margin-bottom:14px;">TEAM — '
        f'<span style="color:#f7c948;">{st.session_state.team_name}</span></p>',
        unsafe_allow_html=True,
    )

    level_key = st.radio(
        "Level",
        options=LEVEL_ORDER,
        format_func=lambda k: LEVELS[k]["label"],
        horizontal=True,
        label_visibility="collapsed",
        key="level_radio",
    )
    level = LEVELS[level_key]
    acc   = level["accent"]

    st.markdown("<hr>", unsafe_allow_html=True)

    col_main, col_ref = st.columns([5, 3], gap="large")

    # ── LEFT COLUMN ───────────────────────────────────────────────────────────
    with col_main:
        # Task card
        st.markdown(f"""
<div style="background:#0a0a16;border:1px solid #1c1c2c;border-radius:8px;
            padding:22px 26px;border-left:3px solid {acc};margin-bottom:20px;">
  <div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;
              text-transform:uppercase;color:{acc};margin-bottom:8px;">{level['label']}</div>
  <h2 style="font-family:Syne,sans-serif;font-size:18px;font-weight:800;
             color:#d0d0e0;margin-bottom:12px;">{level['title']}</h2>
  <p style="color:#444466;font-size:13px;line-height:1.7;margin-bottom:16px;">{level['instructions']}</p>
  <div style="background:#050510;border:1px solid #141424;border-radius:5px;padding:14px 18px;">
    <div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;
                text-transform:uppercase;color:#222240;margin-bottom:6px;">Task</div>
    <div style="font-size:13.5px;color:#b0b0c8;line-height:1.75;">{level['task']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Stats
        lives_left = st.session_state.lives[level_key]
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Lives", ROMAN.get(lives_left, "0"))
        with sc2:
            st.metric("Level Score", st.session_state.level_scores[level_key])
        with sc3:
            st.metric("Total Score", sum(st.session_state.level_scores.values()))

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── TOOL SELECTOR (drag-and-drop only) ───────────────────────────────
        sel_key = f"sel_{level_key}"
        confirmed_key = f"_confirmed_{sel_key}"
        
        # Initialize confirmed selection
        if confirmed_key not in st.session_state:
            st.session_state[confirmed_key] = []

        confirmed, pending = drag_drop_selector(sel_key=sel_key, tool_pool=level["tool_pool"], level_key=level_key)
        
        n_confirmed = len(confirmed)
        n_pending = len(pending)
        has_pending_changes = (set(pending) != set(confirmed)) and n_pending > 0
        
        is_complete = st.session_state.level_complete[level_key]
        no_lives    = lives_left <= 0
        now_ts      = time.time()
        last_ts     = st.session_state.last_deploy_ts[level_key]
        on_cooldown = (now_ts - last_ts) < DEPLOY_COOLDOWN
        cd_remaining= max(0, int(DEPLOY_COOLDOWN - (now_ts - last_ts)))

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Show Confirm Tools button if there are pending changes
        if has_pending_changes and not is_complete and not no_lives:
            st.markdown(
                f'<p style="font-family:IBM Plex Mono,monospace;font-size:10px;'
                f'color:#f7c948;margin-bottom:8px;">{n_pending} tool{"s" if n_pending != 1 else ""} selected — click Confirm to lock in your loadout.</p>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="confirm-btn">', unsafe_allow_html=True)
            if st.button("Confirm Tools", key=f"confirm_{level_key}"):
                st.session_state[confirmed_key] = pending.copy()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        elif n_confirmed == 0:
            st.markdown(
                '<p style="font-family:IBM Plex Mono,monospace;font-size:10px;'
                'color:#333355;margin-bottom:8px;">Drag tools into your loadout, then confirm to deploy.</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<p style="font-family:IBM Plex Mono,monospace;font-size:10px;'
                f'color:#3dffa0;margin-bottom:8px;">{n_confirmed} tool{"s" if n_confirmed != 1 else ""} confirmed and ready.</p>',
                unsafe_allow_html=True,
            )

        # Deploy button - only enabled if tools are confirmed
        deploy_disabled = (n_confirmed == 0 or is_complete or no_lives or on_cooldown)
        st.markdown('<div class="deploy-btn">', unsafe_allow_html=True)
        deploy_clicked  = st.button(
            "Deploy Agent",
            disabled=False,
            key=f"deploy_{level_key}",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Cooldown notice (static, no buggy countdown in button label)
        if on_cooldown and not is_complete and not no_lives:
            st.markdown(
                f'<p style="font-family:IBM Plex Mono,monospace;font-size:10px;'
                f'color:#444466;margin-top:6px;">Cooldown active — retry in {cd_remaining}s.</p>',
                unsafe_allow_html=True,
            )

        if deploy_clicked and not deploy_disabled:
            st.session_state.deploy_error = ""
            st.session_state.last_deploy_ts[level_key] = now_ts

            sel_frozen = frozenset(confirmed)
            success    = is_correct(level_key, sel_frozen)
            lines      = build_terminal_lines(level_key, sel_frozen, success)
            st.session_state.terminal_data = (level_key, lines, success, list(confirmed))

            if success:
                score = compute_score(level_key, lives_left, n_confirmed)
                st.session_state.level_scores[level_key]  = score
                st.session_state.level_complete[level_key] = True
                upsert_leaderboard(st.session_state.team_name, level_key, score)
            else:
                st.session_state.lives[level_key] = max(0, lives_left - 1)

            st.rerun()

        # Status banners
        if is_complete:
            st.markdown(
                f'<div style="background:rgba(61,255,160,.04);border:1px solid rgba(61,255,160,.15);'
                f'border-radius:5px;padding:10px 16px;margin-top:10px;'
                f'font-family:IBM Plex Mono,monospace;font-size:11px;color:#3dffa0;">'
                f'Level complete — {st.session_state.level_scores[level_key]} pts recorded.</div>',
                unsafe_allow_html=True,
            )
        if no_lives and not is_complete:
            st.markdown(
                '<div style="background:rgba(255,107,107,.04);border:1px solid rgba(255,107,107,.15);'
                'border-radius:5px;padding:10px 16px;margin-top:10px;'
                'font-family:IBM Plex Mono,monospace;font-size:11px;color:#ff6b6b;">'
                'No lives remaining for this level. Select a different level.</div>',
                unsafe_allow_html=True,
            )

    # ── RIGHT COLUMN — tool reference ─────────────────────────────────────────
    with col_ref:
        st.markdown(
            '<p style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;'
            'text-transform:uppercase;color:#333355;margin-bottom:12px;">Tool Reference</p>',
            unsafe_allow_html=True,
        )
        for name, desc in level["tool_pool"]:
            st.markdown(f"""
<div style="background:#0a0a16;border:1px solid #1c1c2c;border-radius:5px;
            padding:10px 14px;margin-bottom:6px;display:flex;gap:12px;align-items:flex-start;">
  <div style="width:5px;height:5px;border-radius:50%;background:{acc};
              margin-top:6px;flex-shrink:0;"></div>
  <div>
    <div style="font-size:12px;font-weight:600;color:#b0b0c8;">{name}</div>
    <div style="font-size:11px;color:#2e2e48;line-height:1.5;margin-top:2px;">{desc}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── TERMINAL SECTION ─────────────────────────────────────────────────────
    td = st.session_state.terminal_data
    if td is not None:
        tk, tlines, tsuccess, ttools = td
        if tk == level_key:
            st.markdown("<hr>", unsafe_allow_html=True)
            scroll_to_terminal()

            if tsuccess:
                st.markdown(
                    '<div style="background:rgba(61,255,160,.04);border:1px solid rgba(61,255,160,.15);'
                    'border-radius:5px;padding:11px 20px;margin-bottom:12px;'
                    'font-family:IBM Plex Mono,monospace;font-size:12px;">'
                    '<span style="color:#3dffa0;font-weight:700;">Correct loadout.</span>'
                    ' <span style="color:#444466;">Agent completed the task successfully.</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                lives_now = st.session_state.lives[level_key]
                st.markdown(
                    f'<div style="background:rgba(255,107,107,.04);border:1px solid rgba(255,107,107,.15);'
                    f'border-radius:5px;padding:11px 20px;margin-bottom:12px;'
                    f'font-family:IBM Plex Mono,monospace;font-size:12px;">'
                    f'<span style="color:#ff6b6b;font-weight:700;">Incorrect loadout.</span>'
                    f' <span style="color:#444466;">Agent had to infer missing data. '
                    f'Lives remaining: {ROMAN.get(lives_now, "0")}</span></div>',
                    unsafe_allow_html=True,
                )

            agent_startup_animation(LEVELS[level_key]["task"], ttools)
            render_terminal_animated(tlines)

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD TAB
# ─────────────────────────────────────────────────────────────────────────────

def leaderboard_tab():
    st.markdown("""
<div style="margin-bottom:24px;">
  <div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:3px;
              text-transform:uppercase;color:#a09bff;margin-bottom:10px;">Live Rankings</div>
  <h2 style="font-family:Syne,sans-serif;font-size:26px;font-weight:800;
             color:#d0d0e0;margin-bottom:6px;">Leaderboard</h2>
  <p style="color:#444466;font-size:13px;">
    One entry per team — cumulative score across all levels.
    Updates automatically each time a team improves their personal best.
  </p>
</div>
""", unsafe_allow_html=True)

    cr, cn = st.columns([1, 5])
    with cr:
        st.markdown('<div class="action-btn">', unsafe_allow_html=True)
        if st.button("Refresh", key="lb_refresh"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with cn:
        st.markdown(
            f'<p style="color:#1e1e30;font-family:IBM Plex Mono,monospace;font-size:10px;margin-top:10px;">'
            f'Last rendered: {datetime.now().strftime("%H:%M:%S")}</p>',
            unsafe_allow_html=True,
        )

    lb = load_leaderboard()

    if not lb:
        st.markdown("""
<div style="background:#0a0a16;border:1px dashed #1c1c2c;border-radius:8px;
            padding:64px;text-align:center;color:#1e1e30;margin-top:16px;
            font-family:IBM Plex Mono,monospace;font-size:11px;letter-spacing:1px;">
  No submissions yet.
</div>
""", unsafe_allow_html=True)
        return

    L_ACC = {"easy": "#3dffa0", "medium": "#f7c948", "hard": "#ff6b6b", "expert": "#b06bff"}

    # Table header
    st.markdown("""
<div style="display:grid;grid-template-columns:48px 1fr 90px 68px 68px 68px 68px 96px;
            gap:8px;padding:8px 18px;
            font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:1.5px;
            text-transform:uppercase;color:#1e1e30;border-bottom:1px solid #1c1c2c;margin-bottom:8px;">
  <div>Rank</div><div>Team</div>
  <div style="text-align:right;">Total</div>
  <div style="text-align:right;">L1</div>
  <div style="text-align:right;">L2</div>
  <div style="text-align:right;">L3</div>
  <div style="text-align:right;">L4</div>
  <div style="text-align:right;">Updated</div>
</div>
""", unsafe_allow_html=True)

    for i, entry in enumerate(lb):
        scores = entry.get("level_scores", {})
        top    = (i == 0)
        bg     = "rgba(160,155,255,.03)" if top else "transparent"
        bd     = "rgba(160,155,255,.14)" if top else "#1c1c2c"
        rank   = ["I", "II", "III"][i] if i < 3 else f"{i+1}"

        def lvl_cell(k):
            v = scores.get(k, 0)
            c = L_ACC.get(k, "#444466") if v else "#1c1c2c"
            w = "700" if v else "400"
            return f'<div style="text-align:right;color:{c};font-weight:{w};">{v if v else "—"}</div>'

        st.markdown(f"""
<div style="display:grid;grid-template-columns:48px 1fr 90px 68px 68px 68px 68px 96px;
            gap:8px;padding:13px 18px;
            background:{bg};border:1px solid {bd};border-radius:6px;margin-bottom:6px;
            align-items:center;font-family:IBM Plex Mono,monospace;font-size:12px;">
  <div style="color:#333355;font-family:Syne,sans-serif;font-size:13px;font-weight:700;">{rank}</div>
  <div style="font-family:Syne,sans-serif;font-weight:700;color:#d0d0e0;font-size:14px;">{entry['team']}</div>
  <div style="text-align:right;font-family:Syne,sans-serif;font-weight:800;color:#f7c948;font-size:16px;">{entry['total_score']}</div>
  {lvl_cell('easy')}{lvl_cell('medium')}{lvl_cell('hard')}{lvl_cell('expert')}
  <div style="text-align:right;color:#1e1e30;font-size:10px;">{entry.get('last_updated', '—')}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#1a1a28;'
        'letter-spacing:1px;margin-bottom:8px;">Facilitator controls</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="action-btn">', unsafe_allow_html=True)
    if st.button("Clear Leaderboard", key="lb_clear"):
        clear_leaderboard()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HOW TO PLAY TAB
# ─────────────────────────────────────────────────────────────────────────────

def howto_tab():
    st.markdown(
        '<h2 style="font-family:Syne,sans-serif;font-size:24px;font-weight:800;'
        'color:#d0d0e0;margin-bottom:6px;">How to Play</h2>'
        '<p style="color:#444466;font-size:13px;margin-bottom:24px;">Game mechanics and scoring reference.</p>',
        unsafe_allow_html=True,
    )

    blocks = [
        ("#a09bff", "The Loadout",
         "Each level shows a task and a tool pool on the right. Drag a tool from the pool panel into your "
         "loadout panel, or click an equipped tool to remove it. You may equip up to 5 tools, "
         "Fewer tools on a correct answer earns a higher efficiency bonus."),
        ("#ff6b6b", "Lives",
         "Each level starts with 3 lives, shown as Roman numerals (III → II → I → 0). "
         "An incorrect submission — where the agent cannot satisfy all task constraints without guessing — "
         "costs one life. Lives remaining at the time of a correct submission contribute a bonus to your score. "
         "At 0 lives, that level is locked."),
        ("#3dffa0", "The Terminal",
         "After deploying, an agent startup sequence runs, followed by a line-by-line trace of the agent's "
         "reasoning. Lines prefixed with + show successful data retrieval. Lines prefixed with ! show "
         "capability gaps — points where the agent had to infer missing information. "
         "Inference chains reduce output reliability and lead to failed outcomes."),
        ("#f7c948", "Scoring",
         "Score per correct submission = base score + (lives remaining × 8) + ((5 − tools used) × 6). "
         "The leaderboard shows your cumulative best across all four levels. "
         "A 30-second cooldown between submissions per level prevents rapid guessing."),
    ]

    for color, title, body in blocks:
        st.markdown(f"""
<div style="background:#0a0a16;border:1px solid #1c1c2c;border-radius:8px;
            padding:20px 24px;margin-bottom:12px;border-left:3px solid {color};">
  <h3 style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;
             color:#d0d0e0;margin-bottom:8px;">{title}</h3>
  <p style="color:#444466;font-size:13px;line-height:1.75;margin:0;">{body}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:#0a0a16;border:1px solid #1c1c2c;border-radius:8px;padding:20px 24px;margin-top:4px;">
<h3 style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#d0d0e0;margin-bottom:16px;">Score Reference</h3>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;font-family:IBM Plex Mono,monospace;">
  <div style="background:#050510;border:1px solid #1c1c2c;border-radius:5px;padding:14px;border-top:2px solid #3dffa0;">
    <div style="font-size:9px;letter-spacing:2px;color:#333355;text-transform:uppercase;margin-bottom:6px;">L1 — Easy</div>
    <div style="font-size:20px;color:#f7c948;font-weight:700;">40</div>
    <div style="font-size:10px;color:#222238;margin-top:3px;">base pts</div>
  </div>
  <div style="background:#050510;border:1px solid #1c1c2c;border-radius:5px;padding:14px;border-top:2px solid #f7c948;">
    <div style="font-size:9px;letter-spacing:2px;color:#333355;text-transform:uppercase;margin-bottom:6px;">L2 — Medium</div>
    <div style="font-size:20px;color:#f7c948;font-weight:700;">60</div>
    <div style="font-size:10px;color:#222238;margin-top:3px;">base pts</div>
  </div>
  <div style="background:#050510;border:1px solid #1c1c2c;border-radius:5px;padding:14px;border-top:2px solid #ff6b6b;">
    <div style="font-size:9px;letter-spacing:2px;color:#333355;text-transform:uppercase;margin-bottom:6px;">L3 — Hard</div>
    <div style="font-size:20px;color:#f7c948;font-weight:700;">80</div>
    <div style="font-size:10px;color:#222238;margin-top:3px;">base pts</div>
  </div>
  <div style="background:#050510;border:1px solid #1c1c2c;border-radius:5px;padding:14px;border-top:2px solid #b06bff;">
    <div style="font-size:9px;letter-spacing:2px;color:#333355;text-transform:uppercase;margin-bottom:6px;">L4 — Expert</div>
    <div style="font-size:20px;color:#f7c948;font-weight:700;">100</div>
    <div style="font-size:10px;color:#222238;margin-top:3px;">base pts</div>
  </div>
</div>
<p style="color:#222238;font-size:11px;font-family:IBM Plex Mono,monospace;margin-top:14px;">
  + 8 pts per life remaining &nbsp;·&nbsp; + 6 pts per unused tool slot (max efficiency at 3 tools)
</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()

    tab_game, tab_lb, tab_how = st.tabs(["Game", "Leaderboard", "How to Play"])
    with tab_game:
        game_tab()
    with tab_lb:
        leaderboard_tab()
    with tab_how:
        howto_tab()

if __name__ == "__main__":
    main()