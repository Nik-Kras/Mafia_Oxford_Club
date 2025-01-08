# Done
from src.utils.json_utils import load_json, save_json, STATS_FILE, GAMES_FILE
from typing import Dict, List, Optional

def load_player_stats(username: str) -> Optional[Dict]:
    """Load statistics for a specific player."""
    # NOT IMPLEMENTED
    # Should parse all games and create statistics
    # stats = load_json(STATS_FILE)
    # return stats.get(username, "Not Found")
    return None

def show_last_game():
    games = load_json(GAMES_FILE)
    latest_id = max([game["Game_ID"] for game in games])
    return get_game(latest_id)

def initialize_player_stats() -> Dict:
    """Initialize statistics structure for a new player."""
    return {
        "Don": {"played": 0, "won": 0, "survived": 0},
        "Mafia": {"played": 0, "won": 0, "survived": 0},
        "Team_Black": {"played": 0, "won": 0, "survived": 0},
        "Commissar": {"played": 0, "won": 0, "survived": 0},
        "Citizen": {"played": 0, "won": 0, "survived": 0},
        "Team_Red": {"played": 0, "won": 0, "survived": 0},
        "Elo_rating": 1200
    }

def calculate_winrate(stats: Dict, category: str) -> float:
    """Calculate winrate for a specific category."""
    if stats[category]["played"] == 0:
        return 0.0
    return (stats[category]["won"] / stats[category]["played"]) * 100

def calculate_survival_rate(stats: Dict, category: str) -> float:
    """Calculate survival rate for a specific category."""
    if stats[category]["played"] == 0:
        return 0.0
    return (stats[category]["survived"] / stats[category]["played"]) * 100

def get_leaderboard(sort_by: str = "Team_Red") -> str:
    """Generate a leaderboard sorted by specified criteria."""
    stats = load_json(STATS_FILE)

    # Calculate winrates for all players
    leaderboard_data = []
    for username, player_stats in stats.items():
        leaderboard_data.append({
            "username": username,
            "red_winrate": calculate_winrate(player_stats, "Team_Red"),
            "black_winrate": calculate_winrate(player_stats, "Team_Black"),
            "elo": player_stats.get("Elo_rating", 1200)
        })

    # Sort based on criteria
    if sort_by == "Team_Red":
        leaderboard_data.sort(key=lambda x: x["red_winrate"], reverse=True)
    elif sort_by == "Team_Black":
        leaderboard_data.sort(key=lambda x: x["black_winrate"], reverse=True)
    else:  # "Elo"
        leaderboard_data.sort(key=lambda x: x["elo"], reverse=True)

    # Format leaderboard
    leaderboard = "🏆 Leaderboard 🏆\n\n"
    leaderboard += f"{'Player':<15} {'Red WR':<10} {'Black WR':<10} {'Elo':<6}\n"
    leaderboard += "-" * 41 + "\n"

    for entry in leaderboard_data:
        leaderboard += f"{entry['username']:<15} {entry['red_winrate']:<10.1f} {entry['black_winrate']:<10.1f} {entry['elo']:<6}\n"

    return leaderboard

def get_game(game_id: int) -> Optional[str]:
    """View details of a specific game."""
    try:
        games = load_json(GAMES_FILE)
        game = next((g for g in games if g["Game_ID"] == game_id), None)

        if not game:
            return None
        
        # Format game details
        result = f"Game #{game['Game_ID']} - {game['Date']}\n"
        result += f"Host: {game['Host']}\n\n"
        
        result += "🔴 Team Red:\n"
        for player in game["Team_Red"]:
            status = "💀" if player["status"] == "dead" else "✅"
            result += f"{status} {player['player']} ({player['role']})\n"
        
        result += "\n⚫ Team Black:\n"
        for player in game["Team_Black"]:
            status = "💀" if player["status"] == "dead" else "✅"
            result += f"{status} {player['player']} ({player['role']})\n"
        
        result += f"\nWinner: {game['Victory']} 🏆"
        return result

    except FileNotFoundError:
        return None

def help_command() -> str:
    """Return help message with command descriptions."""
    return """
🎮 Mafia Oxford Club Bot Commands 🎮

Admin Commands:
/play - Start a new game
/add_player <username> - Add a new player
/remove_player <username> - Remove a player

General Commands:
/view_players - See all registered players
/view_games <game_id> - View specific game
/leaderboard - View player rankings
/stats <username> - View player statistics
/help - Show this message

For more information, contact the bot administrator.
"""
