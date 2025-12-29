import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from cs2_database import CS2Database

class CareerPlayer:
    """Represents a player in career mode"""
    def __init__(self, name: str, rating: int = 50, role: str = "Rifler", team_id: int = None):
        self.name = name
        self.base_rating = rating
        self.current_rating = rating
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.matches_played = 0
        self.wins = 0
        self.total_kills = 0
        self.total_deaths = 0
        self.total_assists = 0
        self.achievements = []
        self.created_date = datetime.now().isoformat()
        self.role = role
        self.team_id = team_id
        self.country_id = None

    def add_match_result(self, kills: int, deaths: int, assists: int, won: bool):
        """Add results from a match"""
        self.matches_played += 1
        if won:
            self.wins += 1

        self.total_kills += kills
        self.total_deaths += deaths
        self.total_assists += assists

        # Calculate experience gained
        exp_gained = self._calculate_experience(kills, deaths, assists, won)
        self.add_experience(exp_gained)

    def _calculate_experience(self, kills: int, deaths: int, assists: int, won: bool) -> int:
        """Calculate experience gained from match"""
        base_exp = 50
        kill_exp = kills * 10
        assist_exp = assists * 5
        win_exp = 100 if won else 0

        # Death penalty
        death_penalty = deaths * 2

        total_exp = base_exp + kill_exp + assist_exp + win_exp - death_penalty
        return max(10, total_exp)  # Minimum 10 exp

    def add_experience(self, amount: int):
        """Add experience and handle leveling up"""
        self.experience += amount

        while self.experience >= self.experience_to_next:
            self.level_up()

    def level_up(self):
        """Level up the player"""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.2)  # Exponential growth

        # Improve rating
        rating_improvement = min(5, self.level // 5 + 1)  # Max 5 rating per level up
        self.current_rating = min(100, self.current_rating + rating_improvement)

        # Check for achievements
        self._check_achievements()

    def _check_achievements(self):
        """Check and unlock achievements"""
        if self.level >= 5 and "Rising Star" not in self.achievements:
            self.achievements.append("Rising Star")
        if self.matches_played >= 10 and "Veteran" not in self.achievements:
            self.achievements.append("Veteran")
        if self.wins >= 5 and "Winner" not in self.achievements:
            self.achievements.append("Winner")
        if self.total_kills >= 50 and "Killer" not in self.achievements:
            self.achievements.append("Killer")
        if self.get_kdr() >= 1.5 and "Sharpshooter" not in self.achievements:
            self.achievements.append("Sharpshooter")

    def get_kdr(self) -> float:
        """Get kill/death ratio"""
        return (self.total_kills / self.total_deaths) if self.total_deaths > 0 else self.total_kills

    def get_stats_summary(self) -> Dict:
        """Get a summary of player stats"""
        win_rate = (self.wins / self.matches_played * 100) if self.matches_played > 0 else 0
        kdr = self.get_kdr()

        return {
            "name": self.name,
            "level": self.level,
            "rating": self.current_rating,
            "experience": self.experience,
            "experience_to_next": self.experience_to_next,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "win_rate": round(win_rate, 1),
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
            "total_assists": self.total_assists,
            "kdr": round(kdr, 2),
            "achievements": self.achievements,
            "role": self.role,
            "team_id": self.team_id,
            "country_id": self.country_id
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "base_rating": self.base_rating,
            "current_rating": self.current_rating,
            "level": self.level,
            "experience": self.experience,
            "experience_to_next": self.experience_to_next,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
            "total_assists": self.total_assists,
            "achievements": self.achievements,
            "created_date": self.created_date,
            "role": self.role,
            "team_id": self.team_id,
            "country_id": self.country_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CareerPlayer':
        """Create from dictionary"""
        player = cls(data["name"], data["base_rating"], data.get("role", "Rifler"), data.get("team_id"))
        player.current_rating = data["current_rating"]
        player.level = data["level"]
        player.experience = data["experience"]
        player.experience_to_next = data["experience_to_next"]
        player.matches_played = data["matches_played"]
        player.wins = data["wins"]
        player.total_kills = data["total_kills"]
        player.total_deaths = data["total_deaths"]
        player.total_assists = data["total_assists"]
        player.achievements = data.get("achievements", [])
        player.created_date = data.get("created_date", datetime.now().isoformat())
        player.country_id = data.get("country_id")
        return player


class Career:
    """Represents a career save file"""
    def __init__(self, player_name: str, role: str = "Rifler", team_id: int = None):
        self.player_name = player_name
        self.player = CareerPlayer(player_name, role=role, team_id=team_id)
        self.created_date = datetime.now().isoformat()
        self.last_played = datetime.now().isoformat()
        self.total_matches = 0
        self.tournaments_won = 0
        self.current_streak = 0
        self.best_streak = 0

    def update_last_played(self):
        """Update the last played timestamp"""
        self.last_played = datetime.now().isoformat()

    def add_match_result(self, opponent_team: str, won: bool, player_stats: Dict):
        """Add a match result to the career"""
        self.total_matches += 1
        self.update_last_played()

        # Update streak
        if won:
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
        else:
            self.current_streak = 0

        # Update player stats
        self.player.add_match_result(
            player_stats.get("kills", 0),
            player_stats.get("deaths", 0),
            player_stats.get("assists", 0),
            won
        )

    def get_career_summary(self) -> Dict:
        """Get a summary of the career"""
        return {
            "player_name": self.player_name,
            "created_date": self.created_date,
            "last_played": self.last_played,
            "total_matches": self.total_matches,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "tournaments_won": self.tournaments_won,
            "player_stats": self.player.get_stats_summary()
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "player_name": self.player_name,
            "player": self.player.to_dict(),
            "created_date": self.created_date,
            "last_played": self.last_played,
            "total_matches": self.total_matches,
            "tournaments_won": self.tournaments_won,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "role": self.player.role,
            "team_id": self.player.team_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Career':
        """Create from dictionary"""
        role = data.get("role", "Rifler")
        team_id = data.get("team_id")
        career = cls(data["player_name"], role, team_id)
        career.player = CareerPlayer.from_dict(data["player"])
        career.created_date = data["created_date"]
        career.last_played = data["last_played"]
        career.total_matches = data["total_matches"]
        career.tournaments_won = data.get("tournaments_won", 0)
        career.current_streak = data.get("current_streak", 0)
        career.best_streak = data.get("best_streak", 0)
        return career


class CareerManager:
    """Manages career save files using SQLite database"""
    def __init__(self, db_path: str = "cs2_simulator.db"):
        self.db = CS2Database(db_path)

    def save_career(self, career: Career) -> bool:
        """Save a career to database"""
        try:
            career_id = self.db.save_career(career)
            return career_id is not None
        except Exception as e:
            print(f"Error saving career: {e}")
            return False

    def load_career(self, player_name: str) -> Optional[Career]:
        """Load a career from database"""
        try:
            return self.db.load_career(player_name)
        except Exception as e:
            print(f"Error loading career: {e}")
            return None

    def list_careers(self) -> List[str]:
        """List all saved career player names"""
        try:
            return self.db.list_careers()
        except Exception as e:
            print(f"Error listing careers: {e}")
            return []

    def delete_career(self, player_name: str) -> bool:
        """Delete a career from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM careers WHERE player_name = ?', (player_name,))
                cursor.execute('DELETE FROM career_players WHERE name = ?', (player_name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting career: {e}")
            return False

    def add_match_to_career(self, player_name: str, opponent_team: str, won: bool,
                           player_stats: Dict) -> bool:
        """Add a match result to a career"""
        try:
            # Always save the career first to ensure it exists
            career = self.load_career(player_name)
            if not career:
                # If not found, create and save a new career
                career = Career(player_name)
                self.save_career(career)

            # Add match to career object
            career.add_match_result(opponent_team, won, player_stats)

            # Save updated career
            self.save_career(career)

            # Add match to database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM careers WHERE player_name = ?', (player_name,))
                career_row = cursor.fetchone()
                if career_row:
                    self.db.add_career_match(
                        career_row[0], opponent_team, won,
                        player_stats.get("kills", 0),
                        player_stats.get("deaths", 0),
                        player_stats.get("assists", 0)
                    )
            return True
        except Exception as e:
            print(f"Error adding match to career: {e}")
            return False

    def get_career_match_history(self, player_name: str, limit: int = 1000) -> List[Dict]:
        """Get all match history for a career (default: up to 1000 matches)"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM careers WHERE player_name = ?', (player_name,))
                career_row = cursor.fetchone()
                if career_row:
                    return self.db.get_career_match_history(career_row[0], limit)
                return []
        except Exception as e:
            print(f"Error getting match history: {e}")
            return []

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        return self.db.get_database_stats()

    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        self.db.backup_database(backup_path)