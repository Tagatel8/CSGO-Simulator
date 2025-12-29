#!/usr/bin/env python3
"""
Check for duplicate players in the database
"""
import sqlite3

def check_duplicates():
    conn = sqlite3.connect('cs2_simulator.db')
    cursor = conn.cursor()

    # Total players
    cursor.execute('SELECT COUNT(*) FROM players')
    total = cursor.fetchone()[0]
    print(f"Total players in database: {total}")

    # Check for duplicates
    cursor.execute('''
        SELECT name, COUNT(*) as count
        FROM players
        GROUP BY name
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 10
    ''')

    duplicates = cursor.fetchall()
    if duplicates:
        print("\nDuplicate players found:")
        for name, count in duplicates:
            print(f"  {name}: {count} times")
    else:
        print("\nNo duplicate players found.")

    # Check team distribution
    cursor.execute('''
        SELECT t.name, COUNT(p.id) as player_count
        FROM teams t
        LEFT JOIN players p ON t.id = p.team_id
        GROUP BY t.id, t.name
        ORDER BY player_count DESC
    ''')

    print("\nTeam player counts:")
    for team_name, count in cursor.fetchall():
        print(f"  {team_name}: {count} players")

    conn.close()

if __name__ == "__main__":
    check_duplicates()