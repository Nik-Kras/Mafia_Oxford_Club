from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import utils.commands as commands
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')


def is_admin(update: Update) -> bool:
    return update.message.from_user.username == ADMIN_USERNAME


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Testing command """
    await update.message.reply_text("Welcome to Mafia Oxford Club Bot!")
    
    
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Adds a player to the list, if you are an admin """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /add_player <player_name>")
        return

    result = commands.add_player(username=context.args[0])
    await update.message.reply_text(result)
    
    
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Removes a player to the list, if you are an admin """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /remove_player <player_name>")
        return
    
    result = commands.remove_player(username=context.args[0])
    await update.message.reply_text(result)
    
    
async def view_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Shows a list of all players """
    result = commands.view_players()
    await update.message.reply_text(f"Players:\n{result}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_player", add_player))
    application.add_handler(CommandHandler("remove_player", remove_player))
    application.add_handler(CommandHandler("view_players", view_players))
    
    application.run_polling()

if __name__ == "__main__":
    main()
