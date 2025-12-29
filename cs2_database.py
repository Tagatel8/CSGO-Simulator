import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json


class CS2Database:
    """SQLite database manager for CS2 simulator"""

    def replace_player_with_role_in_team(self, team_id: int, role: str, player_name: str, player_rating: int):
        """Replace a player with the given role in the team with the career player."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get role_id for the role
            cursor.execute('SELECT id FROM roles WHERE name = ?', (role,))
            role_row = cursor.fetchone()
            if not role_row:
                return False
            role_id = role_row[0]
            # Find a player with this role in the team
            cursor.execute('SELECT id FROM players WHERE team_id = ? AND role_id = ? LIMIT 1', (team_id, role_id))
            player_row = cursor.fetchone()
            if player_row:
                cursor.execute('DELETE FROM players WHERE id = ?', (player_row[0],))
            # Always insert the career player into the team
            cursor.execute('INSERT INTO players (name, rating, team_id, role_id, is_career_player) VALUES (?, ?, ?, ?, TRUE)',
                           (player_name, player_rating, team_id, role_id))
            conn.commit()
            return True

    def __init__(self, db_path: str = "cs2_simulator.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Teams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Roles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT
                )
            ''')

            # Players table (for pro players)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    team_id INTEGER,
                    role_id INTEGER,
                    is_career_player BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            ''')

            # Career players table (now with team_id and role)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    base_rating INTEGER DEFAULT 50,
                    current_rating INTEGER DEFAULT 50,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    experience_to_next INTEGER DEFAULT 100,
                    matches_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    total_kills INTEGER DEFAULT 0,
                    total_deaths INTEGER DEFAULT 0,
                    total_assists INTEGER DEFAULT 0,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    team_id INTEGER,
                    role TEXT,
                    country_id INTEGER
                )
            ''')

            # Achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT
                )
            ''')

            # Career player achievements (many-to-many)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_player_achievements (
                    career_player_id INTEGER,
                    achievement_id INTEGER,
                    unlocked_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (career_player_id, achievement_id),
                    FOREIGN KEY (career_player_id) REFERENCES career_players (id),
                    FOREIGN KEY (achievement_id) REFERENCES achievements (id)
                )
            ''')

            # Careers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS careers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT UNIQUE NOT NULL,
                    career_player_id INTEGER,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_played TEXT DEFAULT CURRENT_TIMESTAMP,
                    total_matches INTEGER DEFAULT 0,
                    tournaments_won INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    FOREIGN KEY (career_player_id) REFERENCES career_players (id)
                )
            ''')

            # Career matches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    career_id INTEGER,
                    opponent_team TEXT NOT NULL,
                    won BOOLEAN NOT NULL,
                    player_kills INTEGER,
                    player_deaths INTEGER,
                    player_assists INTEGER,
                    match_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (career_id) REFERENCES careers (id)
                )
            ''')

            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')

            # Insert default achievements
            default_achievements = [
                ("Rising Star", "Reach level 5", "⭐"),
                ("Veteran", "Play 10 matches", "🎖️"),
                ("Winner", "Win 5 matches", "🏆"),
                ("Killer", "Get 50 kills", "🔪"),
                ("Sharpshooter", "Maintain 1.5+ K/D ratio", "🎯"),
                ("Unstoppable", "Win 10 matches in a row", "🔥")
            ]

            cursor.executemany('''
                INSERT OR IGNORE INTO achievements (name, description, icon)
                VALUES (?, ?, ?)
            ''', default_achievements)

            # Insert default roles
            default_roles = [
                ("AWPer", "Primary AWP specialist, long-range sniper", "🎯"),
                ("Rifler", "Primary rifle user, consistent fragger", "🔫"),
                ("IGL", "In-game leader, tactical decision maker", "👑"),
                ("Support", "Secondary AWPer, lurker, or support role", "🛡️"),
                ("Entry Fragger", "First to enter sites, high-risk high-reward", "💥"),
                ("Lurker", "Map control and flanking specialist", "👤")
            ]

            cursor.executemany('''
                INSERT OR IGNORE INTO roles (name, description, icon)
                VALUES (?, ?, ?)
            ''', default_roles)

            # Run migrations for existing databases
            self._run_migrations(cursor)

            conn.commit()

    def _run_migrations(self, cursor):
        """Run database migrations for existing databases"""
        try:
            # Check if role_id column exists in players table
            cursor.execute("PRAGMA table_info(players)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'role_id' not in columns:
                print("Migrating database: Adding role_id column to players table...")
                cursor.execute('ALTER TABLE players ADD COLUMN role_id INTEGER REFERENCES roles(id)')

            # Add team_id and role to career_players if missing
            cursor.execute("PRAGMA table_info(career_players)")
            cp_columns = [row[1] for row in cursor.fetchall()]
            if 'team_id' not in cp_columns:
                print("Migrating database: Adding team_id column to career_players table...")
                cursor.execute('ALTER TABLE career_players ADD COLUMN team_id INTEGER')
            if 'role' not in cp_columns:
                print("Migrating database: Adding role column to career_players table...")
                cursor.execute('ALTER TABLE career_players ADD COLUMN role TEXT')

            # Add country_id to career_players if missing
            cursor.execute("PRAGMA table_info(career_players)")
            cp_columns = [row[1] for row in cursor.fetchall()]
            if 'country_id' not in cp_columns:
                print("Migrating database: Adding country_id column to career_players table...")
                cursor.execute('ALTER TABLE career_players ADD COLUMN country_id INTEGER')

                # Assign realistic roles to existing players
                cursor.execute('SELECT id, name FROM players WHERE role_id IS NULL')
                players_to_update = cursor.fetchall()

                # Get all teams and their players for balanced role assignment
                cursor.execute('SELECT team_id, COUNT(*) as player_count FROM players WHERE role_id IS NULL GROUP BY team_id')
                team_counts = dict(cursor.fetchall())

                # Assign roles using balanced algorithm
                role_assignments = self.assign_realistic_roles(players_to_update, team_counts)

                for player_id, player_name in players_to_update:
                    role_name = role_assignments.get(player_id, "Rifler")
                    cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                    role_row = cursor.fetchone()
                    role_id = role_row[0] if role_row else 2  # Default to Rifler

                    cursor.execute('UPDATE players SET role_id = ? WHERE id = ?', (role_id, player_id))

                print(f"Migrated {len(players_to_update)} players with realistic roles")

                print(f"Migrated {len(players_to_update)} players with roles")

        except Exception as e:
            print(f"Migration error: {e}")

    # Team and Player Management
    def get_player_role_mapping(self):
        """Get mapping of famous CS2 players to their roles"""
        return {
            # Vitality
            "apEX": "IGL",
            "ZywOo": "AWPer",
            "flameZ": "Rifler",
            "mezii": "Support",
            "ropz": "Entry Fragger",

            # G2
            "huNter-": "Rifler",
            "SunPayus": "Entry Fragger",
            "malbsMd": "Support",
            "HeavyGod": "AWPer",
            "MATYS": "IGL",

            # FaZe (assuming based on typical comp)
            "karrigan": "IGL",
            "rain": "AWPer",
            "Twistzz": "Rifler",
            "ropz": "Entry Fragger",  # Note: ropz is in both teams in data
            "broky": "Support",

            # Natus Vincere
            "s1mple": "AWPer",
            "electronic": "Rifler",
            "b1t": "Entry Fragger",
            "Perfecto": "IGL",
            "jL": "Support",

            # Astralis
            "HooXi": "Support",
            "device": "AWPer",
            "Magisk": "Rifler",
            "TeSeS": "Entry Fragger",
            "Staehr": "IGL",

            # Default mappings for other players
            "m0NESY": "AWPer",
            "kyxsan": "Rifler",
            "NiKo": "IGL",
            "Jimpphat": "Entry Fragger",
            "kyousuke": "Support"
        }

    def assign_realistic_roles(self, players, team_counts):
        """Assign realistic roles to players based on team composition needs"""
        import random

        # Role priorities for balanced teams
        role_priorities = {
            "IGL": 1,        # Every team needs 1 IGL
            "AWPer": 1,      # Most teams have 1 AWPer
            "Entry Fragger": 2,  # Teams usually have 1-2 entry fraggers
            "Support": 1,    # Teams need 1 support player
            "Rifler": 3      # Fill remaining spots with riflers (most flexible)
        }

        assignments = {}
        famous_players = self.get_player_role_mapping()

        # Group players by team
        players_by_team = {}
        for player_id, player_name in players:
            # Get team_id for this player
            with self.get_connection() as temp_conn:
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute('SELECT team_id FROM players WHERE id = ?', (player_id,))
                team_id = temp_cursor.fetchone()[0]

            if team_id not in players_by_team:
                players_by_team[team_id] = []
            players_by_team[team_id].append((player_id, player_name))

        # Assign roles for each team
        for team_id, team_players in players_by_team.items():
            team_size = len(team_players)
            assigned_roles = {role: 0 for role in role_priorities.keys()}

            # First, assign famous players their known roles
            for player_id, player_name in team_players:
                if player_name in famous_players:
                    role = famous_players[player_name]
                    assignments[player_id] = role
                    assigned_roles[role] += 1

            # Then assign remaining players based on team needs
            remaining_players = [(pid, name) for pid, name in team_players if pid not in assignments]

            for player_id, player_name in remaining_players:
                # Find the role that this team needs most
                available_roles = []
                for role, max_count in role_priorities.items():
                    if assigned_roles[role] < max_count:
                        available_roles.append((role, max_count - assigned_roles[role]))

                if available_roles:
                    # Weight by how much the role is needed
                    role_weights = [(role, need) for role, need in available_roles]
                    selected_role = random.choices(
                        [r for r, w in role_weights],
                        weights=[w for r, w in role_weights]
                    )[0]
                    assignments[player_id] = selected_role
                    assigned_roles[selected_role] += 1
                else:
                    # If all roles are filled, assign Rifler (most flexible)
                    assignments[player_id] = "Rifler"

        return assignments

    def load_teams_from_json(self, json_file: str = "teams.json") -> Dict:
        """Load teams from JSON file and store in database"""
        if not os.path.exists(json_file):
            return {}

        with open(json_file, 'r') as f:
            data = json.load(f)

        teams_dict = data.get("teams", {})
        player_roles = self.get_player_role_mapping()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Clear existing pro players (not career players)
            cursor.execute('DELETE FROM players WHERE is_career_player = FALSE')
            print(f"Cleared existing pro players from database")

            for team_name, players in teams_dict.items():
                # Get or create team
                cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
                existing_team = cursor.fetchone()

                if existing_team:
                    team_id = existing_team[0]
                else:
                    cursor.execute('INSERT INTO teams (name) VALUES (?)', (team_name,))
                    team_id = cursor.lastrowid

                # Insert players with roles
                for player in players:
                    player_name = player["name"]
                    role_name = player_roles.get(player_name, "Rifler")  # Default to Rifler

                    # Get role ID
                    cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
                    role_row = cursor.fetchone()
                    role_id = role_row[0] if role_row else 2  # Default to Rifler (ID 2)

                    cursor.execute('''
                        INSERT INTO players (name, rating, team_id, role_id, is_career_player)
                        VALUES (?, ?, ?, ?, FALSE)
                    ''', (player_name, player["rating"], team_id, role_id))

            conn.commit()

        return teams_dict

    def get_teams_dict(self) -> Dict:
        """Get teams dictionary from database with role information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get all teams with their players and roles
            cursor.execute('''
                SELECT t.name, p.name, p.rating, r.name as role_name, r.icon as role_icon
                FROM teams t
                LEFT JOIN players p ON t.id = p.team_id
                LEFT JOIN roles r ON p.role_id = r.id
                WHERE p.is_career_player = FALSE
                ORDER BY t.name, p.name
            ''')

            teams_dict = {}
            for row in cursor.fetchall():
                team_name, player_name, rating, role_name, role_icon = row
                if team_name not in teams_dict:
                    teams_dict[team_name] = []
                teams_dict[team_name].append({
                    "name": player_name,
                    "rating": rating,
                    "role": role_name,
                    "role_icon": role_icon
                })

            return teams_dict

    # Career Player Management
    def save_career_player(self, career_player) -> int:
        """Save career player to database (now with team_id and role)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert or update career player
            cursor.execute('''
                INSERT OR REPLACE INTO career_players
                (name, base_rating, current_rating, level, experience, experience_to_next,
                 matches_played, wins, total_kills, total_deaths, total_assists, created_date, team_id, role, country_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                career_player.name,
                career_player.base_rating,
                career_player.current_rating,
                career_player.level,
                career_player.experience,
                career_player.experience_to_next,
                career_player.matches_played,
                career_player.wins,
                career_player.total_kills,
                career_player.total_deaths,
                career_player.total_assists,
                career_player.created_date,
                career_player.team_id,
                career_player.role,
                career_player.country_id
            ))

            career_player_id = cursor.lastrowid if cursor.lastrowid != 0 else cursor.execute('SELECT id FROM career_players WHERE name = ?', (career_player.name,)).fetchone()[0]

            # Update achievements
            cursor.execute('DELETE FROM career_player_achievements WHERE career_player_id = ?',
                         (career_player_id,))

            for achievement in career_player.achievements:
                cursor.execute('SELECT id FROM achievements WHERE name = ?', (achievement,))
                achievement_row = cursor.fetchone()
                if achievement_row:
                    cursor.execute('''
                        INSERT INTO career_player_achievements (career_player_id, achievement_id)
                        VALUES (?, ?)
                    ''', (career_player_id, achievement_row[0]))

            conn.commit()
            return career_player_id

    def load_career_player(self, name: str):
        """Load career player from database (now with team_id and role)"""
        from career_system import CareerPlayer

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM career_players WHERE name = ?', (name,))
            row = cursor.fetchone()

            if not row:
                return None

            # row: (id, name, base_rating, current_rating, level, experience, experience_to_next, matches_played, wins, total_kills, total_deaths, total_assists, created_date, team_id, role, country_id)
            # Adjust indexes: name=1, base_rating=2, current_rating=3, level=4, ..., created_date=12, team_id=13, role=14, country_id=15
            role_val = row[14] if len(row) > 14 else None
            country_val = row[15] if len(row) > 15 else None
            player = CareerPlayer(row[1], row[2], role=role_val, team_id=row[13])  # name, base_rating, role, team_id
            player.current_rating = row[3]
            player.level = row[4]
            player.experience = row[5]
            player.experience_to_next = row[6]
            player.matches_played = row[7]
            player.wins = row[8]
            player.total_kills = row[9]
            player.total_deaths = row[10]
            player.total_assists = row[11]
            player.created_date = row[12]
            player.country_id = country_val

            # Load achievements
            cursor.execute('''
                SELECT a.name FROM achievements a
                JOIN career_player_achievements cpa ON a.id = cpa.achievement_id
                WHERE cpa.career_player_id = ?
            ''', (row[0],))

            player.achievements = [row[0] for row in cursor.fetchall()]

            return player

    # Career Management
    def save_career(self, career) -> int:
        """Save career to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Save career player first
            career_player_id = self.save_career_player(career.player)

            # Save career
            cursor.execute('''
                INSERT OR REPLACE INTO careers
                (player_name, career_player_id, created_date, last_played, total_matches,
                 tournaments_won, current_streak, best_streak)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                career.player_name,
                career_player_id,
                career.created_date,
                career.last_played,
                career.total_matches,
                career.tournaments_won,
                career.current_streak,
                career.best_streak
            ))

            career_id = cursor.lastrowid
            conn.commit()
            return career_id

    def load_career(self, player_name: str):
        """Load career from database"""
        from career_system import Career, CareerPlayer

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM careers WHERE player_name = ?', (player_name,))
            row = cursor.fetchone()

            if not row:
                return None

            career = Career(row[1])  # player_name
            career.created_date = row[3]
            career.last_played = row[4]
            career.total_matches = row[5]
            career.tournaments_won = row[6]
            career.current_streak = row[7]
            career.best_streak = row[8]

            # Load career player
            career.player = self.load_career_player(player_name)

            return career

    def list_careers(self) -> List[str]:
        """List all career player names"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT player_name FROM careers ORDER BY last_played DESC')
            return [row[0] for row in cursor.fetchall()]

    def add_career_match(self, career_id: int, opponent_team: str, won: bool,
                        player_kills: int, player_deaths: int, player_assists: int):
        """Add a match result to career history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO career_matches
                (career_id, opponent_team, won, player_kills, player_deaths, player_assists)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (career_id, opponent_team, won, player_kills, player_deaths, player_assists))
            conn.commit()

    def get_career_match_history(self, career_id: int, limit: int = 10) -> List[Dict]:
        """Get recent match history for a career"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT opponent_team, won, player_kills, player_deaths, player_assists, match_date
                FROM career_matches
                WHERE career_id = ?
                ORDER BY match_date DESC
                LIMIT ?
            ''', (career_id, limit))

            matches = []
            for row in cursor.fetchall():
                matches.append({
                    "opponent": row[0],
                    "won": bool(row[1]),
                    "kills": row[2],
                    "deaths": row[3],
                    "assists": row[4],
                    "date": row[5]
                })
            return matches

    # Settings Management
    def save_setting(self, key: str, value: str):
        """Save a setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                         (key, value))
            conn.commit()

    def load_setting(self, key: str, default: str = "") -> str:
        """Load a setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def load_all_settings(self) -> Dict[str, str]:
        """Load all settings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            return {row[0]: row[1] for row in cursor.fetchall()}

    # Utility methods
    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        import shutil
        shutil.copy2(self.db_path, backup_path)

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Count records in each table
            tables = ['teams', 'players', 'roles', 'career_players', 'careers', 'career_matches', 'achievements']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]

            return stats

    def get_all_roles(self):
        """Return all available roles as a list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, description, icon FROM roles ORDER BY id')
            return [
                {"id": row[0], "name": row[1], "description": row[2], "icon": row[3]}
                for row in cursor.fetchall()
            ]

    def get_random_team_offers(self, min_id=25, max_id=36, count=3):
        """Return a list of random team names with IDs in the given range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM teams WHERE id BETWEEN ? AND ?', (min_id, max_id))
            teams = cursor.fetchall()
        import random
        offers = random.sample(teams, min(count, len(teams))) if teams else []
        return offers