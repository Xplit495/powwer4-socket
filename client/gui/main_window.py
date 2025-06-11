import customtkinter as ctk

from .game_view import GameView
from .login_view import LoginView
from .menu_view import MenuView
from .waiting_view import WaitingView

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Puissance 4 Online"

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
            'your_turn': self.on_your_turn,
            'forfeit': self.on_forfeit
        }
        self.socket_client.set_callbacks(callbacks)

    def on_connect(self):
        print("Connecté au serveur")

    def on_disconnect(self):
        print("Déconnecté du serveur")
        self.root.after(0, lambda: self.show_view("login"))

    def on_login_success(self, data):
        print("Connexion réussie")
        self.current_user = data
        self.root.after(0, lambda: self.show_view("menu"))

    def on_login_error(self, data):
        print(f"Erreur de connexion: {data.get('message', 'Erreur inconnue')}")
        self.root.after(0, lambda: self.views["login"].login_error.configure(
            text=data.get('message', 'Erreur de connexion')
        ))

    def on_register_success(self, data):
        print("Inscription réussie")
        self.root.after(0, lambda: (
            self.views["login"].tabview.set("Connexion"),
            self.views["login"].register_error.configure(text="Inscription réussie ! Vous pouvez vous connecter.")
        ))

    def on_register_error(self, data):
        print(f"Erreur d'inscription: {data.get('message', 'Erreur inconnue')}")
        self.root.after(0, lambda: self.views["login"].register_error.configure(
            text=data.get('message', 'Erreur d\'inscription')
        ))

    def on_queue_joined(self, data):
        print("File d'attente rejointe")
        self.root.after(0, lambda: self.show_view("waiting"))

    def on_game_found(self, data):
        print("Partie trouvée !")
        self.root.after(0, lambda: (
            self.views["game"].setup_game(data),
            self.show_view("game")
        ))

    def on_move_played(self, data):
        print(f"Mouvement joué: {data}")
        self.root.after(0, lambda: (
            self.views["game"].update_board(data.get('board', [])),
            setattr(self.views["game"], 'is_my_turn', data.get('your_turn', False)),
            self.views["game"].update_status()
        ))

    def on_your_turn(self, data):
        print("C'est votre tour !")
        self.root.after(0, lambda: (
            setattr(self.views["game"], 'is_my_turn', True),
            self.views["game"].update_status()
        ))

    def on_game_over(self, data):
        print(f"Partie terminée: {data}")
        winner = data.get('winner')
        if winner == 'draw':
            message = "Match nul !"
        elif winner == self.current_user.get('username'):
            message = "Vous avez gagné !"
        else:
            message = f"{winner} a gagné !"

        self.root.after(0, lambda: (
            print(message),
            self.show_view("menu")
        ))

    def on_forfeit(self, data):
        print(f"Forfait détecté: {data}")
        forfeit_player = data.get('forfeit_player')
        winner = data.get('winner')

        if forfeit_player == self.current_user.get('username'):
            message = "Vous avez abandonné la partie."
        else:
            message = f"{forfeit_player} a abandonné. Vous gagnez !"

        self.root.after(0, lambda: (
            print(message),
            self.show_view("menu")
        ))

    def run(self):
        self.socket_client.connect()
        self.root.mainloop()