# Agent Reveille Runs the Loop

Interactive workshop game for the Aggie Data Science Club.

## Setup

```bash
pip install streamlit
pip install supabase
streamlit run app.py
```

## Requirements

- Python 3.9+
- streamlit >= 1.36.0
- supabase >= 2.0.0 *(optional — for persistent leaderboard)*

## Supabase (optional)

To persist leaderboard scores across sessions, configure Supabase credentials:

 `.streamlit/secrets.toml` (recommended for Streamlit Cloud):
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-or-service-key"
   ```

See `utils/supabase.py` for the required table schema.

## Project Structure

```
app.py                  # Main entry point and page router
components/
  cards.py              # Tool, ordering, and decision card components
  terminal.py           # Animated terminal panel (iframe)
  progress.py           # Level progress bar and score screen
  leaderboard.py        # Leaderboard table display
levels/
  level1.py             # Vacation Loadout — tool selection
  level2.py             # Route Workflow — action ordering
  level3.py             # Checkpoint Rescue — agent intervention
  level4.py             # Mission Control — full loop supervision
utils/
  scoring.py            # Deterministic scoring engine and level configs
  state.py              # Session state management
  supabase.py           # Supabase client with in-memory fallback
```
