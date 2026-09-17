"""Provide the rating system for a completed Peg Solitaire game."""


class GameRating:
    """Determine a player's rating from the number of pegs remaining."""

    @staticmethod
    def determine_rating(pegs_remaining: int) -> str:
        """Return the player's rating based on the remaining pegs."""
        if pegs_remaining < 1:
            raise ValueError("The number of remaining pegs must be at least 1.")

        if pegs_remaining == 1:
            return "Outstanding"
        if pegs_remaining == 2:
            return "Very Good"
        if pegs_remaining == 3:
            return "Good"

        return "Average"