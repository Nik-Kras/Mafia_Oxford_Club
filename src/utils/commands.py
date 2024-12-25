from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import src.utils.game as game
import src.utils.player as player
import src.utils.stats as stats
from src.utils.utils import get_paginated_keyboard, is_admin, STATES, ROLES
    
# Handler: Player Selection
async def handle_player_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    data = query.data

    if data.startswith("select§"):
        username = data.split("§")[1]
        if username in context.user_data["remaining_users"]:
            context.user_data["selected_users"].append(username)
            context.user_data["remaining_users"].remove(username)
            logger.info("Player %s selected.", username)
            await query.edit_message_reply_markup(
                reply_markup=get_paginated_keyboard(context.user_data["remaining_users"], context.user_data["page"], prefix="select")
            )
        else:
            logger.error("Player %s not found in remaining_users.", username)
    elif data.startswith("page§"):
        page = int(data.split("§")[1])
        context.user_data["page"] = page
        await query.edit_message_reply_markup(
            reply_markup=get_paginated_keyboard(context.user_data["remaining_users"], page, prefix="select")
        )
    elif data == "finish":
        context.user_data["state"] = STATES["ASSIGNING_ROLES"]
        selected_users = context.user_data.get('selected_users', [])
        if not selected_users:
            response = "No users selected."
            logger.info("User %s finished selection with no players selected.", query.from_user.username)
            await query.edit_message_text(response)
            return
        
        context.user_data["role_assignment"] = {
            "players": selected_users,
            "current_index": 0
        }
        logger.info("User %s finished selecting players: %s", query.from_user.username, selected_users)
        await query.edit_message_text(f"Selected players:\n" + "\n".join(selected_users))
        await perform_role_assignment(update, context, logger)


# Handler: Role Assignment
async def perform_role_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    players = context.user_data["role_assignment"]["players"]
    current_index = context.user_data["role_assignment"]["current_index"]

    if current_index >= len(players):
        context.user_data["state"] = STATES["KILLING_PLAYER"]
        logger.info("All roles assigned. Moving to the killing phase.")

        # Show the player gallery for the killing phase
        alive_players_keyboard = get_alive_players_keyboard(context, page=0)
        context.user_data["page"] = 0
        
        await query.edit_message_text(
            text="Roles assigned! Now select a player to kill:",
            reply_markup=alive_players_keyboard
        )
        return

    current_player = players[current_index]
    role_buttons = [
        [InlineKeyboardButton(role, callback_data=f"role§{current_player}§{role}")] for role in ROLES
    ]
    keyboard = InlineKeyboardMarkup(role_buttons)
    await query.edit_message_text(
        text=f"Assign a role to: {current_player}",
        reply_markup=keyboard
    )


# Handler: Role Selection
async def handle_role_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    _, player, role = query.data.split("§")

    context.user_data["assigned_roles"][player] = {"role": role, "survived": True}
    logger.info("Assigned role %s to player %s.", role, player)

    context.user_data["role_assignment"]["current_index"] += 1
    await perform_role_assignment(update, context, logger)


def get_alive_players_keyboard(context, page):
    """ Generate inline keyboard for players with survived=True """
    alive_players = [
        player for player, details in context.user_data["assigned_roles"].items()
        if details["survived"]
    ]
    return get_paginated_keyboard(alive_players, page, "kill")


def get_kill_confirmation_keyboard(username):
    """ Generate confirmation keyboard for killing a player """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Kill", callback_data=f"confirm_kill§{username}")],
        [InlineKeyboardButton("Back", callback_data="to_gallery")]
    ])

# Handle player gallery for killing
async def handle_killing_player(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    data = query.data

    # Navigation or selecting a player to kill
    if data.startswith("kill§"):
        username = data.split("§")[1]
        logger.info("User selected %s for potential killing.", username)
        await query.edit_message_text(
            text=f"Do you want to kill {username}?",
            reply_markup=get_kill_confirmation_keyboard(username)
        )
    elif data.startswith("page§"):
        page = int(data.split("§")[1])
        context.user_data["page"] = page
        await query.edit_message_reply_markup(
            reply_markup=get_alive_players_keyboard(context, page)
        )
    elif data == "to_gallery":
        page = context.user_data.get("page", 0)
        logger.info("User navigated back to player gallery.")
        await query.edit_message_text(
            text="Select a player to kill:",
            reply_markup=get_alive_players_keyboard(context, page)
        )
    elif data == "finish":
        context.user_data["state"] = STATES["SELECTING_WINNER"]
        await query.edit_message_text("Killing phase complete. Proceed to select the winning team.")
        logger.info("User finished the killing phase.")
    else:
        logger.warning("Unhandled callback data in killing phase: %s", data)

# Handle confirmation dialog for killing
async def handle_kill_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    data = query.data

    if data.startswith("confirm_kill§"):
        username = data.split("§")[1]
        context.user_data["assigned_roles"][username]["survived"] = False
        logger.info("Player %s killed.", username)
        await query.edit_message_text(
            text=f"Player {username} has been killed.",
        )
        # Back to player gallery
        page = context.user_data.get("page", 0)
        await query.edit_message_text(
            text="Select another player to kill or finish:",
            reply_markup=get_alive_players_keyboard(context, page)
        )
    elif data == "to_gallery":
        logger.info("User navigated back to player gallery.")
        page = context.user_data.get("page", 0)
        await query.edit_message_text(
            text="Select a player to kill:",
            reply_markup=get_alive_players_keyboard(context, page)
        )


# Handler: Selecting Winner
async def handle_selecting_winner(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    query = update.callback_query
    winning_team = query.data.split("§")[1]

    context.user_data["winning_team"] = winning_team
    logger.info("Winning team: %s.", winning_team)

    await query.edit_message_text(f"Game over! Winning team: {winning_team}")


def view_games():
    """
    Description: Allows you to see a gallery of all played games from games.json
    Permission: Everyone
    """
    ...

def view_leaderboard():
    """
    Description: Shows a table of players and their winrate for team red in one column and team black in the other. #TODO: add Elo rating as a 3rd column. You specify how to sort the table
    Permission: Everyone
    """
    ...

def view_player():
    """
    Description: Shows full stats of a single player. His winrate and survival rate for each role and team.
    Permission: Everyone
    """
    ...
    
async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """ Adds a player to the player database """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        logger.warning("Unauthorized access attempt by user %s.", update.message.from_user.username)
        return

    if not context.args:
        await update.message.reply_text("Usage: /add_player <player_name>")
        logger.info("Admin %s used /add_player without providing arguments.", update.message.from_user.username)
        return
    
    return player.add_player(username=context.args[0])
    
async def remove_player(update: Update, context: ContextTypes.DEFAULT_TYPE, logger):
    """ Removes a player from the player database """
    if not is_admin(update):
        await update.message.reply_text("You don't have permission to use this command.")
        logger.warning("Unauthorized access attempt by user %s.", update.message.from_user.username)
        return

    if not context.args:
        await update.message.reply_text("Usage: /remove_player <player_name>")
        logger.info("Admin %s used /remove_player without providing arguments.", update.message.from_user.username)
        return
    
    return player.remove_player(username=context.args[0])
    
def view_players():
    """ Shows a list of all players from the database """
    players = player.get_all_players()
    if players:
        players_message = '\n'.join(players)
        return f"Players:\n{players_message}"
    return "No players found."

def help():
    """
    Description: Shows a supportive message with brief on each command
    Permission: Everyone
    """
    ...
