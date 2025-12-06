# state.py
import streamlit as st
import json
import os

DEFAULT_PLAYERS = ["Amber", "Mandeep", "Rav", "Simer"]
DATA_FILE = "games.json"


def load_games():
    """Read games from games.json if it exists."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # basic sanity: must be a list
            if isinstance(data, list):
                return data
    except json.JSONDecodeError:
        pass

    return []


def save_games(games):
    """Write games list to games.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)


def init_state():
    if "players" not in st.session_state:
        st.session_state.players = DEFAULT_PLAYERS.copy()

    if "games" not in st.session_state:
        # load from disk on startup
        st.session_state.games = load_games()

