import tkinter as tk
from tkinter import ttk
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback
import os

from actionstabfuncs import *
from passingtabfuncs import *
from playerlogic import *
from matchlogic import *
from teamlogic import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soccer Video Analysis")
        self.geometry("1920x1080")

        self.data_file = "data.json"
        self.teams_data = self.load_data()
        self.selected_team = None
        self.selected_match = None

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (IntroScreen, MatchScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(IntroScreen)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                try:
                    raw = json.load(f)
                    teams_data = {}
                    if 'teams' in raw:
                        for team_name, team_data in raw['teams'].items():
                            teams_data[team_name] = Team.from_dict(team_name, team_data)
                    return teams_data
                except:
                    print(traceback.format_exc())
                    messagebox.showerror("Error", "Couldn't read data from file")
                    return {}
        except FileNotFoundError:
            return {}

    def save_data(self):
        data = {
            "teams": {
                name: {
                    "players": [player.serialize() for player in team.players],
                    "matches": [match.to_dict() for match in team.matches],
                } for name, team in self.teams_data.items()
            }
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

    def load_match_screen(self, team_name, match_name):
        self.selected_team = team_name
        self.selected_match = match_name
        players = self.teams_data[team_name].players
        self.frames[MatchScreen].load_team_and_match(team_name, match_name, players)
        self.show_frame(MatchScreen)


# -------- Intro Screen --------
class IntroScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome to Soccer Analysis", font=("Segoe UI", 16)).pack(pady=20)

        # Team Section
        self.team_listbox = tk.Listbox(self, height=6)
        self.team_listbox.pack(pady=10)

        self.refresh_team_list()

        ttk.Button(self, text="Create New Team", command=self.create_team).pack(pady=5)
        ttk.Button(self, text="Edit Team Players", command=self.edit_team_players).pack(pady=5)

        # Match Section
        ttk.Button(self, text="View Team Stats", command=self.view_stats).pack(pady=10)
        ttk.Button(self, text="Select Match", command=self.select_match).pack(pady=5)
        ttk.Button(self, text="Create New Match", command=self.create_match).pack(pady=5)

    def refresh_team_list(self):
        self.team_listbox.delete(0, tk.END)
        for team_name in self.controller.teams_data:
            self.team_listbox.insert(tk.END, team_name)

    def get_selected_team(self):
        selection = self.team_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a team.")
            return None
        return self.team_listbox.get(selection[0])

    def create_team(self):
        name = simpledialog.askstring("New Team", "Enter team name:")
        if not name:
            return

        if name in self.controller.teams_data:
            messagebox.showinfo("Team Exists", "A team with that name already exists.")
            return

        player_str = simpledialog.askstring("Team Players", "Enter player names (comma-separated):")
        players = [p.strip() for p in player_str.split(",")] if player_str else []

        self.controller.teams_data[name] = Team(name, players, [])
        self.controller.save_data()
        self.refresh_team_list()

    def edit_team_players(self):
        team = self.get_selected_team()
        if not team:
            return

        current_players = self.controller.teams_data[team].players
        default = ", ".join(pl.playerName for pl in current_players)
        new_str = simpledialog.askstring("Edit Players", f"Edit player names (comma-separated):", initialvalue=default)
        if new_str is not None:
            self.controller.teams_data[team].players = [Player(p.strip()) for p in new_str.split(",")]
            self.controller.save_data()

    def view_stats(self):
        team = self.get_selected_team()
        if team:
            matches = self.controller.teams_data[team].matches
            messagebox.showinfo("Team Stats", f"Team '{team}' has {len(matches)} match(es).")

    def select_match(self):
        team = self.get_selected_team()
        if not team:
            return

        team_obj = self.controller.teams_data[team]
        matches = team_obj.matches
        if not matches:
            messagebox.showinfo("No Matches", "This team has no matches.")
            return

        # Create display strings and a mapping from display text → match name
        display_options = []
        match_lookup = {}
        for match in matches:
            display = f"{match.name} ({match.date} vs {match.opponent})"
            display_options.append(display)
            match_lookup[display] = match.name

        # Create dropdown window
        win = tk.Toplevel()
        win.title("Select Match")

        tk.Label(win, text="Choose a match:").pack(padx=10, pady=(10, 0))

        selected = tk.StringVar()
        dropdown = ttk.Combobox(win, textvariable=selected, values=display_options, state="readonly", width=50)
        dropdown.pack(padx=10, pady=10)
        dropdown.current(0)

        def confirm():
            display_value = selected.get()
            match_name = match_lookup.get(display_value)
            win.destroy()
            self.controller.load_match_screen(team, match_name)

        tk.Button(win, text="Load Match", command=confirm).pack(pady=(0, 10))


    def create_match(self):
        team = self.get_selected_team()
        if not team:
            return

        match_name = simpledialog.askstring("New Match", "Enter match name:")
        if not match_name:
            return

        match_date = simpledialog.askstring("New Match", "Enter match date (e.g., 2025-04-30):")
        if match_date is None:
            return

        match_opposition = simpledialog.askstring("New Match", "Enter opponent team name:")
        if match_opposition is None:
            return

        team_obj = self.controller.teams_data[team]
        if match_name not in [m.name for m in team_obj.matches]:
            new_match = Match(name=match_name, date=match_date, opponent=match_opposition)
            team_obj.matches.append(new_match)
            self.controller.save_data()
            self.controller.load_match_screen(team, match_name)
        else:
            messagebox.showinfo("Exists", "Match already exists.")

# -------- Match Screen --------
class MatchScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.selected_team = None
        self.selected_match = None

        ttk.Button(self, text="← Back to Team Selection", command=lambda: controller.show_frame(IntroScreen)).pack(anchor="w", padx=10, pady=5)

        self.tabControl = ttk.Notebook(self)
        self.summarytab = ttk.Frame(self.tabControl)
        self.passingtab = PassingTab(ttk.Notebook(self.tabControl), self, ["A", "B", "C"])
        self.actionstab = ttk.Notebook(self.tabControl)

        self.tabControl.add(self.summarytab, text="Summary")
        self.tabControl.add(self.passingtab.tabControl, text="Passing")
        self.tabControl.add(self.actionstab, text="Actions")
        self.tabControl.pack(expand=1, fill="both")

        # Action tabs
        self.action_types = ["Shot", "Tackle", "Cross"]
        self.action_tables = {}

        for action_type in self.action_types:
            frame = ttk.Frame(self.actionstab)
            self.actionstab.add(frame, text=action_type)

            cols = ["Minute", "Team", "Player", "Details", "Outcome"]
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.pack(expand=True, fill="both")

            self.action_tables[action_type] = tree

        self.title_label = ttk.Label(self.summarytab, text="", font=("Segoe UI", 14))
        self.title_label.pack(pady=10)

    def load_team_and_match(self, team_name, match_name, players):
        self.title_label.config(text=f"Match: {match_name} | Team: {team_name}")
        self.players = players  # Store for use in match tabs

        self.selected_team = team_name
        self.selected_match = match_name

        for tree in self.action_tables.values():
            for row in tree.get_children():
                tree.delete(row)

        self.passingtab.load_passingtab_displays(players)

        print("Players available for this match:", players)  # Use or pass to tabs as needed

        # Get the current selected team and match name
        if not team_name or not match_name:
            messagebox.showerror("Error", "No match selected.")
            return

        # Load existing data from the JSON file
        with open("data.json", "r") as f:
            data = json.load(f)
        
        # Check if the team and match exist in the data
        if team_name not in data["teams"]:
            messagebox.showerror("Error", "Team not found.")
            return

        # Find the match data
        match_data = None
        for match in data["teams"][team_name]["matches"]:
            if match["name"] == match_name:
                match_data = match
                break
        
        if match_data:
            # Load the passing data into the passing tab
            passing_data = match_data.get("passing_data", {})
            self.passingtab.load_data(passing_data, [pl.playerName for pl in self.players])  # Assuming a method to load data into the passing tab
        else:
            messagebox.showerror("Error", "Match not found.")

    def save_match_data(self):
        # Get the current selected team and match name
        team_name = self.selected_team
        match_name = self.selected_match
        
        if not team_name or not match_name:
            messagebox.showerror("Error", "No match selected.")
            return

        # Get the passing data from the passing tab
        passing_data = self.passingtab.get_data()  # Assuming a method that gets the data from the passing tab
        
        # Load existing data from the JSON file
        with open("data.json", "r") as f:
            data = json.load(f)
        
        # Ensure the team and match exist in the data
        if team_name not in data["teams"]:
            data["teams"][team_name] = {"matches": []}

        # Find the match to update or create it if it doesn't exist
        match_exists = False
        for match in data["teams"][team_name]["matches"]:
            if match["name"] == match_name:
                match_exists = True
                match["passing_data"] = passing_data
                break

        if not match_exists:
            # If the match doesn't exist, create a new entry for it
            new_match = {
                "name": match_name,
                "passing_data": passing_data,
                "date": "",  # Add the date if required
                "opponent": ""  # Add opponent if required
            }
            data["teams"][team_name]["matches"].append(new_match)
        
        # Save the updated data back to the file
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

app = App()
app.mainloop()

'''

# Read data on load
teams = loadData()

# window
window = tk.Tk()
window.title('Soccer Video Analysis')
window.geometry('1920x900')

style = ttk.Style()
style.configure("Header.TLabel", background="#e0e0e0", font=("Segoe UI", 8, "bold"))
style.configure("Result.TLabel", background="#f5f5f5", font=("Segoe UI", 8, "bold"))
style.configure("Comp.TButton", background="#bfd880", font=("Segoe UI", 8))
style.configure("Incomp.TButton", background="#fa7e70", font=("Segoe UI", 8))

players = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]

action_events = {
    "Shot": [],
    "Tackle": [],
    "Cross": []
}

# Store action data
current_action_type = 'Shot'
action_columns = {
    "Shot": ["Minute", "Team", "Player", "Distance", "Angle", "Expected Goals", "Outcome"],
    "Tackle": ["Minute", "Team", "Player", "Outcome"],
    "Cross": ["Minute", "Team", "Player", "Location", "Outcome"]
}

action_tables = {}
current_match_name = None

# Set up Tabs
tabControl = ttk.Notebook(window)
summarytab = ttk.Frame(tabControl)
passingtab = ttk.Frame(tabControl)
actionstab = ttk.Notebook(tabControl)

tabControl.add(summarytab, text="Summary")
tabControl.add(passingtab, text="Passing")
tabControl.add(actionstab, text="Actions")
tabControl.pack(expand=1, fill="both")

# Passing tab
passnet_tabControl = PassingTab(ttk.Notebook(passingtab), tabControl, players)

# Actions tab
for action_type in action_events:
    frame = ttk.Frame(actionstab)
    actionstab.add(frame, text=action_type)

    add_btn = tk.Button(frame, text=f"Add {action_type}", command=lambda a=action_type: add_event(a))
    add_btn.pack()

    cols = action_columns[action_type]
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True)

    action_tables[action_type] = tree

passnet_tabControl.refresh_passingtab_displays(players)
window.mainloop()

'''