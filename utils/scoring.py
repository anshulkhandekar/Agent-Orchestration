"""Deterministic scoring engine for all levels."""

RETRY_MULTIPLIERS = [1.00, 0.92, 0.85, 0.75]


def get_retry_multiplier(attempt: int) -> float:
    if attempt <= 0:
        return RETRY_MULTIPLIERS[0]
    idx = min(attempt - 1, len(RETRY_MULTIPLIERS) - 1)
    return RETRY_MULTIPLIERS[idx]


def compute_score(level_config: dict, decisions: dict, attempt_count: int) -> dict:
    """
    Compute score for a level.

    Args:
        level_config: contains 'max_score', 'categories' (list of {name, max, evaluator_key})
        decisions: player decisions dict
        attempt_count: which attempt this is (1-indexed)

    Returns:
        {"total": int, "breakdown": {category_name: int}}
    """
    breakdown = {}
    raw_total = 0

    for cat in level_config["categories"]:
        name = cat["name"]
        max_pts = cat["max"]
        eval_key = cat["evaluator_key"]
        score_pct = decisions.get(eval_key, 0.0)
        pts = int(max_pts * score_pct)
        breakdown[name] = pts
        raw_total += pts

    multiplier = get_retry_multiplier(attempt_count)
    total = int(raw_total * multiplier)
    breakdown["retry_multiplier"] = multiplier

    return {"total": total, "breakdown": breakdown}


# ── Level 1 Config ──
LEVEL1_CONFIG = {
    "max_score": 100,
    "categories": [
        {"name": "Correctness", "max": 60, "evaluator_key": "correctness"},
        {"name": "Efficiency", "max": 25, "evaluator_key": "efficiency"},
        {"name": "Outcome Quality", "max": 15, "evaluator_key": "outcome"},
    ],
}

LEVEL1_TOOLS = [
    {"id": "flights", "name": "Flights", "icon": "✈️", "desc": "Search & book flights"},
    {"id": "weather", "name": "Weather", "icon": "🌤️", "desc": "Check climate & forecast"},
    {"id": "events", "name": "Events", "icon": "🎉", "desc": "Local events & activities"},
    {"id": "maps", "name": "Maps", "icon": "🗺️", "desc": "Navigation & directions"},
    {"id": "currency", "name": "Currency", "icon": "💱", "desc": "Exchange rate converter"},
    {"id": "calculator", "name": "Calculator", "icon": "🔢", "desc": "Number crunching"},
    {"id": "restaurants", "name": "Restaurants", "icon": "🍽️", "desc": "Find places to eat"},
    {"id": "translation", "name": "Translation", "icon": "🌐", "desc": "Language translator"},
    {"id": "hotels", "name": "Hotels", "icon": "🏨", "desc": "Find accommodations"},
    {"id": "packing", "name": "Packing", "icon": "🧳", "desc": "Packing list generator"},
]

LEVEL1_CORRECT = {"flights", "weather", "hotels"}

LEVEL1_BRANCHES = {
    frozenset(["flights", "weather", "hotels"]): {
        "outcome": "Perfect! Reveille books a sunny beach getaway with great accommodation at a solid price.",
        "quality": 1.0,
    },
    frozenset(["flights", "hotels", "currency"]): {
        "outcome": "Reveille books flights and a hotel but picks a rainy week — no weather check!",
        "quality": 0.5,
    },
    frozenset(["flights", "weather", "maps"]): {
        "outcome": "Reveille finds sunny destinations and flights but has nowhere to stay.",
        "quality": 0.5,
    },
    frozenset(["weather", "hotels", "maps"]): {
        "outcome": "Reveille finds a warm hotel near the beach… but can't get there without flights!",
        "quality": 0.4,
    },
}


