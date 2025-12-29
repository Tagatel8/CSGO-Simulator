#!/usr/bin/env python3
"""
CS2 Database Demo Script
Demonstrates database functionality and future possibilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cs2_database import CS2Database
from datetime import datetime

def main():
    print("🎯 CS2 Simulator Database Demo")
    print("=" * 40)

    # Initialize database
    db = CS2Database()

    # Show database stats
    print("\n📊 Database Statistics:")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Show teams
    teams = db.get_teams_dict()
    print(f"\n👥 Teams Loaded: {len(teams)}")
    print("Sample teams:", list(teams.keys())[:5])

    # Show sample team with roles
    if teams:
        sample_team = list(teams.keys())[0]
        print(f"\n🎯 {sample_team} Roster:")
        for player in teams[sample_team][:3]:  # Show first 3 players
            role_icon = player.get('role_icon', '❓')
            role_name = player.get('role', 'Unknown')
            print(f"  {role_icon} {player['name']} ({player['rating']}) - {role_name}")

    # Show roles
    print("\n👥 Player Roles:")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, description, icon FROM roles')
        for row in cursor.fetchall():
            print(f"  {row[2]} {row[0]} - {row[1]}")

    # Show achievements
    print("\n🏅 Available Achievements:")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, description FROM achievements')
        for row in cursor.fetchall():
            print(f"  {row[1]} - {row[0]}")

    # Show careers
    careers = db.list_careers()
    print(f"\n💾 Saved Careers: {len(careers)}")
    if careers:
        print("Career names:", careers)

        # Show match history for first career
        match_history = db.get_career_match_history(careers[0], limit=5)
        if match_history:
            print(f"\n📈 Recent matches for {careers[0]}:")
            for match in match_history:
                result = "W" if match["won"] else "L"
                print(f"  {result} vs {match['opponent']} - {match['kills']}/{match['deaths']}/{match['assists']}")

    print("\n🔮 Future Possibilities with Database:")
    print("  • Player transfers between teams")
    print("  • Tournament brackets and leagues")
    print("  • Advanced statistics and analytics")
    print("  • Team customization and management")
    print("  • Historical data analysis")
    print("  • Multiplayer career sharing")

    print("\n💡 Database Commands Available:")
    print("  • db.backup_database('backup.db') - Create backup")
    print("  • db.get_career_match_history(player_name) - Match history")
    print("  • db.load_career(player_name) - Load career data")
    print("  • db.save_career(career) - Save career data")

if __name__ == "__main__":
    main()