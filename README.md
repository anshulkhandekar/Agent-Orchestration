You are an expert full-stack engineer and UI/UX designer.

Build a **production-ready Streamlit web app** for an interactive workshop game called:

# Agent Reveille Runs the Loop

### (Aggie Data Science Club)

This app must be:

* visually polished and modern (startup-quality)
* fully functional with clean architecture
* deterministic (NO LLM or API calls)
* interactive and engaging
* easy to run locally with `streamlit run app.py`

---

# 🧠 CORE CONCEPT

Users play in teams (3–4 people).
They guide an AI agent (Reveille) through 4 levels:

1. Tool selection
2. Workflow sequencing
3. Agent checkpoint correction
4. Full agent loop supervision

The agent is simulated via deterministic logic and terminal-style output.

---

# ⚙️ TECH REQUIREMENTS

## Stack

* Python
* Streamlit
* Optional: Supabase (for leaderboard)

## Must Use

* `st.session_state` for game state
* modular file structure
* reusable UI components
* `st.components.v1.html` for advanced UI (drag/drop, animations)

---

# 📁 PROJECT STRUCTURE

Create this structure:

app.py

levels/

* level1.py
* level2.py
* level3.py
* level4.py

components/

* terminal.py
* cards.py
* leaderboard.py
* progress.py

utils/

* scoring.py
* state.py
* supabase.py (optional fallback to local dict if not configured)

---

# 🎮 GAME FLOW

1. Landing Page

   * Title: Agent Reveille Runs the Loop
   * Subtitle: Aggie Data Science Club
   * Team name input
   * Start button

2. Instructions Modal

   * Explain:

     * scoring (correctness, efficiency, supervision)
     * retries reduce max score
     * goal: highest total score

3. Levels 1 → 4

   * Each level:

     * mission prompt
     * interactive UI
     * terminal simulation
     * scoring screen
     * retry or continue

4. Leaderboard

   * live table
   * shows best score per level + total

---

# 🎨 UI/UX DESIGN

## Style

* Dark theme (#0E1117 background)
* Accent: cyan / electric blue
* Secondary: purple
* Clean, futuristic

## Fonts

* Headers: Syne
* Body: Inter
* Terminal: Space Mono

## Components

### Tool Cards

* hover glow
* selectable
* icon + label

### Workflow Cards

* drag-and-drop OR click-to-order
* animated

### Terminal Panel

* animated typing effect
* color-coded tags:

  * observe (blue)
  * plan (purple)
  * act (green)
  * warning (orange)
  * checkpoint (red)

### Checkpoint Modal

* centered overlay
* 4 large decision buttons

### Score Screen

* animated count-up
* breakdown bars

### Progress Bar

Top:
Level 1 → Level 2 → Level 3 → Level 4

---

# 🧩 GAME LOGIC

All logic must be deterministic using predefined configs.

---

# 🟢 LEVEL 1 — Vacation Loadout

## Prompt

Beach vacation in Europe: warm weather, cheap, near beach.

## Tools (10)

Flights, Weather, Hotels, Maps, Currency, Calculator, Restaurants, Translation, Events, Packing

## Rules

* select exactly 3 tools

## Correct

Flights + Weather + Hotels

## Scoring (100)

* 60 correctness
* 25 efficiency
* 15 outcome quality

## Branching

* missing weather → wrong climate
* missing hotels → vague stay
* etc.

---

# 🟡 LEVEL 2 — Route the Workflow

## Actions (6)

* Identify destinations
* Check weather
* Compare hotels
* Search flights
* Convert prices
* Generate recommendation

## Rules

* pick 4 actions
* order them

## Scoring (150)

* 70 correct selection
* 50 order
* 30 efficiency

---

# 🔵 LEVEL 3 — Checkpoint Rescue

## Scenario

Agent ignored constraints (dog-friendly, budget)

## Terminal shows drift

## Options

A Continue
B Re-check constraints (correct)
C Search more
D Finalize

## Scoring (225)

* 100 intervention
* 75 outcome
* 50 efficiency

---

# 🔴 LEVEL 4 — Mission Control

## Aggie Weekend Planner

3 rounds:

### Round 1

Compare plans (correct)

### Round 2

Balance constraints (correct)

### Round 3

Re-check goals (correct)

## Scoring (325)

---

# 🔁 RETRY SYSTEM

Multiplier per attempt:

* 1.00
* 0.92
* 0.85
* 0.75

Store attempts per level.

---

# 🧮 SCORING ENGINE

Create reusable function:

compute_score(level_config, decisions, attempt_count)

Return:

* total score
* breakdown dict

---

# 🏆 LEADERBOARD

If Supabase configured:

* persist team scores
* store best per level

Else:

* fallback to in-memory dict

Display:
Rank | Team | L1 | L2 | L3 | L4 | Total

---

# 🧠 TERMINAL ENGINE

Build component that:

* takes list of log entries
* renders with typing animation
* color-coded tags

---

# 🧩 IMPORTANT DESIGN RULES

* NO long paragraphs
* short readable logs
* fast interactions
* subtle hints only
* always allow retry
* never block progress

---

# 🚀 FINAL REQUIREMENTS

* clean modular code
* no broken imports
* fully runnable
* polished UI
* smooth transitions
* deterministic logic
* visually impressive

---

Return the FULL codebase with all files.
