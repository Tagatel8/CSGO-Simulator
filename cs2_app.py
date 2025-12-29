import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, colorchooser
import sys
import os
import json
# Add the current directory to the path so we can import cs2_simulator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from cs2_simulator import load_teams_from_json, Team, Player, simulate_series, print_player_stats
    from career_system import CareerManager, Career, CareerPlayer
    from cs2_database import CS2Database
    from career_db_utils import create_career_database
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class CS2SimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 CS2 Match Simulator")
        self.root.geometry("900x700")

        # Ensure window is visible and centered
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))

        # Initialize database
        self.db = CS2Database()

        # Load teams from JSON into database (first time only)
        self.db.load_teams_from_json()

        # Load teams from database
        self.teams_dict = self.db.get_teams_dict()
        if not self.teams_dict:
            tk.messagebox.showerror("Error", "Could not load teams from database")
            root.quit()
            return

        # Set modern theme
        self.setup_theme()

        # Load settings from database
        self.settings = self.load_settings()
        print(f"Loaded settings: {self.settings}")  # Debug

        # Career mode
        self.career_manager = CareerManager()
        self.current_career = None
        self.career_mode = False

        # Apply background color after widgets are created
        self.apply_background_color(silent=True)

        # Create the main UI
        self.create_main_ui()

    def create_main_ui(self):
        """Create the main user interface"""
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Top frame for title and settings
        self.top_frame = ttk.Frame(self.main_container)
        self.top_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        title_label = ttk.Label(self.top_frame, text="🎯 CS2 Match Simulator",
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)

        # Settings button
        settings_btn = ttk.Button(self.top_frame, text="⚙ Settings",
                                 command=self.open_settings)
        settings_btn.pack(side=tk.RIGHT)

        # Mode selection
        self.mode_frame = ttk.LabelFrame(self.main_container, text="Game Mode", padding="15")
        self.mode_frame.pack(fill=tk.X, pady=(0, 20))

        self.mode_var = tk.StringVar(value="quick")
        ttk.Radiobutton(self.mode_frame, text="⚡ Quick Match", variable=self.mode_var,
                       value="quick", command=self.switch_mode).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(self.mode_frame, text="🏆 Career Mode", variable=self.mode_var,
                       value="career", command=self.switch_mode).pack(side=tk.LEFT)

        # Initialize team names for comboboxes
        self.team_names = sorted(list(self.teams_dict.keys()))

        # Show initial quick match UI
        self.show_quick_match_ui()

    def setup_theme(self):
        """Setup modern ttk theme and styling"""
        try:
            # Try to use a modern theme
            style = ttk.Style()

            # Try different modern themes
            available_themes = style.theme_names()
            modern_themes = ['clam', 'alt', 'default']

            for theme in modern_themes:
                if theme in available_themes:
                    style.theme_use(theme)
                    break

            # Configure modern styles
            style.configure('TButton',
                          font=('Segoe UI', 10, 'bold'),
                          padding=8,
                          relief='flat')

            style.configure('Accent.TButton',
                          font=('Segoe UI', 11, 'bold'),
                          padding=12,
                          background='#4CAF50',
                          foreground='white')

            style.configure('TLabel',
                          font=('Segoe UI', 10))

            style.configure('TCombobox',
                          font=('Segoe UI', 10),
                          padding=5)

            style.configure('TRadiobutton',
                          font=('Segoe UI', 10),
                          padding=5)

            style.configure('TFrame',
                          background=self.settings.get("background_color", "#f0f0f0"))

            style.configure('TLabelframe',
                          font=('Segoe UI', 11, 'bold'),
                          padding=10)

            style.configure('TLabelframe.Label',
                          font=('Segoe UI', 11, 'bold'))

        except:
            # Fallback if styling fails
            pass

    def load_settings(self):
        """Load settings from database"""
        default_settings = {
            "background_color": "#f0f0f0"  # Light gray default
        }

        try:
            db_settings = self.db.load_all_settings()
            # Merge with defaults in case new settings are added
            default_settings.update(db_settings)
        except:
            pass  # Use defaults if database error

        return default_settings

    def save_settings(self):
        """Save settings to database"""
        try:
            for key, value in self.settings.items():
                self.db.save_setting(key, value)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")

    def apply_background_color(self, silent=False):
        """Apply the background color to the root window and update ttk styles"""
        color = self.settings.get("background_color", "#f0f0f0")
        self.root.configure(bg=color)

        # Update ttk styles with new background color
        try:
            style = ttk.Style()
            style.configure('TFrame', background=color)
            style.configure('TLabelframe', background=color)
            style.configure('TLabel', background=color)
            style.configure('TRadiobutton', background=color)
        except:
            pass

        # Update ScrolledText background if it exists
        try:
            if hasattr(self, 'results_text'):
                self.results_text.configure(bg=color)
        except tk.TclError:
            pass

        # Force a redraw
        self.root.update_idletasks()
        if not silent:
            messagebox.showinfo("Settings Applied", f"Background color changed to: {color}")

    def switch_mode(self):
        """Switch between quick match and career mode"""
        mode = self.mode_var.get()

        if mode == "career":
            self.career_mode = True
            self.show_career_ui()
        else:
            self.career_mode = False
            self.show_quick_match_ui()

    def show_career_ui(self):
        """Show career mode UI"""
        # Clear existing UI elements
        self.clear_main_content()

        # Career selection/create
        career_select_frame = ttk.LabelFrame(self.main_container, text="Career Mode", padding="15")
        career_select_frame.pack(fill=tk.X, pady=(0, 15))

        # Check for existing careers
        existing_careers = self.career_manager.list_careers()

        if existing_careers:
            ttk.Label(career_select_frame, text="Load Career:").pack(anchor=tk.W, pady=(0, 5))

            career_listbox = tk.Listbox(career_select_frame, height=3)
            career_listbox.pack(fill=tk.X, pady=(0, 10))

            for career_name in existing_careers:
                career_listbox.insert(tk.END, career_name)

            def load_selected_career():
                selection = career_listbox.curselection()
                if selection:
                    career_name = existing_careers[selection[0]]
                    career = self.career_manager.load_career(career_name)
                    if career:
                        self.current_career = career
                        self.show_career_dashboard()
                    else:
                        messagebox.showerror("Error", "Failed to load career")

            ttk.Button(career_select_frame, text="Load Selected Career",
                      command=load_selected_career).pack(side=tk.LEFT, padx=(0, 10))

            def delete_selected_career():
                selection = career_listbox.curselection()
                if selection:
                    career_name = existing_careers[selection[0]]
                    from career_db_utils import delete_career_file
                    deleted = delete_career_file(career_name)
                    # Remove from main DB
                    self.career_manager.delete_career(career_name)
                    if deleted:
                        messagebox.showinfo("Deleted", f"Career '{career_name}' deleted.")
                        self.show_career_ui()
                    else:
                        messagebox.showerror("Error", f"Could not delete career file for '{career_name}'.")

            ttk.Button(career_select_frame, text="Delete Selected Career",
                      command=delete_selected_career).pack(side=tk.LEFT, padx=(0, 10))

        # Create new career
        ttk.Label(career_select_frame, text="Or create a new career:").pack(anchor=tk.W, pady=(10, 5))

        name_frame = ttk.Frame(career_select_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(name_frame, text="Player Name:").pack(side=tk.LEFT, padx=(0, 10))
        self.new_career_name = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.new_career_name)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Role selection for new career
        role_frame = ttk.Frame(career_select_frame)
        role_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(role_frame, text="Role:").pack(side=tk.LEFT, padx=(0, 10))
        self.new_career_role = tk.StringVar(value="Rifler")
        db_roles = self.db.get_all_roles()
        role_names = [r["name"] for r in db_roles]
        role_icons = [r["icon"] for r in db_roles]
        role_display = [f"{icon} {name}" for icon, name in zip(role_icons, role_names)]
        self.role_combo = ttk.Combobox(role_frame, textvariable=self.new_career_role, values=role_names, state="readonly", width=20)
        self.role_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.role_combo.current(role_names.index("Rifler") if "Rifler" in role_names else 0)

        # Country selection (enter country ID)
        country_frame = ttk.Frame(career_select_frame)
        country_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(country_frame, text="Country ID:").pack(side=tk.LEFT, padx=(0, 10))
        self.new_career_country = tk.IntVar(value=0)
        country_entry = ttk.Entry(country_frame, textvariable=self.new_career_country, width=8)
        country_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(country_frame, text="(Enter numeric country ID)").pack(side=tk.LEFT)

        # Transfer offers for new career
        offers_frame = ttk.LabelFrame(career_select_frame, text="Transfer Offers", padding="10")
        offers_frame.pack(fill=tk.X, pady=(0, 10))
        self.transfer_offers = self.db.get_random_team_offers(25, 36, 3)
        self.selected_offer = tk.IntVar(value=self.transfer_offers[0][0] if self.transfer_offers else 25)
        for team_id, team_name in self.transfer_offers:
            ttk.Radiobutton(offers_frame, text=f"Offer from {team_name} (ID: {team_id})", variable=self.selected_offer, value=team_id).pack(anchor=tk.W)

        ttk.Button(career_select_frame, text="🎮 Start New Career",
                  command=self.create_new_career).pack(side=tk.RIGHT)

    def show_quick_match_ui(self):
        """Show quick match UI"""
        # Clear existing UI elements
        self.clear_main_content()

        # Re-create the quick match UI
        self.create_quick_match_ui()

    def clear_main_content(self):
        """Clear the main content area"""
        # Destroy all widgets in main_container except the top frame and mode selection
        for widget in self.main_container.winfo_children():
            if widget not in [self.top_frame, self.mode_frame]:
                widget.destroy()

    def create_quick_match_ui(self):
        """Create the quick match UI elements"""
        # Team selection section
        team_card = ttk.LabelFrame(self.main_container, text="Team Selection", padding="15")
        team_card.pack(fill=tk.X, pady=(0, 15))

        self.team_frame = ttk.Frame(team_card)
        self.team_frame.pack(fill=tk.X)

        # Team 1
        ttk.Label(self.team_frame, text="Team 1:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.team1_var = tk.StringVar()
        self.team1_combo = ttk.Combobox(self.team_frame, textvariable=self.team1_var,
                                       values=self.team_names, state="readonly", width=25)
        self.team1_combo.grid(row=0, column=1, padx=(0, 20), pady=5)
        self.team1_combo.current(0)

        # Team 2
        ttk.Label(self.team_frame, text="Team 2:").grid(row=0, column=2, padx=(0, 10), pady=5, sticky=tk.W)
        self.team2_var = tk.StringVar()
        self.team2_combo = ttk.Combobox(self.team_frame, textvariable=self.team2_var,
                                       values=self.team_names, state="readonly", width=25)
        self.team2_combo.grid(row=0, column=3, padx=(0, 20), pady=5)
        self.team2_combo.current(1)

        # Series type section
        series_card = ttk.LabelFrame(self.main_container, text="Series Configuration", padding="15")
        series_card.pack(fill=tk.X, pady=(0, 15))

        self.series_frame = ttk.Frame(series_card)
        self.series_frame.pack(fill=tk.X)

        ttk.Label(self.series_frame, text="Series Type:").pack(side=tk.LEFT, padx=(0, 15))
        self.series_var = tk.StringVar(value="BO3")
        series_options = ["BO1", "BO3", "BO5"]
        for option in series_options:
            ttk.Radiobutton(self.series_frame, text=option, variable=self.series_var,
                           value=option).pack(side=tk.LEFT, padx=(0, 10))

        # Simulate button
        simulate_btn = ttk.Button(self.main_container, text="🚀 Simulate Series",
                                 command=self.simulate, style='Accent.TButton')
        simulate_btn.pack(pady=(10, 20))

        # Results area
        results_card = ttk.LabelFrame(self.main_container, text="Match Results", padding="15")
        results_card.pack(fill=tk.BOTH, expand=True)

        self.results_frame = ttk.Frame(results_card)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.results_frame, text="Results:").pack(anchor=tk.W, pady=(0, 5))
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap=tk.WORD,
                                                    height=15, font=("Consolas", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def create_new_career(self):
        """Create a new career"""
        player_name = self.new_career_name.get().strip()
        selected_role = self.new_career_role.get().strip() if hasattr(self, 'new_career_role') else "Rifler"
        selected_team_id = self.selected_offer.get() if hasattr(self, 'selected_offer') else 25
        if not player_name:
            messagebox.showerror("Error", "Please enter a player name")
            return

        # Check if career already exists
        if player_name in self.career_manager.list_careers():
            messagebox.showerror("Error", "A career with this name already exists")
            return

        # Create a new DB for this career
        new_db_path = create_career_database(player_name)
        # Use this DB for all career operations
        self.db = CS2Database(new_db_path)

        self.current_career = Career(player_name, role=selected_role, team_id=selected_team_id)
        # Assign selected country id to career player
        try:
            selected_country_id = int(self.new_career_country.get()) if hasattr(self, 'new_career_country') else None
        except Exception:
            selected_country_id = None
        self.current_career.player.country_id = selected_country_id
        self.current_career.player.team_id = selected_team_id  # Ensure player object has team_id
        self.current_career.player.role = selected_role  # Ensure player object has role
        # Replace player with selected role in the team with the career player
        self.db.replace_player_with_role_in_team(selected_team_id, selected_role, player_name, self.current_career.player.base_rating)
        # Ensure career manager uses the career DB as well
        try:
            self.career_manager.db = self.db
        except Exception:
            pass
        self.career_manager.save_career(self.current_career)
        self.show_career_dashboard()

    def show_career_dashboard(self):
        """Show the career dashboard"""
        if not self.current_career:
            return

        # Clear existing UI
        self.clear_main_content()

        # Career dashboard
        dashboard_frame = ttk.LabelFrame(self.main_container, text=f"🏆 {self.current_career.player_name}'s Career", padding="15")
        dashboard_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Player stats
        stats_frame = ttk.Frame(dashboard_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 15))


        # Ensure dashboard always shows the latest team_id from the player object
        player_stats = self.current_career.player.get_stats_summary()

        # Left column - Basic info
        left_frame = ttk.Frame(stats_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        ttk.Label(left_frame, text=f"Level: {player_stats['level']}", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Rating: {player_stats['rating']}").pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Experience: {player_stats['experience']}/{player_stats['experience_to_next']}").pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Matches: {player_stats['matches_played']}").pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Wins: {player_stats['wins']} ({player_stats['win_rate']}%)").pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Role: {player_stats['role']}").pack(anchor=tk.W)
        ttk.Label(left_frame, text=f"Team ID: {player_stats['team_id']}").pack(anchor=tk.W)

        # Right column - Performance
        right_frame = ttk.Frame(stats_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(right_frame, text=f"Kills: {player_stats['total_kills']}").pack(anchor=tk.W)
        ttk.Label(right_frame, text=f"Deaths: {player_stats['total_deaths']}").pack(anchor=tk.W)
        ttk.Label(right_frame, text=f"Assists: {player_stats['total_assists']}").pack(anchor=tk.W)
        ttk.Label(right_frame, text=f"K/D Ratio: {player_stats['kdr']}").pack(anchor=tk.W)

        # Team lineup (always include career player, max 5 total)
        team_id = self.current_career.player.team_id
        team_lineup = []
        if team_id:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, rating FROM players WHERE team_id = ?', (team_id,))
                team_lineup = cursor.fetchall()
        # Add the career player if not already in the lineup
        player_name = self.current_career.player_name
        player_rating = self.current_career.player.base_rating
        if not any(pname == player_name for pname, _ in team_lineup):
            team_lineup = [(player_name, player_rating)] + team_lineup
        # Only show up to 5 players (simulate a real lineup)
        team_lineup = team_lineup[:5]
        if team_lineup:
            ttk.Label(dashboard_frame, text="Team Lineup:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
            for pname, prating in team_lineup:
                ttk.Label(dashboard_frame, text=f"{pname} (Rating: {prating})").pack(anchor=tk.W)

        # Achievements
        if player_stats['achievements']:
            ttk.Label(dashboard_frame, text="🏅 Achievements:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
            achievements_text = ", ".join(player_stats['achievements'])
            ttk.Label(dashboard_frame, text=achievements_text).pack(anchor=tk.W)

        # Career actions
        actions_frame = ttk.Frame(dashboard_frame)
        actions_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(actions_frame, text="🎯 Play Match", command=self.play_career_match).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="💾 Save Career", command=self.save_current_career).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="📜 Match History", command=self.show_match_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="🏠 Main Menu", command=self.return_to_main).pack(side=tk.RIGHT)

    def show_match_history(self):
        """Show a page with all matches history and allow clicking to see results"""
        self.clear_main_content()
        history_frame = ttk.LabelFrame(self.main_container, text="Match History", padding="15")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Get all match history from DB
        matches = self.career_manager.get_career_match_history(self.current_career.player_name, limit=1000)
        if not matches:
            ttk.Label(history_frame, text="No matches played yet.").pack()
            return

        listbox = tk.Listbox(history_frame, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        match_map = {}
        for idx, match in enumerate(matches):
            # Format: [TEAM1] [SCORE1] - [SCORE2] [TEAM2] (date)
            summary = f"{match.get('team1', 'You')} {match.get('score1', '?')} - {match.get('score2', '?')} {match.get('team2', match['opponent'])} ({match.get('date', '')})"
            listbox.insert(tk.END, summary)
            match_map[idx] = match

        def on_select(event):
            selection = listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            match = match_map[idx]
            # Show detailed result in requested format
            result_msg = f"{match.get('team1', 'You')} {match.get('score1', '?')} - {match.get('score2', '?')} {match.get('team2', match['opponent'])}\n\n"
            result_msg += f"[{match.get('team1', 'You')}]\n"
            for p in match.get('team1_players', []):
                result_msg += f"{p['name']} {p['kills']}K {p['deaths']}D {p['assists']}A\n"
            result_msg += f"\n[{match.get('team2', match['opponent'])}]\n"
            for p in match.get('team2_players', []):
                result_msg += f"{p['name']} {p['kills']}K {p['deaths']}D {p['assists']}A\n"
            messagebox.showinfo("Match Details", result_msg)

        listbox.bind('<<ListboxSelect>>', on_select)
        ttk.Button(history_frame, text="Back", command=self.show_career_dashboard).pack(pady=(10, 0))

    def play_career_match(self):
        """Play a match in career mode"""
        if not self.current_career:
            return

        # For now, create a simple match against a random team
        import random
        opponent_name = random.choice([name for name in self.team_names if name != "Free Agent"])


        # Use actual team for career player
        team_id = self.current_career.player.team_id
        # Get team name from team_id
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM teams WHERE id = ?', (team_id,))
            team_row = cursor.fetchone()
            player_team_name = team_row[0] if team_row else "Free Agent"
        # Always build the team lineup for simulation from the database, ensuring the career player is present and the original role is replaced
        user_name = self.current_career.player_name
        user_role = self.current_career.player.role
        user_rating = self.current_career.player.base_rating
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM roles WHERE name = ?', (user_role,))
            role_row = cursor.fetchone()
            role_id = role_row[0] if role_row else None
            # Get all players for the team
            cursor.execute('SELECT name, rating, role_id FROM players WHERE team_id = ?', (team_id,))
            db_players = cursor.fetchall()
            # Remove any player with the same role as the career player
            filtered_players = [p for p in db_players if p[2] != role_id or p[0] == user_name]
            # Add the career player if not present
            if not any(p[0] == user_name for p in filtered_players):
                filtered_players = [(user_name, user_rating, role_id)] + filtered_players
            # Only keep 5 players
            filtered_players = filtered_players[:5]
            player_team_data = [{"name": p[0], "rating": p[1]} for p in filtered_players]
        player_team = Team(player_team_name, [Player(p["name"], p["rating"]) for p in player_team_data])

        opponent_data = self.teams_dict[opponent_name]
        opponent_team = Team(opponent_name, [Player(p["name"], p["rating"]) for p in opponent_data])

        # Simulate match
        winner, loser, w_score, l_score, map_results, all_rounds, overtime_levels, match_player_stats = simulate_series(player_team, opponent_team, "BO1")

        # Find the user's player in their team for stats
        user_name = self.current_career.player_name
        user_stats = next((p for p in match_player_stats.get(player_team_name, []) if p["name"] == user_name), None)
        if user_stats is None:
            # fallback: use first player if available, else zeros
            team_stats = match_player_stats.get(player_team_name, [])
            if team_stats:
                user_stats = team_stats[0]
            else:
                user_stats = {"kills": 0, "deaths": 0, "assists": 0}

        won = winner == player_team_name

        # Add to career using database
        player_stats = {
            "kills": user_stats.get("kills", 0),
            "deaths": user_stats.get("deaths", 0),
            "assists": user_stats.get("assists", 0)
        }

        success = self.career_manager.add_match_to_career(
            self.current_career.player_name, opponent_name, won, player_stats
        )

        if success:
            # Reload career to get updated stats
            self.current_career = self.career_manager.load_career(self.current_career.player_name)
        else:
            messagebox.showerror("Error", "Failed to save match result")

        # Show all player stats for both teams
        result_msg = f"{player_team_name} {w_score} - {l_score} {opponent_name}\n\n"
        result_msg += f"[{player_team_name}]\n"
        for p in match_player_stats.get(player_team_name, []):
            result_msg += f"{p['name']} {p['kills']}K {p['deaths']}D {p['assists']}A\n"
        result_msg += f"\n[{opponent_name}]\n"
        for p in match_player_stats.get(opponent_name, []):
            result_msg += f"{p['name']} {p['kills']}K {p['deaths']}D {p['assists']}A\n"

        messagebox.showinfo("Match Complete", result_msg)

        # Refresh dashboard
        self.show_career_dashboard()

    def save_current_career(self):
        """Save the current career"""
        if self.current_career:
            try:
                success = self.career_manager.save_career(self.current_career)
                if success:
                    messagebox.showinfo("Saved", "Career saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save career")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save career: {e}")

    def return_to_main(self):
        """Return to main menu"""
        self.current_career = None
        self.mode_var.set("quick_match")
        self.switch_mode()

    def open_settings(self):
        """Open the settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.settings.get("background_color", "#f0f0f0"))

        # Background color section
        color_frame = tk.Frame(settings_window, bg=self.settings.get("background_color", "#f0f0f0"))
        color_frame.pack(pady=20, padx=20, fill=tk.X)

        tk.Label(color_frame, text="Background Color:", font=("Arial", 12, "bold"),
                bg=self.settings.get("background_color", "#f0f0f0")).pack(anchor=tk.W)

        # Color preview and buttons
        color_control_frame = tk.Frame(color_frame, bg=self.settings.get("background_color", "#f0f0f0"))
        color_control_frame.pack(fill=tk.X, pady=10)

        # Color preview
        self.color_preview = tk.Frame(color_control_frame, width=50, height=30,
                                    bg=self.settings.get("background_color", "#f0f0f0"),
                                    relief=tk.SUNKEN, borderwidth=2)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 10))

        # Color buttons
        color_buttons_frame = tk.Frame(color_control_frame, bg=self.settings.get("background_color", "#f0f0f0"))
        color_buttons_frame.pack(side=tk.LEFT)

        # Predefined colors
        colors = [
            ("Light Gray", "#f0f0f0"),
            ("White", "#ffffff"),
            ("Light Blue", "#e6f3ff"),
            ("Light Green", "#f0fff0"),
            ("Light Yellow", "#fffef0"),
            ("Light Pink", "#fff0f5")
        ]

        for color_name, color_code in colors:
            btn = tk.Button(color_buttons_frame, text=color_name, bg=color_code,
                          command=lambda c=color_code: self.set_background_color(c, settings_window))
            btn.pack(side=tk.TOP, pady=2, fill=tk.X)

        # Custom color button
        custom_btn = tk.Button(color_buttons_frame, text="Custom Color...",
                             command=lambda: self.choose_custom_color(settings_window))
        custom_btn.pack(side=tk.TOP, pady=(10, 0), fill=tk.X)

        # Save and Cancel buttons
        button_frame = tk.Frame(settings_window, bg=self.settings.get("background_color", "#f0f0f0"))
        button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

        tk.Button(button_frame, text="Save", command=lambda: self.save_and_close_settings(settings_window),
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=10)
        tk.Button(button_frame, text="Cancel", command=settings_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT)

    def set_background_color(self, color, settings_window):
        """Set the background color and update preview"""
        self.settings["background_color"] = color
        self.color_preview.configure(bg=color)
        settings_window.configure(bg=color)

    def choose_custom_color(self, settings_window):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title="Choose Background Color",
                                    initialcolor=self.settings.get("background_color", "#f0f0f0"))
        if color[1]:  # color[1] is the hex value
            self.set_background_color(color[1], settings_window)

    def save_and_close_settings(self, settings_window):
        """Save settings and apply changes"""
        print(f"Saving settings: {self.settings}")  # Debug
        self.save_settings()
        self.apply_background_color()
        settings_window.destroy()

    def create_widgets(self):
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame for title and settings
        self.top_frame = ttk.Frame(self.main_container)
        self.top_frame.pack(fill=tk.X, pady=(0, 20))

        # Title with modern styling
        title_label = ttk.Label(self.top_frame, text="🎯 CS2 Match Simulator",
                               font=("Segoe UI", 18, "bold"))
        title_label.pack(side=tk.LEFT)

        # Settings button with modern styling
        settings_btn = ttk.Button(self.top_frame, text="⚙ Settings", command=self.open_settings)
        settings_btn.pack(side=tk.RIGHT)

        # Mode selection
        self.mode_frame = ttk.LabelFrame(self.main_container, text="Game Mode", padding="15")
        self.mode_frame.pack(fill=tk.X, pady=(0, 15))

        self.mode_var = tk.StringVar(value="quick_match")
        ttk.Radiobutton(self.mode_frame, text="Quick Match", variable=self.mode_var,
                       value="quick_match", command=self.switch_mode).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(self.mode_frame, text="🏆 Career Mode", variable=self.mode_var,
                       value="career", command=self.switch_mode).pack(side=tk.LEFT)

        # Initialize with quick match UI
        self.create_quick_match_ui()

    def simulate(self):
        try:
            team1_name = self.team1_var.get()
            team2_name = self.team2_var.get()
            series_type = self.series_var.get()

            if team1_name == team2_name:
                messagebox.showerror("Error", "Please select two different teams")
                return

            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Simulating... Please wait.\n\n")

            # Create teams
            team1_data = self.teams_dict[team1_name]
            team1_players = [Player(p["name"], p["rating"]) for p in team1_data]
            team1 = Team(team1_name, team1_players)

            team2_data = self.teams_dict[team2_name]
            team2_players = [Player(p["name"], p["rating"]) for p in team2_data]
            team2 = Team(team2_name, team2_players)

            # Redirect stdout to capture print statements
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                winner, loser, team1_wins, team2_wins, map_results, all_rounds, overtime_levels = simulate_series(team1, team2, series_type)

                print("\n=== SERIES RESULTS ===")
                print(f"{winner} wins the {series_type} series {team1_wins} - {team2_wins}")
                print("\nMap results:")
                for result in map_results:
                    print(result)

                print_player_stats(team1)
                print_player_stats(team2)

            # Display results
            results = f.getvalue()
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during simulation: {str(e)}")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = CS2SimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()