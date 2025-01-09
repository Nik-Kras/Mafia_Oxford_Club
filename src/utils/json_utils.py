import json
from typing import Any

STATS_FILE = "database/stats.json"
GAMES_FILE = "database/games.json"
PLAYERS_FILE = "database/players.json"

def load_json(filepath: str, default: Any = None) -> Any:
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(filepath: str, data: Any) -> None:
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
