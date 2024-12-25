from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import src.utils.commands as commands
import src.utils.game as game
from src.utils.utils import get_paginated_keyboard
from dotenv import load_dotenv
import logging
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Set up logging
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "bot.log")
os.makedirs(LOGS_DIR, exist_ok=True)  # Ensure logs directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Optional: To also log to the console
    ]
)

logger = logging.getLogger("my_bot")

# Suppress third-party library logs
for noisy_logger in ["telegram", "telegram.ext", "urllib3", "requests", "httpx", "httpcore"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == str(ADMIN_ID)


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Testing command """
    await game.play_game(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Testing command """
    await update.message.reply_text("Welcome to Mafia Oxford Club Bot!")
    logger.info("User %s started the bot.", update.message.from_user.username)
    
    
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Adds a player to the list, if you are an admin """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        logger.warning("Unauthorized access attempt by user %s.", update.message.from_user.username)
        return

    if not context.args:
        await update.message.reply_text("Usage: /add_player <player_name>")
        logger.info("Admin %s used /add_player without providing arguments.", update.message.from_user.username)
        return

    result = commands.add_player(username=context.args[0])
    await update.message.reply_text(result)
    logger.info("Admin %s added player %s.", update.message.from_user.username, context.args[0])
    
    
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Removes a player to the list, if you are an admin """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        logger.warning("Unauthorized access attempt by user %s.", update.message.from_user.username)
        return

    if not context.args:
        await update.message.reply_text("Usage: /remove_player <player_name>")
        logger.info("Admin %s used /remove_player without providing arguments.", update.message.from_user.username)
        return
    
    result = commands.remove_player(username=context.args[0])
    await update.message.reply_text(result)
    logger.info("Admin %s removed player %s.", update.message.from_user.username, context.args[0])
    
    
async def view_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Shows a list of all players """
    players_list = commands.view_players()
    await update.message.reply_text(players_list)
    logger.info("User %s viewed the players list.", update.message.from_user.username)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    def extract_data_from_query(query):
        """ Query returns just one string, but it is multifunction. This function extracts information """
        if "§" in query.data:
            N = len(query.data.split("§"))
            if N == 2:
                func, data = query.data.split("§")
                return {"function": func, "data": data}
        else:
            return {"function": query.data}
    query_data = extract_data_from_query(query)
    print(query_data)

    if query_data["function"] == "page":
        page = int(query_data["data"])
        context.user_data['page'] = page
        logger.info("User %s navigated to page %d.", query.from_user.username, page)
        await query.edit_message_reply_markup(
            reply_markup=get_paginated_keyboard(context.user_data['remaining_users'], page)
        )
    elif query_data["function"] == "select":
        username = query_data["data"]

        logger.info("User %s is selecting: %s", query.from_user.username, username)
        logger.debug("Remaining users before removal: %s", context.user_data['remaining_users'])
        logger.debug("Selected users before addition: %s", context.user_data['selected_users'])

        print("context.user_data['remaining_users']: ", context.user_data['remaining_users'])

        if username in context.user_data['remaining_users']:
            context.user_data['selected_users'].append(username)
            context.user_data['remaining_users'].remove(username)

            logger.debug("Remaining users after removal: %s", context.user_data['remaining_users'])
            logger.info("Selected users after addition: %s", context.user_data['selected_users'])
        else:
            logger.error("Error: %s not found in remaining_users for user %s.", username, query.from_user.username)
            await query.edit_message_text("Error: User not found in remaining users. Please try again.")
            return

        await query.edit_message_reply_markup(
            reply_markup=get_paginated_keyboard(context.user_data['remaining_users'], context.user_data['page'])
        )
    elif query_data["function"] == "finish":
        # Handle finish
        selected_users = context.user_data.get('selected_users', [])
        if selected_users:
            response = "\n".join(f"{i+1}. {user}" for i, user in enumerate(selected_users))
            logger.info("User %s finished selecting players: %s", query.from_user.username, selected_users)
        else:
            response = "No users selected."
            logger.info("User %s finished selection with no players selected.", query.from_user.username)

        await query.edit_message_text(f"Selected players:\n{response}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("remove_player", remove_player))
    application.add_handler(CommandHandler("view_players", view_players))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
