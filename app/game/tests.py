from django.test import TestCase
from game.models import Game, GameMove, PLAYER_1, PLAYER_2


class GameTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()

    def test_move(self):
        """Test first move and verify next player and state."""
        self.game.move(PLAYER_1, 0, 0)
        self.assertEqual(self.game.next_player, PLAYER_2)
        self.assertFalse(self.game.is_complete())

    def test_wrong_player(self):
        """Test player 1 playing twice in a row."""
        self.game.move(PLAYER_1, 0, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 0, 1)

    def test_move_off_board(self):
        """Test move at coordinate off the board."""
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, -1, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 0, -1)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 7, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 0, 7)

    def test_wrong_next_player(self):
        """Test wrong next player."""
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_2, 0, 1)

    def test_taken_space(self):
        """Test move at a space with an existing move."""
        self.game.move(PLAYER_1, 0, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_2, 0, 0)

    def test_second_move_new_line(self):
        """Test valid move by player 2 on a new line."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 0, 1)

    def test_second_move_same_line(self):
        """Test valid move by player 2 on the same line as first move."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 1, 0)

    def test_second_move_right_side(self):
        """Test valid move by player 2 on the right side."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 6, 0)

    def test_move_discontinuous_space_left(self):
        """Test moves made discontinuous from left side."""
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 1, 0)

        self.game.move(PLAYER_1, 0, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_2, 2, 0)

    def test_move_discontinuous_space_right(self):
        """Test moves made discontinuous from right side."""
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_1, 5, 0)

        self.game.move(PLAYER_1, 6, 0)
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_2, 4, 0)

    def test_complete_straight_row(self):
        """Test win in a straight line, one row."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 0, 1)
        self.game.move(PLAYER_1, 1, 0)
        self.game.move(PLAYER_2, 1, 1)
        self.game.move(PLAYER_1, 2, 0)
        self.game.move(PLAYER_2, 2, 1)
        self.game.move(PLAYER_1, 3, 0)  # Win!
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, PLAYER_1)

    def test_complete_straight_column(self):
        """Test win in a straight line, one column."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 6, 0)
        self.game.move(PLAYER_1, 0, 1)
        self.game.move(PLAYER_2, 6, 1)
        self.game.move(PLAYER_1, 0, 2)
        self.game.move(PLAYER_2, 6, 2)
        self.game.move(PLAYER_1, 0, 3)  # Win!
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, PLAYER_1)

    def test_complete_straight_row_middle(self):
        """Test win in a straight line when the last move is in the middle of the player's moves."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 6, 0)
        self.game.move(PLAYER_1, 0, 1)
        self.game.move(PLAYER_2, 6, 1)
        self.game.move(PLAYER_1, 0, 3)
        self.game.move(PLAYER_2, 6, 2)
        self.game.move(PLAYER_1, 0, 2)  # Win!
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, PLAYER_1)

    def test_complete_straight_row_middle_more_than_4(self):
        """
        Test win in a straight line when the last move is in the middle of the player's moves and there's
        more than 4 in a row.
        """
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 6, 0)
        self.game.move(PLAYER_1, 0, 1)
        self.game.move(PLAYER_2, 6, 1)
        self.game.move(PLAYER_1, 0, 2)
        self.game.move(PLAYER_2, 6, 2)
        self.game.move(PLAYER_1, 0, 5)
        self.game.move(PLAYER_2, 6, 5)
        self.game.move(PLAYER_1, 0, 4)
        self.game.move(PLAYER_2, 6, 4)
        self.game.move(PLAYER_1, 0, 3)  # Win!
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, PLAYER_1)

    def test_complete_diagonal(self):
        """Test win diagonally."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 0, 1)
        self.game.move(PLAYER_1, 1, 1)
        self.game.move(PLAYER_2, 0, 2)
        self.game.move(PLAYER_1, 1, 2)
        self.game.move(PLAYER_2, 0, 3)
        self.game.move(PLAYER_1, 2, 2)
        self.game.move(PLAYER_2, 1, 3)
        self.game.move(PLAYER_1, 0, 4)
        self.game.move(PLAYER_2, 2, 3)
        self.game.move(PLAYER_1, 3, 3)  # Win!
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, PLAYER_1)

    def test_incomplete(self):
        """Test game board is full, with no winner."""
        # Fill up a board with fabricated moves so we don't have to figure out a real board that has no winner.
        for x in range(0, 7):
            for y in range(0, 7):
                if x == 6 and y == 6:
                    # We'll make the final move the real way.
                    continue
                GameMove.objects.create(
                    game=self.game,
                    player=PLAYER_2,
                    x_coord=x,
                    y_coord=y,
                )
        self.game.move(PLAYER_1, 6, 6)
        self.assertTrue(self.game.is_complete())
        self.assertEqual(self.game.winner, None)

    def test_move_in_complete_game(self):
        """Test a move in a game that is complete."""
        self.game.move(PLAYER_1, 0, 0)
        self.game.move(PLAYER_2, 6, 0)
        self.game.move(PLAYER_1, 0, 1)
        self.game.move(PLAYER_2, 6, 1)
        self.game.move(PLAYER_1, 0, 3)
        self.game.move(PLAYER_2, 6, 2)
        self.game.move(PLAYER_1, 0, 2)  # Win!
        with self.assertRaises(ValueError):
            self.game.move(PLAYER_2, 6, 3)
