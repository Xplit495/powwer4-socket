from datetime import datetime
from enum import Enum


class Status(Enum):
    IDLE = 1
    WAITING = 2
    IN_GAME = 3

class Player:
    def __init__(self, player_id, socket_id, username, total_games_count, win_streak, win_games_count):
        self.player_id = player_id
        self.socket_id = socket_id

        self.username = username

        self.total_games_count = total_games_count
        self.win_streak = win_streak
        self.win_games_count = win_games_count
        self.lose_games_count = total_games_count - win_games_count

        self.status = Status.IDLE
        self.current_game_id = None

        self.joined_queue_at = None

    def join_queue(self):
        self.status = Status.WAITING
        self.joined_queue_at = datetime.now()

    def start_game(self, game_id):
        self.status = Status.IN_GAME
        self.current_game_id = game_id
        self.joined_queue_at = None

    def end_game(self, is_winner):
        self.status = Status.IDLE
        self.current_game_id = None
        self.total_games_count += 1
        if is_winner:
            self.win_streak += 1

    def get_win_rate(self):
        if self.total_games_count == 0:
            return 0
        return round((self.total_games_count / self.win_games_count) * 100, 1)