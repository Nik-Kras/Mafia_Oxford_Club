from telegram import Update
from telegram.ext import ContextTypes
import src.utils.player as player
from src.utils.utils import get_paginated_keyboard, STATES


"""
context.user_data["state"] - One of 4 States of the game, check src.utils.utils.STATES
context.user_data["remaining_users"] - List of users to select from in the first stage
context.user_data["selected_users"] - List of selected users in the 1st stage. They will play the game
context.user_data["assigned_roles"]:
{
    'Nikitos': {'role': 'Mafia', 'survived': True},
    'Roman': {'role': 'Citizen', 'survived': True},
    ...
}
In the next game stage you select a user and kill him, updating 'survived' field
Then, when you select which team won -< you save the whole record in the database
"""
async def start_selecting_players(update: Update, context: ContextTypes.DEFAULT_TYPE, players=None):
    """ Selects a set of players for the current game, no roles assigned but players are ordered """
    if players is None:
        all_players = player.get_all_players()
    else:
        all_players = players
    context.user_data["state"] = STATES["SELECTING_PLAYERS"]
    context.user_data["remaining_users"] = all_players.copy()
    context.user_data["selected_users"] = []
    context.user_data["assigned_roles"] = {}
    context.user_data["page"] = 0
    await update.message.reply_text(
        "Select users:",
        reply_markup=get_paginated_keyboard(context.user_data['remaining_users'], context.user_data['page'], prefix="select")
    )
    
def assign_role_to_player():
    """ A player is assigned with a role """

    # team == red or black
    # iteratively add players and their roles to the team: red -> Commissar or Civilian; black -> Don or Mafia
    ...
    
def kill_player(username: str):
    # Updates his status
    ...
    
def select_victory(team: str):
    ...
    
def record_game(record: dict):
    ...
    