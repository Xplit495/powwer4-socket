import threading

import customtkinter as ctk
import socketio

from gui import GameView, LoginView, MenuView, WaitingView

SERVER_URL = "http://localhost:5000"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

class SocketToGui:
    def __init__(self):
        # Initialize the socket client and create a root window for the GUI
        self.socketio = socketio.Client()

        self.username = None

        self.root = ctk.CTk()
        self.root.title("Puissance 4 Online")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.container = ctk.CTkFrame(self.root)
        self.container.pack(fill="both", expand=True)

        self.views = {
            "login": LoginView(self.container, self),
            "waiting": WaitingView(self.container, self),
            "game": GameView(self.container, self)
        }

        self.show_view("login")

        # Define socket event and GUI interaction handlers
        @self.socketio.on('register_success')
        def on_register_success():
            print("Enregistrement réussi !")
            self.root.after(0, self.views["login"].tabview.set, "Connexion")

        @self.socketio.on('register_error')
        def on_register_error(data):
            error_message = data.get('message')
            print(error_message)
            self.root.after(0, self.views["login"].register_error.configure, error_message)

        @self.socketio.on('login_success')
        def on_login_success(data):
            self.username = data.get('player_username')
            print("Connexion réussie ! Bienvenue,", self.username)
            self.views["menu"] = MenuView(self.container, self)
            self.root.after(0, self.show_view, "menu")

        @self.socketio.on('login_error')
        def on_login_error(data):
            error_message = data.get('message')
            print(error_message)
            self.root.after(0, self.views["login"].login_error.configure, error_message)

        @self.socketio.on('logout_success')
        def on_logout_success():
            print("Déconnexion réussie !")
            self.username = None
            self.socketio.disconnect()
            self.socketio.connect(SERVER_URL)
            self.root.after(0, self.show_view, "login")

        @self.socketio.on('queue_joined')
        def on_queue_joined(data):
            queue_size = data.get('size')
            print(f"File d'attente rejointe, il y a {queue_size} joueurs dans la queue.")
            self.root.after(0, self.show_view, "waiting")

        @self.socketio.on('queue_left')
        def on_queue_left():
            print("File d'attente quittée.")
            self.root.after(0, self.show_view, "menu")

        @self.socketio.on('game_found')
        def on_game_found(data):
            print(f"Partie trouvée ! Adversaire: {data.get('opponent_username')}")
            self.root.after(0, self.setup_and_show_game, data)

        @self.socketio.on('game_over')
        def on_game_over(data):
            winner = data.get('winner')
            reason = data.get('reason')

            print("Partie terminée !")

            if reason == "forfeit":
                player_who_forfeit = data.get('player_who_forfeit')
                if player_who_forfeit == self.username:
                    message = "Vous avez abandonné la partie. Vous avez perdu"
                else:
                    message = f"{player_who_forfeit} a abandonné la partie. Vous avez gagné"
            elif reason == "victory":
                if winner == self.username:
                    message = "Vous avez gagné la partie !"
                else:
                    message = f"{winner} a gagné la partie. Vous avez perdu"
            else:
                message = "La partie s'est terminée par une égalité."

            print(message)

            self.root.after(0, self.show_view, "menu")

        @self.socketio.on('move_error')
        def on_move_error(data):
            error_message = data.get('message')
            print(error_message)

        @self.socketio.on('move_played')
        def on_move_played(data):
            grid = data.get('grid')
            self.root.after(0, self.update_game_state, grid)

        @self.socketio.on('your_turn')
        def on_your_turn(data):
            is_my_turn = data.get('your_turn')
            print("C'est votre tour de jouer !")
            self.root.after(0, self.update_turn, is_my_turn)

    # Utils methods for GUI interaction
    def setup_and_show_game(self, data):
        self.views["game"].setup_game(data)
        self.show_view("game")

    def update_game_state(self, grid):
       game_view = self.views["game"]
       game_view.update_board(grid)

    def update_turn(self, is_my_turn):
        game_view = self.views["game"]
        game_view.is_my_turn = is_my_turn
        game_view.update_status()

    def show_view(self, view_name):
        for view in self.views.values():
            view.hide()
        self.views[view_name].show()

    def run(self):
        def connect_socket_thread():
            try:
                self.socketio.connect(SERVER_URL)
                print("Lien établi avec le serveur, vous êtes en ligne !")
            except Exception as e:
                print(f"Erreur de connexion: {e} - Assurez-vous que le serveur est en ligne.")

        thread = threading.Thread(target=connect_socket_thread, daemon=True)
        thread.start()

        self.root.mainloop()