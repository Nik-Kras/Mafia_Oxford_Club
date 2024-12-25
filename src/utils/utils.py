
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

PAGE_SIZE = 5
ROLES = ("Mafia", "Don", "Citizen", "Commissar")
TEAMS = ("Team_Red", "Team_Black")


def get_paginated_keyboard(users, page):
    """Generate inline keyboard for paginated user list."""
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    buttons = [
        [InlineKeyboardButton(user, callback_data=f"select§{user}")] for user in users[start:end]
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
