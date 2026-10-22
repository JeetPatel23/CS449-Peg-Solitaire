"""Create the Sprint 0 graphical interface for Peg Solitaire."""

import tkinter as tk
from tkinter import ttk
from src.solitaire_game import SolitaireGame
from src.game_rating import GameRating


class SolitaireGUI:
    """Display a prototype interface for the Peg Solitaire game."""

    def __init__(self, root):
        """Initialize the application window and its controls."""
        self.root = root
        self.root.title("Peg Solitaire BrainVita")
        self.root.geometry("800x620")
        self.root.resizable(False, False)

        self.board_type = tk.StringVar(value="English")
        self.board_size = tk.StringVar(value="7")
        self.game = SolitaireGame()
        self.record_game = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Select a board type to begin.")
        self.selected = None
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
            text="CS 449 Peg Solitaire",
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
        size_label = ttk.Label(
            controls,
            text="Board Size",
            font=("Arial", 12, "bold"),
        )
        size_label.pack(anchor="w", pady=(15, 5))

        size_selector = ttk.Combobox(
            controls,
            textvariable=self.board_size,
            values=SolitaireGame.BOARD_SIZES,
            state="readonly",
            width=8,
        )
        size_selector.pack(anchor="w")
        
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
        """Draw the board and connect each hole to a mouse click."""
        self.board_canvas.delete("all")

        spacing = 32
        radius = 12
        center = self.game.size // 2

        for position, has_peg in self.game.board.items():
            row, column = position

            if self.game.board_type == "Hexagon":
                x = 205 + (
                    column - center - (row - center) / 2
                ) * spacing
                y = 175 + (row - center) * spacing * 0.866
            else:
                x = 205 + (column - center) * spacing
                y = 175 + (row - center) * spacing

            fill_color = "#4A6FA5" if has_peg else "white"

            if position == self.selected:
                fill_color = "#F4A340"

            hole = self.board_canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=fill_color,
                outline="#23395D",
                width=2,
            )

            self.board_canvas.tag_bind(
                hole,
                "<Button-1>",
                lambda event, pos=position: self.on_hole_click(pos),
            )

    def update_status(self):
        """Update the status text when a setting changes."""
        recording = "enabled" if self.record_game.get() else "disabled"
        self.status.set(
            f"{self.board_type.get()} board selected. "
            f"Recording is {recording}."
        )

    def start_new_game(self):
        """Reset the selected board and clear the selected peg."""
        board_type = self.board_type.get()
        size = int(self.board_size.get())

        self.game.new_game(board_type, size)
        self.selected = None
        self.draw_board()
        self.update_game_status()

    def start_autoplay(self):
        """Respond to the Autoplay button."""
        self.status.set("Autoplay selected for a future sprint.")


    def on_hole_click(self, position):
        """Select a peg or try jumping into an empty hole."""
        if self.game.game_result() != "playing":
            self.update_game_status()
            return

        if self.game.board[position]:
            # Clicking a peg selects it; clicking it again deselects it.
            if self.selected == position:
                self.selected = None
            else:
                self.selected = position

            self.draw_board()
            self.update_game_status()
            return

        if self.selected is None:
            self.status.set("Select a peg first, then an empty hole.")
            return

        if self.game.make_move(self.selected, position):
            self.selected = None
            self.draw_board()
            self.update_game_status()
        else:
            self.status.set(
                "Invalid move. Jump over one peg into an empty hole."
            )

    def update_game_status(self):
        """Display the peg count, instructions, or final result."""
        count = self.game.peg_count()
        result = self.game.game_result()

        if result == "win":
            rating = GameRating.determine_rating(count)
            self.status.set(f"You won! One peg remaining | {rating}")
        elif result == "no_moves":
            rating = GameRating.determine_rating(count)
            self.status.set(
                f"No moves remain | Pegs: {count} | Rating: {rating}"
            )
        elif self.selected is not None:
            self.status.set(
                f"Pegs remaining: {count} | Select an empty destination."
            )
        else:
            self.status.set(
                f"Pegs remaining: {count} | Select a peg to move."
            )

            
def main():
    """Start the Peg Solitaire GUI application."""
    root = tk.Tk()
    SolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()