def evaluate_level1(selected_ids: list) -> dict:
    selected_set = set(selected_ids)
    correct = LEVEL1_CORRECT
    correct_count = len(selected_set & correct)
    correctness = correct_count / len(correct)

    efficiency = 1.0 if len(selected_set) == 3 else max(0, 1.0 - abs(len(selected_set) - 3) * 0.25)

    branch = LEVEL1_BRANCHES.get(frozenset(selected_ids))
    if branch:
        outcome_text = branch["outcome"]
        outcome_score = branch["quality"]
    else:
        missing = correct - selected_set
        extra = selected_set - correct
        problems = []
        if "weather" in missing:
            problems.append("picked a destination during monsoon season")
        if "hotels" in missing:
            problems.append("has no place to stay")
        if "flights" in missing:
            problems.append("can't actually get there")
        if extra:
            problems.append(f"wasted time on {', '.join(extra)}")
        outcome_text = "Reveille " + (" and ".join(problems) if problems else "stumbles through planning") + "."
        outcome_score = max(0.0, correctness * 0.4)

    decisions = {
        "correctness": correctness,
        "efficiency": efficiency,
        "outcome": outcome_score,
    }
    return {"decisions": decisions, "outcome_text": outcome_text}


# ── Level 2 Config ──
LEVEL2_CONFIG = {
    "max_score": 150,
    "categories": [
        {"name": "Selection", "max": 70, "evaluator_key": "selection"},
        {"name": "Order", "max": 50, "evaluator_key": "order"},
        {"name": "Efficiency", "max": 30, "evaluator_key": "efficiency"},
    ],
}

LEVEL2_ACTIONS = [
    {"id": "destinations", "name": "Identify destinations", "icon": "📍", "step": 1},
    {"id": "weather", "name": "Check weather", "icon": "🌤️", "step": 2},
    {"id": "hotels", "name": "Compare hotels", "icon": "🏨", "step": 3},
    {"id": "flights", "name": "Search flights", "icon": "✈️", "step": 4},
    {"id": "currency", "name": "Convert prices", "icon": "💱", "step": None},
    {"id": "recommend", "name": "Generate recommendation", "icon": "📋", "step": None},
]

LEVEL2_CORRECT_IDS = {"destinations", "weather", "hotels", "flights"}
LEVEL2_CORRECT_ORDER = ["destinations", "weather", "flights", "hotels"]


def evaluate_level2(selected_ids: list, ordered_ids: list) -> dict:
    selected_set = set(selected_ids)
    correct_set = LEVEL2_CORRECT_IDS
    correct_count = len(selected_set & correct_set)
    selection = correct_count / len(correct_set)

    # Order scoring: check pairwise ordering
    correct_order = LEVEL2_CORRECT_ORDER
    order_score = 0.0
    if len(ordered_ids) >= 2:
        # Check how many correct pairs are in order
        filtered = [x for x in ordered_ids if x in correct_set]
        correct_pairs = 0
        total_pairs = 0
        for i in range(len(correct_order)):
            for j in range(i + 1, len(correct_order)):
                a, b = correct_order[i], correct_order[j]
                if a in filtered and b in filtered:
                    total_pairs += 1
                    ai = filtered.index(a) if a in filtered else -1
                    bi = filtered.index(b) if b in filtered else -1
                    if ai < bi:
                        correct_pairs += 1
        order_score = correct_pairs / max(total_pairs, 1)

    efficiency = 1.0 if len(selected_ids) == 4 else max(0, 1.0 - abs(len(selected_ids) - 4) * 0.2)

    decisions = {
        "selection": selection,
        "order": order_score,
        "efficiency": efficiency,
    }

    if selection == 1.0 and order_score >= 0.8:
        outcome = "Reveille follows a perfect workflow — destinations → weather → flights → hotels!"
    elif selection >= 0.75:
        outcome = "Reveille has most of the right steps but the sequence needs work."
    else:
        outcome = "Reveille's workflow is scattered — key steps are missing."

    return {"decisions": decisions, "outcome_text": outcome}


# ── Level 3 Config ──
LEVEL3_CONFIG = {
    "max_score": 225,
    "categories": [
        {"name": "Intervention", "max": 100, "evaluator_key": "intervention"},
        {"name": "Outcome Quality", "max": 75, "evaluator_key": "outcome"},
        {"name": "Efficiency", "max": 50, "evaluator_key": "efficiency"},
    ],
}

LEVEL3_OPTIONS = [
    {"id": "A", "label": "Let the agent continue comparing premium hotels", "icon": "▶️"},
    {"id": "B", "label": "Pause it, restore the original constraints, then rerun hotel search", "icon": "🛑"},
    {"id": "C", "label": "Ask it to justify this hotel before changing anything", "icon": "🧾"},
    {"id": "D", "label": "Expand the search radius but keep the current shortlist", "icon": "🧭"},
]

