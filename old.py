import tkinter as tk
from tkinter import ttk

class passingButton:
    def __init__(self):
        self.button = None
        self.buttonValue = tk.IntVar(value=0)

change_history = []

def reset_all():
    for p1 in players:
        for p2 in players:
            if p1 != p2:
                passingcompbuttons[p1][p2].buttonValue = 0
                passingincompbuttons[p1][p2].buttonValue = 0
    change_history.clear()
    refresh_all_displays()

def undo_last_change():
    if not change_history:
        return
    p, p2, comp, old_val = change_history.pop()
    if comp:
        passingcompbuttons[p][p2].buttonValue = old_val
    else:
        passingincompbuttons[p][p2].buttonValue = old_val
    refresh_all_displays()

def edit_value():
    def submit_edit():
        p1 = from_player.get()
        p2 = to_player.get()
        val = int(new_value.get())
        is_comp = var_type.get() == "Complete"
        if p1 == p2:
            return  # Ignore same player
        change_history.append((p1, p2, is_comp,
            passingcompbuttons[p1][p2].buttonValue if is_comp else passingincompbuttons[p1][p2].buttonValue))
        if is_comp:
            passingcompbuttons[p1][p2].buttonValue = val
        else:
            passingincompbuttons[p1][p2].buttonValue = val
        refresh_all_displays()
        edit_win.destroy()

    edit_win = tk.Toplevel(window)
    edit_win.title("Edit Value")

    from_player = ttk.Combobox(edit_win, values=players)
    to_player = ttk.Combobox(edit_win, values=players)
    var_type = ttk.Combobox(edit_win, values=["Complete", "Incomplete"])
    new_value = tk.Entry(edit_win)

    ttk.Label(edit_win, text="From:").grid(row=0, column=0)
    from_player.grid(row=0, column=1)
    ttk.Label(edit_win, text="To:").grid(row=1, column=0)
    to_player.grid(row=1, column=1)
    ttk.Label(edit_win, text="Type:").grid(row=2, column=0)
    var_type.grid(row=2, column=1)
    ttk.Label(edit_win, text="New Value:").grid(row=3, column=0)
    new_value.grid(row=3, column=1)

    ttk.Button(edit_win, text="Submit", command=submit_edit).grid(row=4, column=0, columnspan=2)

def refresh_all_displays():
    for p1 in players:
        for p2 in players:
            if p1 != p2:
                comp_btn = passingcompbuttons[p1][p2]
                incomp_btn = passingincompbuttons[p1][p2]
                comp_btn.button.config(text=str(comp_btn.buttonValue))
                incomp_btn.button.config(text=str(incomp_btn.buttonValue))
    # Trigger team + individual stat updates
    updatePassingButton(players[0], players[1], True)  # fake update to trigger recalculation


def updatePassingButton(p, p2, comp):

    prev_val = passingcompbuttons[p][p2].buttonValue if comp else passingincompbuttons[p][p2].buttonValue
    change_history.append((p, p2, comp, prev_val))

    if comp:
        current_val = passingcompbuttons[p][p2].buttonValue.get()
        passingcompbuttons[p][p2].buttonValue.set(current_val + 1)
        made_comp_totals[p].set(made_comp_totals[p].get() + 1)
        received_comp_totals[p2].set(received_comp_totals[p2].get() + 1)
    else:
        current_val = passingincompbuttons[p][p2].buttonValue.get()
        passingincompbuttons[p][p2].buttonValue.set(current_val + 1)
        made_incomp_totals[p].set(made_incomp_totals[p2].get() + 1)
        received_incomp_totals[p2].set(received_incomp_totals[p2].get() + 1)

    # Update total and percentage
    total = made_comp_totals[p].get() + made_incomp_totals[p].get()
    total_passes[p].set(total)

    if total > 0:
        perc = round((made_comp_totals[p].get() / total) * 100)
        percentages[p].set(f"{perc}%")
    else:
        percentages[p].set("0%")

    # Update team totals
    team_comp = sum(var.get() for var in made_comp_totals.values())
    team_incomp = sum(var.get() for var in made_incomp_totals.values())
    team_total = team_comp + team_incomp

    team_comp_total.set(team_comp)
    team_incomp_total.set(team_incomp)

    if team_total > 0:
        team_percent = round((team_comp / team_total) * 100)
        team_percentage.set(f"{team_percent}%")
    else:
        team_percentage.set("0%")

    print(f"{p} passing stats -> Complete: {made_comp_totals[p].get()}, Incomplete: {made_incomp_totals[p].get()}, Total: {total}, Percent: {percentages[p].get()}")
    

# window
window = tk.Tk()
window.title('Soccer Video Analysis')
window.geometry('1920x900')

style = ttk.Style()
style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))
style.configure("Result.TLabel", font=("Segoe UI", 10, "bold"))
style.configure("Input.TButton", font=("Segoe UI", 10))

tabControl = ttk.Notebook(window)

summarytab = ttk.Frame(tabControl)
passingtab = ttk.Frame(tabControl)
shootingtab = ttk.Frame(tabControl)

tabControl.add(summarytab, text="Summary")
tabControl.add(passingtab, text="Passing")
tabControl.add(shootingtab, text="Shot Actions")

tabControl.pack(expand=1, fill="both")

# 
players = ["Natasha", "Tehan", "Gracie", "Sammy", "Rose", "Rina", "Bri", "Lucia", "Alice", "Freida", "Maja"]

