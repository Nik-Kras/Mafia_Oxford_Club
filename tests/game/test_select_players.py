import pytest
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.bot import play, handle_callback
from src.utils.utils import get_paginated_keyboard
from src.utils.game import select_players
from unittest.mock import MagicMock, AsyncMock
import asyncio
import json

def get_all_mock_players():
    with open("tests/mock_players.json", "r") as file:
        MOCK_PLAYERS = json.load(file)
    print(f"\n{MOCK_PLAYERS}\n")
    return MOCK_PLAYERS

def create_mock_update(data=None, message_text=None):
    mock_update = MagicMock()
    mock_update.callback_query = MagicMock()
    mock_update.message = MagicMock()

    # Mock async methods
    mock_update.message.reply_text = AsyncMock()
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_reply_markup = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()

    # Set callback data and message text
    mock_update.callback_query.data = data
    mock_update.message.text = message_text

    return mock_update

# Mock Context object
def create_mock_context():
    mock_players = get_all_mock_players()
    print("mock_players: ", mock_players)
    mock_context = MagicMock()
    mock_context.user_data = {
        "page": 0,
        "remaining_users": mock_players.copy(),
        "selected_users": [],
    }
    print("mock_context: ", mock_context['user_data']['remaining_users'].__dict__)
    return mock_context

# Test the Players Selection from /play command
@pytest.mark.asyncio
async def test_select_players_initialization():
    update = create_mock_update(message_text="/play")
    context = create_mock_context()

    await play(update, context)

    # Assert the correct message is sent
    update.message.reply_text.assert_called_once()
    # call_args = update.message.reply_text.call_args[0]
    call_args = update.message.reply_text.call_args
    print("call_args: ", call_args)
    assert "Select users:" in call_args[0]

    # Assert keyboard is generated correctly
    keyboard = call_args[1]["reply_markup"].inline_keyboard
    assert len(keyboard) == 7  # 5 player buttons + 1 "Right Arrow" button + 1 "Finish" button 

# Test navigation buttons
@pytest.mark.asyncio
async def test_pagination():

    # Assume we clicked to the page 1 from page 0
    update = create_mock_update(data="page§1")
    context = create_mock_context()
    context.user_data["page"] = 0

    await handle_callback(update, context)

    # Assert page is updated and buttons are refreshed
    assert context.user_data["page"] == 1

    update.callback_query.edit_message_reply_markup.assert_called_once()
    call_args = update.callback_query.edit_message_reply_markup.call_args[1]
    keyboard = call_args["reply_markup"].inline_keyboard
    assert len(keyboard) == 7  # 5 player buttons + 1 for navigation buttons + 1 finish button

# Test selecting a player
@pytest.mark.asyncio
async def test_select_player():
    update = create_mock_update(data="select§Nikitos")
    context = create_mock_context()

    await handle_callback(update, context)

    assert "Nikitos" in context.user_data["selected_users"]
    assert "Nikitos" not in context.user_data["remaining_users"]

    # Assert buttons are refreshed
    update.callback_query.edit_message_reply_markup.assert_called_once()

# Test the "Finish" button
@pytest.mark.asyncio
async def test_finish_selection():
    update = create_mock_update(data="finish")
    context = create_mock_context()
    context.user_data["selected_users"] = ["Nikitos", "DonVito_13"]

    await handle_callback(update, context)

    # Assert the final message is sent
    update.callback_query.edit_message_text.assert_called_once_with(
        "Selected players:\n1. Nikitos\n2. DonVito_13"
    )

@pytest.mark.asyncio
async def test_select_multiple_players_with_pagination():
    # Step 1: Mock the update and context
    update = create_mock_update(data=None)  # Start without callback data
    context = create_mock_context()

    # Step 2: Simulate /play command to initialize player selection
    await select_players(update, context, players=context.user_data["remaining_users"])
    
    print("Here is what we start with: ")
    print(update.__dict__)
    print(context['user_data']['remaining_users'])

    # Assert the initialization is correct
    update.message.reply_text.assert_called_once()
    initial_call_args = update.message.reply_text.call_args.kwargs
    assert "reply_markup" in initial_call_args
    keyboard = initial_call_args["reply_markup"].inline_keyboard
    assert len(keyboard) == 7  # 5 players + 1 "➡️" button + 1 "Finish" button

    # Step 3: Select two players from the first page
    for user in ["Nikitos", "MilkyWay🥛"]:
        update.callback_query.data = f"select§{user}"
        await handle_callback(update, context)

        # Assert user is added to selected_users
        assert user in context.user_data["selected_users"]
        # Assert user is removed from remaining_users
        assert user not in context.user_data["remaining_users"]

    # Step 4: Navigate to the second page
    update.callback_query.data = "page§1"
    await handle_callback(update, context)

    # Assert page update
    assert context.user_data["page"] == 1

    # Step 5: Select two players from the second page
    for user in ["MobsterQueen", "Underboss_9"]:
        update.callback_query.data = f"select§{user}"
        await handle_callback(update, context)

        # Assert user is added to selected_users
        assert user in context.user_data["selected_users"]
        # Assert user is removed from remaining_users
        assert user not in context.user_data["remaining_users"]

    # Step 6: Finish selection and verify the order of selected users
    update.callback_query.data = "finish"
    await handle_callback(update, context)

    # Assert the final message is sent with the correct order
    update.callback_query.edit_message_text.assert_called_once_with(
        "Selected players:\n1. Nikitos\n2. MilkyWay🥛\n3. MobsterQueen\n4. Underboss_9"
    )

async def main():
    await test_select_multiple_players_with_pagination()

if __name__ == "__main__":
    asyncio.run(main())