LEVEL3_OUTCOMES = {
    "A": {
        "intervention": 0.0,
        "outcome": 0.15,
        "efficiency": 0.3,
        "text": "Reveille keeps optimizing for rating and location, then books a polished but invalid option that still breaks budget and pet requirements.",
    },
    "B": {
        "intervention": 1.0,
        "outcome": 1.0,
        "efficiency": 1.0,
        "text": "You stop the drift at the checkpoint, restore the real constraints, and rerun the hotel search. Reveille finds a valid dog-friendly option under budget.",
    },
    "C": {
        "intervention": 0.55,
        "outcome": 0.45,
        "efficiency": 0.55,
        "text": "The justification exposes the problem, but the agent still hasn't been reset. Useful diagnosis, incomplete recovery.",
    },
    "D": {
        "intervention": 0.35,
        "outcome": 0.35,
        "efficiency": 0.45,
        "text": "A wider search adds inventory, but the shortlist is still anchored to the wrong constraints, so the drift persists longer than it should.",
    },
}


def evaluate_level3(choice: str) -> dict:
    result = LEVEL3_OUTCOMES.get(choice, LEVEL3_OUTCOMES["A"])
    decisions = {
        "intervention": result["intervention"],
        "outcome": result["outcome"],
        "efficiency": result["efficiency"],
    }
    return {"decisions": decisions, "outcome_text": result["text"]}


# ── Level 4 Config ──
LEVEL4_CONFIG = {
    "max_score": 325,
    "categories": [
        {"name": "Round 1 — Plan Comparison", "max": 110, "evaluator_key": "round1"},
        {"name": "Round 2 — Constraint Balance", "max": 110, "evaluator_key": "round2"},
        {"name": "Round 3 — Goal Alignment", "max": 105, "evaluator_key": "round3"},
    ],
}

LEVEL4_ROUNDS = {
    1: {
        "title": "Round 1: Compare Plans",
        "scenario": "Reveille generated 3 plans for Aggie Weekend but hasn't compared them yet. What should it do?",
        "options": [
            {"id": "1A", "label": "Compare plans side-by-side", "icon": "📊"},
            {"id": "1B", "label": "Pick the first plan", "icon": "1️⃣"},
            {"id": "1C", "label": "Generate more plans", "icon": "➕"},
            {"id": "1D", "label": "Ask user to decide", "icon": "🙋"},
        ],
        "correct": "1A",
        "outcomes": {
            "1A": {"score": 1.0, "text": "Reveille compares all plans — identifies the best value/fun balance!"},
            "1B": {"score": 0.3, "text": "Reveille picks plan 1 without comparing. It might not be the best."},
            "1C": {"score": 0.2, "text": "More plans without comparing existing ones just adds noise."},
            "1D": {"score": 0.5, "text": "Asking is okay, but the agent should compare first to help the user."},
        },
    },
    2: {
        "title": "Round 2: Balance Constraints",
        "scenario": "The best plan is slightly over budget and the game time conflicts with dinner reservations. What should Reveille do?",
        "options": [
            {"id": "2A", "label": "Ignore the conflicts", "icon": "🙈"},
            {"id": "2B", "label": "Balance constraints", "icon": "⚖️"},
            {"id": "2C", "label": "Cancel everything", "icon": "❌"},
            {"id": "2D", "label": "Pick cheaper plan", "icon": "💰"},
        ],
        "correct": "2B",
        "outcomes": {
            "2A": {"score": 0.1, "text": "Ignoring conflicts leads to a botched weekend with overlapping events."},
            "2B": {"score": 1.0, "text": "Reveille adjusts timing and finds budget-friendly alternatives. Great balance!"},
            "2C": {"score": 0.0, "text": "Cancelling everything? That's giving up, not problem-solving."},
            "2D": {"score": 0.4, "text": "Cheaper plan fixes budget but doesn't resolve the time conflict."},
        },
    },
    3: {
        "title": "Round 3: Re-check Goals",
        "scenario": "Final plan is ready. But does it still match the original goals: fun, affordable, group-friendly?",
        "options": [
            {"id": "3A", "label": "Ship it as-is", "icon": "🚀"},
            {"id": "3B", "label": "Add more activities", "icon": "🎯"},
            {"id": "3C", "label": "Re-check goals", "icon": "🔄"},
            {"id": "3D", "label": "Start over", "icon": "🔁"},
        ],
        "correct": "3C",
        "outcomes": {
            "3A": {"score": 0.3, "text": "Plan ships but might miss the mark on original goals."},
            "3B": {"score": 0.2, "text": "Adding activities without checking goals might make it worse."},
            "3C": {"score": 1.0, "text": "Reveille validates against original goals — everything checks out! Perfect loop closure."},
            "3D": {"score": 0.0, "text": "Starting over wastes all the work done so far."},
        },
    },
}


