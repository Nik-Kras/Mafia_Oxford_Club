# Done
from telegram import Update
from telegram.ext import ContextTypes
from .utils import get_paginated_keyboard, STATES
from .game import Game, start_role_assignment, start_killing_phase, start_winner_selection
from .stats import show_last_game

async def handle_callback_by_state(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Route callbacks based on game state."""
    states = {
        STATES["SELECTING_PLAYERS"]: handle_player_selection,
        STATES["ASSIGNING_ROLES"]: handle_role_assignment,
        STATES["KILLING_PLAYER"]: handle_killing_phase,
        STATES["SELECTING_WINNER"]: handle_winner_selection
    }
    
    current_state = context.user_data.get("state")
    handler = states.get(current_state)
    
    if handler:
        await handler(update, context, logger)
    else:
        logger.warning("Unhandled state: %s", current_state)
        await update.callback_query.edit_message_text("Invalid game state. Please start a new game.")

# Stage 1 of the game
async def handle_player_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Handle player selection phase callbacks."""
    query = update.callback_query
    data = query.data
    game: Game = context.user_data["game"]

    if data.startswith("select§"):
        username = data.split("§")[1]
        if username in context.user_data["remaining_users"]:
            game.add_player(username)
            context.user_data["remaining_users"].remove(username)
            await query.edit_message_reply_markup(
                reply_markup=get_paginated_keyboard(
                    context.user_data["remaining_users"],
                    context.user_data["page"],
                    "select"
                )
            )
    elif data.startswith("page§"):
        page = int(data.split("§")[1])
        context.user_data["page"] = page
        await query.edit_message_reply_markup(
            reply_markup=get_paginated_keyboard(
                context.user_data["remaining_users"],
                page,
                "select"
            )
        )
    elif data == "finish":
        if game.selected_usernames:
            context.user_data["state"] = STATES["ASSIGNING_ROLES"]
            await start_role_assignment(update, context, logger)
        else:
            await query.edit_message_text("No players selected. Please start a new game.")

# Stage 2 of the game
async def handle_role_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Handle role assignment phase callbacks."""
    query = update.callback_query
    role = query.data.split("§")[1]

    game: Game = context.user_data["game"]
    current_player = game.selected_usernames.pop(0)
    game.assign_role(current_player, role)
    
    if game.selected_usernames:
        await start_role_assignment(update, context, logger)
    else:
        context.user_data["state"] = STATES["KILLING_PLAYER"]
        await start_killing_phase(update, context, logger)

# Stage 3 of the game
async def handle_killing_phase(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Handle killing phase callbacks."""
    query = update.callback_query
    data = query.data
    
    if data.startswith("kill§"):
        username = data.split("§")[1]
        username = username.split("[")[0].strip()
        game: Game = context.user_data["game"]
        game.kill_player(username)
        await start_killing_phase(update, context, logger)
    elif data == "finish":
        context.user_data["state"] = STATES["SELECTING_WINNER"]
        await start_winner_selection(update, context, logger)

# Stage 4 of the game
async def handle_winner_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """Handle winner selection phase callbacks."""
    query = update.callback_query
    winning_team = query.data.split("§")[1]
    
    game: Game = context.user_data["game"]
    game.set_winner(winning_team)
    game.save()
    message = f"Game completed! {winning_team} wins! 🎉\n"
    message += show_last_game()
    
    await query.edit_message_text(message)
