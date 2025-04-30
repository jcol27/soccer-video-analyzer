import tkinter as tk
from tkinter import messagebox
from matplotlib import pyplot as plt

def update_pitch(current_action_type):
    pass


def add_event(tabControl, team_var, player_var, x_var, y_var, minute_var, pitch_widget, current_match_name, current_action_type, action_tables, matches_data):
    global click_listener_enabled
    click_listener_enabled = True

    new_event = {'Minute': '', 'Team': '', 'Player': '', 'Distance': '', 'Angle': '', 'Expected Goals': '', 'Outcome': '', 'X': '', 'Y': ''}

    def save_event():
        selected_team = team_var.get()
        selected_player = player_var.get()
        minute = minute_var.get()

        new_event['Team'] = selected_team
        new_event['Player'] = selected_player
        new_event['Minute'] = minute
        new_event['X'] = x_var.get()
        new_event['Y'] = y_var.get()

        if current_match_name:
            matches_data[current_match_name][current_action_type].append(new_event)
        else:
            messagebox.showwarning("No Match Selected", "Please select or create a match first.")
            popup.destroy()
            return
        table = action_tables[current_action_type]
        table.insert('', 'end', values=(minute, selected_team, selected_player, new_event['X'], new_event['Y']))

        popup.destroy()
        update_pitch(current_action_type)

    popup = tk.Toplevel(tabControl)
    popup.title("Add Event")

    def on_pitch_click(event, pitch_widget):
        nonlocal x_var, y_var
        if click_listener_enabled:
            widget_width = pitch_widget.winfo_width()
            widget_height = pitch_widget.winfo_height()
            x_click = (event.x / widget_width) * 100
            y_click = (1 - event.y / widget_height) * 100
            x_var.set(f"{x_click:.2f}")
            y_var.set(f"{y_click:.2f}")
            pitch_widget.unbind("<Button-1>")
            click_listener_enabled = False

    pitch_widget.unbind("<Button-1>")  # Ensure no double bindings
    pitch_widget.bind("<Button-1>", on_pitch_click)


def draw_pitch(pitch_ax, pitch_canvas):
    pitch_ax.clear()
    pitch_ax.set_xlim(0, 100)
    pitch_ax.set_ylim(0, 100)
    pitch_ax.set_aspect('equal')
    pitch_ax.axis('off')

    # Pitch outline and center line
    pitch_ax.plot([0, 0, 100, 100, 0], [0, 100, 100, 0, 0], color='black')  # outer boundary
    pitch_ax.plot([50, 50], [0, 100], color='black')  # halfway line

    # Centre circle
    centre_circle = plt.Circle((50, 50), 9.15, color='black', fill=False)  # 9.15 meters in radius (10% of pitch height here)
    pitch_ax.add_artist(centre_circle)

    # Centre spot
    pitch_ax.plot(50, 50, 'o', color='black')

    # Penalty spots
    pitch_ax.plot(50, 11, 'o', color='black')  # bottom penalty spot
    pitch_ax.plot(50, 89, 'o', color='black')  # top penalty spot

    # Penalty areas (18-yard boxes)
    # Bottom penalty box
    pitch_ax.plot([21.1, 78.9], [16.5, 16.5], color='black')  # top line
    pitch_ax.plot([21.1, 21.1], [0, 16.5], color='black')  # left line
    pitch_ax.plot([78.9, 78.9], [0, 16.5], color='black')  # right line

    # Top penalty box
    pitch_ax.plot([21.1, 78.9], [83.5, 83.5], color='black')  # bottom line
    pitch_ax.plot([21.1, 21.1], [83.5, 100], color='black')  # left line
    pitch_ax.plot([78.9, 78.9], [83.5, 100], color='black')  # right line

    # 6-yard boxes (goal areas)
    # Bottom 6-yard box
    pitch_ax.plot([36.8, 63.2], [5.5, 5.5], color='black')
    pitch_ax.plot([36.8, 36.8], [0, 5.5], color='black')
    pitch_ax.plot([63.2, 63.2], [0, 5.5], color='black')

    # Top 6-yard box
    pitch_ax.plot([36.8, 63.2], [94.5, 94.5], color='black')
    pitch_ax.plot([36.8, 36.8], [94.5, 100], color='black')
    pitch_ax.plot([63.2, 63.2], [94.5, 100], color='black')

    # Optional: Draw goals
    goal_width = 7.32  # meters
    goal_start = 50 - (goal_width / 2) * (100 / 105)  # scaled for our pitch
    goal_end = 50 + (goal_width / 2) * (100 / 105)

    # Bottom goal
    pitch_ax.plot([goal_start, goal_end], [0, 0], color='blue')

    # Top goal
    pitch_ax.plot([goal_start, goal_end], [100, 100], color='blue')

    pitch_canvas.draw_idle()
