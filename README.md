# Mafia_Oxford_Club

Project Structure:

## DataBases

1. Players
* Filename: players.json
* Description: A list of unique players. PS: Could be used to keep real name and username pairs
* Purpose: Will be used to select a player from the list of all possible players to either add to the game or view their stats

Example:
```json
[
    "Nikitos",
    "Vukladach",
    "Rysalochka"
]
```

2. Games
* Filename: games.json
* Description: Records of all games with players, their roles, date of the gae and winning team.
* Purpose: To view played games. To calculate player's stats

Example:
```json
[
    {
        "Game_ID": 1,
        "Date": "12.03.2015",
        "Host": "Roman",
        "Team_Red":
        [
            {"player": "Nikitos", "role": "Commissar", "status": "alive"},
            {"player": "Vukladach", "role": "Citizen", "status": "alive"}
        ],
        "Team_Black":
        [
            {"player": "Rysalochka", "role": "Don", "status": "dead"}
        ],
        "Victory": "City",
    },
]
```

3. Stats
* Filename: stats.json
* Description: Statistics on each player's performance
* Purpose: To view player's statistics (winrate and survive rate for each role)

Example:
```json
{
    "Nikitos": 
    {
        "Don": {"played": 10, "won": 8, "survived": 6},
        "Mafia": {"played": 1, "won": 0, "survived": 0},
        "Team_Black": {"played": 11, "won": 8, "survived": 6},
        "Commissar": {"played": 0, "won": 0, "survived": 0},
        "Citizen": {"played": 5, "won": 2, "survived": 4},
        "Team_Red": {"played": 5, "won": 2, "survived": 4},
        "Host": 1203,
        "Elo_rating": "Not Implemented",
    },
}
```

## Functionalities

### Play a game
* Description: Records a full game
* Permission: Admin only

With this command you assign a role for each player, then you update the status of players being killed. At the end, you put the winning team and the whole record goes to the games.json

### Add/Remove player
* Description: Commands to add or remove players from the players.json
* Permission: Admin only

### View games
* Description: Allows you to see a gallery of all played games from games.json
* Permission: Everyone

### Leaderboard
* Description: Shows a table of players and their winrate for team red in one column and team black in the other. #TODO: add Elo rating as a 3rd column. You specify how to sort the table
* Permission: Everyone

### Player stats
* Description: Shows full stats of a single player. His winrate and survival rate for each role and team.
* Permission: Everyone

### Help
* Description: Shows a supportive message with brief on each command
* Permission: Everyone
