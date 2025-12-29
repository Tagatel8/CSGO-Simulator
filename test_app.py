import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cs2_simulator import load_teams_from_json, Team, Player, simulate_series

def test_simulation():
    # Load teams
    teams_dict = load_teams_from_json()
    if not teams_dict:
        print("Failed to load teams")
        return

    # Create two teams
    team1_data = teams_dict["Vitality"]
    team1_players = [Player(p["name"], p["rating"]) for p in team1_data]
    team1 = Team("Vitality", team1_players)

    team2_data = teams_dict["G2"]
    team2_players = [Player(p["name"], p["rating"]) for p in team2_data]
    team2 = Team("G2", team2_players)

    # Simulate a BO1
    print("Testing simulation...")
    winner, loser, team1_wins, team2_wins, map_results, all_rounds, overtime_levels = simulate_series(team1, team2, "BO1")

    print(f"Winner: {winner}")
    print(f"Score: {team1_wins} - {team2_wins}")
    print("Test completed successfully!")

if __name__ == "__main__":
    test_simulation()