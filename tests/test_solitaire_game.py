"""Tests for board creation, moves, and game results."""

import unittest

from src.solitaire_game import SolitaireGame


class TestSolitaireGame(unittest.TestCase):

    def test_board_types_and_sizes(self):
        expected_counts = {
            ("English", 7): 32,
            ("English", 9): 44,
            ("Hexagon", 7): 36,
            ("Hexagon", 9): 60,
            ("Diamond", 7): 24,
            ("Diamond", 9): 40,
        }

        for (board_type, size), expected in expected_counts.items():
            with self.subTest(board_type=board_type, size=size):
                game = SolitaireGame(board_type, size)
                center = size // 2

                self.assertEqual(game.peg_count(), expected)
                self.assertFalse(game.board[(center, center)])
                self.assertEqual(len(game.board), expected + 1)

    def test_new_game_resets_board_and_changes_settings(self):
        game = SolitaireGame()
        game.make_move((1, 3), (3, 3))

        game.new_game("Diamond", 9)

        self.assertEqual(game.board_type, "Diamond")
        self.assertEqual(game.size, 9)
        self.assertEqual(game.peg_count(), 40)
        self.assertFalse(game.board[(4, 4)])

    def test_valid_jump_updates_all_three_holes(self):
        game = SolitaireGame()

        moved = game.make_move((1, 3), (3, 3))

        self.assertTrue(moved)
        self.assertFalse(game.board[(1, 3)])
        self.assertFalse(game.board[(2, 3)])
        self.assertTrue(game.board[(3, 3)])
        self.assertEqual(game.peg_count(), 31)

    def test_invalid_moves_leave_board_unchanged(self):
        cases = [
            ("empty start", (3, 3), (3, 5), None),
            ("occupied destination", (3, 1), (3, 3), (3, 3)),
            ("missing middle peg", (1, 3), (3, 3), (2, 3)),
            ("outside layout", (0, 2), (0, 0), None),
            ("wrong distance", (2, 3), (3, 3), None),
        ]

        for name, start, destination, changed_hole in cases:
            with self.subTest(case=name):
                game = SolitaireGame()

                if name == "occupied destination":
                    game.board[changed_hole] = True
                elif name == "missing middle peg":
                    game.board[changed_hole] = False

                before = game.board.copy()

                self.assertFalse(game.make_move(start, destination))
                self.assertEqual(game.board, before)

    def test_last_jump_produces_a_win(self):
        game = SolitaireGame()

        for position in game.board:
            game.board[position] = False

        game.board[(3, 1)] = True
        game.board[(3, 2)] = True

        self.assertTrue(game.make_move((3, 1), (3, 3)))
        self.assertEqual(game.peg_count(), 1)
        self.assertEqual(game.game_result(), "win")

    def test_separated_pegs_produce_no_moves_result(self):
        game = SolitaireGame()

        for position in game.board:
            game.board[position] = False

        game.board[(0, 2)] = True
        game.board[(6, 4)] = True

        self.assertFalse(game.has_valid_moves())
        self.assertEqual(game.game_result(), "no_moves")

    def test_new_board_is_still_playable(self):
        game = SolitaireGame()

        self.assertTrue(game.has_valid_moves())
        self.assertEqual(game.game_result(), "playing")


if __name__ == "__main__":
    unittest.main()