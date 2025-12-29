#!/usr/bin/env python3
"""
Check for duplicate players in JSON
"""
import json

def check_json_duplicates():
    with open('teams.json', 'r') as f:
        data = json.load(f)

    players = {}
    for team, player_list in data['teams'].items():
        for player in player_list:
            name = player['name']
            if name not in players:
                players[name] = []
            players[name].append(team)

    # Find players on multiple teams
    multis = [(name, teams) for name, teams in players.items() if len(teams) > 1]

    print(f"Total unique players in JSON: {len(players)}")
    print(f"Players on multiple teams: {len(multis)}")

    if multis:
        print("\nPlayers on multiple teams:")
        for name, teams in multis[:10]:  # Show first 10
            print(f"  {name}: {teams}")

    # Check if any player appears more than once in the same team
    team_duplicates = {}
    for team, player_list in data['teams'].items():
        team_players = [p['name'] for p in player_list]
        if len(team_players) != len(set(team_players)):
            duplicates = [name for name in team_players if team_players.count(name) > 1]
            team_duplicates[team] = list(set(duplicates))

    if team_duplicates:
        print(f"\nTeams with duplicate players: {len(team_duplicates)}")
        for team, dups in team_duplicates.items():
            print(f"  {team}: {dups}")
    else:
        print("\nNo teams have duplicate players within them.")

if __name__ == "__main__":
    check_json_duplicates()