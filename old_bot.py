# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
# import json
# from datetime import datetime

# # Load or initialize the database
# DATABASE_FILE = "mafia_database.json"
# try:
#     with open(DATABASE_FILE, "r") as f:
#         database = json.load(f)
# except FileNotFoundError:
#     database = {}

# # Save database function
# def save_database():
#     with open(DATABASE_FILE, "w") as f:
#         json.dump(database, f, indent=4)

# # Globals for managing game state
# game_state = {
#     "host": None,
#     "don": None,
#     "commissar": None,
#     "mafia": [],
#     "people": [],
#     "step": None,
#     "players": [],
# }

# # Add user to database
# async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if len(context.args) != 1:
#         await update.message.reply_text("Usage: /add USERNAME")
#         return
#     username = context.args[0]
#     if username in database:
#         await update.message.reply_text(f"User {username} already exists.")
#     else:
#         database[username] = {"games": []}
#         save_database()
#         await update.message.reply_text(f"User {username} added to the database.")

# # Update player record
# def update_player(username, role, result, host):
#     record = {
#         "role": role,
#         "result": result,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "host": host,
#     }
#     database[username]["games"].append(record)
#     save_database()

# # Display a paginated table of usernames
# async def display_user_table(update, context, message, callback_prefix, page=0):
#     usernames = game_state["players"]
#     start = page * 5
#     end = start + 5
#     keyboard = [
#         [InlineKeyboardButton(username, callback_data=f"{callback_prefix}:{username}")]
#         for username in usernames[start:end]
#     ]
#     if start > 0:
#         keyboard.append([InlineKeyboardButton("Prev", callback_data=f"{callback_prefix}_page:{page-1}")])
#     if end < len(usernames):
#         keyboard.append([InlineKeyboardButton("Next", callback_data=f"{callback_prefix}_page:{page+1}")])
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     if update.message:
#         # Regular command
#         await update.message.reply_text(message, reply_markup=reply_markup)
#     elif update.callback_query:
#         # Inline button interaction
#         await update.callback_query.edit_message_text(message, reply_markup=reply_markup)

# # Start game command
# async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     game_state["step"] = "select_host"
#     game_state["players"] = list(database.keys())
#     await display_user_table(update, context, "Choose the host:", "select_host")

# # Handle role selection
# async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split(":")
#     step = data[0]
#     username = data[1] if len(data) > 1 else None

#     if step.endswith("_page"):  # Handle pagination
#         page = int(data[1])
#         callback_prefix = step.split("_")[0]
#         if "_" in step:  # Ensure we can safely split by "_"
#             role = callback_prefix.split("_")[1] if len(callback_prefix.split("_")) > 1 else "role"
#             message = f"Choose {role}:"
#         else:
#             message = "Choose a player:"
#         await display_user_table(update, context, message, callback_prefix, page)
#         return

#     if step == "select_host":
#         game_state["host"] = username
#         update_player(username, "host", "playing", None)
#         game_state["step"] = "select_don"
#         await display_user_table(update, context, "Choose Don:", "select_don")

#     elif step == "select_don":
#         game_state["don"] = username
#         update_player(username, "Don", "playing", game_state["host"])
#         game_state["step"] = "select_commissar"
#         await display_user_table(update, context, "Choose Commissar:", "select_commissar")

#     elif step == "select_commissar":
#         game_state["commissar"] = username
#         update_player(username, "Commissar", "playing", game_state["host"])
#         game_state["step"] = "select_mafia"
#         await display_user_table(update, context, "Select Mafia. Press 'Mafia is selected' when done.", "select_mafia")

#     elif step == "select_mafia":
#         if username:
#             game_state["mafia"].append(username)
#             update_player(username, "Black", "playing", game_state["host"])
#         else:
#             game_state["step"] = "select_people"
#             await display_user_table(update, context, "Select People. Press 'People are selected' when done.", "select_people")

#     elif step == "select_people":
#         if username:
#             game_state["people"].append(username)
#             update_player(username, "White", "playing", game_state["host"])
#         else:
#             game_state["step"] = "game_outcome"
#             buttons = [
#                 [InlineKeyboardButton("Mafia Won", callback_data="mafia_won")],
#                 [InlineKeyboardButton("People Won", callback_data="people_won")],
#             ]
#             await update.callback_query.edit_message_text(
#                 "Select the winning team:", reply_markup=InlineKeyboardMarkup(buttons)
#             )

#     elif step in ["mafia_won", "people_won"]:
#         winning_team = "Mafia" if step == "mafia_won" else "People"
#         losing_team = "People" if step == "mafia_won" else "Mafia"
#         for username in game_state["mafia"] + ([game_state["don"]] if winning_team == "Mafia" else []):
#             update_player(username, "Black" if username in game_state["mafia"] else "Don", "win", game_state["host"])
#         for username in game_state["people"] + ([game_state["commissar"]] if losing_team == "People" else []):
#             update_player(username, "White" if username in game_state["people"] else "Commissar", "lose", game_state["host"])
#         await update.callback_query.edit_message_text("Game outcome recorded.")

