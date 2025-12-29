#!/usr/bin/env python3
"""
Check database schema and constraints
"""
import sqlite3

def check_schema():
    conn = sqlite3.connect('cs2_simulator.db')
    cursor = conn.cursor()

    # Check indexes
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
    print("Database indexes:")
    for name, sql in cursor.fetchall():
        print(f"  {name}: {sql}")

    # Check table schema
    cursor.execute("PRAGMA table_info(players)")
    print("\nPlayers table schema:")
    for row in cursor.fetchall():
        cid, name, type_, notnull, default, pk = row
        print(f"  {name}: {type_} {'NOT NULL' if notnull else ''} {'PRIMARY KEY' if pk else ''}")

    # Check for duplicate players again
    cursor.execute('''
        SELECT name, team_id, COUNT(*) as count
        FROM players
        GROUP BY name, team_id
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 5
    ''')

    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\nStill have {len(duplicates)} duplicate groups within teams:")
        for name, team_id, count in duplicates:
            print(f"  {name} (team {team_id}): {count} times")
    else:
        print("\nNo duplicates within teams found.")

    conn.close()

if __name__ == "__main__":
    check_schema()