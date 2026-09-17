"""Create the Sprint 0 graphical interface for Peg Solitaire."""

import tkinter as tk
from tkinter import ttk


class SolitaireGUI:
    """Display a prototype interface for the Peg Solitaire game."""

    def __init__(self, root):
        """Initialize the application window and its controls."""
        self.root = root
        self.root.title("Peg Solitaire BrainVita")
        self.root.geometry("720x560")
        self.root.resizable(False, False)

        self.board_type = tk.StringVar(value="English")
        self.record_game = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Select a board type to begin.")

        self.create_interface()

    def create_interface(self):
        """Create and organize the interface components."""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text="Peg Solitaire BrainVita",
            font=("Arial", 24, "bold"),
        )
        title.pack(pady=(0, 10))

        subtitle = ttk.Label(
            main_frame,
            text="CS 449 Sprint 0 GUI Prototype",
            font=("Arial", 12),
        )
        subtitle.pack(pady=(0, 10))

        # This visible line satisfies the line requirement.
        divider = tk.Canvas(
            main_frame,
            width=650,
            height=10,
            highlightthickness=0,
        )
        divider.create_line(0, 5, 650, 5, fill="#4A6FA5", width=2)
        divider.pack()

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=15)

        self.board_canvas = tk.Canvas(
            content_frame,
            width=410,
            height=350,
            background="#F2F5F9",
            highlightbackground="#AAB7C4",
            highlightthickness=1,
        )
        self.board_canvas.pack(side="left", padx=(0, 20))

        controls = ttk.LabelFrame(
            content_frame,
            text="Game Settings",
            padding=15,
        )
        controls.pack(side="right", fill="y")

        board_label = ttk.Label(
            controls,
            text="Board Type",
            font=("Arial", 12, "bold"),
        )
        board_label.pack(anchor="w", pady=(0, 5))

        for board_name in ("English", "Hexagon", "Diamond"):
            radio_button = ttk.Radiobutton(
                controls,
                text=board_name,
                value=board_name,
                variable=self.board_type,
                command=self.update_status,
            )
            radio_button.pack(anchor="w", pady=3)

        record_checkbox = ttk.Checkbutton(
            controls,
            text="Record game",
            variable=self.record_game,
            command=self.update_status,
        )
        record_checkbox.pack(anchor="w", pady=(20, 10))

        new_game_button = ttk.Button(
            controls,
            text="New Game",
            command=self.start_new_game,
        )
        new_game_button.pack(fill="x", pady=5)

        autoplay_button = ttk.Button(
            controls,
            text="Autoplay",
            command=self.start_autoplay,
        )
        autoplay_button.pack(fill="x", pady=5)

        status_label = ttk.Label(
            main_frame,
            textvariable=self.status,
            font=("Arial", 11),
        )
        status_label.pack(pady=(5, 0))

        self.draw_board()

    def draw_board(self):
        """Draw a simple English Peg Solitaire board prototype."""
        self.board_canvas.delete("all")

        spacing = 42
        radius = 14
        start_x = 78
        start_y = 45

        for row in range(7):
            for column in range(7):
                corner_position = (
                    row < 2 or row > 4
                ) and (
                    column < 2 or column > 4
                )

                if corner_position:
                    continue

                x = start_x + column * spacing
                y = start_y + row * spacing

                if row == 3 and column == 3:
                    fill_color = "white"
                else:
                    fill_color = "#4A6FA5"

                self.board_canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill=fill_color,
                    outline="#23395D",
                    width=2,
                )

    def update_status(self):
        """Update the status text when a setting changes."""
        recording = "enabled" if self.record_game.get() else "disabled"
        self.status.set(
            f"{self.board_type.get()} board selected. "
            f"Recording is {recording}."
        )

    def start_new_game(self):
        """Respond to the New Game button."""
        self.status.set(
            f"New {self.board_type.get()} game selected."
        )

    def start_autoplay(self):
        """Respond to the Autoplay button."""
        self.status.set("Autoplay selected for a future sprint.")


def main():
    """Start the Peg Solitaire GUI application."""
    root = tk.Tk()
    SolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()