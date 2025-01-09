from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional
from .json_utils import load_json, PLAYERS_FILE

PAGE_SIZE = 5

ROLES = ["Don", "Mafia", "Commissar", "Citizen", "Host"]
TEAMS = ["Team_Red", "Team_Black"]

STATES = {
    "SELECTING_PLAYERS": "selecting_players",
    "ASSIGNING_ROLES": "assigning_roles",
    "KILLING_PLAYER": "killing_player",
    "SELECTING_WINNER": "selecting_winner"
}

def get_paginated_keyboard(
    items: List[str],
    page: int,
    prefix: str = "select",
    additional_buttons: Optional[List[List[InlineKeyboardButton]]] = None
) -> InlineKeyboardMarkup:
    """
    Generate a paginated inline keyboard.
    
    Args:
        items: List of items to paginate
        page: Current page number
        prefix: Prefix for callback data
        additional_buttons: Optional additional buttons to add at the bottom
    """
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    
    # Item buttons
    buttons = [
        [InlineKeyboardButton(item, callback_data=f"{prefix}§{item}")]
        for item in items[start:end]
    ]
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page§{page-1}"))
    if end < len(items):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page§{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Additional buttons
    if additional_buttons:
        buttons.extend(additional_buttons)
    
    # Always add finish button
    buttons.append([InlineKeyboardButton("Finish", callback_data="finish")])
    
    return InlineKeyboardMarkup(buttons)

# NOT TESTED
def calculate_elo_change(winner_rating: int, loser_rating: int, k_factor: int = 32) -> tuple[int, int]:
    """
    Calculate Elo rating changes for winner and loser.
    
    Args:
        winner_rating: Current rating of the winner
        loser_rating: Current rating of the loser
        k_factor: How much ratings can change (default: 32)
    
    Returns:
        Tuple of (winner_change, loser_change)
    """
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    change = round(k_factor * (1 - expected_winner))
    return change, -change
