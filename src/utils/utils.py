
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import logging
import os


PAGE_SIZE = 5
ROLES = ("Mafia", "Don", "Citizen", "Commissar")
TEAMS = ("Team_Red", "Team_Black")
STATES = {
    "SELECTING_PLAYERS": "selecting_players",
    "ASSIGNING_ROLES": "assigning_roles",
    "KILLING_PLAYER": "killing_player",
    "SELECTING_WINNER": "selecting_winner",
}

load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')


def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == str(ADMIN_ID)


def get_paginated_keyboard(users, page, prefix="kill"):
    """Generate inline keyboard for paginated user list."""
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    buttons = [
        [InlineKeyboardButton(user, callback_data=f"{prefix}§{user}")] for user in users[start:end]
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page§{page - 1}"))
    if end < len(users):
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"page§{page + 1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton("Finish", callback_data="finish")])
    return InlineKeyboardMarkup(buttons)
