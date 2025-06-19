from datetime import datetime
from enum import Enum


class Status(Enum):
    ONLINE = 0
    CONNECTED = 1
    IN_QUEUE = 2
    IN_GAME = 3

class Player:
    def __init__(self, socket_id, player_ip, authenticated):
        # This 3 arguments are initialized when the player connect to the server.
        self.socket_id = socket_id
        self.player_ip = player_ip
        self.authenticated = authenticated # This argument is updated when the player login.
        # This 7 arguments are initialized when the player login.
        self.player_id = None
        self.username = None
        self.total_games_count = None
        self.win_games_count = None
        self.lose_games_count = None
        self.tie_games_count = None
        self.connected_at = None
        # This 3 arguments are often updated during the game.
        self.status = Status.ONLINE
        self.current_game_id = None
        self.joined_queue_at = None

    def join_queue(self):
        self.status = Status.IN_QUEUE
        self.joined_queue_at = datetime.now()

    def leave_queue(self):
        self.status = Status.CONNECTED
        self.joined_queue_at = None

    def start_game(self, game_id):
        self.status = Status.IN_GAME
        self.current_game_id = game_id
        self.joined_queue_at = None

    def end_game(self, result):
        self.status = Status.CONNECTED
        self.current_game_id = None
        self.total_games_count += 1
        match result:
            case 'tie':
                self.tie_games_count += 1
            case 'win':
                self.win_games_count += 1
            case 'lose':
                self.lose_games_count += 1