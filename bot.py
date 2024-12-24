from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import utils.commands as commands
import utils.game as game
from utils.utils import get_paginated_keyboard
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')


def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == str(ADMIN_ID)


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Testing command """
    await game.play_game(update, context)


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
    await update.message.reply_text(commands.view_players())


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    def extract_data_from_query(query):
        """ Query returns just one string, but it is multifunction. This function extracts information """
        if ";" in query.data:
            N = len(query.data.split(";"))
            if N == 2:
                func, data = query.data.split(";")
                return {"function": func, "data": data}
        else:
            return {"function": query.data}

    query_data = extract_data_from_query(query)

    if query_data["function"] == "page":
        page = int(query_data["data"])
        context.user_data['page'] = page
        await query.edit_message_reply_markup(
            reply_markup=get_paginated_keyboard(context.user_data['remaining_users'], page)
        )
    elif query_data["function"] == "select":
        username = query_data["data"]

        # Debug log
        print("***")
        print(f"Selecting user: {username}")
        print(f"Remaining users before removal: {context.user_data['remaining_users']}")
        print(f"Selected users before addition: {context.user_data['selected_users']}")

        if username in context.user_data['remaining_users']:
            context.user_data['selected_users'].append(username)
            context.user_data['remaining_users'].remove(username)

            # Debug log after changes
            print(f"Remaining users after removal: {context.user_data['remaining_users']}")
            print(f"Selected users after addition: {context.user_data['selected_users']}")
        else:
            print(f"Error: {username} not found in remaining_users")
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
        else:
            response = "No users selected."

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
