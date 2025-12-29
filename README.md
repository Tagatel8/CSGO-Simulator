# 🎯 CS2 Match Simulator

A modern, user-friendly desktop application for simulating Counter-Strike 2 matches between professional teams with career mode progression.

## ✨ Features

- **Modern UI**: Clean, card-based interface with professional styling
- Simulate matches between real CS2 professional teams
- Choose from BO1, BO3, or BO5 series formats
- View detailed match results including:
  - Map-by-map results
  - Player statistics (Kills, Assists, Deaths)
  - HLTV-style ratings
  - Overtime information
- **🎨 Customizable**: Change background colors and personalize your experience
- **⚙ Settings**: Easy-to-use settings panel for customization
- **🏆 Career Mode**: Full career progression system
  - Create and save player careers
  - Level up and improve stats
  - Track achievements and statistics
  - Persistent save system

## Teams Included

The simulator includes data for professional teams such as:
- Vitality, G2, FaZe, Natus Vincere
- And many more from the current CS2 pro scene

## How to Run

### Prerequisites
- Python 3.6 or higher
- Tkinter (usually included with Python installations)

### Running the App
1. Make sure you're in the project directory
2. Run: `python cs2_app.py`

### Database Demo
Run `python db_demo.py` to see database statistics and explore available features.

## 🎨 Customization

Click the "⚙ Settings" button to access:
- **Background Color**: Choose from predefined colors or select a custom color
- Settings are automatically saved and applied

## 🏆 Career Mode

Select "🏆 Career Mode" to access:

### Creating a Career
- Enter your player name
- Start as a level 1 player with base stats
- Progress through matches to gain experience and level up

### Career Features
- **Experience & Levels**: Gain XP from matches, level up to improve rating
- **Statistics Tracking**: Kills, deaths, assists, win rate, K/D ratio
- **Achievements**: Unlock achievements like "Rising Star", "Veteran", "Winner"
- **Persistent Saves**: Your career is automatically saved and can be loaded later
- **Match History**: Track your performance across all career matches

### Career Progression
- **Rating Improvement**: Higher levels unlock better base ratings
- **Experience Curve**: Each level requires more XP than the last
- **Win Streaks**: Track current and best win streaks
- **Tournament Potential**: Foundation for future tournament features

## Modern UI Features

- **Card-based Layout**: Organized sections with clear visual hierarchy
- **Segoe UI Fonts**: Modern typography for better readability
- **Responsive Design**: Proper spacing and padding throughout
- **Emoji Icons**: Visual enhancements for better user experience
- **Styled Buttons**: Modern button designs with hover effects

## Files

- `cs2_app.py` - The main GUI application with modern styling and career mode
- `cs2_simulator.py` - The simulation engine
- `career_system.py` - Career mode data structures and database integration
- `cs2_database.py` - SQLite database manager for persistent storage
- `cs2_simulator.db` - SQLite database file (created automatically)
- `teams.json` - Team and player data (loaded into database on first run)
- `settings.json` - Legacy settings file (settings now stored in database)
- `test_app.py` - Simple test script
- `run_app.bat` - Windows batch file for easy launching
- `db_demo.py` - Database functionality demonstration script

## 🎭 Player Roles System

**Realistic CS2 Team Compositions:**
- **🎯 AWPer**: Primary AWP specialist, long-range sniper (ZywOo, s1mple)
- **🔫 Rifler**: Primary rifle user, consistent fragger (device, electronic)
- **👑 IGL**: In-game leader, tactical decision maker (apEX, karrigan)
- **🛡️ Support**: Secondary AWPer, lurker, or support role (jL, mezii)
- **💥 Entry Fragger**: First to enter sites, high-risk high-reward (b1t, Twistzz)
- **👤 Lurker**: Map control and flanking specialist (flameZ, Magisk)

**Database Integration:**
- Roles stored in dedicated `roles` table
- Each player linked to specific role via foreign key
- Automatic role assignment for known pro players
- Extensible system for custom roles

**Benefits for Transfers:**
- Teams can search for players by role
- Balanced team compositions
- Realistic transfer market dynamics
- Role-based player development paths

## Simulation Details

The simulator uses a probabilistic model based on player ratings to determine match outcomes. Each simulation includes:

- Round-by-round results
- Kill/death/assist tracking
- Overtime calculations
- HLTV-style performance ratings

## Career Mode Technical Details

**Database System:**
- SQLite database (`cs2_simulator.db`) for all persistent data
- Automatic database initialization on first run
- Teams loaded from JSON and stored in database
- Thread-safe database connections

**Data Tables:**
- `teams` & `players` - Professional teams and players with roles
- `roles` - Player role definitions (AWPer, IGL, etc.)
- `career_players` - Career mode player profiles
- `careers` - Career save files with metadata
- `career_matches` - Detailed match history
- `achievements` & `career_player_achievements` - Achievement system
- `settings` - User preferences

**Progression Mechanics:**
- Experience gained: 50 base + 10 per kill + 5 per assist + 100 for win
- Level scaling: Exponential XP requirements (1.2x multiplier per level)
- Rating improvement: Up to 5 points per level (capped at level/5)
- Achievement unlocks based on milestones

**Data Persistence:**
- All career data stored in SQLite database
- Match history with detailed statistics
- Automatic saving after each match
- Multiple careers supported per database
- Database backup functionality available

## 🗄️ Database System

**Why SQLite?**
- **Better Performance**: Faster queries and data retrieval than JSON files
- **Data Integrity**: ACID compliance ensures data consistency
- **Relationships**: Proper foreign keys and table relationships
- **Scalability**: Easy to add new features like transfers, tournaments, etc.
- **Backup & Recovery**: Built-in database backup functionality
- **Concurrent Access**: Multiple processes can safely access data
- **Future-Proof**: Foundation for advanced features like player transfers, team management, and league systems

**Database Features:**
- Automatic initialization on first run
- Teams loaded from JSON and stored in database
- Persistent career saves with full match history
- Achievement system with unlock tracking
- Settings stored in database
- Backup functionality for data safety

## 🔄 Migration from JSON to Database

**What Changed:**
- Career saves moved from JSON files to SQLite database
- Settings migrated from JSON to database tables
- Teams loaded from JSON into database on first run
- Match history now stored with detailed statistics
- Improved data relationships and integrity

**Benefits:**
- No more scattered JSON files
- Faster loading and saving
- Better data consistency
- Support for complex queries
- Foundation for advanced features