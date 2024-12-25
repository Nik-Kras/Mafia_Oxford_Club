from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import src.utils.commands as commands
import src.utils.game as game
from src.utils.utils import get_paginated_keyboard, is_admin, STATES
from dotenv import load_dotenv
import logging
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

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


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the game and initialize player selection."""
    await game.start_selecting_players(update, context)
    logger.info("User %s initiated player selection.", update.message.from_user.username)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Testing command """
    await update.message.reply_text("Welcome to Mafia Oxford Club Bot!")
    logger.info("User %s started the bot.", update.message.from_user.username)
    
    
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Adds a player to the list, if you are an admin """
    result = await commands.add_player(update, context, logger)
    await update.message.reply_text(result)
    logger.info("Admin %s added player %s.", update.message.from_user.username, context.args[0])
    
    
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Removes a player to the list, if you are an admin """
    result = await commands.remove_player(update, context, logger)
    await update.message.reply_text(result)
    logger.info("Admin %s removed player %s.", update.message.from_user.username, context.args[0])
    
    
async def view_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Shows a list of all players """
    players_list = commands.view_players()
    await update.message.reply_text(players_list)
    logger.info("User %s viewed the players list.", update.message.from_user.username)


# Callback Handler: Main Dispatcher
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_state = context.user_data.get("state", None)
    logger.info("Handling callback in state: %s", current_state)

    if current_state == STATES["SELECTING_PLAYERS"]:
        await commands.handle_player_selection(update, context, logger)
    elif current_state == STATES["ASSIGNING_ROLES"]:
        await commands.handle_role_assignment(update, context, logger)
    elif current_state == STATES["KILLING_PLAYER"]:
        if query.data.startswith("confirm_kill"):
            await commands.handle_kill_confirmation(update, context, logger)
        # As there are only 2 states, let's keep it simple
        # elif query.data == "to_gallery":
        #     await commands.handle_killing_player(update, context, logger)
        else:
            await commands.handle_killing_player(update, context, logger)
    elif current_state == STATES["SELECTING_WINNER"]:
        await commands.handle_selecting_winner(update, context, logger)
    else:
        logger.warning("Unknown state: %s", current_state)
        await query.edit_message_text("Unexpected state. Please restart the game.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("remove_player", remove_player))
    application.add_handler(CommandHandler("view_players", view_players))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
