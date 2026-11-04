"""Create the Sprint 0 graphical interface for Peg Solitaire."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.solitaire_game import SolitaireGame
from src.game_rating import GameRating
from src.game_session import GameSession


class SolitaireGUI:
    """Display a prototype interface for the Peg Solitaire game."""

    @property
    def game(self):
        """Always return the current session's game."""
        return self.session.game
    

    def __init__(self, root):
        """Initialize the application window and its controls."""
        self.root = root
        self.root.title("Peg Solitaire BrainVita")
        self.root.geometry("850x780")
        self.root.resizable(False, False)

        self.board_type = tk.StringVar(value="English")
        self.board_size = tk.StringVar(value="7")
        self.mode = tk.StringVar(value="Manual")
        self.session = GameSession()
        self.timer = None
        self.replaying = False
        self.recording = False
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

        mode_label = ttk.Label(
            controls,
            text="Game Mode",
            font=("Arial", 12, "bold"),
        )
        mode_label.pack(anchor="w", pady=(10, 5))

        mode_selector = ttk.Combobox(
            controls,
            textvariable=self.mode,
            values=("Manual", "Automated"),
            state="readonly",
            width=12,
        )
        mode_selector.pack(anchor="w")

        for label, callback in (
            ("Randomize", self.randomize_board),
            ("Save Recording", self.save_recording),
            ("Replay File", self.replay_file),
        ):
            button = ttk.Button(
                controls,
                text=label,
                command=callback,
            )
            button.pack(fill="x", pady=3)
        
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
        """Create a fresh game using the selected settings."""
        board_type = self.board_type.get()
        size = int(self.board_size.get())

        self.stop_timer()

        self.replaying = False
        self.recording = self.record_game.get()

        self.session = GameSession(
            board_type,
            size,
            self.mode.get(),
        )

        self.selected = None
        self.draw_board()
        self.update_game_status()

    def start_autoplay(self):
        """Start an automated game's animation."""
        if self.replaying or self.session.mode != "Automated":
            self.status.set(
                "Choose Automated and click New Game first."
            )
            return

        if self.timer is None:
            self.autoplay_step()

    def stop_timer(self):
        """Cancel an existing autoplay or replay callback."""
        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def autoplay_step(self):
        """Make one move and schedule the next if play can continue."""
        self.timer = None

        if self.session.step():
            self.draw_board()
            self.update_game_status()

            if self.game.game_result() == "playing":
                self.timer = self.root.after(
                    150,
                    self.autoplay_step,
                )
        else:
            self.update_game_status()

    def randomize_board(self):
        """Shuffle a manual board and update the display."""
        if self.replaying or not self.session.randomize():
            self.status.set(
                "Randomization is available in manual mode."
            )
            return

        self.selected = None
        self.draw_board()
        self.update_game_status()

    def save_recording(self):
        """Ask where to save the current recorded session."""
        if not self.recording or self.replaying:
            self.status.set(
                "Check Record game before starting a new game."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Text recording", "*.json")],
        )

        if not path:
            return

        try:
            self.session.save(path)
            self.status.set("Recording saved.")
        except OSError as error:
            messagebox.showerror("Save failed", str(error))

    def replay_file(self):
        """Load a recording and begin displaying its saved states."""
        path = filedialog.askopenfilename(
            filetypes=[("Text recording", "*.json")],
        )

        if not path:
            return

        try:
            loaded = GameSession.load(path)
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror("Replay failed", str(error))
            return

        self.stop_timer()

        self.session = loaded

        self.replaying = True
        self.recording = False
        self.selected = None

        self.board_type.set(self.game.board_type)
        self.board_size.set(str(self.game.size))
        self.mode.set(loaded.mode)

        self.replay_step(0)

    def replay_step(self, index):
        """Display one frame and schedule the next frame."""
        self.timer = None

        self.session.show_frame(index)
        self.draw_board()

        self.status.set(
            f"Replay frame {index + 1} "
            f"of {len(self.session.frames)}"
        )

        if index + 1 < len(self.session.frames):
            self.timer = self.root.after(
                300,
                lambda: self.replay_step(index + 1),
            )
        else:
            self.status.set(
                "Replay complete. Start New Game to play."
            )



    def on_hole_click(self, position):
        """Select a peg or try jumping into an empty hole."""
        if self.replaying or self.session.mode != "Manual":
            return
        
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

        if self.session.move(self.selected, position):
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