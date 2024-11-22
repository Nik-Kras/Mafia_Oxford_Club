from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json
from datetime import datetime

# Load or initialize the database
DATABASE_FILE = "mafia_database.json"
try:
    with open(DATABASE_FILE, "r") as f:
        database = json.load(f)
except FileNotFoundError:
    database = {}

# Save database function
def save_database():
    with open(DATABASE_FILE, "w") as f:
        json.dump(database, f, indent=4)

# Globals for managing game state
game_state = {
    "host": None,
    "don": None,
    "commissar": None,
    "mafia": [],
    "people": [],
    "step": None,
    "players": [],
}

# Add user to database
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /add USERNAME")
        return
    username = context.args[0]
    if username in database:
        await update.message.reply_text(f"User {username} already exists.")
    else:
        database[username] = {"games": []}
        save_database()
        await update.message.reply_text(f"User {username} added to the database.")

# Update player record
def update_player(username, role, result, host):
    record = {
        "role": role,
        "result": result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host": host,
    }
    database[username]["games"].append(record)
    save_database()

# Display a paginated table of usernames
async def display_user_table(update, context, message, callback_prefix, page=0):
    usernames = game_state["players"]
    start = page * 5
    end = start + 5
    keyboard = [
        [InlineKeyboardButton(username, callback_data=f"{callback_prefix}:{username}")]
        for username in usernames[start:end]
    ]
    if start > 0:
        keyboard.append([InlineKeyboardButton("Prev", callback_data=f"{callback_prefix}_page:{page-1}")])
    if end < len(usernames):
        keyboard.append([InlineKeyboardButton("Next", callback_data=f"{callback_prefix}_page:{page+1}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        # Regular command
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        # Inline button interaction
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)

# Start game command
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_state["step"] = "select_host"
    game_state["players"] = list(database.keys())
    await display_user_table(update, context, "Choose the host:", "select_host")

# Handle role selection
async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")
    step = data[0]
    username = data[1] if len(data) > 1 else None

    if step.endswith("_page"):  # Handle pagination
        page = int(data[1])
        callback_prefix = step.split("_")[0]
        if "_" in step:  # Ensure we can safely split by "_"
            role = callback_prefix.split("_")[1] if len(callback_prefix.split("_")) > 1 else "role"
            message = f"Choose {role}:"
        else:
            message = "Choose a player:"
        await display_user_table(update, context, message, callback_prefix, page)
        return

    if step == "select_host":
        game_state["host"] = username
        update_player(username, "host", "playing", None)
        game_state["step"] = "select_don"
        await display_user_table(update, context, "Choose Don:", "select_don")

    elif step == "select_don":
        game_state["don"] = username
        update_player(username, "Don", "playing", game_state["host"])
        game_state["step"] = "select_commissar"
        await display_user_table(update, context, "Choose Commissar:", "select_commissar")

    elif step == "select_commissar":
        game_state["commissar"] = username
        update_player(username, "Commissar", "playing", game_state["host"])
        game_state["step"] = "select_mafia"
        await display_user_table(update, context, "Select Mafia. Press 'Mafia is selected' when done.", "select_mafia")

    elif step == "select_mafia":
        if username:
            game_state["mafia"].append(username)
            update_player(username, "Black", "playing", game_state["host"])
        else:
            game_state["step"] = "select_people"
            await display_user_table(update, context, "Select People. Press 'People are selected' when done.", "select_people")

    elif step == "select_people":
        if username:
            game_state["people"].append(username)
            update_player(username, "White", "playing", game_state["host"])
        else:
            game_state["step"] = "game_outcome"
            buttons = [
                [InlineKeyboardButton("Mafia Won", callback_data="mafia_won")],
                [InlineKeyboardButton("People Won", callback_data="people_won")],
            ]
            await update.callback_query.edit_message_text(
                "Select the winning team:", reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif step in ["mafia_won", "people_won"]:
        winning_team = "Mafia" if step == "mafia_won" else "People"
        losing_team = "People" if step == "mafia_won" else "Mafia"
        for username in game_state["mafia"] + ([game_state["don"]] if winning_team == "Mafia" else []):
            update_player(username, "Black" if username in game_state["mafia"] else "Don", "win", game_state["host"])
        for username in game_state["people"] + ([game_state["commissar"]] if losing_team == "People" else []):
            update_player(username, "White" if username in game_state["people"] else "Commissar", "lose", game_state["host"])
        await update.callback_query.edit_message_text("Game outcome recorded.")

# Show stats for a specific user
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    usernames = list(database.keys())
    start = page * 5
    end = start + 5
    keyboard = [
        [InlineKeyboardButton(username, callback_data=f"stats:{username}")]
        for username in usernames[start:end]
    ]
    if start > 0:
        keyboard.append([InlineKeyboardButton("Prev", callback_data=f"stats_page:{page-1}")])
    if end < len(usernames):
        keyboard.append([InlineKeyboardButton("Next", callback_data=f"stats_page:{page+1}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Choose a user to view stats:", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("Choose a user to view stats:", reply_markup=reply_markup)

# Handle button interactions for /stats
async def stats_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")
    if data[0] == "stats":
        username = data[1]
        if username not in database:
            await query.edit_message_text(f"User {username} not found.")
            return
        games = database[username]["games"]
        roles = {}
        for game in games:
            role = game["role"]
            if role not in roles:
                roles[role] = {"total": 0, "wins": 0}
            roles[role]["total"] += 1
            if game["result"] == "win":
                roles[role]["wins"] += 1

        stats = f"{username}\nRole | Winrate | Total Games\n" + "-" * 30 + "\n"
        total_wins = 0
        for role, data in roles.items():
            winrate = f"{(data['wins'] / data['total']) * 100:.0f}%"
            stats += f"{role:<10} | {winrate:<8} | {data['total']}\n"
            total_wins += data["wins"]
        total_games = len(games)
        total_winrate = f"{(total_wins / total_games) * 100:.0f}%" if total_games else "0%"
        stats += f"\nTotal Winrate: {total_winrate} ({total_games})"
        await query.edit_message_text(f"<pre>{stats}</pre>", parse_mode="HTML")

    elif data[0] == "stats_page":
        page = int(data[1])
        await show_stats(update, context, page)

# Show the rating table
async def show_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    header = f"{'Name':<15} | {'Winrate':<10} | {'Games Played':<12}"
    separator = "-" * len(header)
    rows = []
    for username, data in database.items():
        games = data["games"]
        total_games = len(games)
        wins = sum(1 for game in games if game["result"] == "win")
        winrate = f"{(wins / total_games) * 100:.0f}%" if total_games > 0 else "0%"
        rows.append(f"{username:<15} | {winrate:<10} | {total_games:<12}")
    table = f"{header}\n{separator}\n" + "\n".join(rows)
    await update.message.reply_text(f"<pre>{table}</pre>", parse_mode="HTML")

# Record game result
async def record_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text("Usage: /record USERNAME ROLE RESULT")
        return
    username, role, result = context.args
    if username not in database:
        await update.message.reply_text(f"User {username} not found. Add them with /add first.")
        return
    if result.lower() not in ["win", "lose"]:
        await update.message.reply_text("Result must be 'win' or 'lose'.")
        return
    update_player(username, role, result.lower(), None)
    await update.message.reply_text(f"Recorded: {username} as {role} - {result}.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/add USERNAME - Add a new user to the database\n"
        "/start_game - Start a new game and select roles\n"
        "/stats USERNAME - Show stats for a specific user\n"
        "/table - Show the rating table\n"
        "/record USERNAME ROLE RESULT - Record a game result for a user\n"
        "/help - Show this help message\n"
    )
    await update.message.reply_text(help_text)

# Main function
def main():
    application = Application.builder().token("7618494324:AAHDX6QgeH7dT3rKEDTE-8Jbp9fm_smuaWI").build()

    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("start_game", start_game))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("table", show_table))
    application.add_handler(CommandHandler("record", record_game))
    application.add_handler(CommandHandler("help", help_command)) 
    application.add_handler(CallbackQueryHandler(handle_role_selection))
    application.add_handler(CallbackQueryHandler(stats_button_handler, pattern="^stats.*"))

    application.run_polling()

if __name__ == "__main__":
    main()