def evaluate_level4(choices: dict) -> dict:
    round_scores = {}
    outcome_parts = []
    for r in [1, 2, 3]:
        choice = choices.get(r)
        rdata = LEVEL4_ROUNDS[r]
        outcome = rdata["outcomes"].get(choice, {"score": 0.0, "text": "No selection made."})
        round_scores[f"round{r}"] = outcome["score"]
        outcome_parts.append(f"R{r}: {outcome['text']}")

    decisions = round_scores
    outcome_text = " | ".join(outcome_parts)
    return {"decisions": decisions, "outcome_text": outcome_text}


# ── Level 5 Config ──
LEVEL5_CONFIG = {
    "max_score": 450,
    "categories": [
        {"name": "Agent Selection", "max": 180, "evaluator_key": "selection"},
        {"name": "Orchestration Order", "max": 150, "evaluator_key": "order"},
        {"name": "Efficiency", "max": 70, "evaluator_key": "efficiency"},
        {"name": "Final Output Quality", "max": 50, "evaluator_key": "outcome"},
    ],
}

LEVEL5_AGENTS = [
    {"id": "travel_scout", "name": "Travel Scout", "icon": "🧭", "desc": "Maps arrival windows, travel friction, and lodging zones."},
    {"id": "budget_buddy", "name": "Budget Buddy", "icon": "💸", "desc": "Keeps recommendations inside budget and flags waste."},
    {"id": "event_finder", "name": "Event Finder", "icon": "🎟️", "desc": "Finds high-signal ADSC weekend events and campus moments."},
    {"id": "food_guide", "name": "Food Guide", "icon": "🍽️", "desc": "Optimizes restaurant picks and dining convenience."},
    {"id": "weather_watch", "name": "Weather Watch", "icon": "🌤️", "desc": "Checks forecast risks and outdoor timing changes."},
    {"id": "final_synthesizer", "name": "Final Synthesizer", "icon": "🧩", "desc": "Combines specialist findings into one coherent package."},
]

LEVEL5_CORRECT_IDS = {"travel_scout", "budget_buddy", "event_finder", "final_synthesizer"}
LEVEL5_CORRECT_ORDER = ["travel_scout", "event_finder", "budget_buddy", "final_synthesizer"]
LEVEL5_REDUNDANT = {"food_guide", "weather_watch"}

LEVEL5_BRANCHES = {
    frozenset(["travel_scout", "event_finder", "budget_buddy", "final_synthesizer"]): {
        "order": tuple(LEVEL5_CORRECT_ORDER),
        "text": "Reveille delegates discovery well, budgets after collecting options, and hands the package to the synthesizer only once the pieces are ready. Crisp orchestration.",
        "quality": 1.0,
    },
    frozenset(["travel_scout", "event_finder", "weather_watch", "final_synthesizer"]): {
        "order": ("travel_scout", "weather_watch", "event_finder", "final_synthesizer"),
        "text": "The team builds a weather-aware itinerary, but no budget specialist reconciles tradeoffs, so the final weekend plan runs expensive.",
        "quality": 0.68,
    },
    frozenset(["travel_scout", "budget_buddy", "food_guide", "final_synthesizer"]): {
        "order": ("travel_scout", "budget_buddy", "food_guide", "final_synthesizer"),
        "text": "The plan is organized and affordable, but it misses the highest-value event intelligence that makes the weekend feel special.",
        "quality": 0.58,
    },
}


