from tkinter import messagebox, simpledialog
import tkinter as tk

class Match:
    def __init__(self, name, date, opponent, lineup):
        self.name = name
        self.date = date
        self.opponent = opponent
        self.lineup = lineup

    def to_dict(self):
        return {
            "name": self.name,
            "date": self.date,
            "opponent": self.opponent,
            "lineup": self.lineup
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            date=data.get("date", ""),
            opponent=data.get("opponent", ""),
            lineup=data.get("lineup", "")
        )

class MatchPlayerSelector:
    def __init__(self, parent, squad, lineup, save_callback):
        self.top = tk.Toplevel(parent)
        self.top.wm_minsize(width=300, height=200)
        self.top.title("Select Match Players")
        self.selected = lineup
        self.check_vars = {}
        self.save_callback = save_callback

        for p in squad:
            var = tk.BooleanVar(value=p in lineup)
            cb = tk.Checkbutton(self.top, text=p.playerName, variable=var, command=self.update_count)
            cb.pack(anchor="w", padx=10)
            self.check_vars[p] = var

        self.count_var = tk.StringVar()
        self.count_label = tk.Label(self.top, textvariable=self.count_var, font=("Segoe UI", 9, "bold"))
        self.count_label.pack(pady=(0, 5))  # Put below title or above checkboxes

        # Initialize count
        self.update_count()

        tk.Button(self.top, text="Save", command=self.save_selection).pack(pady=10)

    def save_selection(self):
        self.selected[:] = [p for p, v in self.check_vars.items() if v.get()]
        self.save_callback([x.playerName for x in self.selected[:]])
        self.top.destroy()

    def update_count(self):
        selected = sum(var.get() for var in self.check_vars.values())
        self.count_var.set(f"Players selected: {selected}")

def create_new_match(matches_data, match_selector):
    global current_match_name
    new_match_name = simpledialog.askstring("New Match", "Enter match name:")
    if new_match_name:
        matches_data[new_match_name] = {'Shot': [], 'Tackle': [], 'Cross': []}
        match_selector['values'] = list(matches_data.keys())
        match_selector.set(new_match_name)
        current_match_name = new_match_name

def on_match_selected(event, match_selector, matches_data):
    global current_match_name
    selected = match_selector.get()
    if selected in matches_data:
        current_match_name = selected