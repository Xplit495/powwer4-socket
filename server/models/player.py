from datetime import datetime
from enum import Enum

class Status(Enum):
    ONLINE = 0
    IDLE = 1
    WAITING = 2
    IN_GAME = 3

class Player:
    def __init__(self, player_ip, connected_at, authenticated):
        self.player_ip = player_ip
        self.connected_at = connected_at
        self.authenticated = authenticated

        self.player_id = None

        self.username = None

        self.total_games_count = None
        self.win_games_count = None
        self.lose_games_count = None # total_games_count - win_games_count

        self.status = Status.ONLINE
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
            self.win_games_count += 1

    def get_win_rate(self):
        if self.total_games_count == 0:
            return 0
        return round((self.win_games_count / self.total_games_count) * 100, 1)