class MatchmakingQueue:
    def __init__(self):
        self.queue = []

    def add_player(self, player):
        self.queue.append(player)

    def remove_player(self, player):
        if player in self.queue:
            self.queue.remove(player)

    def find_match(self):
        if len(self.queue) >= 2:
            return self.queue.pop(0), self.queue.pop(0)
        return None

    def clear_queue(self):
        self.queue.clear()

    def is_player_in_queue(self, player):
        return player in self.queue