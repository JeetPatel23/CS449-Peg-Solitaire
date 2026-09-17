"""Unit tests for the Peg Solitaire game-rating system."""

import unittest

from src.game_rating import GameRating


class TestGameRating(unittest.TestCase):
    """Test the rating returned for different game results."""

    def test_one_peg_is_outstanding(self):
        """One remaining peg should receive the highest rating."""
        self.assertEqual(GameRating.determine_rating(1), "Outstanding")

    def test_two_pegs_is_very_good(self):
        """Two remaining pegs should receive a Very Good rating."""
        self.assertEqual(GameRating.determine_rating(2), "Very Good")

    def test_three_pegs_is_good(self):
        """Three remaining pegs should receive a Good rating."""
        self.assertEqual(GameRating.determine_rating(3), "Good")

    def test_four_or_more_pegs_is_average(self):
        """Four or more remaining pegs should receive an Average rating."""
        self.assertEqual(GameRating.determine_rating(4), "Average")
        self.assertEqual(GameRating.determine_rating(10), "Average")

    def test_zero_pegs_raises_error(self):
        """An impossible peg count should raise an error."""
        with self.assertRaises(ValueError):
            GameRating.determine_rating(0)


if __name__ == "__main__":
    unittest.main()