passingcomp = {p1: {p2: 0 for p2 in players} for p1 in players}
passingincomp = {p1: {p2: 0 for p2 in players} for p1 in players}

passingcompbuttons = {p1: {p2: passingButton() for p2 in players} for p1 in players}
passingincompbuttons = {p1: {p2: passingButton() for p2 in players} for p1 in players}

made_comp_totals = {p: tk.IntVar(value=0) for p in players}
made_incomp_totals = {p: tk.IntVar(value=0) for p in players}

received_comp_totals = {p: tk.IntVar(value=0) for p in players}
received_incomp_totals = {p: tk.IntVar(value=0) for p in players}

total_passes = {p: tk.IntVar(value=0) for p in players}
percentages = {p: tk.StringVar(value="0%") for p in players}

team_comp_total = tk.IntVar(value=0)
team_incomp_total = tk.IntVar(value=0)
team_percentage = tk.StringVar(value="0%")

for i in range(len(players)*2 + 5):
    passingtab.grid_columnconfigure(i, weight=1)
for i in range(len(players) + 5):
    passingtab.grid_rowconfigure(i, weight=1)

# Table
ttk.Label(passingtab, text="To Player", style="Header.TLabel", anchor="center", justify="center").grid(row = 0, column = 2, sticky="nswe")
ttk.Label(passingtab, text="From Player", style="Header.TLabel", anchor="center", justify="center").grid(row = 3, column = 0, sticky="nswe")

ttk.Label(passingtab, text="Total\nComplete", style="Header.TLabel", anchor="center", justify="center").grid(row = 2, column = len(players)*2 + 2, sticky="nswe")
ttk.Label(passingtab, text="Total\nIncomplete", style="Header.TLabel", anchor="center", justify="center").grid(row = 2, column = len(players)*2 + 3, sticky="nswe")
ttk.Label(passingtab, text="Percentage\nComplete", style="Header.TLabel", anchor="center", justify="center").grid(row = 2, column = len(players)*2 + 4, sticky="nswe")
ttk.Label(passingtab, text="Player\nTotals", style="Header.TLabel", anchor="center", justify="center").grid(row = len(players) + 3, column = 1, sticky="nswe")

ttk.Label(passingtab, text="Team\nTotals", style="Result.TLabel", anchor="center", justify="center").grid(row=len(players)+4, column=1, sticky="nswe")
ttk.Label(passingtab, textvariable=team_comp_total, style="Result.TLabel", anchor="center").grid(row=len(players)+4, column=len(players)*2 + 2, sticky="nswe")
ttk.Label(passingtab, textvariable=team_incomp_total, style="Result.TLabel", anchor="center").grid(row=len(players)+4, column=len(players)*2 + 3, sticky="nswe")
ttk.Label(passingtab, textvariable=team_percentage, style="Result.TLabel", anchor="center").grid(row=len(players)+4, column=len(players)*2 + 4, sticky="nswe")

for i, p in enumerate(players):
    pcolheader = ttk.Label(passingtab, text=f"{p}", style="Header.TLabel", anchor="center")
    prowheader = ttk.Label(passingtab, text=f"{p}", style="Header.TLabel", anchor="center")
    pcolheader.grid(row = 1, column = 2*i + 2, sticky="nswe", columnspan=2)
    prowheader.grid(row = i+3, column = 1, sticky="nswe")

    tk.Label(passingtab, text="Complete", anchor="center").grid(row = 2, column = 2*i + 2, sticky="nswe")
    tk.Label(passingtab, text="Incomplete", anchor="center").grid(row = 2, column = 2*i + 3, sticky="nswe")

    # Display stats at end of each row
    ttk.Label(passingtab, textvariable=made_comp_totals[p], style="Result.TLabel", anchor="center").grid(row=i+3, column=len(players)*2 + 2, sticky="nswe")
    ttk.Label(passingtab, textvariable=made_incomp_totals[p], style="Result.TLabel", anchor="center").grid(row=i+3, column=len(players)*2 + 3, sticky="nswe")
    ttk.Label(passingtab, textvariable=percentages[p], style="Result.TLabel", anchor="center").grid(row=i+3, column=len(players)*2 + 4, sticky="nswe")


    # Passes buttons (comp/incomp)
    for i2, p2 in enumerate(players):
        if p != p2:
            def make_command(p1=p, p2=p2):  # default arguments avoid late binding
                return lambda: updatePassingButton(p1, p2, True)

            def make_command_incomp(p1=p, p2=p2):
                return lambda: updatePassingButton(p1, p2, False)

            btn_comp = ttk.Button(passingtab, textvariable=passingcompbuttons[p][p2].buttonValue, command=make_command())
            btn_comp.grid(row=i+3, column=2*i2 + 2, sticky="nswe")
            passingcompbuttons[p][p2].button = btn_comp

            btn_incomp = ttk.Button(passingtab, textvariable=passingincompbuttons[p][p2].buttonValue, command=make_command_incomp())
            btn_incomp.grid(row=i+3, column=2*i2 + 3, sticky="nswe")
            passingincompbuttons[p][p2].button = btn_incomp

# Totals at bottom row
for i, p in enumerate(players):
    ttk.Label(passingtab, textvariable=received_comp_totals[p], style="Header.TLabel", anchor="center").grid(row=len(players)+3, column=2*i + 2)
    ttk.Label(passingtab, textvariable=received_incomp_totals[p], style="Header.TLabel", anchor="center").grid(row=len(players)+3, column=2*i + 3)


window.mainloop()