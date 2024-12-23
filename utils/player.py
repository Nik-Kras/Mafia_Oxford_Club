import json

PLAYERS_FILE = "database/players.json"

def add_player(username: str) -> bool:
    """Adds a player to the players.json database."""
    try:
        with open(PLAYERS_FILE, "r") as file:
            players = json.load(file)

        if username in players:
            return f"{username} already exists."

        players.append(username)
        with open(PLAYERS_FILE, "w") as file:
            json.dump(players, file, indent=4)
        return f"{username} has been added."

    except Exception as e:
        raise e
        return f"Error: {e}"
    
def remove_player(username: str) -> bool:
    """Removes a player from the players.json database."""
    try:
        with open(PLAYERS_FILE, "r") as file:
            players = json.load(file)

        if username not in players:
            return f"{username} does not exist."

        players.remove(username)
        with open(PLAYERS_FILE, "w") as file:
            json.dump(players, file, indent=4)
        return f"{username} has been removed."

    except Exception as e:
        return f"Error: {e}"
    
def get_all_players() -> str:
    """Returns a string of all players."""
    try:
        with open(PLAYERS_FILE, "r") as file:
            players = json.load(file)

        if players:
            return "\n".join(players)
        return "No players found."

    except Exception as e:
        return f"Error: {e}"
