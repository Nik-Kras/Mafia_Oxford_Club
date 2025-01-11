from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import src.utils.commands as commands
import src.utils.handlers as handlers
from dotenv import load_dotenv
import os
from src.utils.logger import MafiaLogger

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize single logger instance
logger = MafiaLogger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message and bot introduction."""
    welcome_message = (
        "🎮 Welcome to Mafia Oxford Club Bot! 🎮\n\n"
        "I help manage and track Mafia games. Use /help to see available commands."
    )
    await update.message.reply_text(welcome_message)
    logger.log_command(update, "/start")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback handler for inline buttons."""
    query = update.callback_query
    await query.answer()
    
    current_state = context.user_data.get("state", None)
    logger.log_callback(update, f"State: {current_state}, Data: {query.data}")
    await handlers.handle_callback_by_state(update, context, logger)

def main():
    """Initialize and run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Basic commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", commands.help_command))
    
    # Player management commands
    application.add_handler(CommandHandler("add_player", commands.add_player))
    application.add_handler(CommandHandler("remove_player", commands.remove_player))
    application.add_handler(CommandHandler("view_players", commands.view_players))
    
    # Game commands
    application.add_handler(CommandHandler("play", commands.play))
    application.add_handler(CommandHandler("view_game", commands.view_game))
    
    # Stats commands
    application.add_handler(CommandHandler("stats", commands.view_player_stats))
    application.add_handler(CommandHandler("leaderboard", commands.view_leaderboard))
    
    # Callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("Bot started successfully")
    application.run_polling()

if __name__ == "__main__":
    main()