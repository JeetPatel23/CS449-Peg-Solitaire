"""Tests for game modes, randomization, recording, and replay."""

import json
import random
import tempfile
import unittest
from pathlib import Path

from src.game_session import (
    GameSession,
    ManualGame,
    AutomatedGame,
)


class TestGameSession(unittest.TestCase):

    def test_modes_share_rules(self):
        for mode, expected in (
            ("Manual", ManualGame),
            ("Automated", AutomatedGame),
        ):
            session = GameSession(mode=mode)

            self.assertIsInstance(session.game, expected)
            self.assertTrue(
                session.game.is_valid_move((1, 3), (3, 3))
            )

    def test_manual_move_and_invalid_recording(self):
        session = GameSession()

        self.assertFalse(session.move((3, 3), (3, 5)))
        self.assertEqual(len(session.frames), 1)

        self.assertTrue(session.move((1, 3), (3, 3)))
        self.assertEqual(len(session.frames), 2)

    def test_automated_games_finish(self):
        for board in ("English", "Hexagon", "Diamond"):
            for size in (7, 9):
                with self.subTest(board=board, size=size):
                    session = GameSession(
                        board,
                        size,
                        "Automated",
                    )
                    count = session.game.peg_count()
                    rng = random.Random(8)

                    while session.step(rng):
                        self.assertEqual(
                            session.game.peg_count(),
                            count - 1,
                        )
                        count -= 1

                    self.assertIn(
                        session.game.game_result(),
                        ("win", "no_moves"),
                    )
                    self.assertFalse(session.step())

    def test_randomization_preserves_count_and_layout(self):
        session = GameSession()
        session.move((1, 3), (3, 3))

        before = session.game.board.copy()
        session.randomize(random.Random(42))

        self.assertEqual(
            set(before),
            set(session.game.board),
        )
        self.assertEqual(
            sum(before.values()),
            session.game.peg_count(),
        )
        self.assertNotEqual(before, session.game.board)
        self.assertEqual(
            session.frames[-1]["action"],
            "randomize",
        )

    def test_wrong_mode_actions_are_rejected(self):
        manual = GameSession()
        automated = GameSession(mode="Automated")

        self.assertFalse(manual.step())
        self.assertFalse(
            automated.move((1, 3), (3, 3))
        )
        self.assertFalse(automated.randomize())

    def test_recording_round_trip_every_frame(self):
        session = GameSession()
        session.move((1, 3), (3, 3))
        session.randomize(random.Random(2))

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "game.json"

            session.save(path)
            loaded = GameSession.load(path)

            self.assertEqual(
                loaded.frames,
                session.frames,
            )

            for index, frame in enumerate(session.frames):
                loaded.show_frame(index)

                actual_pegs = {
                    position
                    for position, occupied
                    in loaded.game.board.items()
                    if occupied
                }
                expected_pegs = {
                    tuple(position)
                    for position in frame["pegs"]
                }

                self.assertEqual(
                    actual_pegs,
                    expected_pegs,
                )

    def test_bad_recordings_rejected(self):
        invalid_recordings = (
            {"version": 9},
            {
                "version": 1,
                "board_type": "English",
                "size": 7,
                "mode": "Manual",
                "frames": [],
            },
            {
                "version": 1,
                "board_type": "English",
                "size": 7,
                "mode": "Manual",
                "frames": [
                    {
                        "action": "move",
                        "pegs": [[99, 99]],
                    }
                ],
            },
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"

            for data in invalid_recordings:
                path.write_text(
                    json.dumps(data),
                    encoding="utf-8",
                )

                with self.assertRaises(ValueError):
                    GameSession.load(path)

    def test_invalid_settings_rejected(self):
        invalid_settings = (
            ("English", 7, "Other"),
            ("Other", 7, "Manual"),
            ("English", 8, "Manual"),
        )

        for settings in invalid_settings:
            with self.assertRaises(ValueError):
                GameSession(*settings)


if __name__ == "__main__":
    unittest.main()