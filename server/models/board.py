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

    def is_column_full(self, column):
        return self.grid[0][column] is not None

    def is_board_full(self):
        for col in range(7):
            if self.grid[0][col] is None:
                return False
        return True