from datetime import datetime

from .board import Board


class Game:
    def __init__(self, game_id, player1, player2, current_player_index):
        self.board = Board()
        self.game_id = game_id
        self.players = [player1, player2]
        self.current_player_index = current_player_index
        self.is_finished = False
        self.winner = None
        self.game_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def play_move(self, row, column):
        player_number = self.current_player_index + 1

        self.board.add_piece(row, column, player_number)

    def player_win(self, row, column, player_number):
        directions = [
            (0, 1),   # Horizontal →
            (1, 0),   # Vertical ↓
            (1, 1),   # Diagonal ↘
            (1, -1)   # Diagonal ↙
        ]

        for row_direction, col_direction in directions:
            consecutive_pieces = 1  # The current piece counts as one

            # Check in one direction
            for step in range(1, 4):
                check_row = row + row_direction * step
                check_col = column + col_direction * step

                if (0 <= check_row < 6 and 0 <= check_col < 7 and
                    self.board.get_cell(check_row, check_col) == player_number):
                    consecutive_pieces += 1
                else:
                    break

            # Check in the opposite direction
            for step in range(1, 4):
                check_row = row - row_direction * step
                check_col = column - col_direction * step

                if (0 <= check_row < 6 and 0 <= check_col < 7 and
                    self.board.get_cell(check_row, check_col) == player_number):
                    consecutive_pieces += 1
                else:
                    break

            if consecutive_pieces >= 4:
                return True

        return False

    def get_opponent_socket_id(self, player_socket_id):
        if self.players[0].socket_id == player_socket_id:
            return self.players[1].socket_id
        return self.players[0].socket_id