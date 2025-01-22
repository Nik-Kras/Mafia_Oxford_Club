from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps
from .verification import is_admin
from .player import add_player_to_db, remove_player_from_db, get_all_players
from .stats import get_leaderboard, get_game, load_player_stats
from .game import start_selecting_players
from .json_utils import load_json, PLAYERS_FILE
from .utils import get_paginated_keyboard
from .verification import is_admin
from src.utils.logger import log_command_usage

def admin_required():
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            if not is_admin(update):
                await update.message.reply_text("Only administrators can use this command.")
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

@admin_required()
@log_command_usage("/play")
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new game."""
    await start_selecting_players(update, context)

@admin_required()
@log_command_usage("/add_player")
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a new player to the database."""
    if not context.args:
        await update.message.reply_text("Usage: /add_player <username>")
        return
    
    result = add_player_to_db(context.args[0])
    await update.message.reply_text(result)

@admin_required()
@log_command_usage("/remove_player")
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a player from the database."""
    if not context.args:
        await update.message.reply_text("Usage: /remove_player <username>")
        return
    
    result = remove_player_from_db(context.args[0])
    await update.message.reply_text(result)

@log_command_usage("/view_players")
async def view_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all registered players."""
    players = get_all_players()
    if players:
        message = "Registered players:\n" + "\n".join(f"• {player}" for player in players)
    else:
        message = "No players registered."
    await update.message.reply_text(message)

@log_command_usage("/view_game")
async def view_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display game history."""
    if not context.args:
        await update.message.reply_text("Usage: /view_game <game_id>")
        return
    
    try:
        game_id = int(context.args[0])
        game_details = get_game(game_id)
        message = game_details if game_details else "Game not found."
    except ValueError:
        message = "Invalid game ID. Please use a number."
    
    await update.message.reply_text(message)

@log_command_usage("/view_player_stats")
async def view_player_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display player statistics."""
    all_players = load_json(PLAYERS_FILE)

    context.user_data["state"] = "SELECT_FOR_STATS"
    context.user_data["remaining_users"] = all_players.copy()
    context.user_data["page"] = 0
    
    await update.message.reply_text(
        "Select players for the game:",
        reply_markup=get_paginated_keyboard(all_players, 0, "select")
    )

@log_command_usage("/view_leaderboard")
async def view_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display player leaderboard."""
    sort_options = {
        "red": "Team_Red",
        "black": "Team_Black",
        "elo": "Elo"
    }
    
    sort_by = "Team_Red"  # default
    if context.args:
        sort_by = sort_options.get(context.args[0].lower(), "Team_Red")
    
    leaderboard = get_leaderboard(sort_by)
    await update.message.reply_text(f"```{leaderboard}```", parse_mode='MarkdownV2')

@log_command_usage("/help_command")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help message."""
    if is_admin(update):
        help_text = """
🎮 Mafia Oxford Club Bot Commands 🎮

Game Commands:
/play - Start a new game session (Admin only)
/view_game [game_id] - View game history or specific game

Player Management:
/add_player <username> - Add a new player (Admin only)
/remove_player <username> - Remove a player (Admin only)
/view_players - List all registered players

Statistics:
/stats - View player statistics
/leaderboard [red|black|elo] - View player rankings

Other:
/help - Show this message

For more information or help, contact the administrator. @nitosAI
"""
    else:
        help_text = """
🎮 Mafia Oxford Club Bot Commands 🎮

Game Commands:
/view_game [game_id] - View game history or specific game

Player Management:
/view_players - List all registered players

Statistics:
/stats - View player statistics
/leaderboard [red|black|elo] - View player rankings

Other:
/help - Show this message

For more information or help, contact the administrator. @nitosAI
"""
    await update.message.reply_text(help_text)
