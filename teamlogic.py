from playerlogic import *
from matchlogic import *

class Team:
    def __init__(self, name, squad, matches):
        self.name = name
        self.squad = []
        self.matches = []

        # Read team stored players
        for player in squad:
            player = Player(player)
            self.squad.append(player)
        
        # Read team stored matches
        self.matches = matches


    def to_dict(self):
        return {
            "name": self.name,
            "squad": self.squad,
            "matches": [m.to_dict() for m in self.matches]
        }

    @classmethod
    def from_dict(cls, name, data):
        name = name
        squad = data.get("squad", [])
        matches_data = data.get("matches", [])
        matches = [Match.from_dict(m) for m in matches_data]
        return cls(name=name, squad=squad, matches=matches)

class EditSquadPopup:
    def __init__(self, master, team):
        self.top = tk.Toplevel(master)
        self.top.title(f"Edit Squad - {team.name}")
        self.top.geometry("400x800")
        self.team = team

        self.list_frame = tk.Frame(self.top)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(1, weight=0)

        self.render_player_list()

        # Add player entry section
        self.add_frame = tk.Frame(self.top)
        self.add_frame.pack(fill=tk.X, padx=10, pady=(5, 0))

        self.new_player_entry = tk.Entry(self.add_frame)
        self.new_player_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        add_button = tk.Button(self.add_frame, text="Add", command=self.add_player)
        add_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Save button
        self.save_button = tk.Button(self.top, text="Save & Close", command=lambda master=master: self.updateSquad(master))
        self.save_button.pack(pady=(5, 10))

    def updateSquad(self, master):
        master.save_data()
        self.top.destroy()

    def render_player_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Sort players alphabetically by name
        sorted_players = sorted(self.team.squad, key=lambda p: p.playerName.lower())

        for i, player in enumerate(sorted_players):
            name_label = tk.Label(self.list_frame, text=player.playerName, anchor="w")
            name_label.grid(row=i, column=0, sticky="w")

            remove_button = tk.Button(self.list_frame, text="Remove", command=lambda p=player: self.remove_player(p))
            remove_button.grid(row=i, column=1, padx=5, pady=2, sticky="e")

    def remove_player(self, player):
        self.team.squad.remove(player)
        self.render_player_list()

    def add_player(self):
        name = self.new_player_entry.get().strip()
        if name and not any(p.playerName.lower() == name.lower() for p in self.team.squad):
            new_player = Player(name)
            self.team.squad.append(new_player)
            self.new_player_entry.delete(0, tk.END)
            self.render_player_list()

class SquadManager:
    def __init__(self, parent, team_name, team_data, save_callback):
        self.top = tk.Toplevel(parent)
        self.top.title(f"Manage Squad - {team_name}")
        self.team_data = team_data
        self.save_callback = save_callback

        self.listbox = tk.Listbox(self.top, height=15, width=30)
        self.listbox.pack(padx=10, pady=5)

        for player in self.team_data.get("squad", []):
            self.listbox.insert(tk.END, player)

        add_btn = tk.Button(self.top, text="Add Player", command=self.add_player)
        remove_btn = tk.Button(self.top, text="Remove Selected", command=self.remove_selected)
        add_btn.pack(pady=(10, 0))
        remove_btn.pack(pady=(5, 10))

    def add_player(self):
        name = simpledialog.askstring("Add Player", "Enter player name:", parent=self.top)
        if name and name not in self.team_data["squad"]:
            self.team_data.setdefault("squad", []).append(name)
            self.listbox.insert(tk.END, name)
            self.save_callback()

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        name = self.listbox.get(selection[0])
        if messagebox.askyesno("Remove Player", f"Remove {name} from squad?"):
            self.listbox.delete(selection[0])
            self.team_data["squad"].remove(name)
            self.save_callback()