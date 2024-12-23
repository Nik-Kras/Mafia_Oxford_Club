import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Constants
DB_FILE = "mafia_database.json"

# Load or initialize the database
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return json.load(file)
    return {"players": {}, "games": []}

def save_database(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

db = load_database()

# Utility Functions
def add_user(username):
    if username not in db["players"]:
        db["players"][username] = {"games_played": 0, "wins": 0, "roles": {}}
        save_database(db)

def update_stats(username, role, result):
    add_user(username)
    db["players"][username]["games_played"] += 1
    if result == "win":
        db["players"][username]["wins"] += 1
    if role not in db["players"][username]["roles"]:
        db["players"][username]["roles"][role] = {"games": 0, "wins": 0}
    db["players"][username]["roles"][role]["games"] += 1
    if result == "win":
        db["players"][username]["roles"][role]["wins"] += 1
    save_database(db)

# Global variables for game management
game_setup = {
    "host": None,
    "roles": {"Don": None, "Commissar": None, "Mafia": [], "People": []},
    "current_role": None,
    "players": [],
    "page": 0,
}

# Inline Keyboard Utility Functions
def get_paginated_buttons(player_list, page, role, max_per_page=5):
    """Generate buttons for paginated player selection."""
    start = page * max_per_page
    end = start + max_per_page
    buttons = [
        [InlineKeyboardButton(username, callback_data=f"assign_{role}_{username}")]
        for username in player_list[start:end]
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"nav_prev_{role}"))
    if end < len(player_list):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"nav_next_{role}"))
    if role in ["Mafia", "People"]:
        nav_buttons.append(
            InlineKeyboardButton(
                f"{role} Selected",
                callback_data=f"finish_{role}"
            )
        )
    if nav_buttons:
        buttons.append(nav_buttons)
    return InlineKeyboardMarkup(buttons)

# Command Handlers
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/help - Show this help message\n"
        "/add USERNAME - Add a new player\n"
        "/start_game - Start a new game\n"
        "/stats - Show player statistics\n"
        "/table - Show ranking table\n"
        "/record USERNAME ROLE RESULT - Record a game result\n"
    )
    await update.message.reply_text(help_text)

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /add USERNAME")
        return
    username = context.args[0]
    add_user(username)
    await update.message.reply_text(f"User '{username}' has been added to the database.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /stats USERNAME")
        return
    username = context.args[0]
    if username not in db["players"]:
        await update.message.reply_text(f"User '{username}' not found.")
        return
    stats = db["players"][username]
    roles_stats = "\n".join(
        f"  {role}: {info['wins']}/{info['games']} wins"
        for role, info in stats["roles"].items()
    )
    stats_text = (
        f"Stats for {username}:\n"
        f"Total Games: {stats['games_played']}\n"
        f"Wins: {stats['wins']}\n"
        f"Roles:\n{roles_stats}"
    )
    await update.message.reply_text(stats_text)

async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaderboard = sorted(
        db["players"].items(),
        key=lambda item: (-item[1]["wins"], item[1]["games_played"]),
    )
    table_text = "Leaderboard:\n"
    table_text += "\n".join(
        f"{username}: {stats['wins']} wins, {stats['games_played']} games"
        for username, stats in leaderboard
    )
    await update.message.reply_text(table_text)

async def record_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /record USERNAME ROLE RESULT")
        return
    username, role, result = context.args[0], context.args[1], context.args[2].lower()
    if result not in ["win", "lose"]:
        await update.message.reply_text("Result must be 'win' or 'lose'.")
        return
    if username not in db["players"]:
        await update.message.reply_text(f"User '{username}' not found.")
        return
    update_stats(username, role, result)
    await update.message.reply_text(f"Recorded {result} for {username} as {role}.")

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initialize the game setup process."""
    global game_setup
    game_setup = {
        "host": None,
        "roles": {"Don": None, "Commissar": None, "Mafia": [], "People": []},
        "current_role": "host",
        "players": list(db["players"].keys()),
        "page": 0,
    }

    if not game_setup["players"]:
        await update.message.reply_text("No players found in the database. Add players first with /add.")
        return

    await update.message.reply_text(
        "Select a host for the game:",
        reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "host"),
    )

async def handle_role_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle role assignment via callback queries."""
    global game_setup
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("assign_"):
        _, role, username = data.split("_")
        if role == "host":
            game_setup["host"] = username
            game_setup["current_role"] = "Don"
            game_setup["page"] = 0
            await query.edit_message_text(
                f"Host assigned: {username}\n\nSelect a Don:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "Don"),
            )
        elif role == "Don":
            game_setup["roles"]["Don"] = username
            game_setup["current_role"] = "Commissar"
            game_setup["page"] = 0
            await query.edit_message_text(
                f"Don assigned: {username}\n\nSelect a Commissar:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "Commissar"),
            )
        elif role == "Commissar":
            game_setup["roles"]["Commissar"] = username
            game_setup["current_role"] = "Mafia"
            game_setup["page"] = 0
            await query.edit_message_text(
                f"Commissar assigned: {username}\n\nSelect Mafia players:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "Mafia"),
            )
        elif role == "Mafia":
            game_setup["roles"]["Mafia"].append(username)
            await query.edit_message_text(
                f"Mafia assigned: {', '.join(game_setup['roles']['Mafia'])}\n\nSelect more Mafia players or finish selection:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "Mafia"),
            )
        elif role == "People":
            game_setup["roles"]["People"].append(username)
            await query.edit_message_text(
                f"People assigned: {', '.join(game_setup['roles']['People'])}\n\nSelect more People or finish selection:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "People"),
            )
    elif data.startswith("finish_"):
        role = data.split("_")[1]
        if role == "Mafia":
            game_setup["current_role"] = "People"
            game_setup["page"] = 0
            await query.edit_message_text(
                f"Mafia selection completed.\n\nSelect People:",
                reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], "People"),
            )
        elif role == "People":
            db["games"].append(game_setup)
            save_database(db)
            await query.edit_message_text(
                f"Game setup complete!\n\nHost: {game_setup['host']}\nDon: {game_setup['roles']['Don']}\n"
                f"Commissar: {game_setup['roles']['Commissar']}\nMafia: {', '.join(game_setup['roles']['Mafia'])}\n"
                f"People: {', '.join(game_setup['roles']['People'])}\n"
                "Good luck!",
            )
    elif data.startswith("nav_"):
        direction, role = data.split("_")[1:]
        if direction == "prev":
            game_setup["page"] = max(0, game_setup["page"] - 1)
        elif direction == "next":
            game_setup["page"] += 1
        await query.edit_message_reply_markup(
            reply_markup=get_paginated_buttons(game_setup["players"], game_setup["page"], role),
        )

# Add CallbackQueryHandler for role assignment
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("table", table_command))
    application.add_handler(CommandHandler("record", record_command))
    application.add_handler(CommandHandler("start_game", start_game))
    application.add_handler(CallbackQueryHandler(handle_role_assignment))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
