"""Manage game modes and text recording independently from Tkinter."""

import json
import random

from src.solitaire_game import SolitaireGame


class ManualGame(SolitaireGame):
    """Use the common rules with moves selected by a human."""


class AutomatedGame(SolitaireGame):
    """Choose legal moves automatically using the shared game rules."""

    def step(self, rng=None):
        """Make one automatic move, or return None if no moves remain."""
        moves = self.legal_moves()

        if not moves:
            return None

        start, destination = (rng or random).choice(moves)
        self.make_move(start, destination)

        return start, destination


class GameSession:
    """Manage the selected mode and record successful actions."""

    def __init__(self, board_type="English", size=7, mode="Manual"):
        if mode not in ("Manual", "Automated"):
            raise ValueError("Unsupported game mode.")

        self.mode = mode

        game_class = ManualGame if mode == "Manual" else AutomatedGame
        self.game = game_class(board_type, size)

        self.frames = []
        self.capture("new_game")

    def capture(self, action):
        """Store the current arrangement as a recording frame."""
        pegs = [
            list(position)
            for position, occupied in self.game.board.items()
            if occupied
        ]

        self.frames.append({
            "action": action,
            "pegs": pegs,
        })

    def move(self, start, destination):
        """Apply and record a successful manual move."""
        if self.mode != "Manual":
            return False

        if not self.game.make_move(start, destination):
            return False

        self.capture("move")
        return True

    def step(self, rng=None):
        """Apply and record one automated move."""
        if self.mode != "Automated":
            return False

        move = self.game.step(rng)

        if move is None:
            return False

        self.capture("automated_move")
        return True

    def randomize(self, rng=None):
        """Randomize and record a manual game's board."""
        if self.mode != "Manual":
            return False

        self.game.randomize(rng)
        self.capture("randomize")
        return True

    def save(self, path):
        """Save the game history as readable JSON text."""
        data = {
            "version": 1,
            "board_type": self.game.board_type,
            "size": self.game.size,
            "mode": self.mode,
            "frames": self.frames,
        }

        with open(path, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2)

    @staticmethod
    def load(path):
        """Check a recording's structure and board coordinates."""
        with open(path, encoding="utf-8") as source:
            data = json.load(source)

        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("Unsupported recording format.")

        session = GameSession(
            data.get("board_type"),
            data.get("size"),
            data.get("mode"),
        )

        frames = data.get("frames")

        if not isinstance(frames, list) or not frames:
            raise ValueError("Recording must contain frames.")

        allowed_actions = (
            "new_game",
            "move",
            "automated_move",
            "randomize",
        )

        for frame in frames:
            if (
                not isinstance(frame, dict)
                or frame.get("action") not in allowed_actions
            ):
                raise ValueError("Invalid recording frame.")

            pegs = frame.get("pegs")

            if not isinstance(pegs, list) or not pegs:
                raise ValueError("Invalid peg list.")

            positions = []

            for peg in pegs:
                if (
                    not isinstance(peg, list)
                    or len(peg) != 2
                    or any(type(value) is not int for value in peg)
                ):
                    raise ValueError("Invalid peg coordinate.")

                position = tuple(peg)

                if position not in session.game.board:
                    raise ValueError("Peg outside board.")

                positions.append(position)

            if len(set(positions)) != len(positions):
                raise ValueError("Duplicate peg.")

        session.frames = frames
        return session

    def show_frame(self, index):
        """Restore a saved board arrangement for replay."""
        occupied = {
            tuple(position)
            for position in self.frames[index]["pegs"]
        }

        self.game.board = {
            position: position in occupied
            for position in self.game.board
        }