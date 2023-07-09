from django.db import models

PLAYER_1 = "1"
PLAYER_2 = "2"
PLAYER_CHOICES = [
    (PLAYER_1, "player 1"),
    (PLAYER_2, "player 2"),
]


class Game(models.Model):
    """
    Game board is an (x, y) coordinate system with (0, 0) being the bottom-left corner.
    (6, 6) represents the top-right corner. (Note this is different than the diagram in the requirements doc.)

    y
    6 _ _ _ _ _ _ _
    5 _ _ _ _ _ _ _
    4 _ _ _ _ _ _ _
    3 _ _ _ _ _ _ _
    2 _ _ _ _ _ _ _
    1 _ _ _ _ _ _ _
    0 _ _ _ _ _ _ _
      0 1 2 3 4 5 6 x

    A space with no associated GameMove is empty.

    Use integer sequence as ID, as usual in Django. Views must not let clients supply game ID since it is easily
    guessable.
    """
    STATE_MATCH_MAKING = "match making"
    STATE_IN_PROGRESS = "in progress"
    STATE_COMPLETED = "completed"
    STATE_CHOICES = [
        (STATE_MATCH_MAKING, "Match making"),
        (STATE_IN_PROGRESS, "In progress"),
        (STATE_COMPLETED, "Completed")
    ]
    state = models.CharField(max_length=20, null=False, blank=False, default=STATE_MATCH_MAKING)
    next_player = models.CharField(max_length=10, null=False, blank=False, choices=PLAYER_CHOICES, default=PLAYER_1)
    winner = models.CharField(max_length=10, null=True, blank=True, choices=PLAYER_CHOICES)

    _board = None  # This gets lazy loaded from GameMoves.

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Game {self.id} ({self.state})"

    def get_board(self):
        """
        Load existing moves into a 2-dimensional list.

        Outer list is rows (y axis). Inner lists are columns (x axis). So refer to a space as board[y][x].
        """
        if not self._board:
            # Set up a blank board-
            self._board = []
            for x in range(0, 7):
                self._board.append([])
                for y in range(0, 7):
                    self._board[x].append(None)

            # Get existing moves
            moves = self.gamemove_set.all()
            for move in moves:
                self._board[move.x_coord][move.y_coord] = move.player

        return self._board

    def move(self, player, x, y):
        """
        Perform validation, register the move, check if game is complete, update game state and next player.
        """
        if player != self.next_player:
            # This is not the player you are looking for.
            raise ValueError("The player is not the expected player.")
        if not self._valid_coordinates(x, y):
            raise ValueError("The coordinates aren't valid for the board.")
        if self.is_complete():
            raise ValueError("The game is already complete.")

        if self._get_space_player(x, y) is not None:
            raise ValueError("This space is already chosen.")
        if not self._is_continuous_from_side(x, y):
            raise ValueError("This space isn't available until the spaces from the side are chosen.")

        # Finally after all those checks, this is a valid move.
        self._record_move(player, x, y)
        if self._is_winning_move(player, x, y):
            # The game is over
            self.winner = player
            self.state = self.STATE_COMPLETED
        elif self._all_spaces_chosen():
            # Winner remains None
            self.state = self.STATE_COMPLETED
        else:
            # The game is still going.
            self.next_player = PLAYER_2 if self.next_player == PLAYER_1 else PLAYER_1

    def is_complete(self):
        return self.state == self.STATE_COMPLETED

    def _record_move(self, player, x, y):
        """Save a GameMove object representing this and update _board."""
        GameMove.objects.create(
            game=self,
            player=player,
            x_coord=x,
            y_coord=y,
        )
        self._board[y][x] = player

    def _is_winning_move(self, player, x, y):
        """
        Return if the player has made a winning move, having 4 or more in a row.

        The continuous counts in either direction should add up to 3 or more because they don't include the current
        move.
        """
        def add(coord):
            return coord + 1

        def subtract(coord):
            return coord - 1

        def noop(coord):
            return coord

        # Check ↕
        if self._count_continuous(player, x, y, noop, add) + \
                self._count_continuous(player, x, y, noop, subtract) >= 3:
            return True
        # Check ↔
        if self._count_continuous(player, x, y, add, noop) + \
                self._count_continuous(player, x, y, subtract, noop) >= 3:
            return True
        # Check ⤢
        if self._count_continuous(player, x, y, add, add) + \
                self._count_continuous(player, x, y, subtract, subtract) >= 3:
            return True
        # Check ⤡
        if self._count_continuous(player, x, y, subtract, add) + \
                self._count_continuous(player, x, y, add, subtract) >= 3:
            return True

    def _count_continuous(self, player, x, y, x_callable, y_callable):
        """
        Return the number of continuous spaces the player has played from the coordinates.

        The direction to check is controlled by the x and y callables, which should take 1 coordinate arg and either
        add 1, subtract 1, or make no change.
        """
        continuous_spaces = 0  # Do not include the starting space.
        check_x = x
        check_y = y
        continuous = True
        while continuous:
            check_x = x_callable(check_x)
            check_y = y_callable(check_y)
            if not self._valid_coordinates(check_x, check_y):
                # We're off the board now.
                continuous = False
            else:
                if self._get_space_player(check_x, check_y) == player:
                    continuous_spaces += 1
                else:
                    continuous = False

        return continuous_spaces

    def _get_space_player(self, x, y):
        """Return the player who chose this space, or None."""
        b = self.get_board()
        return b[y][x]

    def _valid_coordinates(self, x, y):
        """Return if the coordinates are valid (they exist on the board)."""
        return 0 <= x <= 6 and 0 <= y <= 6

    def _is_continuous_from_side(self, x, y):
        """
        Return if the move is continuous from left or right.
        """
        board = self.get_board()
        row = board[y]

        # Check continuous from left.
        continuous_from_left = True
        for check_x in range(0, x):
            if row[check_x] is None:
                continuous_from_left = False
                break

        # Check continuous from right.
        continuous_from_right = True
        for check_x in range(x+1, 7):
            if row[check_x] is None:
                continuous_from_right = False
                break

        return continuous_from_left or continuous_from_right

    def _all_spaces_chosen(self):
        """Return if all the spaces have been chosen."""
        for x in range(0, 7):
            for y in range(0, 7):
                if self._get_space_player(x, y) is None:
                    return False
        return True


class GameMove(models.Model):
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.CharField(max_length=10, null=False, blank=False, choices=PLAYER_CHOICES)
    x_coord = models.SmallIntegerField(null=False, blank=False)
    y_coord = models.SmallIntegerField(null=False, blank=False)

    class Meta:
        ordering = ["game", "x_coord", "y_coord"]
        constraints = [
            models.UniqueConstraint(fields=['game', 'x_coord', 'y_coord'], name='unique_game_move'),
        ]

    def __str__(self):
        return f"({self.x_coord}, {self.y_coord}) game {self.game.id}"
