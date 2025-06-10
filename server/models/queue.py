class MatchmakingQueue:
    def __init__(self):
        self.queue = []

    def add_player(self, socket_id):
        self.queue.append(socket_id)

    def remove_player(self, socket_id):
        self.queue.remove(socket_id)

    def find_match(self):
        return self.queue.pop(0), self.queue.pop(0)

    def get_position(self, socket_id):
        return self.queue.index(socket_id) + 1

    def size(self):
        return len(self.queue)