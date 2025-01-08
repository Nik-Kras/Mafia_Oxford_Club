# Done
from .json_utils import load_json, save_json, PLAYERS_FILE

def add_player_to_db(username: str) -> bool:
    """Adds a player to the players.json database."""
    players = load_json(PLAYERS_FILE)
    if username in players:
        return f"{username} already exists."
    players.append(username)
    save_json(PLAYERS_FILE, players)
    return f"{username} has been added."
    
def remove_player_from_db(username: str) -> bool:
    """Removes a player from the players.json database."""
    players = load_json(PLAYERS_FILE)
    if username not in players:
        return f"{username} does not exist."
    players.remove(username)
    save_json(PLAYERS_FILE, players)
    return f"{username} has been removed."
    
def get_all_players() -> list:
    """Returns a string of all players."""
    players = load_json(PLAYERS_FILE)
    return players
