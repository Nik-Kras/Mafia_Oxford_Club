from telegram import Update
from telegram.ext import ContextTypes
import src.utils.player as player
from src.utils.utils import get_paginated_keyboard

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Everything from setecting teams to selecting victory and saving a record
    await select_players(update, context)

async def select_players(update: Update, context: ContextTypes.DEFAULT_TYPE, players=None):
    """ Selects a set of players for the current game, no roles assigned but players are ordered """
    if players is None:
        all_players = player.get_all_players()
    else:
        all_players = players
    context.user_data['page'] = 0
    context.user_data['remaining_users'] = all_players.copy()
    context.user_data['selected_users'] = []

    await update.message.reply_text(
        "Select users:",
        reply_markup=get_paginated_keyboard(context.user_data['remaining_users'], context.user_data['page'])
    )
    
def assign_role_to_player():
    """ A player is assigned with a role """

    # team == red or black
    # iteratively add players and their roles to the team: red -> Commissar or Civilian; black -> Don or Mafia
    ...
    ...
    
def kill_player(username: str):
    # Updates his status
    ...
    
def select_victory(team: str):
    ...
    
def record_game(record: dict):
    ...
    