def evaluate_level5(selected_ids: list, ordered_ids: list) -> dict:
    selected_set = set(selected_ids)
    correct_count = len(selected_set & LEVEL5_CORRECT_IDS)
    selection = correct_count / len(LEVEL5_CORRECT_IDS)

    filtered = [agent_id for agent_id in ordered_ids if agent_id in LEVEL5_CORRECT_IDS]
    correct_pairs = 0
    total_pairs = 0
    for i in range(len(LEVEL5_CORRECT_ORDER)):
        for j in range(i + 1, len(LEVEL5_CORRECT_ORDER)):
            first = LEVEL5_CORRECT_ORDER[i]
            second = LEVEL5_CORRECT_ORDER[j]
            if first in filtered and second in filtered:
                total_pairs += 1
                if filtered.index(first) < filtered.index(second):
                    correct_pairs += 1
    order = correct_pairs / max(total_pairs, 1)

    redundant_count = len(selected_set & LEVEL5_REDUNDANT)
    efficiency = 1.0
    if len(selected_ids) != 4:
        efficiency = max(0.0, efficiency - abs(len(selected_ids) - 4) * 0.2)
    efficiency = max(0.0, efficiency - redundant_count * 0.18)
    if "final_synthesizer" not in selected_set:
        efficiency = min(efficiency, 0.25)
    elif ordered_ids and ordered_ids[-1] != "final_synthesizer":
        efficiency = min(efficiency, 0.42)

    branch = LEVEL5_BRANCHES.get(frozenset(selected_ids))
    if branch and tuple(ordered_ids) == branch["order"]:
        outcome_text = branch["text"]
        outcome = branch["quality"]
    else:
        problems = []
        if "final_synthesizer" not in selected_set:
            problems.append("no one assembles the specialist outputs into a final package")
        elif ordered_ids and ordered_ids[-1] != "final_synthesizer":
            problems.append("the synthesizer fires too early and freezes an incomplete draft")
        if "event_finder" not in selected_set:
            problems.append("the event slate feels generic because no specialist mapped the weekend signal")
        if "budget_buddy" not in selected_set:
            problems.append("tradeoffs stay unresolved and costs drift upward")
        if redundant_count >= 2:
            problems.append("too many overlapping helpers create coordination overhead")

        outcome_text = "Reveille's agent team produces a workable draft, but " + "; ".join(problems) + "."
        outcome = max(0.2, selection * 0.45 + order * 0.25 + efficiency * 0.2)

    decisions = {
        "selection": selection,
        "order": order,
        "efficiency": max(0.0, min(1.0, efficiency)),
        "outcome": max(0.0, min(1.0, outcome)),
    }
    return {"decisions": decisions, "outcome_text": outcome_text}


# ── Level 6 Config ──
LEVEL6_CONFIG = {
    "max_score": 600,
    "categories": [
        {"name": "Orchestration Decisions", "max": 220, "evaluator_key": "orchestration"},
        {"name": "Conflict Resolution", "max": 180, "evaluator_key": "conflict"},
        {"name": "Efficiency", "max": 100, "evaluator_key": "efficiency"},
        {"name": "Mission Quality", "max": 100, "evaluator_key": "mission"},
    ],
}

