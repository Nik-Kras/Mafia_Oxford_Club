from telegram import Update
from telegram.ext import ContextTypes
import utils.game as game
import utils.player as player
import utils.stats as stats


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Description: Commands to add or remove players from the players.json
    Permission: Admin only
    """
    game.select_players(update, context)


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
    
def add_player(username: str):
    """ Adds a player to the player database """
    return player.add_player(username)
    
def remove_player(username: str):
    """ Removes a player from the player database """
    return player.remove_player(username)
    
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
