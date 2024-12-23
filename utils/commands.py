import utils.game as game
import utils.player as player
import utils.stats as stats


def play():
    """
    Description: Commands to add or remove players from the players.json
    Permission: Admin only
    """
    ...

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
    return player.get_all_players()

def help():
    """
    Description: Shows a supportive message with brief on each command
    Permission: Everyone
    """
    ...