LEVEL6_ROUNDS = {
    1: {
        "title": "Round 1: Split the Mission",
        "scenario": "Reveille must plan ADSC weekend for a larger visiting group. How should the swarm be structured?",
        "options": [
            {"id": "1A", "label": "One generalist agent handles everything", "icon": "🧍"},
            {"id": "1B", "label": "Two focused agents split logistics and experience, then sync", "icon": "🧠"},
            {"id": "1C", "label": "Three specialists with overlapping scopes", "icon": "🕸️"},
            {"id": "1D", "label": "Start synthesizing before delegation finishes", "icon": "⏱️"},
        ],
        "correct": "1B",
        "outcomes": {
            "1A": {"score": 0.35, "efficiency": 0.55, "text": "Simple to manage, but one agent becomes a bottleneck and misses cross-checks."},
            "1B": {"score": 1.0, "efficiency": 1.0, "text": "Clean split: one branch handles logistics, one handles the experience layer, then they meet at a checkpoint."},
            "1C": {"score": 0.58, "efficiency": 0.42, "text": "Coverage is broad, but overlapping scopes create unnecessary coordination churn."},
            "1D": {"score": 0.1, "efficiency": 0.15, "text": "Synthesis starts before the swarm has stable findings, so bad assumptions get locked in early."},
        },
    },
    2: {
        "title": "Round 2: Resolve Conflict",
        "scenario": "Sub-agents return three different plans: the cheapest, the best-weather option, and the most exciting but more expensive weekend. What should Reveille do?",
        "options": [
            {"id": "2A", "label": "Choose the cheapest option only", "icon": "💵"},
            {"id": "2B", "label": "Choose the most exciting plan only", "icon": "🎉"},
            {"id": "2C", "label": "Compare all plans against the full constraint set", "icon": "⚖️"},
            {"id": "2D", "label": "Finalize the first acceptable result", "icon": "🏁"},
        ],
        "correct": "2C",
        "outcomes": {
            "2A": {"score": 0.38, "text": "Budget improves, but the group experience quality falls off and weather risk stays under-modeled."},
            "2B": {"score": 0.3, "text": "Excitement wins, but budget and logistics drift too far from the brief."},
            "2C": {"score": 1.0, "text": "The swarm reconciles budget, logistics, weather, and experience quality before choosing a plan."},
            "2D": {"score": 0.16, "text": "Fast, but brittle. The first acceptable answer hides unresolved tradeoffs."},
        },
    },
    3: {
        "title": "Round 3: Final Assembly",
        "scenario": "A noisy branch keeps proposing extra options, while the strongest branch is solid but incomplete. How should Reveille finish?",
        "options": [
            {"id": "3A", "label": "Finalize immediately", "icon": "🚀"},
            {"id": "3B", "label": "Drop the noisy branch and synthesize the strong remaining outputs", "icon": "🧩"},
            {"id": "3C", "label": "Rerun the entire swarm from scratch", "icon": "🔁"},
            {"id": "3D", "label": "Add another late specialist before finalizing", "icon": "➕"},
        ],
        "correct": "3B",
        "outcomes": {
            "3A": {"efficiency": 0.55, "text": "The plan is serviceable, but premature finalization leaves some quality on the table."},
            "3B": {"efficiency": 1.0, "text": "You prune noise, preserve signal, and finalize with disciplined synthesis."},
            "3C": {"efficiency": 0.12, "text": "A full rerun burns time and compute while the good branch was already mostly there."},
            "3D": {"efficiency": 0.28, "text": "Late delegation adds more noise than value and delays final assembly."},
        },
    },
}


def evaluate_level6(choices: dict) -> dict:
    round1 = LEVEL6_ROUNDS[1]["outcomes"].get(choices.get(1), {"score": 0.0, "efficiency": 0.0, "text": "No selection made."})
    round2 = LEVEL6_ROUNDS[2]["outcomes"].get(choices.get(2), {"score": 0.0, "text": "No selection made."})
    round3 = LEVEL6_ROUNDS[3]["outcomes"].get(choices.get(3), {"efficiency": 0.0, "text": "No selection made."})

    orchestration = round1.get("score", 0.0)
    conflict = round2.get("score", 0.0)
    efficiency = max(0.0, min(1.0, (round1.get("efficiency", 0.0) * 0.45) + (round3.get("efficiency", 0.0) * 0.55)))

    path = (choices.get(1), choices.get(2), choices.get(3))
    if path == ("1B", "2C", "3B"):
        mission = 1.0
        ending = "Elite orchestration"
        summary = "Reveille runs a disciplined swarm: smart split, thoughtful reconciliation, clean pruning, excellent final weekend package."
    elif choices.get(1) == "1B" and choices.get(2) == "2C":
        mission = 0.82
        ending = "Strong but slightly wasteful"
        summary = "The plan stays aligned with the brief, but the final assembly could have been cleaner."
    elif choices.get(2) == "2C" and choices.get(3) == "3B":
        mission = 0.72
        ending = "Good plan, weak coordination"
        summary = "Reveille recovers well after a shaky split, producing a good final package with some orchestration scars."
    elif choices.get(1) == "1C":
        mission = 0.5
        ending = "Over-delegated"
        summary = "Too many overlapping specialists slow the swarm and blur ownership, even though pieces of the plan are strong."
    elif choices.get(1) == "1D" or choices.get(3) == "3D":
        mission = 0.28
        ending = "Drifted swarm"
        summary = "Premature or late-stage delegation makes the swarm noisy, expensive, and hard to trust."
    else:
        mission = 0.42
        ending = "Chaotic but salvageable"
        summary = "There is enough signal to build a weekend package, but the coordination choices leave obvious waste and unresolved tradeoffs."

    decisions = {
        "orchestration": orchestration,
        "conflict": conflict,
        "efficiency": efficiency,
        "mission": mission,
    }
    outcome_text = f"{ending}: {summary}"
    return {"decisions": decisions, "outcome_text": outcome_text, "ending": ending}