# # Show stats for a specific user
# async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
#     usernames = list(database.keys())
#     start = page * 5
#     end = start + 5
#     keyboard = [
#         [InlineKeyboardButton(username, callback_data=f"stats:{username}")]
#         for username in usernames[start:end]
#     ]
#     if start > 0:
#         keyboard.append([InlineKeyboardButton("Prev", callback_data=f"stats_page:{page-1}")])
#     if end < len(usernames):
#         keyboard.append([InlineKeyboardButton("Next", callback_data=f"stats_page:{page+1}")])
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     if update.callback_query:
#         await update.callback_query.edit_message_text(
#             "Choose a user to view stats:", reply_markup=reply_markup
#         )
#     else:
#         await update.message.reply_text("Choose a user to view stats:", reply_markup=reply_markup)

# # Handle button interactions for /stats
# async def stats_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split(":")
#     if data[0] == "stats":
#         username = data[1]
#         if username not in database:
#             await query.edit_message_text(f"User {username} not found.")
#             return
#         games = database[username]["games"]
#         roles = {}
#         for game in games:
#             role = game["role"]
#             if role not in roles:
#                 roles[role] = {"total": 0, "wins": 0}
#             roles[role]["total"] += 1
#             if game["result"] == "win":
#                 roles[role]["wins"] += 1

#         stats = f"{username}\nRole | Winrate | Total Games\n" + "-" * 30 + "\n"
#         total_wins = 0
#         for role, data in roles.items():
#             winrate = f"{(data['wins'] / data['total']) * 100:.0f}%"
#             stats += f"{role:<10} | {winrate:<8} | {data['total']}\n"
#             total_wins += data["wins"]
#         total_games = len(games)
#         total_winrate = f"{(total_wins / total_games) * 100:.0f}%" if total_games else "0%"
#         stats += f"\nTotal Winrate: {total_winrate} ({total_games})"
#         await query.edit_message_text(f"<pre>{stats}</pre>", parse_mode="HTML")

#     elif data[0] == "stats_page":
#         page = int(data[1])
#         await show_stats(update, context, page)

# # Show the rating table
# async def show_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     header = f"{'Name':<15} | {'Winrate':<10} | {'Games Played':<12}"
#     separator = "-" * len(header)
#     rows = []
#     for username, data in database.items():
#         games = data["games"]
#         total_games = len(games)
#         wins = sum(1 for game in games if game["result"] == "win")
#         winrate = f"{(wins / total_games) * 100:.0f}%" if total_games > 0 else "0%"
#         rows.append(f"{username:<15} | {winrate:<10} | {total_games:<12}")
#     table = f"{header}\n{separator}\n" + "\n".join(rows)
#     await update.message.reply_text(f"<pre>{table}</pre>", parse_mode="HTML")

# # Record game result
# async def record_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if len(context.args) != 3:
#         await update.message.reply_text("Usage: /record USERNAME ROLE RESULT")
#         return
#     username, role, result = context.args
#     if username not in database:
#         await update.message.reply_text(f"User {username} not found. Add them with /add first.")
#         return
#     if result.lower() not in ["win", "lose"]:
#         await update.message.reply_text("Result must be 'win' or 'lose'.")
#         return
#     update_player(username, role, result.lower(), None)
#     await update.message.reply_text(f"Recorded: {username} as {role} - {result}.")

# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     help_text = (
#         "/add USERNAME - Add a new user to the database\n"
#         "/start_game - Start a new game and select roles\n"
#         "/stats USERNAME - Show stats for a specific user\n"
#         "/table - Show the rating table\n"
#         "/record USERNAME ROLE RESULT - Record a game result for a user\n"
#         "/help - Show this help message\n"
#     )
#     await update.message.reply_text(help_text)

# # Main function
# def main():
#     application = Application.builder().token("7618494324:AAHDX6QgeH7dT3rKEDTE-8Jbp9fm_smuaWI").build()

#     application.add_handler(CommandHandler("add", add_user))
#     application.add_handler(CommandHandler("start_game", start_game))
#     application.add_handler(CommandHandler("stats", show_stats))
#     application.add_handler(CommandHandler("table", show_table))
#     application.add_handler(CommandHandler("record", record_game))
#     application.add_handler(CommandHandler("help", help_command)) 
#     application.add_handler(CallbackQueryHandler(handle_role_selection))
#     application.add_handler(CallbackQueryHandler(stats_button_handler, pattern="^stats.*"))

#     application.run_polling()

# if __name__ == "__main__":
#     main()

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os

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
    application = ApplicationBuilder().token("7618494324:AAHDX6QgeH7dT3rKEDTE-8Jbp9fm_smuaWI").build()

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
