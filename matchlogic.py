from tkinter import messagebox, simpledialog

class Match:
    def __init__(self, name, date, opponent):
        self.name = name
        self.date = date
        self.opponent = opponent

    def to_dict(self):
        return {
            "name": self.name,
            "date": self.date,
            "opponent": self.opponent
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            date=data.get("date", ""),
            opponent=data.get("opponent", "")
        )


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