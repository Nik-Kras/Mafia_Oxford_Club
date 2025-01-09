from src.utils.json_utils import load_json, save_json, STATS_FILE, GAMES_FILE, PLAYERS_FILE
from typing import Dict, List, Optional

def load_player_stats(username: str) -> Optional[Dict]:
    """Load statistics for a specific player."""
    generate_stats_dataset()
    stats = load_json(STATS_FILE)
    return stats.get(username, None)

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
        "Host": 0,
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
    generate_stats_dataset()
    leaderboard = generate_leaderboard_string(sort_by)
    return leaderboard

def generate_stats_dataset():
    """Using games dataset generates stats dataset"""
    games = load_json(GAMES_FILE)
    stats = initialize_empty_stats()

    for game in games:
        for team in ("Team_Red", "Team_Black"):
            for player in game[team]:
                if player["player"] in stats:
                    role = player["role"]
                    survived = player["status"]
                    username = player["player"]
                    stats[username][team]["played"] += 1
                    stats[username][role]["played"] += 1
                    if game["Victory"] == "City":
                        stats[username][team]["won"] += 1
                        stats[username][role]["won"] += 1
                    if survived == "alive":
                        stats[username][team]["survived"] += 1
                        stats[username][role]["survived"] += 1
    
    save_json(STATS_FILE, stats)
    return stats


def initialize_empty_stats() -> dict:
    """Creates empty leaderboard with all players"""
    players = load_json(PLAYERS_FILE)
    players = {player: initialize_player_stats() for player in players}
    return players

def generate_leaderboard_string(sort_by: str ):
    """Visualizes stats dataset"""
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
    sort_keys = {
        "Team_Red": lambda x: x["red_winrate"],
        "Team_Black": lambda x: x["black_winrate"],
        "Elo": lambda x: x["elo"]
    }
    leaderboard_data.sort(key=sort_keys.get(sort_by, sort_keys["Elo"]), reverse=True)

    # Define fixed column widths
    RANK_WIDTH = 4
    PLAYER_WIDTH = 20
    WR_WIDTH = 8
    ELO_WIDTH = 8

    def pad_string(text, width, align='left'):
        """Pad string to exact width with proper alignment."""
        if align == 'left':
            return f"{str(text):<{width}}"
        else:  # right align
            return f"{str(text):>{width}}"

    # Create header
    table_content = "🏆 LEADERBOARD 🏆\n\n"
    
    # Add column headers
    header_line = (
        f"{pad_string('#', RANK_WIDTH)}│"
        f"{pad_string('Player', PLAYER_WIDTH)}│"
        f"{pad_string('Red WR', WR_WIDTH)}│"
        f"{pad_string('Black WR', WR_WIDTH)}│"
        f"{pad_string('Elo', ELO_WIDTH)}\n"
    )
    
    # Create separator
    separator = (
        f"{pad_string('', RANK_WIDTH, 'left').replace(' ', '─')}┼"
        f"{pad_string('', PLAYER_WIDTH, 'left').replace(' ', '─')}┼"
        f"{pad_string('', WR_WIDTH, 'left').replace(' ', '─')}┼"
        f"{pad_string('', WR_WIDTH, 'left').replace(' ', '─')}┼"
        f"{pad_string('', ELO_WIDTH, 'left').replace(' ', '─')}\n"
    )

    # Add header parts to table content
    table_content += header_line + separator

    # Add player entries
    for index, entry in enumerate(leaderboard_data, 1):
        rank = pad_string(index, RANK_WIDTH)
        username = pad_string(entry['username'][:PLAYER_WIDTH], PLAYER_WIDTH)
        red_wr = pad_string(f"{entry['red_winrate']:.1f}", WR_WIDTH)
        black_wr = pad_string(f"{entry['black_winrate']:.1f}", WR_WIDTH)
        elo = pad_string(entry['elo'], ELO_WIDTH)

        line = f"{rank}│{username}│{red_wr}│{black_wr}│{elo}\n"
        table_content += line

    # Wrap the entire table in markdown code block
    return table_content

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
