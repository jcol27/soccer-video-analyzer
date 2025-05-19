import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox


class passingButton:
    def __init__(self):
        self.button = None
        self.buttonValue = 0

class PassingTab:
    def __init__(self, tabControl, toplevel, players):
        self.tabControl = tabControl
        self.toplevel = toplevel
        self.table_tab = ttk.Frame(self.tabControl)
        self.comp_tab = ttk.Frame(self.tabControl)
        self.incomp_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.table_tab, text="Passing Table")
        self.tabControl.add(self.comp_tab, text="Completed Pass Network")
        self.tabControl.add(self.incomp_tab, text="Incomplete Pass Network")
        self.tabControl.grid(row=0, column=0, sticky="nsew")

        self.tabControl.pack(expand=1, fill="both")

        self.addition = True

    def get_data(self):
        return {
            "comp": {
                p1: {p2: self.passingcompbuttons[p1][p2].buttonValue for p2 in self.passingcompbuttons[p1]}
                for p1 in self.passingcompbuttons
            },
            "incomp": {
                p1: {p2: self.passingincompbuttons[p1][p2].buttonValue for p2 in self.passingincompbuttons[p1]}
                for p1 in self.passingincompbuttons
            }
        }

    def load_data(self, data, players):
        comp_data = data.get("comp", {})
        incomp_data = data.get("incomp", {})
        
        for p1 in players:
            for p2 in players:
                if p1 != p2:
                    self.passingcompbuttons[p1][p2].buttonValue = comp_data.get(p1, {}).get(p2, 0)
                    self.passingincompbuttons[p1][p2].buttonValue = incomp_data.get(p1, {}).get(p2, 0)

        self.refresh_passingtab_displays(players)

    def load_passingtab_displays(self, players):

        self.change_history = []

        self.tabControl.bind("<<NotebookTabChanged>>", lambda event: self.on_passing_tab_change(event, players))

        for widget in self.table_tab.winfo_children():
            widget.destroy()

        self.table_tab.grid_columnconfigure(0, weight=1, uniform="fred")
        self.table_tab.grid_columnconfigure(1, weight=2, uniform="fred")
        for i in range(2,len(players)*2+2):
            self.table_tab.grid_columnconfigure(i, weight=1, uniform="fred")

        self.table_tab.grid_columnconfigure(len(players)*2 + 2, weight=2, uniform="fred")
        for i in range(len(players)*2 + 3,len(players)*2 + 6):
            self.table_tab.grid_columnconfigure(i, weight=2, uniform="fred")

        for i in range(len(players) + 5):
            self.table_tab.grid_rowconfigure(i, weight=1, uniform="fred")

        self.row_labels = {p: {"comp": None, "incomp": None, "percent": None} for p in players}
        self.col_labels = {p: {"comp": None, "incomp": None} for p in players}

        self.team_comp_label = tk.Label(self.table_tab, text="0", font=("Segoe UI", 8, "bold"))
        self.team_comp_label.grid(row=len(players)+3, column=len(players)*2 + 3)
        self.team_incomp_label = tk.Label(self.table_tab, text="0", font=("Segoe UI", 8, "bold"))
        self.team_incomp_label.grid(row=len(players)+3, column=len(players)*2 + 4)
        self.team_compperc_label = tk.Label(self.table_tab, text="0.0%", font=("Segoe UI", 8, "bold"))
        self.team_compperc_label.grid(row=len(players)+3, column=len(players)*2 + 5)

        tk.Label(self.table_tab, text="To Player", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=0, column=2, columnspan=2)
        tk.Label(self.table_tab, text="From\nPlayer", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=3, column=0)
        tk.Label(self.table_tab, text="From\nPlayer", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=3, column=len(players)*2 + 2)
        tk.Label(self.table_tab, text="Made\nComplete", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=2, column=len(players)*2 + 3)
        tk.Label(self.table_tab, text="Made\nIncomplete", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=2, column=len(players)*2 + 4)
        tk.Label(self.table_tab, text="Percentage\nMade\nComplete", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=2, column=len(players)*2 + 5)
        tk.Label(self.table_tab, text="Total", font=("Segoe UI", 8, "bold"), anchor="center", justify="center").grid(row=len(players)+3, column=1)

        self.passingcomp = {p1: {p2: 0 for p2 in players} for p1 in players}
        self.passingincomp = {p1: {p2: 0 for p2 in players} for p1 in players}

        self.passingcompbuttons = {p1: {p2: passingButton() for p2 in players} for p1 in players}
        self.passingincompbuttons = {p1: {p2: passingButton() for p2 in players} for p1 in players}

        self.made_comp_totals = {p: tk.IntVar(value=0) for p in players}
        self.made_incomp_totals = {p: tk.IntVar(value=0) for p in players}

        self.received_comp_totals = {p: tk.IntVar(value=0) for p in players}
        self.received_incomp_totals = {p: tk.IntVar(value=0) for p in players}

        self.total_passes = {p: tk.IntVar(value=0) for p in players}
        self.percentages = {p: tk.StringVar(value="0%") for p in players}

        for i, p in enumerate(players):
            pcolheader = tk.Label(self.table_tab, text=f"{p}", font=("Segoe UI", 8, "bold"), anchor="center")
            prowheader = tk.Label(self.table_tab, text=f"{p}", font=("Segoe UI", 8, "bold"), anchor="center")
            prowheader2 = tk.Label(self.table_tab, text=f"{p}", font=("Segoe UI", 8, "bold"), anchor="center")
            pcolheader.grid(row=1, column=2*i + 2, sticky="nswe", columnspan=2)
            prowheader.grid(row=i+3, column=1, sticky="nswe")
            prowheader2.grid(row=i+3, column=len(players)*2 + 2, sticky="nswe")

            tk.Label(self.table_tab, text="", font=("Segoe UI", 9), anchor="center").grid(row=2, column=2*i + 2)
            tk.Label(self.table_tab, text="", font=("Segoe UI", 9), anchor="center").grid(row=2, column=2*i + 3)

            self.row_labels[p]["comp"] = tk.Label(self.table_tab, text="0")
            self.row_labels[p]["incomp"] = tk.Label(self.table_tab, text="0")
            self.row_labels[p]["percent"] = tk.Label(self.table_tab, text="0%")
            self.row_labels[p]["comp"].grid(row=i+3, column=len(players)*2 + 3)
            self.row_labels[p]["incomp"].grid(row=i+3, column=len(players)*2 + 4)
            self.row_labels[p]["percent"].grid(row=i+3, column=len(players)*2 + 5)

            style = ttk.Style()
            style.configure("Comp.TButton", background="#bfd880", font=("Segoe UI", 8))
            style.configure("Incomp.TButton", background="#fa7e70", font=("Segoe UI", 8))

            for i2, p2 in enumerate(players):
                if p != p2:
                    btn_comp = ttk.Button(self.table_tab, text="0", style="Comp.TButton", width=6, command=lambda p1=p, p2=p2: self.updatePassingButton(p1, p2, players, True, self.passingcompbuttons))
                    btn_comp.grid(row=i+3, column=2*i2 + 2, sticky="nswe")
                    self.passingcompbuttons[p][p2].button = btn_comp

                    btn_incomp = ttk.Button(self.table_tab, text="0", style="Incomp.TButton", width=6, command=lambda p1=p, p2=p2: self.updatePassingButton(p1, p2, players, False, self.passingincompbuttons))
                    btn_incomp.grid(row=i+3, column=2*i2 + 3, sticky="nswe")
                    self.passingincompbuttons[p][p2].button = btn_incomp

            self.col_labels[p]["comp"] = tk.Label(self.table_tab, text="0")
            self.col_labels[p]["comp"].grid(row=len(players)+3, column=2*i + 2)
            self.col_labels[p]["incomp"] = tk.Label(self.table_tab, text="0")
            self.col_labels[p]["incomp"].grid(row=len(players)+3, column=2*i + 3)

        ttk.Button(self.table_tab, text="Reset All", command=lambda : self.confirm_reset_all(players)).grid(row=len(players)+5, column=2, columnspan=3, sticky="nswe")
        ttk.Button(self.table_tab, text="Undo", command=lambda : self.undo_last_change(players)).grid(row=len(players)+5, column=5, columnspan=3, sticky="nswe")
        ttk.Button(self.table_tab, text="Edit", command=lambda : self.edit_value(players)).grid(row=len(players)+5, column=8, columnspan=3, sticky="nswe")
        self.addsubbutton = ttk.Button(self.table_tab, text="Toggle Subtraction", command=self.toggleaddsub)
        self.addsubbutton.grid(row=len(players)+5, column=11, columnspan=3, sticky="nswe")

    def toggleaddsub(self):
        self.addition = not self.addition
        if self.addition:
            self.addsubbutton.config(text="Toggle Subtraction")
        else:
            self.addsubbutton.config(text="Toggle Addition")

    def refresh_passingtab_displays(self, players):
        for p1 in players:
            row_total = 0
            row_comp = 0
            row_incomp = 0
            for p2 in players:
                if p1 != p2:
                    comp_btn = self.passingcompbuttons[p1][p2]
                    incomp_btn = self.passingincompbuttons[p1][p2]
                    comp_btn.button.config(text=str(comp_btn.buttonValue))
                    incomp_btn.button.config(text=str(incomp_btn.buttonValue))

                    row_total += comp_btn.buttonValue + incomp_btn.buttonValue
                    row_comp += comp_btn.buttonValue
                    row_incomp += incomp_btn.buttonValue

            percent = f"{(row_comp / row_total * 100):.1f}%" if row_total > 0 else "0%"
            self.row_labels[p1]["comp"].config(text=str(row_comp), font=("Segoe UI", 8, "bold"))
            self.row_labels[p1]["incomp"].config(text=str(row_incomp), font=("Segoe UI", 8, "bold"))
            self.row_labels[p1]["percent"].config(text=percent, font=("Segoe UI", 8, "bold"))

        # Update column totals and team totals
        total_comp = total_incomp = 0
        for p2 in players:
            col_comp = 0
            col_incomp = 0
            for p1 in players:
                if p1 != p2:
                    col_comp += self.passingcompbuttons[p1][p2].buttonValue
                    col_incomp += self.passingincompbuttons[p1][p2].buttonValue
                    total_comp += self.passingcompbuttons[p1][p2].buttonValue
                    total_incomp += self.passingincompbuttons[p1][p2].buttonValue
            self.col_labels[p2]["comp"].config(text=f"{col_comp}", font=("Segoe UI", 8, "bold"))
            self.col_labels[p2]["incomp"].config(text=f"{col_incomp}", font=("Segoe UI", 8, "bold"))

        # Team totals
        team_total = total_comp + total_incomp
        team_comp_percent = f"{(total_comp / team_total * 100):.1f}%" if team_total > 0 else "0%"
        self.team_comp_label.config(text=str(total_comp), font=("Segoe UI", 8, "bold"))
        self.team_incomp_label.config(text=str(total_incomp), font=("Segoe UI", 8, "bold"))
        self.team_compperc_label.config(text=team_comp_percent, font=("Segoe UI", 8, "bold"))

    def draw_pass_network(self, frame, players, passbuttons):
        print(f"Updating pass network for {frame}")

        # Clear graph only (not buttons)
        for widget in frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 6))
        G = nx.DiGraph()

        for p in players:
            G.add_node(p)

        # Add edges
        for p1 in players:
            for p2 in players:
                if p1 != p2:
                    val = passbuttons[p1][p2].buttonValue
                    if val > 0:
                        G.add_edge(p1, p2, weight=val)

        pos = nx.spring_layout(G)

        # Calculate node sizes
        node_pass_counts = {}
        for p in players:
            count = 0
            for p2 in players:
                if p != p2:
                    count += passbuttons[p][p2].buttonValue + passbuttons[p2][p].buttonValue
            node_pass_counts[p] = count

        min_size = 10
        max_size = 5000
        max_pass = max(node_pass_counts.values()) or 1
        node_sizes = [
            min_size + (node_pass_counts[p] / max_pass) * (max_size - min_size)
            for p in players
        ]

        edge_min_width = 1
        edge_max_width = 20

        # Draw graph
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color="#6e172e")
        nx.draw_networkx_edges(G, pos, ax=ax, width=[(G[u][v]['weight'] / max(G[u][v]['weight'] for u, v in G.edges())) * (edge_max_width - edge_min_width) + edge_min_width for u, v in G.edges()], edge_color="gray")
        nx.draw_networkx_labels(G, pos, ax=ax, font_color="#e5a300", font_size=16)

        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)

        # Remove axis
        ax.set_axis_off()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw_idle()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        plt.close(fig)

    def on_passing_tab_change(self, event, players):
        # Get the index of the current selected tab
        selected_tab_index = self.tabControl.index("current")

        # Check if the selected tab is the 'Completed Pass Network' tab
        if selected_tab_index == self.tabControl.index(self.comp_tab):
            self.draw_pass_network(self.comp_tab, players, self.passingcompbuttons)  # Call the function to draw the completed pass network

        # Optionally, you can handle the incomplete tab similarly:
        elif selected_tab_index == self.tabControl.index(self.incomp_tab):
            self.draw_pass_network(self.incomp_tab, players, self.passingincompbuttons)  # Call the function to draw the incomplete pass network
        
        else:
            print("No matching tab")

    def updatePassingButton(self, p, p2, players, comp, passingbuttons):
        prev_val = passingbuttons[p][p2].buttonValue
        self.change_history.append((p, p2, comp, prev_val))

        if self.addition:
            passingbuttons[p][p2].buttonValue += 1
        else:
            passingbuttons[p][p2].buttonValue = max(0,passingbuttons[p][p2].buttonValue - 1)


        self.refresh_passingtab_displays(players)

        self.toplevel.save_match_data()

    def reset_all(self, players):
        for p1 in players:
            for p2 in players:
                if p1 != p2:
                    self.passingcompbuttons[p1][p2].buttonValue = 0
                    self.passingincompbuttons[p1][p2].buttonValue = 0

        self.change_history.clear()
        self.refresh_passingtab_displays(players)

        self.toplevel.save_match_data()

    def confirm_reset_all(self, players):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all passing data?"):
            self.reset_all(players)

    def undo_last_change(self, players):
        if not self.change_history:
            return
        p, p2, comp, old_val = self.change_history.pop()
        if comp:
            self.passingcompbuttons[p][p2].buttonValue = old_val
        else:
            self.passingincompbuttons[p][p2].buttonValue = old_val
        self.refresh_passingtab_displays(players)

        self.toplevel.save_match_data()

    def edit_value(self, players):
        def submit_edit():
            p1 = from_player.get()
            p2 = to_player.get()
            val = int(new_value.get())
            is_comp = var_type.get() == "Complete"
            if p1 == p2:
                return  # Ignore same player
            self.change_history.append((p1, p2, is_comp,
                self.passingcompbuttons[p1][p2].buttonValue if is_comp else self.passingincompbuttons[p1][p2].buttonValue))
            if is_comp:
                self.passingcompbuttons[p1][p2].buttonValue = val
            else:
                self.passingincompbuttons[p1][p2].buttonValue = val
            self.refresh_passingtab_displays(players)
            edit_win.destroy()

        edit_win = tk.Toplevel(self.toplevel)
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

        self.toplevel.save_match_data()