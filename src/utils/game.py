# Done
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import List, Dict, Optional
from src.utils.json_utils import save_json, load_json, GAMES_FILE, PLAYERS_FILE
from datetime import datetime
from .utils import get_paginated_keyboard, STATES, ROLES

class PlayerInGame:
    def __init__(self, role: str):
        self.role: str = role
        self.survived: bool = True

class Game:
    def __init__(self):
        self.selected_usernames: List[str] = []
        self.players: Dict[str, PlayerInGame] = {}
        self.host: Optional[str] = None
        self.winning_team: Optional[str] = None
        self.game_id: Optional[int] = None
        self.date: Optional[str] = None

    def add_player(self, username: str) -> None:
        """Add a player to the game."""
        self.selected_usernames.append(username)

    def assign_role(self, username: str, role: str):
        """Select a role for the player."""
        if role == "Host":
            self.host = username
        else:
            self.players[username] = PlayerInGame(role=role)

    def kill_player(self, username: str) -> None:
        """Mark a player as dead."""
        self.players[username].survived = False

    def set_winner(self, team: str) -> None:
        """Set the winning team."""
        self.winning_team = team
        self.date = datetime.now().strftime("%d.%m.%Y")
        self.game_id = self._get_next_game_id()

    def save(self) -> None:
        """Save the game record to the database."""
        game_record = self._create_game_record()
        self._save_to_file(game_record)

    def _create_game_record(self) -> Dict:
        """Create a game record dictionary."""
        team_red = []
        team_black = []

        for username, details in self.players.items():
            player_record = {
                "player": username,
                "role": details.role,
                "status": "alive" if details.survived else "dead"
            }
            
            if details.role in ["Citizen", "Commissar"]:
                team_red.append(player_record)
            else:
                team_black.append(player_record)

        return {
            "Game_ID": self.game_id,
            "Date": self.date,
            "Host": self.host,
            "Team_Red": team_red,
            "Team_Black": team_black,
            "Victory": self.winning_team
        }

    def _get_next_game_id(self) -> int:
        """Get the next available game ID."""
        try:
            games = load_json(GAMES_FILE)
            return max(game["Game_ID"] for game in games) + 1
        except (FileNotFoundError, ValueError):
            return 1

    def _save_to_file(self, game_record: Dict) -> None:
        """Save the game record to file."""
        games = load_json(GAMES_FILE)
        games.append(game_record)
        save_json(GAMES_FILE, games)

# Stage 1: Select players in Game.selected_usernames using .add_player
async def start_selecting_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initialize player selection phase."""
    context.user_data["game"] = Game()
    context.user_data["state"] = STATES["SELECTING_PLAYERS"]
    
    all_players = load_json(PLAYERS_FILE)
    
    context.user_data["remaining_users"] = all_players.copy()
    context.user_data["page"] = 0
    
    await update.message.reply_text(
        "Select players for the game:",
        reply_markup=get_paginated_keyboard(all_players, 0, "select")
    )

# Stage 2: Assign roles in Game.players using .assign_role
async def start_role_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Initialize role assignment phase."""
    current_player = context.user_data["game"].selected_usernames[0]
    keyboard = [[InlineKeyboardButton(role, callback_data=f"role§{role}")] for role in ROLES]
    await update.callback_query.edit_message_text(
        f"Assign role to {current_player}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Stage 3: Kill players in Game.players using .kill_player
async def start_killing_phase(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Initialize killing phase."""
    game: Game = context.user_data["game"]
    alive_players = [player for player, details in game.players.items() if details.survived]
    
    if not alive_players:
        context.user_data["state"] = STATES["SELECTING_WINNER"]
        await start_winner_selection(update, context, logger)
        return
    
    visual_players = [f"{username} [{game.players[username].role}]" for username in alive_players]
    
    await update.callback_query.edit_message_text(
        "Select a player to kill:",
        reply_markup=get_paginated_keyboard(visual_players, 0, "kill")
    )

# Stage 4: Select winning team using .set_winner and save the game with .save
async def start_winner_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Initialize winner selection phase."""
    keyboard = [
        [InlineKeyboardButton("City Victory", callback_data="win§City")],
        [InlineKeyboardButton("Mafia Victory", callback_data="win§Mafia")]
    ]
    await update.callback_query.edit_message_text(
        "Select the winning team:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
