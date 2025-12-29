#!/usr/bin/env python3
"""
Reset and reload the database with correct data
"""
import sqlite3
import os
import json
from cs2_database import CS2Database

def reset_and_reload():
    """Reset the database and reload data correctly"""
    db_path = "cs2_simulator.db"

    # Delete existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")

    # Create fresh database
    db = CS2Database()

    # Load teams from JSON
    teams_dict = db.load_teams_from_json()
    print(f"Loaded {len(teams_dict)} teams from JSON")

    # Check results
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM players')
    player_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT name) FROM players')
    unique_players = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM teams')
    team_count = cursor.fetchone()[0]

    print(f"Database now has:")
    print(f"  Teams: {team_count}")
    print(f"  Total players: {player_count}")
    print(f"  Unique players: {unique_players}")

    if player_count == unique_players:
        print("✅ Database is clean!")
    else:
        print("❌ Still have issues!")

    conn.close()

if __name__ == "__main__":
    reset_and_reload()