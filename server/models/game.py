class Board:
    def __init__(self):
        self.grid = [[None for _ in range(7)] for _ in range(6)]

    def add_piece(self, row, column, player_number):
        self.grid[row][column] = player_number

    def get_cell(self, row, column):
        return self.grid[row][column]

    def get_lowest_empty_row(self, column):
        for row in range(5, -1, -1):
            if self.grid[row][column] is None:
                return row
        return None

    def is_valid_column(self, column):
        return self.grid[0][column] is None

    def is_full(self):
        for col in range(7):
            if self.grid[0][col] is None:
                return False
        return True


class Game:
    def __init__(self, player1, player2):
        self.board = Board()
        self.players = [player1, player2]
        self.current_player_index = 0
        self.is_finished = False
        self.winner = None
        self.last_move = None

    def play_move(self, player, column):
        if self.players[self.current_player_index] != player:
            return {"success": False, "error": "Not your turn!"}

        if not self.board.is_valid_column(column):
            return {"success": False, "error": "Column is full!"}

        row = self.board.get_lowest_empty_row(column)
        player_number = self.current_player_index + 1

        self.board.add_piece(row, column, player_number)
        self.last_move = (row, column)

        if self.check_victory(row, column, player_number):
            self.winner = player_number
            self.is_finished = True
        elif self.board.is_full():
            self.is_finished = True
        else:
            self.current_player_index = 1 - self.current_player_index

        return {"success": True, "row": row, "column": column}

    def check_victory(self, row, col, player_number):
        # Vérifie si le dernier coup est gagnant
        directions = [
            (0, 1),   # Horizontal →
            (1, 0),   # Vertical ↓
            (1, 1),   # Diagonale ↘
            (1, -1)   # Diagonale ↙
        ]

        for dr, dc in directions:
            count = 1  # Le pion qu'on vient de placer

            # Vérifier dans un sens
            for i in range(1, 4):
                r = row + dr * i
                c = col + dc * i

                if (0 <= r < 6 and 0 <= c < 7 and
                    self.board.get_cell(r, c) == player_number):
                    count += 1
                else:
                    break

            # Vérifier dans l'autre sens
            for i in range(1, 4):
                r = row - dr * i
                c = col - dc * i

                if (0 <= r < 6 and 0 <= c < 7 and
                    self.board.get_cell(r, c) == player_number):
                    count += 1
                else:
                    break

            if count >= 4:
                return True

        return False