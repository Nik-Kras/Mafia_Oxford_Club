from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps
from .verification import is_admin
from .player import add_player_to_db, remove_player_from_db, get_all_players
from .stats import get_leaderboard, get_game, load_player_stats
from .game import start_selecting_players

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
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new game."""
    await start_selecting_players(update, context)

@admin_required()
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a new player to the database."""
    if not context.args:
        await update.message.reply_text("Usage: /add_player <username>")
        return
    
    result = add_player_to_db(context.args[0])
    await update.message.reply_text(result)

@admin_required()
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a player from the database."""
    if not context.args:
        await update.message.reply_text("Usage: /remove_player <username>")
        return
    
    result = remove_player_from_db(context.args[0])
    await update.message.reply_text(result)

async def view_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display all registered players."""
    players = get_all_players()
    if players:
        message = "Registered players:\n" + "\n".join(f"• {player}" for player in players)
    else:
        message = "No players registered."
    await update.message.reply_text(message)

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

async def view_player_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display player statistics."""
    if not context.args:
        await update.message.reply_text("Usage: /stats <username>")
        return
    
    username = context.args[0]
    stats = load_player_stats(username)
    
    if not stats:
        await update.message.reply_text(f"No statistics found for {username}")
        return
    
    message = f"📊 Statistics for {username}\n\n"
    
    # Team stats
    message += "Team Performance:\n"
    for team in ["Team_Red", "Team_Black"]:
        games = stats[team]["played"]
        if games > 0:
            winrate = (stats[team]["won"] / games) * 100
            survivalrate = (stats[team]["survived"] / games) * 100
            message += f"{team}: {games} games, {winrate:.1f}% wins, {survivalrate:.1f}% survival\n"
    
    # Role stats
    message += "\nRole Performance:\n"
    for role in ["Don", "Mafia", "Commissar", "Citizen"]:
        games = stats[role]["played"]
        if games > 0:
            winrate = (stats[role]["won"] / games) * 100
            survivalrate = (stats[role]["survived"] / games) * 100
            message += f"{role}: {games} games, {winrate:.1f}% wins, {survivalrate:.1f}% survival\n"
    
    # Elo rating
    message += f"\nElo Rating: {stats['Elo_rating']}"
    
    await update.message.reply_text(message)

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help message."""
    help_text = """
🎮 Mafia Oxford Club Bot Commands 🎮

Game Commands:
/play - Start a new game session
/view_game [game_id] - View game history or specific game

Player Management:
/add_player <username> - Add a new player (Admin only)
/remove_player <username> - Remove a player (Admin only)
/view_players - List all registered players

Statistics:
/stats <username> - View player statistics
/leaderboard [red|black|elo] - View player rankings

Other:
/help - Show this message

For more information or help, contact the administrator.
"""
    await update.message.reply_text(help_text)
