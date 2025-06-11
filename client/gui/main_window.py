import customtkinter as ctk
from client.config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from .login_view import LoginView
from .menu_view import MenuView
from .waiting_view import WaitingView
from .game_view import GameView

class MainWindow:
    def __init__(self, socket_client):
        self.socket_client = socket_client
        self.current_user = None

        self.root = ctk.CTk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.container = ctk.CTkFrame(self.root)
        self.container.pack(fill="both", expand=True)

        self.views = {
            "login": LoginView(self.container, self),
            "menu": MenuView(self.container, self),
            "waiting": WaitingView(self.container, self),
            "game": GameView(self.container, self)
        }

        self.setup_socket_callbacks()

        self.show_view("login")

    def show_view(self, view_name):
        for view in self.views.values():
            view.hide()
        self.views[view_name].show()

    def setup_socket_callbacks(self):
        callbacks = {
            'connect': self.on_connect,
            'disconnect': self.on_disconnect,
            'login_success': self.on_login_success,
            'login_error': self.on_login_error,
            'register_success': self.on_register_success,
            'register_error': self.on_register_error,
            'queue_joined': self.on_queue_joined,
            'game_found': self.on_game_found,
            'move_played': self.on_move_played,
            'game_over': self.on_game_over,
            'your_turn': self.on_your_turn
        }
        self.socket_client.set_callbacks(callbacks)

    def on_connect(self):
        print("Connecté au serveur")

    def on_login_success(self, data):
        self.root.after(0, lambda: self.show_view("menu"))

    def on_queue_joined(self, data):
        self.root.after(0, lambda: self.show_view("waiting"))

    def on_game_found(self, data):
        self.root.after(0, lambda: (
            self.views["game"].setup_game(data),
            self.show_view("game")
        ))


    def run(self):
        self.socket_client.connect()
        self.root.mainloop()