def load_teams_from_db(db_path="cs2_simulator.db"):
    from cs2_database import CS2Database
    db = CS2Database(db_path)
    teams_dict = db.get_teams_dict()
    teams = {}
    for team_name, players in teams_dict.items():
        teams[team_name] = [Player(p["name"], p["rating"]) for p in players]
    return teams
import random
import json

ROUNDS_TO_WIN = 13

class Player:
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.kills = 0
        self.assists = 0
        self.deaths = 0

    def get_impact(self):
        # forme du jour : -5 à +5
        return self.rating + random.uniform(-5, 5)


class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players

    def get_power(self):
        impacts = [p.get_impact() for p in self.players]
        return sum(impacts) / len(impacts)


def simulate_round(team1, team2):
    p1 = team1.get_power()
    p2 = team2.get_power()
    prob_t1_win = (p1 ** 3) / (p1 ** 3 + p2 ** 3) if p1 + p2 > 0 else 0.5
    winner = team1 if random.random() < prob_t1_win else team2
    loser = team2 if winner == team1 else team1

    # Simulate kills for winner
    win_kills = random.randint(4, 6)
    weights = [p.rating for p in winner.players]
    kill_players = random.choices(winner.players, weights=weights, k=win_kills)
    for p in kill_players:
        p.kills += 1

    # Deaths for loser
    death_players = random.choices(loser.players, k=win_kills)
    for p in death_players:
        p.deaths += 1

    # Assists for winner
    assist_count = random.randint(0, win_kills // 2)
    assist_players = random.choices(winner.players, weights=weights, k=assist_count)
    for p in assist_players:
        p.assists += 1

    return winner == team1  # True if team1 wins the round


def simulate_series(team1, team2, series_type):
    if series_type == "BO1":
        maps_to_win = 1
    elif series_type == "BO3":
        maps_to_win = 2
    elif series_type == "BO5":
        maps_to_win = 3
    else:
        raise ValueError("Invalid series type")

    # Reset stats for the series
    for team in [team1, team2]:
        for p in team.players:
            p.kills = 0
            p.assists = 0
            p.deaths = 0

    team1_wins = 0
    team2_wins = 0
    map_results = []
    all_rounds = []
    overtime_levels = []

    match_player_stats = {
        team1.name: [],
        team2.name: []
    }
    while team1_wins < maps_to_win and team2_wins < maps_to_win:
        map_num = team1_wins + team2_wins + 1
        print(f"\n--- Map {map_num} ---")
        
        winner, loser, w_score, l_score, rounds, overtime_level = simulate_match(team1, team2, reset_stats=False)
        
        if winner == team1.name:
            team1_wins += 1
        else:
            team2_wins += 1
        
        map_results.append(f"Map {map_num}: {winner} {w_score} - {l_score} {loser}")
        all_rounds.extend(rounds)
        overtime_levels.append(overtime_level)
        
        print(f"Map {map_num} Result: {winner} {w_score} - {l_score} {loser}")
        if overtime_level > 0:
            print(f"(After {overtime_level} overtime{'s' if overtime_level > 1 else ''})")
            # Collect player stats for both teams after the series
            for p in team1.players:
                match_player_stats[team1.name].append({
                    "name": p.name,
                    "kills": p.kills,
                    "deaths": p.deaths,
                    "assists": p.assists
                })
            for p in team2.players:
                match_player_stats[team2.name].append({
                    "name": p.name,
                    "kills": p.kills,
                    "deaths": p.deaths,
                    "assists": p.assists
                })

    series_winner = team1 if team1_wins == maps_to_win else team2
    series_loser = team2 if series_winner == team1 else team1
    
    # Calculate HLTV-style ratings for the entire series
    total_rounds = len(all_rounds)
    for team in [team1, team2]:
        for p in team.players:
            if total_rounds > 0:
                if p.kills == 0:
                    p.hltv_rating = 0.3
                else:
                    p.hltv_rating = max(0.5, 1.5 * (p.kills - p.deaths) / total_rounds + 1.0)
            else:
                p.hltv_rating = 1.0
            return series_winner.name, series_loser.name, team1_wins, team2_wins, map_results, all_rounds, overtime_levels, match_player_stats
    return series_winner.name, series_loser.name, team1_wins, team2_wins, map_results, all_rounds, overtime_levels


def simulate_match(team1, team2, reset_stats=True):
    if reset_stats:
        # Reset stats
        for team in [team1, team2]:
            for p in team.players:
                p.kills = 0
                p.assists = 0
                p.deaths = 0

    score1 = 0
    score2 = 0
    rounds = []
    target = 13
    margin = 1
    overtime_level = 0
    max_rounds = 40  # Prevent infinite loops

    while True:
        team1_wins_round = simulate_round(team1, team2)
        if team1_wins_round:
            score1 += 1
        else:
            score2 += 1

        round_num = score1 + score2
        rounds.append(f"Round {round_num}: {team1.name if team1_wins_round else team2.name} wins")

        # Check for max rounds
        if round_num >= max_rounds:
            if score1 > score2:
                winner = team1
            elif score2 > score1:
                winner = team2
            else:
                # Tie, random winner
                winner = team1 if random.random() < 0.5 else team2
            break

        # Check if match ends
        if score1 >= target and (score1 - score2) >= margin:
            winner = team1
            break
        if score2 >= target and (score2 - score1) >= margin:
            winner = team2
            break

        # Check for overtime
        if score1 >= 12 and score2 >= 12 and target == 13:
            target = 16
            margin = 2
            overtime_level = 1
        elif score1 >= 15 and score2 >= 15 and target == 16:
            target = 19
            margin = 3
            overtime_level = 2
        elif score1 >= 18 and score2 >= 18 and target == 19:
            target = 22
            margin = 4
            overtime_level = 3
        elif score1 >= 21 and score2 >= 21 and target == 22:
            target = 25
            margin = 5
            overtime_level = 4
        elif score1 >= 24 and score2 >= 24 and target == 25:
            target = 28
            margin = 6
            overtime_level = 5
        elif score1 >= 27 and score2 >= 27 and target == 28:
            target = 31
            margin = 7
            overtime_level = 6
        elif score1 >= 30 and score2 >= 30 and target == 31:
            target = 34
            margin = 8
            overtime_level = 7
        elif score1 >= 33 and score2 >= 33 and target == 34:
            target = 37
            margin = 9
            overtime_level = 8

    loser = team2 if winner == team1 else team1
    w_score = score1 if winner == team1 else score2
    l_score = score2 if winner == team1 else score1
    total_rounds = score1 + score2

    return winner.name, loser.name, w_score, l_score, rounds, overtime_level


def print_player_stats(team):
    print(f"\n{team.name} Player Stats:")
    for p in team.players:
        print(f"  {p.name}: {p.kills}K / {p.assists}A / {p.deaths}D - Rating: {p.hltv_rating:.2f}")


def load_teams_from_json(filename="teams.json"):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get("teams", {})
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}.")
        return {}


def select_team(teams_dict, team_number, exclude_team=None):
    team_names = [name for name in teams_dict.keys() if name != exclude_team]
    print(f"\nAvailable teams:")
    for i, name in enumerate(team_names, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = int(input(f"Choose Team {team_number} (1-{len(team_names)}): ")) - 1
            if 0 <= choice < len(team_names):
                selected_name = team_names[choice]
                players_data = teams_dict[selected_name]
                players = [Player(p["name"], p["rating"]) for p in players_data]
                return Team(selected_name, players)
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")


def select_series_type():
    print("\nChoose series type:")
    print("1. BO1 (Best of 1)")
    print("2. BO3 (Best of 3)")
    print("3. BO5 (Best of 5)")
    
    while True:
        try:
            choice = int(input("Enter choice (1-3): "))
            if choice == 1:
                return "BO1"
            elif choice == 2:
                return "BO3"
            elif choice == 3:
                return "BO5"
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")



